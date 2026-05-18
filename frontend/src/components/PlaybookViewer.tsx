/** Center column of the Knowledge page — playbook prose.
 *
 * Presentational: the parent (KnowledgePage) owns the fetch and passes the
 * result down so the right-hand metadata sidebar can use the same data
 * without duplicating the request. Stats / related / evidence-ticket list
 * live in the right sidebar; this column carries the title + narrative
 * sections.
 *
 * Each resolution step, "when this applies" bullet, and "typical actions"
 * cell is wrapped in <InlineEditable> so an operator can hover, click the
 * pencil, edit the text, and submit a /suggestions row — which a reviewer
 * later accepts (writing the change to disk + committing) or rejects from
 * the Suggestions page.
 */
import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { submitSuggestion } from '../lib/api';
import type { PlaybookDetail, TicketActionRow } from '../lib/types';

import { InlineEditable } from './InlineEditable';
import { useToast } from './Toast';
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
        {playbook.when_applies && (
          <WhenApplies markdown={playbook.when_applies} playbookId={playbook.id} />
        )}
        {playbook.resolution_steps.length > 0 && (
          <ResolutionSteps steps={playbook.resolution_steps} playbookId={playbook.id} />
        )}
        {playbook.typical_actions_rows.length > 0 && (
          <ActionsTable rows={playbook.typical_actions_rows} playbookId={playbook.id} />
        )}
        {playbook.evidence_quotes.length > 0 && (
          <EvidenceQuotes quotes={playbook.evidence_quotes} />
        )}
        {playbook.risks && <Risks markdown={playbook.risks} />}
        <p className="text-[11px] text-slate-400 border-t border-panel-divider pt-4">
          Hover any step, bullet, or table cell and click the pencil to suggest an edit.
          Pending suggestions are reviewed under the <span className="font-mono">Suggestions</span> tab.
        </p>
      </article>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Header
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


// ---------------------------------------------------------------------------
// When this applies — bullets are individually editable.
// ---------------------------------------------------------------------------

interface Bullet {
  /** The raw markdown line (including ``- `` prefix and any trailing spaces). */
  rawLine: string;
  /** Text content without the leading ``- ``. */
  display: string;
}

function parseBullets(md: string): Bullet[] {
  const out: Bullet[] = [];
  for (const line of md.split('\n')) {
    const match = line.match(/^(\s*-\s+)(.*\S.*)$/);
    if (match) {
      out.push({ rawLine: line, display: match[2] });
    }
  }
  return out;
}


function WhenApplies({
  markdown,
  playbookId,
}: {
  markdown: string;
  playbookId: string;
}) {
  const bullets = useMemo(() => parseBullets(markdown), [markdown]);
  const toast = useToast();

  if (bullets.length === 0) {
    // Fall back to plain markdown rendering when the section doesn't look
    // like a bullet list.
    return (
      <section>
        <SectionHeading>When this applies</SectionHeading>
        <div className="prose prose-sm prose-slate max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </div>
      </section>
    );
  }

  return (
    <section>
      <SectionHeading>When this applies</SectionHeading>
      <ul className="space-y-1.5 list-none pl-0">
        {bullets.map((b, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-slate-700 leading-relaxed">
            <span className="text-slate-400 mt-1 select-none">•</span>
            <div className="flex-1 min-w-0">
              <InlineEditable
                displayText={b.display}
                ariaLabel={`bullet ${i + 1}`}
                onSubmit={async (newText) => {
                  const prefix = b.rawLine.match(/^(\s*-\s+)/)?.[1] ?? '- ';
                  await submitSuggestion({
                    playbook_id: playbookId,
                    section: 'when_applies',
                    step_number: i + 1,
                    old_text: b.rawLine,
                    new_text: `${prefix}${newText}`,
                  });
                  toast.success('Suggestion submitted');
                }}
              />
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Resolution flow — numbered steps, each editable.
// ---------------------------------------------------------------------------

function ResolutionSteps({
  steps,
  playbookId,
}: {
  steps: string[];
  playbookId: string;
}) {
  const toast = useToast();
  return (
    <section>
      <SectionHeading>Typical resolution flow</SectionHeading>
      <ol className="space-y-3">
        {steps.map((step, i) => (
          <li key={i} className="flex gap-3 items-start">
            <StepCircle n={i + 1} />
            <div className="flex-1 min-w-0 pt-1 text-sm text-slate-700 leading-relaxed">
              <InlineEditable
                displayText={step}
                ariaLabel={`resolution step ${i + 1}`}
                onSubmit={async (newText) => {
                  const oldRaw = `${i + 1}. ${step}`;
                  const newRaw = `${i + 1}. ${newText}`;
                  await submitSuggestion({
                    playbook_id: playbookId,
                    section: 'resolution_step',
                    step_number: i + 1,
                    old_text: oldRaw,
                    new_text: newRaw,
                  });
                  toast.success('Suggestion submitted');
                }}
              />
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Typical actions — every cell is independently editable.
// ---------------------------------------------------------------------------

const CELL_FIELDS = ['what', 'who', 'tool', 'duration'] as const;
type CellField = (typeof CELL_FIELDS)[number];


function ActionsTable({
  rows,
  playbookId,
}: {
  rows: TicketActionRow[];
  playbookId: string;
}) {
  const toast = useToast();

  function submitCell(rowIdx: number, field: CellField, oldValue: string, newValue: string) {
    return submitSuggestion({
      playbook_id: playbookId,
      section: `typical_action_${field}`,
      step_number: rowIdx + 1,
      old_text: oldValue,
      new_text: newValue,
    }).then(() => toast.success('Suggestion submitted'));
  }

  return (
    <section>
      <SectionHeading>Typical actions</SectionHeading>
      <div className="overflow-hidden border border-panel-border rounded-lg">
        <table className="w-full text-sm table-fixed">
          <colgroup>
            <col className="w-2/5" />
            <col className="w-1/5" />
            <col className="w-1/5" />
            <col className="w-1/5" />
          </colgroup>
          <thead>
            <tr className="bg-slate-50 border-b border-panel-border">
              <th className="text-left px-4 py-2 font-medium text-slate-600 text-xs uppercase tracking-wider">What</th>
              <th className="text-left px-4 py-2 font-medium text-slate-600 text-xs uppercase tracking-wider">Who</th>
              <th className="text-left px-4 py-2 font-medium text-slate-600 text-xs uppercase tracking-wider">Tool</th>
              <th className="text-left px-4 py-2 font-medium text-slate-600 text-xs uppercase tracking-wider">Duration</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                className={i < rows.length - 1 ? 'border-b border-panel-divider' : ''}
              >
                {CELL_FIELDS.map((field) => {
                  const value = row[field];
                  const monoFields: CellField[] = ['who', 'duration'];
                  return (
                    <td
                      key={field}
                      className={`px-4 py-2.5 align-top text-slate-700 ${
                        monoFields.includes(field) ? 'font-mono text-xs' : ''
                      }`}
                    >
                      <InlineEditable
                        variant="inline"
                        displayText={value}
                        ariaLabel={`${field} cell, row ${i + 1}`}
                        onSubmit={(nv) => submitCell(i, field, value, nv)}
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Evidence quotes (read-only — these are extracted from real ticket bodies)
// ---------------------------------------------------------------------------

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
