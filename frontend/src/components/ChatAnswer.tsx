/** Renders a streaming Claude answer with inline [playbook-id] citations.
 *
 * Pre-processes the markdown to wrap every ``[playbook-id]`` match in backticks
 * so ReactMarkdown emits a ``<code>`` element. The ``code`` override below
 * inspects the text — if it matches a citation pattern it renders a small
 * pill, otherwise it falls back to a normal inline code element.
 *
 * Citations whose ids appear in the ``citedIds`` set are highlighted blue;
 * others (rare — the model invented an id) render in muted slate.
 */
import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';


const CITATION_TOKEN_RE = /^\[([a-z0-9][a-z0-9_-]+)\]$/;
const CITATION_GLOBAL_RE = /(\[[a-z0-9][a-z0-9_-]+\])/g;


function preprocess(text: string): string {
  return text.replace(CITATION_GLOBAL_RE, '`$1`');
}


export function ChatAnswer({
  text,
  citedIds,
}: {
  text: string;
  citedIds: Set<string>;
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
            const m = raw.match(CITATION_TOKEN_RE);
            if (m) {
              const id = m[1];
              const isCited = citedIds.has(id);
              const tone = isCited
                ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'
                : 'bg-slate-50 text-slate-500 border-slate-200';
              return (
                <a
                  href={`/knowledge/${id}`}
                  className={`inline-flex items-center px-1 py-0 mx-0.5 rounded text-[10px] font-mono no-underline border ${tone}`}
                  title={isCited ? 'Cited source' : 'Suggested source (not cited)'}
                >
                  [{id}]
                </a>
              );
            }
            // Default inline-code rendering.
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
