/** Streaming Claude answer with footnote-style citation superscripts.
 *
 * Inline ``[playbook-id]`` matches in the model output are remapped to
 * small numbered superscripts (¹ ² ³ …) using the ``citations`` map
 * built by the parent. The map is sourced from ``citation_index`` —
 * resolved server-side against the full playbook corpus — so every
 * citation in the prose is guaranteed to map to a real playbook the
 * operator can open. A citation that the model emitted but that no
 * longer exists in the corpus (hallucinated id) is silently dropped:
 * we never render a broken ``?`` marker that would shake trust in the
 * surrounding prose.
 *
 * Citations whose target wasn't in the retrieved top-K (``in_topk =
 * false``) render with a subtly muted style so the operator can tell
 * "the model leaned on a source we didn't show it" apart from "the
 * model anchored on what we retrieved" — without breaking the visual
 * flow of the answer.
 *
 * The hover card is rendered through a React portal into
 * ``document.body`` so it sits above every parent — important because
 * the chat panel uses ``overflow-y: auto`` and any in-DOM popover
 * would be clipped by the scroll container.
 *
 * The text is preprocessed so every ``[playbook-id]`` becomes
 * ``cite:<id>`` wrapped in inline-code; ReactMarkdown then routes it
 * through the ``code`` override below.
 */
import { useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import type { CitationIndexEntry, RetrievalHitOut } from '../lib/types';


export interface CitationInfo {
  number: number;
  title: string;
  description?: string;
  in_topk: boolean;
}


const CITATION_GLOBAL_RE = /(\[[a-z0-9][a-z0-9_-]+\])/g;


function preprocess(text: string): string {
  return text.replace(CITATION_GLOBAL_RE, (full) => '`cite:' + full.slice(1, -1) + '`');
}


export function ChatAnswer({
  text,
  citations,
}: {
  text: string;
  citations: Map<string, CitationInfo>;
}) {
  const processed = useMemo(() => preprocess(text), [text]);

  return (
    <div className="prose prose-sm prose-slate max-w-none min-w-0 break-words prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-pre:overflow-x-auto prose-headings:font-semibold prose-headings:tracking-tight prose-p:leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code(props) {
            const { children, className } = props as {
              children: React.ReactNode;
              className?: string;
            };
            const raw = String(children ?? '');
            const m = raw.match(/^cite:(.+)$/);
            if (m) {
              const id = m[1];
              const info = citations.get(id);
              if (info) {
                return <CitationLink id={id} info={info} />;
              }
              // The citation marker is in the prose but we don't have a
              // resolved entry yet. Two cases:
              //
              //   • During streaming, before the `done` event lands the
              //     full citation_index, some ids may not yet resolve.
              //     We render nothing rather than a placeholder so the
              //     text reads cleanly; once the index arrives, this
              //     code re-renders and the pill appears in place.
              //
              //   • Hallucinated id (does not exist in the corpus). We
              //     also render nothing — a broken ``?`` marker would
              //     shake the operator's trust in the surrounding prose
              //     even though the underlying claim may be correct.
              return null;
            }
            return (
              <code
                className={
                  className ?? 'px-1 py-0 bg-hover text-ink-body rounded text-[0.9em]'
                }
              >
                {children}
              </code>
            );
          },
        }}
      >
        {processed}
      </ReactMarkdown>
    </div>
  );
}


// ---------------------------------------------------------------------------
// CitationLink — superscript anchor + portal-rendered hover preview
// ---------------------------------------------------------------------------

const POPOVER_WIDTH = 320;
const POPOVER_GAP = 8;
const SHOW_DELAY_MS = 200;
const HIDE_DELAY_MS = 80;

interface PopoverPos {
  top: number;
  left: number;
}


function CitationLink({ id, info }: { id: string; info: CitationInfo }) {
  const anchorRef = useRef<HTMLSpanElement | null>(null);
  const showTimerRef = useRef<number | null>(null);
  const hideTimerRef = useRef<number | null>(null);
  const [pos, setPos] = useState<PopoverPos | null>(null);

  function computePos(): PopoverPos {
    const el = anchorRef.current;
    if (!el) return { top: 0, left: 0 };
    const rect = el.getBoundingClientRect();
    const vw = window.innerWidth;
    // Always open upward so the popover never overlaps the pinned chat input
    // at the bottom of the panel. The portal uses translateY(-100%) to flip
    // the card above the anchor.
    const centerX = rect.left + rect.width / 2;
    let left = centerX - POPOVER_WIDTH / 2;
    left = Math.max(8, Math.min(left, vw - POPOVER_WIDTH - 8));
    const top = rect.top - POPOVER_GAP;
    return { top, left };
  }

  function open() {
    if (hideTimerRef.current) {
      window.clearTimeout(hideTimerRef.current);
      hideTimerRef.current = null;
    }
    if (pos) return;
    showTimerRef.current = window.setTimeout(() => {
      setPos(computePos());
    }, SHOW_DELAY_MS);
  }

  function close() {
    if (showTimerRef.current) {
      window.clearTimeout(showTimerRef.current);
      showTimerRef.current = null;
    }
    hideTimerRef.current = window.setTimeout(() => {
      setPos(null);
    }, HIDE_DELAY_MS);
  }

  return (
    <>
      <span
        ref={anchorRef}
        className="sp-citation-wrap"
        onMouseEnter={open}
        onMouseLeave={close}
        onFocus={open}
        onBlur={close}
      >
        <Link
          to={`/knowledge/${id}`}
          className={
            info.in_topk
              ? 'sp-citation'
              : 'sp-citation sp-citation-soft'
          }
          title={
            info.in_topk
              ? undefined
              : 'Source from broader corpus (not in retrieved top-K)'
          }
        >
          {info.number}
        </Link>
      </span>
      {pos &&
        createPortal(
          <div
            role="tooltip"
            onMouseEnter={open}
            onMouseLeave={close}
            style={{
              position: 'fixed',
              top: pos.top,
              left: pos.left,
              width: POPOVER_WIDTH,
              transform: 'translateY(-100%)',
              zIndex: 9999,
            }}
            className="bg-card border border-line rounded-lg shadow-lg p-4 text-[12px] font-sans"
          >
            <div className="text-[13px] font-semibold text-ink leading-snug mb-1">
              {info.title}
            </div>
            {info.description && (
              <div className="text-[12px] text-ink-body leading-relaxed line-clamp-3 mb-2">
                {info.description}
              </div>
            )}
            <div className="flex items-center justify-between gap-2">
              <Link
                to={`/knowledge/${id}`}
                className="text-[11px] font-medium text-accent-fg hover:underline"
              >
                Open playbook →
              </Link>
              {!info.in_topk && (
                <span className="text-[10px] text-ink-muted">
                  not in retrieved set
                </span>
              )}
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}


/** Build the ``{playbook_id → {number, title, in_topk}}`` map.
 *
 * Resolution sources, in priority order:
 *
 *   1. ``citation_index`` — the server-resolved canonical map. Every
 *      ``[id]`` that appears in the answer is looked up against the
 *      FULL playbook corpus on the backend, so citations to sources
 *      outside the retrieved top-K still resolve to a real playbook
 *      with metadata. This is the source of truth once the ``done``
 *      event has landed (or when re-loading a saved session).
 *
 *   2. ``retrievedSources`` — the top-K hits. Used as a fallback so
 *      citations resolve mid-stream (before the index arrives) and so
 *      old saved sessions without a citation_index still render
 *      something useful.
 *
 * Numbers are assigned by **first appearance** of the id in the
 * answer; ids that were retrieved but never cited pick up the next
 * numbers so the side rail and the prose stay in sync (1, 2, 3, …).
 * Hallucinated ids (not present in either source) get no entry — the
 * markdown renderer drops them rather than rendering a broken marker.
 */
export function buildCitationMap(
  answerText: string,
  retrievedSources: RetrievalHitOut[],
  citationIndex: CitationIndexEntry[] = [],
): Map<string, CitationInfo> {
  // citation_index is the canonical resolver. Skip hallucinated ids
  // (exists=false) so they never reach the prose.
  const fromIndex = new Map<string, CitationIndexEntry>();
  for (const entry of citationIndex) {
    if (entry.exists !== false) fromIndex.set(entry.playbook_id, entry);
  }
  const fromTopK = new Map<string, RetrievalHitOut>();
  for (const s of retrievedSources) fromTopK.set(s.playbook_id, s);

  function resolve(
    id: string,
  ): { title: string; description?: string; in_topk: boolean } | null {
    const entry = fromIndex.get(id);
    if (entry) {
      return {
        title: entry.title,
        description: entry.description,
        in_topk: entry.in_topk,
      };
    }
    const hit = fromTopK.get(id);
    if (hit) {
      return {
        title: hit.title,
        description: hit.description,
        in_topk: true,
      };
    }
    return null;
  }

  const map = new Map<string, CitationInfo>();
  let counter = 1;

  for (const match of answerText.matchAll(CITATION_GLOBAL_RE)) {
    const id = match[0].slice(1, -1);
    if (map.has(id)) continue;
    const meta = resolve(id);
    if (meta) {
      map.set(id, { number: counter++, ...meta });
    }
  }
  // Retrieved-but-uncited top-K sources still get a number so the
  // (optional) side rail can list them with stable indices.
  for (const s of retrievedSources) {
    if (!map.has(s.playbook_id)) {
      map.set(s.playbook_id, {
        number: counter++,
        title: s.title,
        description: s.description,
        in_topk: true,
      });
    }
  }
  return map;
}
