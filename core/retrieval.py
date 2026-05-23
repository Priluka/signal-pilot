"""Playbook indexing and filtered retrieval.

Loads markdown playbooks with YAML frontmatter from ``config.PLAYBOOKS_DIR``,
embeds the searchable surface (title + description + "When this applies"
section), persists vectors to an .npz cache keyed by file mtime, and exposes
``retrieve()`` — language- and country-filtered cosine top-k.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import yaml

import config
from core.embeddings import EmbeddingProvider, get_embedding_provider


# Files that live in the playbooks tree but are not playbooks.
_NON_PLAYBOOK_BASENAMES = {"_index.md", "README.md"}

# Map of free-text country tokens (commonly seen in Jira labels OR in the
# body of the query itself, e.g. an operator typing "stuck session u Beču")
# to ISO codes. Covers English country names, Croatian adjectives (the
# operator's native voice), and the major cities in each country — most
# location hints in real tickets are city names, not country names.
_COUNTRY_TOKEN_TO_ISO: dict[str, str] = {
    # English country names + ISO
    "croatia": "hr", "croatian": "hr", "hr": "hr",
    "italy": "it", "italian": "it", "italia": "it", "it": "it",
    "austria": "at", "austrian": "at", "at": "at",
    "slovakia": "sk", "slovak": "sk", "sk": "sk",
    "germany": "de", "german": "de", "deutschland": "de", "de": "de",
    # Croatian adjectives + country-name stems. Operators commonly
    # write tickets in Croatian about customers in other countries.
    # Stems (e.g. "italij") combined with the declension suffixes in
    # _COUNTRY_TEXT_RE cover all noun cases of the country name:
    # "Italija" / "Italije" / "Italiji" / "Italiju" / "Italijom".
    "hrvatska": "hr", "hrvatski": "hr", "hrvatsk": "hr",
    "talijanski": "it", "talijanska": "it", "talijan": "it", "italij": "it",
    "austrijski": "at", "austrijska": "at", "austrijanac": "at", "austrij": "at",
    "slovački": "sk", "slovačka": "sk", "slovačk": "sk",
    "njemački": "de", "njemačka": "de", "nijemac": "de", "njemačk": "de",
    # Cities — most location hints in the wild are city names
    "zagreb": "hr", "rijeka": "hr", "osijek": "hr",
    "dubrovnik": "hr", "zadar": "hr", "pula": "hr",
    "rome": "it", "roma": "it", "milan": "it", "milano": "it",
    "naples": "it", "napoli": "it", "turin": "it", "torino": "it",
    "florence": "it", "firenze": "it", "venice": "it", "venezia": "it",
    "bologna": "it", "bari": "it", "palermo": "it",
    "vienna": "at", "wien": "at", "beč": "at",
    "salzburg": "at", "graz": "at", "linz": "at",
    "innsbruck": "at", "klagenfurt": "at",
    "bratislava": "sk", "košice": "sk", "kosice": "sk",
    "berlin": "de", "munich": "de", "münchen": "de", "muenchen": "de",
    "hamburg": "de", "frankfurt": "de", "köln": "de", "koeln": "de",
    "cologne": "de", "stuttgart": "de",
}

# Built once at import time — compiled re for free-text country/city
# detection in queries. Two subtleties:
#
#   1. Only tokens >= 3 chars are eligible for text matching. The
#      two-letter ISO codes ("at", "it", "de") would over-match common
#      English words (e.g. "items" matches "it") and only make sense
#      as exact label tokens, handled separately by country_from_labels.
#
#   2. Tokens are followed by an OPTIONAL declension/plural suffix from
#      a fixed list — enough to absorb Croatian noun declensions
#      ("Beč" + "u" = "Beču", locative case) and English plurals
#      ("Italian" + "s"), but tight enough that "rome" doesn't match
#      inside "romeo" and "bari" doesn't match inside "barista".
_TEXT_TOKENS = {k: v for k, v in _COUNTRY_TOKEN_TO_ISO.items() if len(k) >= 3}

_COUNTRY_TEXT_RE = re.compile(
    r"\b(" + "|".join(
        re.escape(tok) for tok in sorted(_TEXT_TOKENS, key=len, reverse=True)
    ) + r")(?:a|e|i|u|oj|om|em|ima|ama|s|ski|ska|sko|ske|skog|skim|skih)?\b",
    re.IGNORECASE | re.UNICODE,
)

# Bump applied to embedding similarity for playbooks whose country_focus
# matches the location hint. Cosine sims live roughly in [0.3, 0.8]; a
# bump of 0.10 is enough to flip rank when the embedding margin is small
# but not enough to override a strong semantic mismatch.
_COUNTRY_BOOST = 0.10

# Same magnitude as the country boost — applied per-playbook when the
# query carries one of the playbook's signature keywords. Used to nail
# down high-confidence routes that pure semantic similarity misses (e.g.
# an Italian-language "noleggio + addebito fantasma" query should land
# on the rental-car ghost-charge playbook regardless of how the embedder
# ranks Italian phrasing against Croatian playbook text).
_KEYWORD_BOOST = 0.10

# {playbook_id: [compiled regex patterns]} — when ANY pattern matches
# the query text, the named playbook gets a score bump in search(). Keep
# this dict tight: only add an entry when the playbook is unambiguously
# the right route for the keyword (false positives here are worse than
# nothing, because they bias retrieval). All patterns are word-bounded
# and case-insensitive.
_PLAYBOOK_KEYWORD_BOOSTS: dict[str, list[str]] = {
    # Tourist returns rental car → next renter triggers a Ticketless
    # charge against the previous holder's still-linked Bmove account.
    # Signature tokens across the four big languages we see.
    "croatia-ticketless-rental-car-ghost-charge": [
        r"\bnoleggio\b",      # IT
        r"\bnoleggi\w*\b",    # IT declensions (noleggiata, noleggiare)
        r"\baddebito fantasma\b",  # IT "ghost charge"
        r"\brental\b",        # EN
        r"\brent[- ]?a[- ]?car\b",  # EN
        r"\bMietwagen\b",     # DE
        r"\bnajam\b",         # HR
        r"\bnajml?j?en\w*\b", # HR declensions (najmljen, najmljeno, najmljena)
        r"\bghost charge\b",  # EN
        r"\bphantom charge\b",  # EN
    ],
}
_PLAYBOOK_KEYWORD_RES: dict[str, list] = {
    pb_id: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in pats]
    for pb_id, pats in _PLAYBOOK_KEYWORD_BOOSTS.items()
}


def keyword_boosted_playbooks(text: str) -> set[str]:
    """Return the set of playbook ids the query text should boost.

    Returns the empty set when no signature keywords are present, which
    is the common case. The set is consumed by ``PlaybookIndex.search``
    as a soft preference on top of the embedding rank.
    """
    if not text:
        return set()
    out: set[str] = set()
    for pb_id, patterns in _PLAYBOOK_KEYWORD_RES.items():
        if any(p.search(text) for p in patterns):
            out.add(pb_id)
    return out

_SECTION_RE = re.compile(
    r"^#{2,}\s+(?P<title>.+?)\s*\n(?P<body>.*?)(?=^#{2,}\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_FRONTMATTER_RE = re.compile(r"^---\n(?P<yaml>.*?)\n---\n(?P<body>.*)$", re.DOTALL)


def extract_section(body: str, *needles: str) -> str:
    """Return the body of the first ``## Heading`` (any level ≥2) whose title
    contains any of *needles* (case-insensitive). Empty string if no match.
    """
    needles_lower = [n.lower() for n in needles]
    for match in _SECTION_RE.finditer(body):
        title = match.group("title").lower()
        if any(n in title for n in needles_lower):
            return match.group("body").strip()
    return ""


@dataclass
class Playbook:
    """One markdown playbook, parsed."""

    id: str
    path: Path
    title: str
    description: str
    category: str
    ticket_class: str
    issue_category: str
    languages: list[str]
    country_focus: list[str]
    resolution_pattern: str
    when_applies: str
    resolution_flow: str
    typical_actions: str
    risks: str
    body: str
    raw: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def search_text(self) -> str:
        """The concatenated surface we embed for retrieval."""
        parts = [self.title, self.description]
        if self.when_applies:
            parts.append(self.when_applies)
        return "\n\n".join(p for p in parts if p)


@dataclass
class RetrievalHit:
    """A retrieval result, ranked."""

    playbook: Playbook
    score: float
    rank: int


def _parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    match = _FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError("Missing or malformed YAML frontmatter")
    meta = yaml.safe_load(match.group("yaml")) or {}
    if not isinstance(meta, dict):
        raise ValueError("Frontmatter did not parse to a mapping")
    return meta, match.group("body")


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def load_playbook(path: Path) -> Playbook:
    raw = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)
    pb_id = str(meta.get("id") or path.stem)
    return Playbook(
        id=pb_id,
        path=path,
        title=str(meta.get("title", pb_id)),
        description=str(meta.get("description", "")),
        category=str(meta.get("category", "")),
        ticket_class=str(meta.get("ticket_class", "")),
        issue_category=str(meta.get("issue_category", "")),
        languages=[s.lower() for s in _as_str_list(meta.get("languages"))],
        country_focus=[s.lower() for s in _as_str_list(meta.get("country_focus"))],
        resolution_pattern=str(meta.get("resolution_pattern", "")),
        when_applies=extract_section(body, "When this applies"),
        resolution_flow=extract_section(body, "Typical resolution flow", "Resolution flow"),
        typical_actions=extract_section(body, "Typical actions"),
        risks=extract_section(body, "Safety constraints", "Risks"),
        body=body,
        raw=raw,
        metadata=meta,
    )


def discover_playbook_paths(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.md")
        if p.name not in _NON_PLAYBOOK_BASENAMES
    )


def _signature(paths: Sequence[Path]) -> str:
    """Hash of (relative_path, mtime, size) tuples so the cache invalidates
    whenever any indexed file changes."""
    hasher = hashlib.sha256()
    for p in paths:
        stat = p.stat()
        hasher.update(p.name.encode())
        hasher.update(str(stat.st_mtime_ns).encode())
        hasher.update(str(stat.st_size).encode())
    return hasher.hexdigest()


class PlaybookIndex:
    """In-memory index over playbooks with cached embeddings."""

    def __init__(
        self,
        playbooks: list[Playbook],
        embeddings: np.ndarray,
        provider_name: str,
    ) -> None:
        if len(playbooks) != embeddings.shape[0]:
            raise ValueError("playbooks/embeddings length mismatch")
        self.playbooks = playbooks
        self.embeddings = embeddings  # (N, dim), L2-normalized
        self.provider_name = provider_name
        self._by_id = {p.id: p for p in playbooks}

    def __len__(self) -> int:
        return len(self.playbooks)

    def get(self, playbook_id: str) -> Playbook | None:
        return self._by_id.get(playbook_id)

    def filtered_indices(
        self,
        country: str | None,
        language: str | None,
        ticket_class: str | None,
    ) -> np.ndarray:
        keep = np.ones(len(self.playbooks), dtype=bool)
        for i, pb in enumerate(self.playbooks):
            if ticket_class and pb.ticket_class and pb.ticket_class != ticket_class:
                keep[i] = False
                continue
            if country and pb.country_focus:
                if country not in pb.country_focus and "other" not in pb.country_focus:
                    keep[i] = False
                    continue
            if language and pb.languages:
                if language not in pb.languages and "other" not in pb.languages:
                    keep[i] = False
        return np.flatnonzero(keep)

    def search(
        self,
        query_vector: np.ndarray,
        *,
        country: str | None = None,
        language: str | None = None,
        ticket_class: str | None = None,
        country_boost: str | None = None,
        keyword_boost_ids: set[str] | None = None,
        top_k: int = config.TOP_K_RETRIEVAL,
        min_confidence: float = config.MIN_RETRIEVAL_CONFIDENCE,
    ) -> list[RetrievalHit]:
        candidates = self.filtered_indices(country, language, ticket_class)
        # Fallback: if filters wiped everything out, search the full index so
        # we always return *something* — the UI can warn on low confidence.
        if candidates.size == 0:
            candidates = np.arange(len(self.playbooks))
        sims = self.embeddings[candidates] @ query_vector
        # Country boost: when the query carries a location hint, lift the
        # score of playbooks whose ``country_focus`` explicitly contains
        # that ISO code. Tuned to flip rank when the embedding margin is
        # small (e.g. "Italian invoice" vs a generic invoice playbook),
        # not enough to override a strong semantic mismatch.
        if country_boost:
            for local_idx, global_idx in enumerate(candidates):
                if country_boost in self.playbooks[int(global_idx)].country_focus:
                    sims[local_idx] += _COUNTRY_BOOST
        # Keyword boost: per-playbook signature tokens lifted when the
        # query unambiguously routes there ("noleggio + addebito" → the
        # rental ghost-charge playbook).
        if keyword_boost_ids:
            for local_idx, global_idx in enumerate(candidates):
                if self.playbooks[int(global_idx)].id in keyword_boost_ids:
                    sims[local_idx] += _KEYWORD_BOOST
        order = np.argsort(-sims)[:top_k]
        hits: list[RetrievalHit] = []
        for rank, local_idx in enumerate(order):
            score = float(sims[local_idx])
            if score < min_confidence and rank > 0:
                break
            global_idx = int(candidates[local_idx])
            hits.append(
                RetrievalHit(
                    playbook=self.playbooks[global_idx],
                    score=score,
                    rank=rank,
                )
            )
        return hits


def _load_cache(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = np.load(path, allow_pickle=False)
        return {
            "signature": str(data["signature"]),
            "provider": str(data["provider"]),
            "ids": [str(x) for x in data["ids"].tolist()],
            "embeddings": data["embeddings"],
        }
    except Exception:
        return None


def _save_cache(path: Path, *, signature: str, provider: str, ids: list[str], embeddings: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        signature=np.array(signature),
        provider=np.array(provider),
        ids=np.array(ids),
        embeddings=embeddings,
    )


def build_index(
    *,
    playbooks_dir: Path = config.PLAYBOOKS_DIR,
    cache_path: Path = config.EMBEDDING_CACHE_PATH,
    provider: EmbeddingProvider | None = None,
) -> PlaybookIndex:
    provider = provider or get_embedding_provider()
    paths = discover_playbook_paths(playbooks_dir)
    if not paths:
        raise FileNotFoundError(f"No playbooks found under {playbooks_dir}")
    playbooks = [load_playbook(p) for p in paths]
    signature = _signature(paths)

    cache = _load_cache(cache_path)
    cache_hit = (
        cache is not None
        and cache["signature"] == signature
        and cache["provider"] == provider.name
        and cache["ids"] == [pb.id for pb in playbooks]
    )
    if cache_hit:
        assert cache is not None  # narrow for type-checker; cache_hit implies non-None
        embeddings = cache["embeddings"].astype(np.float32)
    else:
        embeddings = provider.embed_matrix([pb.search_text for pb in playbooks])
        _save_cache(
            cache_path,
            signature=signature,
            provider=provider.name,
            ids=[pb.id for pb in playbooks],
            embeddings=embeddings,
        )

    return PlaybookIndex(playbooks=playbooks, embeddings=embeddings, provider_name=provider.name)


def detect_language(text: str) -> str | None:
    """Best-effort ISO 639-1 language code. None on failure or empty input."""
    if not text or not text.strip():
        return None
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        return detect(text).lower()
    except Exception:
        return None


def country_from_labels(labels: Iterable[str]) -> str | None:
    """Map Jira label tokens like 'croatia' to ISO codes like 'hr'."""
    for label in labels:
        token = str(label).strip().lower()
        if token in _COUNTRY_TOKEN_TO_ISO:
            return _COUNTRY_TOKEN_TO_ISO[token]
    return None


def country_from_text(text: str) -> str | None:
    """Detect a country ISO code from a free-text query.

    Scans the query for any known country name, adjective, or major city
    (see ``_COUNTRY_TOKEN_TO_ISO``) and returns the first match. The
    point is to handle operator queries like ``"stuck session u Beču"``
    (Vienna mentioned in Croatian sentence) or ``"Italian invoice
    requests"`` (country adjective) that would otherwise route purely
    on the detected sentence language and miss the country-specific
    playbook.

    Returns ``None`` if nothing is found.
    """
    if not text:
        return None
    match = _COUNTRY_TEXT_RE.search(text)
    if not match:
        return None
    return _TEXT_TOKENS[match.group(1).lower()]


def retrieve(
    index: PlaybookIndex,
    ticket_text: str,
    *,
    labels: Iterable[str] | None = None,
    ticket_class: str | None = None,
    top_k: int = config.TOP_K_RETRIEVAL,
    provider: EmbeddingProvider | None = None,
) -> list[RetrievalHit]:
    """End-to-end retrieval for one ticket: detect language + country,
    embed, search.

    Country signal priority:

      1. Jira label match (``country_from_labels``) — the most reliable
         signal because the label was set deliberately. The detected
         language is also kept as a filter, since the ticket is usually
         written in the customer's language.

      2. Free-text country/city mention in the query
         (``country_from_text``) — fired e.g. by an operator typing
         ``"stuck session u Beču"``. When this is the only signal we
         deliberately drop the language filter, because the query
         language reflects the operator's voice (Croatian) and would
         otherwise wipe out the location-relevant playbook (tagged
         with the customer's language, e.g. German for Austria).

      3. Neither — fall back to language filter only, no country.

    The detected country (from labels OR text) is also passed as a
    soft score boost, so even when filtering would let a non-matching
    playbook through, the location-relevant one wins close calls.
    """
    provider = provider or get_embedding_provider()
    query_vector = np.asarray(provider.embed(ticket_text), dtype=np.float32)
    label_country = country_from_labels(labels or [])
    if label_country is not None:
        country: str | None = label_country
        language: str | None = detect_language(ticket_text)
    else:
        text_country = country_from_text(ticket_text)
        if text_country is not None:
            country = text_country
            language = None
        else:
            country = None
            language = detect_language(ticket_text)
    return index.search(
        query_vector,
        country=country,
        language=language,
        ticket_class=ticket_class,
        country_boost=country,
        keyword_boost_ids=keyword_boosted_playbooks(ticket_text),
        top_k=top_k,
    )
