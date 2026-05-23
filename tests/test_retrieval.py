"""Tests for core.retrieval.

These cover the deterministic logic — frontmatter parsing, filter rules,
language/country extraction, and top-k ranking — without loading the BGE-m3
model. A tiny ``StubEmbedder`` returns hand-crafted unit vectors so we know
exactly which playbook should rank where.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

import numpy as np
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.embeddings import EmbeddingProvider
from core.retrieval import (
    PlaybookIndex,
    build_index,
    country_from_labels,
    country_from_text,
    discover_playbook_paths,
    load_playbook,
    retrieve,
)


PLAYBOOK_PARKING = """---
id: hr-parking-fail
title: HR parking payment failure
description: Croatian users report failed parking payments.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
languages: [hr, en]
country_focus: [hr]
resolution_pattern: vendor_escalation
---

# HR parking payment failure

## When this applies

- User pays via app in Croatia and is later fined.

## Typical resolution flow

1. Acknowledge.
2. Escalate to vendor.
"""

PLAYBOOK_INVOICE = """---
id: it-invoice
title: Italian invoice request
description: Italian users ask for a missing invoice.
category: end_user/billing
ticket_class: end_user
issue_category: billing_request
languages: [it]
country_focus: [it]
resolution_pattern: self_service
---

# Italian invoice request

## When this applies

- Customer needs an invoice copy.
"""

PLAYBOOK_GENERIC = """---
id: generic-bug
title: Generic bug report
description: Anyone reports any bug.
category: end_user/bugs
ticket_class: end_user
issue_category: bug_in_product
languages: [other, en]
country_focus: [other]
resolution_pattern: triage
---

# Generic bug report

## When this applies

- Any unspecified bug.
"""


@pytest.fixture
def playbooks_dir(tmp_path: Path) -> Path:
    root = tmp_path / "playbooks"
    (root / "end_user" / "bugs").mkdir(parents=True)
    (root / "end_user" / "billing").mkdir(parents=True)
    (root / "end_user" / "bugs" / "hr-parking-fail.md").write_text(PLAYBOOK_PARKING)
    (root / "end_user" / "bugs" / "generic-bug.md").write_text(PLAYBOOK_GENERIC)
    (root / "end_user" / "billing" / "it-invoice.md").write_text(PLAYBOOK_INVOICE)
    # Decoys that must be skipped:
    (root / "end_user" / "bugs" / "_index.md").write_text("# Index — should be skipped")
    (root / "README.md").write_text("# Top-level README — should be skipped")
    return root


class StubEmbedder(EmbeddingProvider):
    """Deterministic 3-dim embedder. Each canonical text gets its own axis.

    Anything we haven't pre-registered embeds to a normalized vector built from
    a stable hash of the text — far from the three canonical axes, so it never
    accidentally outranks a real match.
    """

    name = "stub"
    dim = 3

    def __init__(self, axes: dict[str, np.ndarray]) -> None:
        self._axes = axes

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for text in texts:
            vec = None
            for needle, axis in self._axes.items():
                if needle in text:
                    vec = axis
                    break
            if vec is None:
                rng = np.random.default_rng(abs(hash(text)) % (2**32))
                vec = rng.standard_normal(self.dim).astype(np.float32)
                vec = vec / np.linalg.norm(vec)
            out.append(vec.tolist())
        return out


@pytest.fixture
def stub_embedder() -> StubEmbedder:
    return StubEmbedder(
        axes={
            "HR parking payment failure": np.array([1.0, 0.0, 0.0], dtype=np.float32),
            "Italian invoice request": np.array([0.0, 1.0, 0.0], dtype=np.float32),
            "Generic bug report": np.array([0.0, 0.0, 1.0], dtype=np.float32),
            # Queries align to the same axes so top-1 is deterministic.
            "parking": np.array([1.0, 0.0, 0.0], dtype=np.float32),
            "invoice": np.array([0.0, 1.0, 0.0], dtype=np.float32),
        }
    )


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------
def test_load_playbook_parses_frontmatter_and_when_applies(tmp_path: Path) -> None:
    path = tmp_path / "pb.md"
    path.write_text(PLAYBOOK_PARKING)
    pb = load_playbook(path)
    assert pb.id == "hr-parking-fail"
    assert pb.title == "HR parking payment failure"
    assert pb.country_focus == ["hr"]
    assert pb.languages == ["hr", "en"]
    assert "fined" in pb.when_applies
    # search_text should contain title + description + when_applies content.
    assert "HR parking payment failure" in pb.search_text
    assert "fined" in pb.search_text


def test_load_playbook_rejects_missing_frontmatter(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text("# just a heading\n\nno yaml here")
    with pytest.raises(ValueError):
        load_playbook(path)


def test_discover_skips_index_and_readme_files(playbooks_dir: Path) -> None:
    paths = discover_playbook_paths(playbooks_dir)
    names = {p.name for p in paths}
    assert "_index.md" not in names
    assert "README.md" not in names
    assert names == {"hr-parking-fail.md", "generic-bug.md", "it-invoice.md"}


# ---------------------------------------------------------------------------
# Country / label mapping
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "labels,expected",
    [
        (["croatia", "payment-issue"], "hr"),
        (["italy"], "it"),
        (["austrian", "bug"], "at"),
        (["sk", "test"], "sk"),
        (["payment-issue"], None),
        ([], None),
    ],
)
def test_country_from_labels(labels: list[str], expected: str | None) -> None:
    assert country_from_labels(labels) == expected


# ---------------------------------------------------------------------------
# Index build + filtered retrieval
# ---------------------------------------------------------------------------
def test_build_index_embeds_all_playbooks(playbooks_dir: Path, stub_embedder: StubEmbedder, tmp_path: Path) -> None:
    index = build_index(
        playbooks_dir=playbooks_dir,
        cache_path=tmp_path / "cache.npz",
        provider=stub_embedder,
    )
    assert len(index) == 3
    assert index.embeddings.shape == (3, 3)


def test_search_filters_by_country_keeps_match_and_other(playbooks_dir: Path, stub_embedder: StubEmbedder, tmp_path: Path) -> None:
    index = build_index(
        playbooks_dir=playbooks_dir,
        cache_path=tmp_path / "cache.npz",
        provider=stub_embedder,
    )
    # Query aligns with HR parking; filter to country='hr' should retain
    # hr-parking-fail (hr) and generic-bug (other), exclude it-invoice.
    qvec = np.asarray(stub_embedder.embed("parking"), dtype=np.float32)
    hits = index.search(qvec, country="hr", language=None, ticket_class="end_user", top_k=3)
    ids = [h.playbook.id for h in hits]
    assert "it-invoice" not in ids
    assert hits[0].playbook.id == "hr-parking-fail"


def test_search_falls_back_to_full_index_when_filters_empty(playbooks_dir: Path, stub_embedder: StubEmbedder, tmp_path: Path) -> None:
    index = build_index(
        playbooks_dir=playbooks_dir,
        cache_path=tmp_path / "cache.npz",
        provider=stub_embedder,
    )
    # No playbook is country_focus=[us], so all should be filtered out;
    # we still expect a hit list back rather than an empty result.
    qvec = np.asarray(stub_embedder.embed("invoice"), dtype=np.float32)
    hits = index.search(qvec, country="us", language=None, ticket_class="end_user", top_k=2)
    assert len(hits) >= 1


def test_top_k_ordering_is_deterministic(playbooks_dir: Path, stub_embedder: StubEmbedder, tmp_path: Path) -> None:
    index = build_index(
        playbooks_dir=playbooks_dir,
        cache_path=tmp_path / "cache.npz",
        provider=stub_embedder,
    )
    qvec = np.asarray(stub_embedder.embed("invoice"), dtype=np.float32)
    hits1 = index.search(qvec, country=None, language=None, ticket_class=None, top_k=3)
    hits2 = index.search(qvec, country=None, language=None, ticket_class=None, top_k=3)
    assert [h.playbook.id for h in hits1] == [h.playbook.id for h in hits2]
    assert hits1[0].playbook.id == "it-invoice"


def test_cache_round_trip_uses_persisted_embeddings(playbooks_dir: Path, stub_embedder: StubEmbedder, tmp_path: Path) -> None:
    cache = tmp_path / "cache.npz"
    first = build_index(playbooks_dir=playbooks_dir, cache_path=cache, provider=stub_embedder)
    # Track that the second build does NOT recompute by handing it an embedder
    # that would raise if called.
    class ExplodingEmbedder(EmbeddingProvider):
        name = stub_embedder.name  # match cached provider name so the cache is honored
        dim = 3
        def embed(self, text: str) -> list[float]:
            raise AssertionError("should not embed — cache should be used")
        def embed_batch(self, texts):  # type: ignore[override]
            raise AssertionError("should not embed — cache should be used")

    second = build_index(playbooks_dir=playbooks_dir, cache_path=cache, provider=ExplodingEmbedder())
    np.testing.assert_array_equal(first.embeddings, second.embeddings)


# ---------------------------------------------------------------------------
# End-to-end retrieve()
# ---------------------------------------------------------------------------
def test_retrieve_end_to_end_with_labels(playbooks_dir: Path, stub_embedder: StubEmbedder, tmp_path: Path) -> None:
    index = build_index(
        playbooks_dir=playbooks_dir,
        cache_path=tmp_path / "cache.npz",
        provider=stub_embedder,
    )
    hits = retrieve(
        index,
        ticket_text="I tried to pay for parking but got a fine",
        labels=["croatia", "payment-issue"],
        provider=stub_embedder,
    )
    # parking query → hr-parking-fail axis; labels resolve to country=hr.
    assert hits[0].playbook.id == "hr-parking-fail"


# ---------------------------------------------------------------------------
# country_from_text — free-text city/country detection in queries
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text, expected",
    [
        # City names — the most common location signal in real queries
        ("stuck session u Beču", "at"),
        ("Vienna parking dispute", "at"),
        ("Wien session bug", "at"),
        ("customer in Rome", "it"),
        ("session in Milano", "it"),
        ("Munich charge issue", "de"),
        ("München session", "de"),
        ("Bratislava parking", "sk"),
        # Country adjectives / names in either language
        ("Italian invoice requests", "it"),
        ("austrijski korisnik dobio kaznu", "at"),
        ("talijanski zahtjev za fakturu", "it"),
        ("German customer query", "de"),
        # No location hint
        ("generic invoice question", None),
        ("how do I issue a refund", None),
        ("", None),
    ],
)
def test_country_from_text(text: str, expected: str | None) -> None:
    assert country_from_text(text) == expected


def test_retrieve_uses_text_country_when_no_label(
    playbooks_dir: Path, stub_embedder: StubEmbedder, tmp_path: Path
) -> None:
    """Operator writes about Italy in English; no labels → text-derived
    country should route to it-invoice over generic playbooks."""
    index = build_index(
        playbooks_dir=playbooks_dir,
        cache_path=tmp_path / "cache.npz",
        provider=stub_embedder,
    )
    hits = retrieve(
        index,
        ticket_text="Italian invoice request",
        labels=[],
        provider=stub_embedder,
    )
    assert hits[0].playbook.id == "it-invoice"


def test_search_country_boost_lifts_matching_playbook(
    playbooks_dir: Path, stub_embedder: StubEmbedder, tmp_path: Path
) -> None:
    """Without boost the embedding alone might prefer a generic match;
    with boost, a playbook explicitly tagged for the location wins
    close calls."""
    index = build_index(
        playbooks_dir=playbooks_dir,
        cache_path=tmp_path / "cache.npz",
        provider=stub_embedder,
    )
    qvec = np.asarray(stub_embedder.embed("invoice"), dtype=np.float32)
    # No boost → generic ranking
    baseline = index.search(qvec, top_k=3)
    boosted = index.search(qvec, country_boost="it", top_k=3)
    # Boosted ranking must place the it-tagged playbook at the top (or
    # at least no lower than baseline did).
    it_baseline_rank = next(
        (i for i, h in enumerate(baseline) if h.playbook.id == "it-invoice"),
        None,
    )
    it_boosted_rank = next(
        (i for i, h in enumerate(boosted) if h.playbook.id == "it-invoice"),
        None,
    )
    assert it_boosted_rank is not None
    if it_baseline_rank is not None:
        assert it_boosted_rank <= it_baseline_rank
