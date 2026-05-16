/** Center column of the Knowledge page — playbook prose.
 *
 * Presentational only: the parent (KnowledgePage) owns the fetch and passes
 * the result down so the right-hand metadata sidebar can use the same data
 * without duplicating the request. Stats / related / evidence-ticket lists
 * live in the right sidebar; this column carries the title + narrative
 * sections + suggest-an-edit form.
 */
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { submitSuggestion } from '../lib/api';
import type { PlaybookDetail } from '../lib/types';

import {
  Chip,
  SectionHeading,
  StatusBadge,
  StepCircle,
  TicketChip,
} from './ui';


interface Props {
  playbook: PlaybookDetail | null;
  loading: boolean;
  error: string | null;
  hasSelection: boolean;
}


export function PlaybookViewer({ playbook, loading, error, hasSelection }: Props) {
  if (!hasSelection) {
    return (
      <div className="flex items-center justify-center flex-1 text-sm text-slate-400">
        Select a playbook from the list to view its content.
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center flex-1 text-sm text-slate-400">
        Loading…
      </div>
    );
  }

  if (error || !playbook) {
    return (
      <div className="flex items-center justify-center flex-1 text-sm text-red-600">
        {error ?? 'Not found'}
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin">
      <article className="max-w-3xl mx-auto px-8 py-8 space-y-8">
        <Header playbook={playbook} />
        {playbook.when_applies && <WhenApplies markdown={playbook.when_applies} />}
        {playbook.resolution_steps.length > 0 && (
          <ResolutionSteps steps={playbook.resolution_steps} />
        )}
        {playbook.typical_actions_rows.length > 0 && (
          <ActionsTable rows={playbook.typical_actions_rows} />
        )}
        {playbook.evidence_quotes.length > 0 && (
          <EvidenceQuotes quotes={playbook.evidence_quotes} />
        )}
        {playbook.risks && <Risks markdown={playbook.risks} />}
        <SuggestEdit playbookId={playbook.id} />
      </article>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Sub-sections
// ---------------------------------------------------------------------------

function Header({ playbook }: { playbook: PlaybookDetail }) {
  return (
    <header>
      <div className="flex items-start gap-3">
        <h1 className="flex-1 text-2xl font-semibold tracking-tight text-slate-900 leading-snug">
          {playbook.title}
        </h1>
        <StatusBadge status={playbook.status} />
      </div>
      <div className="mt-2 text-[11px] text-slate-500 font-mono">{playbook.id}</div>
      <div className="mt-4 flex flex-wrap items-center gap-2">
        <Chip tone="blue">{playbook.ticket_class}</Chip>
        <Chip>{playbook.issue_category}</Chip>
        {playbook.country_focus.filter((c) => c !== 'other').map((c) => (
          <Chip key={c}>country: {c}</Chip>
        ))}
        {playbook.languages.filter((l) => l !== 'other').map((l) => (
          <Chip key={l}>lang: {l}</Chip>
        ))}
        {playbook.project_keys.map((k) => (
          <Chip key={k}>source: {k}</Chip>
        ))}
      </div>
    </header>
  );
}


function WhenApplies({ markdown }: { markdown: string }) {
  return (
    <section>
      <SectionHeading>When this applies</SectionHeading>
      <div className="prose prose-sm prose-slate max-w-none">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
      </div>
    </section>
  );
}


function ResolutionSteps({ steps }: { steps: string[] }) {
  return (
    <section>
      <SectionHeading>Typical resolution flow</SectionHeading>
      <ol className="space-y-3">
        {steps.map((step, i) => (
          <li key={i} className="flex gap-3 items-start">
            <StepCircle n={i + 1} />
            <div className="text-sm text-slate-700 pt-1 leading-relaxed">{step}</div>
          </li>
        ))}
      </ol>
    </section>
  );
}


function ActionsTable({
  rows,
}: {
  rows: { what: string; who: string; tool: string; duration: string }[];
}) {
  return (
    <section>
      <SectionHeading>Typical actions</SectionHeading>
      <div className="overflow-hidden border border-panel-border rounded-lg">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b border-panel-border">
              <th className="text-left px-4 py-2 font-medium text-slate-600 text-xs uppercase tracking-wider">
                What
              </th>
              <th className="text-left px-4 py-2 font-medium text-slate-600 text-xs uppercase tracking-wider">
                Who
              </th>
              <th className="text-left px-4 py-2 font-medium text-slate-600 text-xs uppercase tracking-wider">
                Tool
              </th>
              <th className="text-left px-4 py-2 font-medium text-slate-600 text-xs uppercase tracking-wider w-20">
                Duration
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr
                key={i}
                className={i < rows.length - 1 ? 'border-b border-panel-divider' : ''}
              >
                <td className="px-4 py-2.5 text-slate-700">{r.what}</td>
                <td className="px-4 py-2.5 text-slate-600 font-mono text-xs">{r.who}</td>
                <td className="px-4 py-2.5 text-slate-600">{r.tool}</td>
                <td className="px-4 py-2.5 text-slate-700 font-mono text-xs">{r.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}


function EvidenceQuotes({
  quotes,
}: {
  quotes: { ticket_id: string; language: string | null; quote: string }[];
}) {
  return (
    <section>
      <SectionHeading>Evidence quotes</SectionHeading>
      <ul className="space-y-3">
        {quotes.map((q, i) => (
          <li
            key={i}
            className="border border-panel-border rounded-lg p-3 bg-panel-surface"
          >
            <div className="flex items-center gap-2 mb-1.5">
              <TicketChip id={q.ticket_id} />
              {q.language && (
                <span className="text-[11px] text-slate-500 italic">{q.language}</span>
              )}
            </div>
            <blockquote className="text-sm text-slate-700 leading-relaxed">
              "{q.quote}"
            </blockquote>
          </li>
        ))}
      </ul>
    </section>
  );
}


function Risks({ markdown }: { markdown: string }) {
  return (
    <section>
      <SectionHeading>Risks & safety constraints</SectionHeading>
      <details className="border border-panel-border rounded-lg overflow-hidden">
        <summary className="px-4 py-2.5 text-sm text-slate-700 cursor-pointer hover:bg-slate-50 select-none">
          Show details
        </summary>
        <div className="px-4 py-3 bg-slate-50/50 prose prose-sm prose-slate max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </div>
      </details>
    </section>
  );
}


function SuggestEdit({ playbookId }: { playbookId: string }) {
  const [text, setText] = useState('');
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim() || status === 'saving') return;
    setStatus('saving');
    setErrorMsg(null);
    try {
      await submitSuggestion({ playbook_id: playbookId, text });
      setStatus('saved');
      setText('');
      setTimeout(() => setStatus('idle'), 2500);
    } catch (err) {
      setErrorMsg((err as Error).message);
      setStatus('error');
    }
  }

  return (
    <section className="border-t border-panel-divider pt-6">
      <SectionHeading>Suggest an edit</SectionHeading>
      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
          placeholder="Spotted something wrong, missing, or out-of-date in this playbook? Describe the change."
          className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15 resize-y"
          disabled={status === 'saving'}
        />
        <div className="flex items-center justify-between gap-3">
          <p className="text-[11px] text-slate-400">
            {status === 'error' && errorMsg ? (
              <span className="text-red-600">{errorMsg}</span>
            ) : (
              <>Stored under /suggestions for review.</>
            )}
          </p>
          <button
            type="submit"
            disabled={!text.trim() || status === 'saving'}
            className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors"
          >
            {status === 'saving' ? 'Saving…' : status === 'saved' ? 'Saved' : 'Submit'}
          </button>
        </div>
      </form>
    </section>
  );
}
