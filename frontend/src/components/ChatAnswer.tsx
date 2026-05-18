/** Streaming Claude answer with footnote-style citation superscripts.
 *
 * Inline ``[playbook-id]`` matches in the model output are remapped to small
 * blue superscript numbers (¹ ² ³ …) using the ``citations`` map built by
 * the parent. Each number is a hash link to the matching source card at the
 * bottom of the page and shows the source title in its native tooltip.
 *
 * The text is preprocessed so every ``[playbook-id]`` becomes ``cite:<id>``
 * wrapped in inline-code; ReactMarkdown then routes it through the ``code``
 * override below, which renders the <sup> link.
 */
import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';


export interface CitationInfo {
  number: number;
  title: string;
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
    <div className="prose prose-sm prose-slate max-w-none prose-pre:bg-slate-900 prose-pre:text-slate-100 prose-headings:font-semibold prose-headings:tracking-tight prose-p:leading-relaxed">
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
                return (
                  <Link
                    to={`/knowledge/${id}`}
                    title={info.title}
                    className="sp-citation"
                  >
                    {info.number}
                  </Link>
                );
              }
              // Citation marker but the id wasn't in our source list — render
              // it muted so the operator can still spot it.
              return (
                <span className="sp-citation sp-citation-unknown" title="Source not in retrieved set">
                  ?
                </span>
              );
            }
            return (
              <code
                className={className ?? 'px-1 py-0 bg-slate-100 text-slate-700 rounded text-[0.9em]'}
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


/** Build the {playbook_id → {number, title}} map.
 *
 * Numbers are assigned by **first appearance** of the id in the answer
 * text, then any retrieved-but-uncited source picks up the next number.
 * Result: cited sources read 1, 2, 3… in narrative order.
 */
export function buildCitationMap(
  answerText: string,
  retrievedSources: { playbook_id: string; title: string }[],
): Map<string, CitationInfo> {
  const known = new Map(retrievedSources.map((s) => [s.playbook_id, s.title]));
  const map = new Map<string, CitationInfo>();
  let counter = 1;

  for (const match of answerText.matchAll(CITATION_GLOBAL_RE)) {
    const id = match[0].slice(1, -1);
    if (known.has(id) && !map.has(id)) {
      map.set(id, { number: counter++, title: known.get(id)! });
    }
  }
  for (const s of retrievedSources) {
    if (!map.has(s.playbook_id)) {
      map.set(s.playbook_id, { number: counter++, title: s.title });
    }
  }
  return map;
}
