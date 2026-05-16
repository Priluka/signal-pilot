/** Right column of the Knowledge page — full playbook detail. */
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { getPlaybook } from '../lib/api';
import type { PlaybookDetail } from '../lib/types';

import {
  Chip,
  ConfidenceBar,
  SectionHeading,
  StatusBadge,
  StepCircle,
  TicketChip,
} from './ui';


export function PlaybookViewer() {
  const { slug } = useParams();
  const [playbook, setPlaybook] = useState<PlaybookDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) {
      setPlaybook(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    getPlaybook(slug)
      .then((data) => {
        if (!cancelled) setPlaybook(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

  if (!slug) {
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
        <Stats playbook={playbook} />
        {playbook.when_applies && <WhenApplies markdown={playbook.when_applies} />}
        {playbook.resolution_steps.length > 0 && (
          <ResolutionSteps steps={playbook.resolution_steps} />
        )}
        {playbook.typical_actions_rows.length > 0 && (
          <ActionsTable rows={playbook.typical_actions_rows} />
        )}
        {playbook.evidence_quotes.length > 0 && (
          <Evidence
            quotes={playbook.evidence_quotes}
            allTickets={playbook.evidence_tickets}
            clusterSize={playbook.cluster_size}
          />
        )}
        {playbook.risks && <Risks markdown={playbook.risks} />}
        {playbook.related_playbooks.length > 0 && (
          <Related ids={playbook.related_playbooks} />
        )}
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


function Stats({ playbook }: { playbook: PlaybookDetail }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-4 border-y border-panel-divider">
      <Stat label="Confidence">
        <ConfidenceBar score={playbook.extraction_confidence} />
      </Stat>
      <Stat label="Learned from">
        <span className="text-sm font-medium text-slate-900">
          {playbook.cluster_size ?? '—'} tickets
        </span>
      </Stat>
      <Stat label="Frequency">
        <span className="text-sm font-medium text-slate-900">
          {playbook.frequency_per_month != null
            ? `${playbook.frequency_per_month.toFixed(2)}/mo`
            : '—'}
        </span>
      </Stat>
      <Stat label="Updated">
        <span className="text-sm font-medium text-slate-900">
          {playbook.updated ?? '—'}
        </span>
      </Stat>
    </div>
  );
}


function Stat({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-[11px] font-semibold tracking-wider uppercase text-slate-500">
        {label}
      </div>
      <div className="mt-1">{children}</div>
    </div>
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


function Evidence({
  quotes,
  allTickets,
  clusterSize,
}: {
  quotes: { ticket_id: string; language: string | null; quote: string }[];
  allTickets: string[];
  clusterSize: number | null;
}) {
  return (
    <section>
      <SectionHeading>Evidence</SectionHeading>
      <p className="text-xs text-slate-500 mb-3">
        Derived from {clusterSize ?? allTickets.length} tickets · {quotes.length} representative quotes
      </p>
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
      {allTickets.length > quotes.length && (
        <details className="mt-3">
          <summary className="text-xs text-slate-500 cursor-pointer hover:text-slate-700">
            Show all {allTickets.length} source tickets
          </summary>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {allTickets.map((t) => (
              <TicketChip key={t} id={t} />
            ))}
          </div>
        </details>
      )}
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


function Related({ ids }: { ids: string[] }) {
  return (
    <section>
      <SectionHeading>Related playbooks</SectionHeading>
      <ul className="space-y-1">
        {ids.map((id) => (
          <li key={id}>
            <Link
              to={`/knowledge/${id}`}
              className="text-sm text-blue-600 hover:text-blue-700 hover:underline font-mono"
            >
              {id}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}


function SuggestEdit({ playbookId }: { playbookId: string }) {
  const [text, setText] = useState('');
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    // Backend route for suggestions is pending — log locally for now so the
    // form is functional end-to-end as soon as we wire /suggestions later.
    // eslint-disable-next-line no-console
    console.info('[suggestion]', { playbookId, text });
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setText('');
    }, 2500);
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
        />
        <div className="flex items-center justify-between">
          <p className="text-[11px] text-slate-400">
            Suggestions are reviewed before being merged into the playbook.
          </p>
          <button
            type="submit"
            disabled={!text.trim()}
            className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors"
          >
            {submitted ? 'Saved' : 'Submit'}
          </button>
        </div>
      </form>
    </section>
  );
}
