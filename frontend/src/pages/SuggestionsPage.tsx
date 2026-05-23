/** /suggestions — review queue for operator-submitted playbook edits.
 *
 * Diff-style cards, grouped by status: pending (white, bordered, with
 * Accept/Reject buttons) on top, resolved (muted gray, no border, status
 * text only) below. Diffs are always visible — no expand/collapse — since
 * they're usually one or two lines. Newest first within each group.
 * Filter (all/pending/accepted/rejected) lives behind a dropdown next to
 * the title, matching the chrome of the other views.
 *
 * Accept rewrites the playbook markdown on disk and creates a git commit;
 * reject is a state change only.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import {
  Check,
  CheckCircle2,
  Lightbulb,
  ListFilter,
  X,
} from 'lucide-react';

import { useToast } from '../components/Toast';
import {
  acceptSuggestion,
  listPlaybooks,
  listSuggestions,
  rejectSuggestion,
} from '../lib/api';
import { invalidate } from '../lib/cache';
import type { PlaybookSummary, SuggestionRecord } from '../lib/types';


type Filter = 'all' | 'pending' | 'accepted' | 'rejected';


export function SuggestionsPage() {
  const toast = useToast();

  const [suggestions, setSuggestions] = useState<SuggestionRecord[]>([]);
  const [playbooks, setPlaybooks] = useState<PlaybookSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>('all');
  const [busyId, setBusyId] = useState<number | null>(null);

  function refresh() {
    setLoading(true);
    setError(null);
    Promise.all([listSuggestions(), listPlaybooks()])
      .then(([s, p]) => {
        setSuggestions(s);
        setPlaybooks(p);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const titleById = useMemo(() => {
    const m = new Map<string, string>();
    for (const pb of playbooks) m.set(pb.id, pb.title);
    return m;
  }, [playbooks]);

  const counts = useMemo(
    () => ({
      all: suggestions.length,
      pending: suggestions.filter((s) => s.status === 'pending').length,
      accepted: suggestions.filter((s) => s.status === 'accepted').length,
      rejected: suggestions.filter((s) => s.status === 'rejected').length,
    }),
    [suggestions],
  );

  const filtered = useMemo(() => {
    if (filter === 'all') return suggestions;
    return suggestions.filter((s) => s.status === filter);
  }, [suggestions, filter]);

  const pendingGroup = filtered.filter((s) => s.status === 'pending');
  const resolvedGroup = filtered.filter((s) => s.status !== 'pending');

  async function handleAccept(s: SuggestionRecord) {
    setBusyId(s.id);
    try {
      const updated = await acceptSuggestion(s.id);
      setSuggestions((prev) => prev.map((x) => (x.id === s.id ? updated : x)));
      invalidate('playbooks');
      invalidate(`playbook:${s.playbook_id}`);
      window.dispatchEvent(new Event('suggestions-changed'));
      toast.success(`#${s.id} accepted · committed to repo`);
    } catch (err) {
      toast.error((err as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  async function handleReject(s: SuggestionRecord) {
    setBusyId(s.id);
    try {
      const updated = await rejectSuggestion(s.id);
      setSuggestions((prev) => prev.map((x) => (x.id === s.id ? updated : x)));
      window.dispatchEvent(new Event('suggestions-changed'));
      toast.success(`#${s.id} rejected`);
    } catch (err) {
      toast.error((err as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="h-full flex flex-col">
      <Header filter={filter} counts={counts} onFilterChange={setFilter} />

      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading && (
          <div className="px-6 py-6 text-sm text-ink-muted">Loading…</div>
        )}
        {error && (
          <div className="px-6 py-6 text-sm text-red-600 dark:text-red-400">{error}</div>
        )}
        {!loading && !error && filtered.length === 0 && (
          <EmptyState filter={filter} totalCount={counts.all} />
        )}
        {!loading && !error && filtered.length > 0 && (
          <div className="px-4 py-2">
            {pendingGroup.length > 0 && (
              <>
                <GroupLabel>Pending review</GroupLabel>
                <ul className="space-y-0">
                  {pendingGroup.map((s) => (
                    <li key={s.id}>
                      <PendingCard
                        suggestion={s}
                        playbookTitle={titleById.get(s.playbook_id)}
                        busy={busyId === s.id}
                        onAccept={() => handleAccept(s)}
                        onReject={() => handleReject(s)}
                      />
                    </li>
                  ))}
                </ul>
              </>
            )}
            {resolvedGroup.length > 0 && (
              <div
                className={
                  pendingGroup.length > 0
                    ? 'border-t border-line-subtle pt-6 mt-6'
                    : ''
                }
              >
                <GroupLabel>Resolved</GroupLabel>
                <ul className="space-y-0">
                  {resolvedGroup.map((s) => (
                    <li key={s.id}>
                      <ResolvedCard
                        suggestion={s}
                        playbookTitle={titleById.get(s.playbook_id)}
                      />
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Header
// ---------------------------------------------------------------------------

function Header({
  filter,
  counts,
  onFilterChange,
}: {
  filter: Filter;
  counts: Record<Filter, number>;
  onFilterChange: (f: Filter) => void;
}) {
  return (
    <header className="px-6 pt-5 pb-4 border-b border-line-subtle shrink-0">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h1 className="text-base font-semibold tracking-tight text-ink flex items-baseline gap-2">
            <span>Suggestions</span>
            {filter !== 'all' && (
              <span className="text-[12px] font-normal text-ink-muted capitalize">
                · {filter} ({counts[filter]})
              </span>
            )}
          </h1>
          <p className="text-[12px] text-ink-body mt-0.5">
            Operator-submitted playbook edits
          </p>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          <FilterMenu filter={filter} counts={counts} onChange={onFilterChange} />
        </div>
      </div>
    </header>
  );
}


function FilterMenu({
  filter,
  counts,
  onChange,
}: {
  filter: Filter;
  counts: Record<Filter, number>;
  onChange: (f: Filter) => void;
}) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    function onClickAway(e: MouseEvent) {
      const target = e.target as Node | null;
      if (target && rootRef.current && !rootRef.current.contains(target)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', onClickAway);
    return () => document.removeEventListener('mousedown', onClickAway);
  }, [open]);

  const highlighted = open || filter !== 'all';
  const items: { key: Filter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'pending', label: 'Pending' },
    { key: 'accepted', label: 'Accepted' },
    { key: 'rejected', label: 'Rejected' },
  ];

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        title="Filter"
        onClick={() => setOpen((v) => !v)}
        className={`w-7 h-7 inline-flex items-center justify-center rounded-md transition-colors duration-150 focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-1 outline-none ${
          highlighted
            ? 'bg-hover text-ink-body'
            : 'text-ink-muted hover:bg-hover hover:text-ink-body'
        }`}
      >
        <ListFilter width={16} height={16} strokeWidth={1.75} />
      </button>

      {open && (
        <div className="absolute top-full right-0 mt-1 w-48 bg-card border border-line rounded-md shadow-md py-1 z-20">
          <div className="px-3 py-2 text-[12px] text-ink-muted border-b border-line-subtle">
            Status
          </div>
          {items.map((it) => {
            const active = filter === it.key;
            return (
              <button
                key={it.key}
                type="button"
                onClick={() => {
                  onChange(it.key);
                  setOpen(false);
                }}
                className={`w-full text-left px-3 py-1.5 text-[13px] flex items-center justify-between gap-2 transition-colors duration-150 ${
                  active
                    ? 'bg-hover text-ink font-medium'
                    : 'text-ink-body hover:bg-hover hover:text-ink'
                }`}
              >
                <span>{it.label}</span>
                <span className="text-[11px] font-mono text-ink-muted">
                  {counts[it.key]}
                </span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}


function GroupLabel({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-[11px] uppercase tracking-wider font-semibold text-ink-muted px-2 pt-3 pb-2">
      {children}
    </h2>
  );
}


// ---------------------------------------------------------------------------
// Pending card — prominent, with Accept/Reject buttons
// ---------------------------------------------------------------------------

function PendingCard({
  suggestion,
  playbookTitle,
  busy,
  onAccept,
  onReject,
}: {
  suggestion: SuggestionRecord;
  playbookTitle: string | undefined;
  busy: boolean;
  onAccept: () => void;
  onReject: () => void;
}) {
  const kind = suggestion.type ?? 'edit';
  const isBullet = suggestion.section === 'when_applies';
  return (
    <article className="bg-card border border-line rounded-lg p-4 mb-4">
      <CardHeader
        kind={kind}
        isBullet={isBullet}
        playbookTitle={playbookTitle ?? suggestion.playbook_id}
        section={suggestion.section}
        stepNumber={suggestion.step_number}
        author={suggestion.author}
        timestamp={suggestion.timestamp}
      />
      <Diff suggestion={suggestion} />
      <div className="flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onReject}
          disabled={busy}
          className="bg-transparent border border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800/60 dark:text-red-400 dark:hover:bg-red-950/40 rounded-md px-3 h-8 text-[12px] font-medium transition-colors duration-150 disabled:opacity-60"
        >
          Reject
        </button>
        <button
          type="button"
          onClick={onAccept}
          disabled={busy}
          className="bg-accent text-white hover:bg-accent-hover rounded-md px-3 h-8 text-[12px] font-medium transition-colors duration-150 disabled:opacity-60"
        >
          {busy ? 'Working…' : 'Accept'}
        </button>
      </div>
    </article>
  );
}


// ---------------------------------------------------------------------------
// Resolved card — muted, status text instead of buttons
// ---------------------------------------------------------------------------

function ResolvedCard({
  suggestion,
  playbookTitle,
}: {
  suggestion: SuggestionRecord;
  playbookTitle: string | undefined;
}) {
  const kind = suggestion.type ?? 'edit';
  const isBullet = suggestion.section === 'when_applies';
  return (
    <article className="bg-app rounded-lg px-3.5 pt-3.5 pb-4 mb-4 border-b border-line-subtle opacity-75 dark:opacity-60">
      <CardHeader
        kind={kind}
        isBullet={isBullet}
        playbookTitle={playbookTitle ?? suggestion.playbook_id}
        section={suggestion.section}
        stepNumber={suggestion.step_number}
        author={suggestion.author}
        timestamp={suggestion.timestamp}
      />
      <Diff suggestion={suggestion} />
      <StatusIndicator status={suggestion.status} />
    </article>
  );
}


// ---------------------------------------------------------------------------
// Shared card chrome
// ---------------------------------------------------------------------------

function CardHeader({
  kind,
  isBullet,
  playbookTitle,
  section,
  stepNumber,
  author,
  timestamp,
}: {
  kind: 'edit' | 'add' | 'remove';
  isBullet: boolean;
  playbookTitle: string;
  section: string;
  stepNumber: number | null;
  author: string;
  timestamp: string;
}) {
  const location = section + (stepNumber != null ? ` #${stepNumber}` : '');
  return (
    <header className="mb-3">
      <div className="flex items-start gap-2">
        <KindBadge kind={kind} isBullet={isBullet} />
        <span className="text-[12px] font-medium text-ink leading-tight">
          {playbookTitle}
        </span>
      </div>
      <div className="text-[11px] font-mono text-ink-muted mt-1">
        {location} · {author} · {formatTimestamp(timestamp)}
      </div>
    </header>
  );
}


function KindBadge({
  kind,
  isBullet,
}: {
  kind: 'edit' | 'add' | 'remove';
  isBullet: boolean;
}) {
  if (kind === 'remove') {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded bg-red-50 text-red-700 border border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800/60 shrink-0">
        Removal
      </span>
    );
  }
  if (kind === 'add') {
    return isBullet ? (
      <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60 shrink-0">
        New condition
      </span>
    ) : (
      <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded bg-blue-50 text-blue-700 border border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800/60 shrink-0">
        New step
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/60 shrink-0">
      Edit
    </span>
  );
}


function Diff({ suggestion }: { suggestion: SuggestionRecord }) {
  const kind = suggestion.type ?? 'edit';
  return (
    <div className="rounded-md overflow-hidden border border-line mb-3">
      {(kind === 'remove' || kind === 'edit') && (
        <div className="bg-red-50 px-3.5 py-2.5 border-l-[3px] border-l-red-400 font-mono text-[12px] text-red-700 dark:bg-red-950/40 dark:text-red-200 dark:border-l-red-500">
          <span className="text-red-600 dark:text-red-400 mr-1.5 select-none">−</span>
          <span className="line-through opacity-80 whitespace-pre-wrap leading-relaxed">
            {suggestion.old_text}
          </span>
        </div>
      )}
      {(kind === 'add' || kind === 'edit') && (
        <div className="bg-emerald-50 px-3.5 py-2.5 border-l-[3px] border-l-emerald-500 font-mono text-[12px] text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-200 dark:border-l-emerald-400">
          <span className="text-emerald-600 dark:text-emerald-400 mr-1.5 select-none">+</span>
          <span className="whitespace-pre-wrap leading-relaxed">
            {suggestion.new_text}
          </span>
        </div>
      )}
    </div>
  );
}


function StatusIndicator({ status }: { status: SuggestionRecord['status'] }) {
  if (status === 'accepted') {
    return (
      <div className="flex items-center gap-1.5 mt-2">
        <Check width={14} height={14} strokeWidth={2} className="text-emerald-600 dark:text-emerald-400" />
        <span className="text-[11px] font-medium text-emerald-600 dark:text-emerald-400">Accepted</span>
      </div>
    );
  }
  if (status === 'rejected') {
    return (
      <div className="flex items-center gap-1.5 mt-2">
        <X width={14} height={14} strokeWidth={2} className="text-red-600 dark:text-red-400" />
        <span className="text-[11px] font-medium text-red-600 dark:text-red-400">Rejected</span>
      </div>
    );
  }
  return null;
}


// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------

function EmptyState({
  filter,
  totalCount,
}: {
  filter: Filter;
  totalCount: number;
}) {
  // "All caught up" means there is data, just nothing pending to review.
  // "No suggestions yet" means the queue is empty entirely.
  const caughtUp = filter === 'pending' && totalCount > 0;
  const Icon = caughtUp ? CheckCircle2 : Lightbulb;
  const title = caughtUp ? 'All caught up' : 'No suggestions yet';
  const subtext = caughtUp
    ? 'No pending suggestions to review'
    : 'Playbook edits submitted by operators will appear here';
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <Icon
        width={40}
        height={40}
        strokeWidth={1.5}
        className="text-ink-muted opacity-50 mb-3"
      />
      <div className="text-[13px] text-ink-muted">{title}</div>
      <div className="text-[12px] text-ink-muted opacity-70 mt-1">
        {subtext}
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatTimestamp(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}
