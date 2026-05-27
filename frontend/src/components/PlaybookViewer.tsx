/** Center column of the Knowledge page — playbook prose.
 *
 * Linear/Notion-grade reading layout: narrow max-width column, generous
 * whitespace between sections, tight typography rhythm. Hover any step,
 * bullet, or table cell to surface inline edit / add / remove actions
 * that submit suggestions for reviewer approval.
 */
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { BookOpen, ChevronRight, Pencil, Plus, X } from 'lucide-react';

import { submitSuggestion } from '../lib/api';
import { countryLabel, sourceLabel, ticketClassLabel } from '../lib/labels';
import type { PlaybookDetail, TicketActionRow } from '../lib/types';


interface Props {
  playbook: PlaybookDetail | null;
  loading: boolean;
  error: string | null;
  hasSelection: boolean;
}


// ---------------------------------------------------------------------------
// Shared atoms
// ---------------------------------------------------------------------------

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-[11px] uppercase tracking-wider font-semibold text-ink-muted mb-4">
      {children}
    </h2>
  );
}


function StatusBadge({ status }: { status: string }) {
  const norm = (status || '').toLowerCase();
  const tone =
    norm === 'active'
      ? { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-200', dot: 'bg-emerald-500' }
      : norm === 'draft'
      ? { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200', dot: 'bg-amber-500' }
      : { bg: 'bg-hover', text: 'text-ink-muted', border: 'border-line', dot: 'bg-ink-muted' };
  return (
    <span
      className={`inline-flex items-center gap-1.5 text-[11px] font-medium border rounded-full px-2 py-0.5 align-middle ml-3 ${tone.bg} ${tone.text} ${tone.border}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${tone.dot}`} />
      {status || 'unknown'}
    </span>
  );
}


function Tag({ children, accent }: { children: React.ReactNode; accent?: boolean }) {
  const tone = accent
    ? 'bg-accent-subtle text-accent-fg border-accent/20'
    : 'bg-app text-ink-muted border-line';
  return (
    <span
      className={`text-[11px] font-medium px-2 py-0.5 rounded-md border ${tone}`}
    >
      {children}
    </span>
  );
}


// ---------------------------------------------------------------------------
// Add / remove / hover-action atoms
// ---------------------------------------------------------------------------

function AddItemForm({
  placeholder,
  ctaLabel,
  onSubmit,
  onCancel,
}: {
  placeholder: string;
  ctaLabel: string;
  onSubmit: (text: string) => Promise<void>;
  onCancel: () => void;
}) {
  const [draft, setDraft] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    const trimmed = draft.trim();
    if (!trimmed) return;
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit(trimmed);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="my-1">
      <textarea
        autoFocus
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') onCancel();
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
        }}
        rows={Math.max(2, Math.min(6, draft.split('\n').length + 1))}
        placeholder={placeholder}
        disabled={submitting}
        className="w-full px-3 py-2 text-[13px] text-ink bg-card border border-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30 resize-y leading-relaxed"
      />
      {error && <div className="mt-1 text-[11px] text-red-600">{error}</div>}
      <div className="mt-2 flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          className="text-[12px] text-ink-body hover:text-ink rounded-md px-3 h-7"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={submit}
          disabled={submitting || !draft.trim()}
          className="bg-accent text-white rounded-md px-3 h-7 text-[12px] font-medium hover:bg-accent-hover transition-colors duration-150 disabled:bg-line disabled:text-ink-muted"
        >
          {submitting ? 'Submitting…' : ctaLabel}
        </button>
      </div>
    </div>
  );
}


function RemoveConfirm({
  text,
  onConfirm,
  onCancel,
}: {
  text: string;
  onConfirm: () => Promise<void>;
  onCancel: () => void;
}) {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function confirm() {
    setSubmitting(true);
    setError(null);
    try {
      await onConfirm();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="my-1 border-l-2 border-red-300 bg-red-50/50 pl-3 pr-2 py-2 rounded">
      <p className="text-[13px] text-red-800">Suggest removing this item?</p>
      <p className="mt-1 text-[12px] text-ink-body italic line-clamp-2">{text}</p>
      {error && <div className="mt-1 text-[11px] text-red-700">{error}</div>}
      <div className="mt-2 flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          disabled={submitting}
          className="text-[12px] text-ink-body hover:text-ink rounded-md px-3 h-7"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={confirm}
          disabled={submitting}
          className="bg-red-600 text-white rounded-md px-3 h-7 text-[12px] font-medium hover:bg-red-700 transition-colors duration-150 disabled:opacity-60"
        >
          {submitting ? 'Submitting…' : 'Yes, suggest removal'}
        </button>
      </div>
    </div>
  );
}


function HoverActions({
  onEdit,
  onAdd,
  onRemove,
}: {
  onEdit?: () => void;
  onAdd: () => void;
  onRemove: () => void;
}) {
  // Small icon cluster that fades in on row hover. Each button is a quiet
  // 24px square — generous click target without being heavy. The actions
  // are intentionally subtle so they never compete with the prose.
  return (
    <span className="opacity-0 group-hover/step:opacity-100 transition-opacity duration-150 flex items-center gap-1 shrink-0">
      {onEdit && (
        <button
          type="button"
          onClick={onEdit}
          aria-label="Suggest edit"
          title="Suggest edit"
          className="w-6 h-6 inline-flex items-center justify-center rounded-md text-ink-muted hover:bg-hover hover:text-ink-body transition-colors duration-150"
        >
          <Pencil width={13} height={13} strokeWidth={1.75} />
        </button>
      )}
      <button
        type="button"
        onClick={onAdd}
        aria-label="Suggest adding an item here"
        title="Suggest adding an item"
        className="w-6 h-6 inline-flex items-center justify-center rounded-md text-ink-muted hover:bg-hover hover:text-ink-body transition-colors duration-150"
      >
        <Plus width={13} height={13} strokeWidth={1.75} />
      </button>
      <button
        type="button"
        onClick={onRemove}
        aria-label="Suggest removing this item"
        title="Suggest removal"
        className="w-6 h-6 inline-flex items-center justify-center rounded-md text-ink-muted hover:bg-red-50 hover:text-red-600 transition-colors duration-150"
      >
        <X width={13} height={13} strokeWidth={1.75} />
      </button>
    </span>
  );
}


function AddLink({
  label,
  onClick,
  className,
}: {
  label: string;
  onClick: () => void;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`text-[12px] text-accent-fg hover:underline mt-2 ${className ?? ''}`}
    >
      {label}
    </button>
  );
}


// ---------------------------------------------------------------------------
// Inline editor — pencil click swaps the row to a textarea with Cancel /
// Submit. Reused by the bullets and the resolution steps; the table uses
// its own inline editor below because it's denser.
// ---------------------------------------------------------------------------

function EditableRow({
  text,
  onSubmit,
  editing,
  onStartEdit,
  onCancelEdit,
  className,
}: {
  text: string;
  onSubmit: (newText: string) => Promise<void>;
  editing: boolean;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  className?: string;
}) {
  const [draft, setDraft] = useState(text);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync local draft to incoming text whenever we leave edit mode.
  if (!editing && draft !== text) {
    setDraft(text);
  }

  async function submit() {
    const trimmed = draft.trim();
    if (!trimmed || trimmed === text.trim()) {
      onCancelEdit();
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit(draft);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (!editing) {
    return <span className={className}>{text}</span>;
  }
  return (
    <div className="my-1">
      <textarea
        autoFocus
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') onCancelEdit();
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
        }}
        rows={Math.max(2, Math.min(8, draft.split('\n').length + 1))}
        disabled={submitting}
        className="w-full p-3 text-[13px] text-ink bg-card border border-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30 resize-y leading-relaxed min-h-[60px]"
      />
      {error && <div className="mt-1 text-[11px] text-red-600">{error}</div>}
      <div className="mt-2 flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onCancelEdit}
          disabled={submitting}
          className="text-[12px] text-ink-body hover:text-ink rounded-md px-3 h-7"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={submit}
          disabled={submitting || !draft.trim()}
          className="bg-accent text-white rounded-md px-3 h-7 text-[12px] font-medium hover:bg-accent-hover transition-colors duration-150 disabled:bg-line disabled:text-ink-muted"
        >
          {submitting ? 'Submitting…' : 'Submit suggestion'}
        </button>
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Main viewer
// ---------------------------------------------------------------------------

export function PlaybookViewer({ playbook, loading, error, hasSelection }: Props) {
  if (!hasSelection) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 px-6 text-center text-ink-muted">
        <BookOpen
          width={32}
          height={32}
          strokeWidth={1.5}
          className="text-ink-faint mb-3"
        />
        <p className="text-sm">Select a playbook from the list to view its content.</p>
      </div>
    );
  }
  if (loading) {
    return (
      <div className="flex items-center justify-center flex-1 text-sm text-ink-muted">
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
      <article className="max-w-3xl mx-auto py-8 px-10 space-y-8">
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
        <p className="text-[12px] text-ink-muted italic mt-8 pt-6 border-t border-line-subtle">
          Hover any step, bullet, or table cell and click the pencil to suggest
          an edit. Pending suggestions live under the{' '}
          <Link
            to="/suggestions"
            className="not-italic font-mono text-accent-fg hover:underline"
          >
            Suggestions
          </Link>{' '}
          tab.
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
    <header className="border-b border-line-subtle pb-8">
      <h1 className="text-xl font-semibold text-ink leading-tight">
        {playbook.title}
        <StatusBadge status={playbook.status} />
      </h1>
      <div className="mt-1 text-[12px] font-mono text-ink-muted">{playbook.id}</div>
      <div className="mt-3 flex flex-wrap gap-1.5">
        <Tag accent>{ticketClassLabel(playbook.ticket_class)}</Tag>
        <Tag>{playbook.issue_category}</Tag>
        {playbook.country_focus
          .filter((c) => c !== 'other')
          .map((c) => {
            const { flag, name } = countryLabel(c);
            return (
              <Tag key={`country-${c}`}>
                {flag && <span className="mr-1">{flag}</span>}
                {name}
              </Tag>
            );
          })}
        {playbook.project_keys.map((k) => (
          <Tag key={`src-${k}`}>From: {sourceLabel(k)}</Tag>
        ))}
      </div>
    </header>
  );
}


// ---------------------------------------------------------------------------
// When this applies
// ---------------------------------------------------------------------------

interface Bullet {
  rawLine: string;
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
  const [editingAt, setEditingAt] = useState<number | null>(null);
  const [addingAt, setAddingAt] = useState<number | null>(null);
  const [removingAt, setRemovingAt] = useState<number | null>(null);

  async function submitEdit(i: number, b: Bullet, newText: string) {
    const prefix = b.rawLine.match(/^(\s*-\s+)/)?.[1] ?? '- ';
    await submitSuggestion({
      playbook_id: playbookId,
      section: 'when_applies',
      step_number: i + 1,
      old_text: b.rawLine,
      new_text: `${prefix}${newText}`,
    });
    window.dispatchEvent(new Event('suggestions-changed'));
    setEditingAt(null);
  }

  async function submitAdd(position: string, text: string) {
    await submitSuggestion({
      playbook_id: playbookId,
      section: 'when_applies',
      type: 'add',
      position,
      new_text: text,
    });
    window.dispatchEvent(new Event('suggestions-changed'));
  }

  async function submitRemove(b: Bullet, stepNumber: number) {
    await submitSuggestion({
      playbook_id: playbookId,
      section: 'when_applies',
      type: 'remove',
      step_number: stepNumber,
      old_text: b.rawLine,
    });
    window.dispatchEvent(new Event('suggestions-changed'));
  }

  if (bullets.length === 0) {
    return (
      <section>
        <SectionLabel>When this applies</SectionLabel>
        <div className="prose prose-sm prose-slate max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </div>
      </section>
    );
  }

  return (
    <section>
      <SectionLabel>When this applies</SectionLabel>
      <ul className="list-none pl-0">
        {bullets.map((b, i) => {
          const inAddMode = addingAt === i;
          const inRemoveMode = removingAt === i;
          const inEditMode = editingAt === i;
          return (
            <li
              key={i}
              className="group/step flex items-start gap-3 py-2"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-ink-muted mt-2 shrink-0" />
              <div className="flex-1 min-w-0">
                {inAddMode ? (
                  <AddItemForm
                    placeholder="New condition"
                    ctaLabel="Submit suggestion"
                    onSubmit={async (text) => {
                      await submitAdd(`after:${i + 1}`, text);
                      setAddingAt(null);
                    }}
                    onCancel={() => setAddingAt(null)}
                  />
                ) : inRemoveMode ? (
                  <RemoveConfirm
                    text={b.display}
                    onConfirm={async () => {
                      await submitRemove(b, i + 1);
                      setRemovingAt(null);
                    }}
                    onCancel={() => setRemovingAt(null)}
                  />
                ) : (
                  <EditableRow
                    text={b.display}
                    editing={inEditMode}
                    onStartEdit={() => setEditingAt(i)}
                    onCancelEdit={() => setEditingAt(null)}
                    onSubmit={(newText) => submitEdit(i, b, newText)}
                    className="text-[13px] text-ink leading-relaxed"
                  />
                )}
              </div>
              {!inAddMode && !inRemoveMode && !inEditMode && (
                <HoverActions
                  onEdit={() => {
                    setAddingAt(null);
                    setRemovingAt(null);
                    setEditingAt(i);
                  }}
                  onAdd={() => {
                    setEditingAt(null);
                    setRemovingAt(null);
                    setAddingAt(i);
                  }}
                  onRemove={() => {
                    setEditingAt(null);
                    setAddingAt(null);
                    setRemovingAt(i);
                  }}
                />
              )}
            </li>
          );
        })}
      </ul>
      {addingAt === -1 ? (
        <div className="mt-2 pl-4">
          <AddItemForm
            placeholder="New condition"
            ctaLabel="Submit suggestion"
            onSubmit={async (text) => {
              await submitAdd('end', text);
              setAddingAt(null);
            }}
            onCancel={() => setAddingAt(null)}
          />
        </div>
      ) : (
        <AddLink
          label="+ Add condition"
          onClick={() => {
            setEditingAt(null);
            setRemovingAt(null);
            setAddingAt(-1);
          }}
          className="pl-4"
        />
      )}
    </section>
  );
}


// ---------------------------------------------------------------------------
// Resolution flow — numbered steps
// ---------------------------------------------------------------------------

function ResolutionSteps({
  steps,
  playbookId,
}: {
  steps: string[];
  playbookId: string;
}) {
  const [editingAt, setEditingAt] = useState<number | null>(null);
  const [addingAt, setAddingAt] = useState<number | null>(null);
  const [removingAt, setRemovingAt] = useState<number | null>(null);

  async function submitEdit(i: number, step: string, newText: string) {
    const oldRaw = `${i + 1}. ${step}`;
    const newRaw = `${i + 1}. ${newText}`;
    await submitSuggestion({
      playbook_id: playbookId,
      section: 'resolution_step',
      step_number: i + 1,
      old_text: oldRaw,
      new_text: newRaw,
    });
    window.dispatchEvent(new Event('suggestions-changed'));
    setEditingAt(null);
  }

  async function submitAdd(position: string, text: string) {
    await submitSuggestion({
      playbook_id: playbookId,
      section: 'resolution_flow',
      type: 'add',
      position,
      new_text: text,
    });
    window.dispatchEvent(new Event('suggestions-changed'));
  }

  async function submitRemove(step: string, stepNumber: number) {
    const rawLine = `${stepNumber}. ${step}`;
    await submitSuggestion({
      playbook_id: playbookId,
      section: 'resolution_flow',
      type: 'remove',
      step_number: stepNumber,
      old_text: rawLine,
    });
    window.dispatchEvent(new Event('suggestions-changed'));
  }

  return (
    <section>
      <SectionLabel>Typical resolution flow</SectionLabel>
      <ol className="list-none pl-0">
        {steps.map((step, i) => {
          const inAddMode = addingAt === i;
          const inRemoveMode = removingAt === i;
          const inEditMode = editingAt === i;
          return (
            <li key={i} className="group/step flex items-start gap-4 py-3">
              <span className="w-7 h-7 rounded-full bg-app border border-line flex items-center justify-center shrink-0 mt-0.5">
                <span className="text-[12px] font-medium text-ink-body tabular-nums">
                  {i + 1}
                </span>
              </span>
              <div className="flex-1 min-w-0 pt-0.5">
                {inAddMode ? (
                  <AddItemForm
                    placeholder="New step"
                    ctaLabel="Submit suggestion"
                    onSubmit={async (text) => {
                      await submitAdd(`after:${i + 1}`, text);
                      setAddingAt(null);
                    }}
                    onCancel={() => setAddingAt(null)}
                  />
                ) : inRemoveMode ? (
                  <RemoveConfirm
                    text={step}
                    onConfirm={async () => {
                      await submitRemove(step, i + 1);
                      setRemovingAt(null);
                    }}
                    onCancel={() => setRemovingAt(null)}
                  />
                ) : (
                  <EditableRow
                    text={step}
                    editing={inEditMode}
                    onStartEdit={() => setEditingAt(i)}
                    onCancelEdit={() => setEditingAt(null)}
                    onSubmit={(newText) => submitEdit(i, step, newText)}
                    className="block text-[13px] text-ink leading-relaxed"
                  />
                )}
              </div>
              {!inAddMode && !inRemoveMode && !inEditMode && (
                <HoverActions
                  onEdit={() => {
                    setAddingAt(null);
                    setRemovingAt(null);
                    setEditingAt(i);
                  }}
                  onAdd={() => {
                    setEditingAt(null);
                    setRemovingAt(null);
                    setAddingAt(i);
                  }}
                  onRemove={() => {
                    setEditingAt(null);
                    setAddingAt(null);
                    setRemovingAt(i);
                  }}
                />
              )}
            </li>
          );
        })}
      </ol>
      {addingAt === -1 ? (
        <div className="mt-3 pl-11">
          <AddItemForm
            placeholder="New step"
            ctaLabel="Submit suggestion"
            onSubmit={async (text) => {
              await submitAdd('end', text);
              setAddingAt(null);
            }}
            onCancel={() => setAddingAt(null)}
          />
        </div>
      ) : (
        <AddLink
          label="+ Add step"
          onClick={() => {
            setEditingAt(null);
            setRemovingAt(null);
            setAddingAt(-1);
          }}
          className="pl-11"
        />
      )}
    </section>
  );
}


// ---------------------------------------------------------------------------
// Typical actions table
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
  function submitCell(
    rowIdx: number,
    field: CellField,
    oldValue: string,
    newValue: string,
  ) {
    return submitSuggestion({
      playbook_id: playbookId,
      section: `typical_action_${field}`,
      step_number: rowIdx + 1,
      old_text: oldValue,
      new_text: newValue,
    }).then(() => {
      window.dispatchEvent(new Event('suggestions-changed'));
    });
  }

  return (
    <section>
      <SectionLabel>Typical actions</SectionLabel>
      <div className="border border-line rounded-lg overflow-hidden">
        <table className="w-full table-fixed">
          <colgroup>
            <col className="w-2/5" />
            <col className="w-1/5" />
            <col className="w-1/5" />
            <col className="w-1/5" />
          </colgroup>
          <thead>
            <tr className="bg-app">
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-left">
                What
              </th>
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-left">
                Who
              </th>
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-left">
                Tool
              </th>
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-left">
                Duration
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr
                key={i}
                className="border-t border-line-subtle hover:bg-hover transition-colors duration-150"
              >
                {CELL_FIELDS.map((field) => {
                  const value = row[field] ?? '';
                  const isMono = field === 'duration' || field === 'who';
                  const empty = !value || value === '-' || value === '–';
                  return (
                    <td
                      key={field}
                      className={`px-4 py-3 align-top text-[13px] ${
                        isMono ? 'font-mono text-[12px]' : ''
                      } ${empty ? 'text-ink-muted' : 'text-ink'} leading-relaxed`}
                    >
                      <TableCell
                        value={value}
                        rowIdx={i}
                        field={field}
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


function TableCell({
  value,
  rowIdx,
  field,
  onSubmit,
}: {
  value: string;
  rowIdx: number;
  field: CellField;
  onSubmit: (newValue: string) => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!editing) {
    return (
      <span className="group/cell inline-flex items-baseline gap-1">
        <span>{value || '—'}</span>
        <button
          type="button"
          onClick={() => {
            setDraft(value);
            setError(null);
            setEditing(true);
          }}
          aria-label={`Edit ${field} cell, row ${rowIdx + 1}`}
          className="opacity-0 group-hover/cell:opacity-100 transition-opacity duration-150 text-ink-muted hover:text-ink-body"
        >
          <Pencil width={11} height={11} strokeWidth={1.75} />
        </button>
      </span>
    );
  }

  async function submit() {
    const trimmed = draft.trim();
    if (!trimmed || trimmed === value.trim()) {
      setEditing(false);
      setDraft(value);
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit(draft);
      setEditing(false);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <textarea
        autoFocus
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Escape') {
            setEditing(false);
            setDraft(value);
          }
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
        }}
        rows={2}
        disabled={submitting}
        className="w-full px-2 py-1 text-[13px] text-ink bg-card border border-accent rounded focus:outline-none focus:ring-2 focus:ring-accent/30 resize-y leading-relaxed"
      />
      {error && <div className="mt-1 text-[10px] text-red-600">{error}</div>}
      <div className="mt-1 flex items-center justify-end gap-1.5">
        <button
          type="button"
          onClick={() => {
            setEditing(false);
            setDraft(value);
          }}
          disabled={submitting}
          className="text-[11px] text-ink-body hover:text-ink rounded px-2 h-6"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={submit}
          disabled={submitting || !draft.trim()}
          className="bg-accent text-white rounded px-2 h-6 text-[11px] font-medium hover:bg-accent-hover transition-colors duration-150 disabled:bg-line disabled:text-ink-muted"
        >
          {submitting ? '…' : 'Submit'}
        </button>
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Evidence quotes
// ---------------------------------------------------------------------------

function EvidenceQuotes({
  quotes,
}: {
  quotes: { ticket_id: string; language: string | null; quote: string }[];
}) {
  return (
    <section>
      <SectionLabel>Evidence quotes</SectionLabel>
      <ul className="space-y-3 list-none pl-0">
        {quotes.map((q, i) => (
          <li
            key={i}
            className="border border-line rounded-lg p-4 space-y-2 bg-card"
          >
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono font-medium bg-app border border-line rounded px-1.5 py-0.5 text-ink-body">
                {q.ticket_id}
              </span>
              {q.language && (
                <span className="text-[11px] text-ink-muted">{q.language}</span>
              )}
            </div>
            <blockquote className="border-l-2 border-line pl-3 text-[13px] text-ink-body italic leading-relaxed">
              {q.quote}
            </blockquote>
          </li>
        ))}
      </ul>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Risks (collapsible)
// ---------------------------------------------------------------------------

function Risks({ markdown }: { markdown: string }) {
  const [open, setOpen] = useState(false);
  return (
    <section>
      <SectionLabel>Risks &amp; safety constraints</SectionLabel>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 py-2 text-[13px] font-medium text-ink hover:text-accent-fg transition-colors duration-150"
      >
        <ChevronRight
          width={14}
          height={14}
          strokeWidth={1.75}
          className={`text-ink-muted transition-transform duration-150 ${open ? 'rotate-90' : ''}`}
        />
        <span>{open ? 'Hide details' : 'Show details'}</span>
      </button>
      {open && (
        <div className="pt-2 pl-6 text-[13px] text-ink-body leading-relaxed prose prose-sm prose-slate max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
        </div>
      )}
    </section>
  );
}
