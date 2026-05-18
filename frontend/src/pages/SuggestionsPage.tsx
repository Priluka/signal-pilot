/** /suggestions — review queue for operator-submitted playbook edits.
 *
 * Newest first. Each row shows a red-tinted ``old_text`` block above a
 * green-tinted ``new_text`` block, the targeted playbook, the section +
 * step, the author and time. Pending rows have Accept / Reject buttons;
 * Accept rewrites the playbook on disk and creates a git commit on the
 * signal-pilot repo. Accepted / rejected rows show a status pill.
 */
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { useToast } from '../components/Toast';
import {
  acceptSuggestion,
  listPlaybooks,
  listSuggestions,
  rejectSuggestion,
} from '../lib/api';
import { invalidate } from '../lib/cache';
import type { PlaybookSummary, SuggestionRecord } from '../lib/types';


export function SuggestionsPage() {
  const toast = useToast();

  const [suggestions, setSuggestions] = useState<SuggestionRecord[]>([]);
  const [playbooks, setPlaybooks] = useState<PlaybookSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'accepted' | 'rejected'>('all');
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

  const filtered = useMemo(() => {
    if (filter === 'all') return suggestions;
    return suggestions.filter((s) => s.status === filter);
  }, [suggestions, filter]);

  async function handleAccept(s: SuggestionRecord) {
    setBusyId(s.id);
    try {
      const updated = await acceptSuggestion(s.id);
      setSuggestions((prev) => prev.map((x) => (x.id === s.id ? updated : x)));
      // The playbook markdown on disk just changed — purge the in-memory
      // fetch cache so the Knowledge Library re-fetches fresh content
      // instead of showing the pre-accept version.
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

  const counts = {
    all: suggestions.length,
    pending: suggestions.filter((s) => s.status === 'pending').length,
    accepted: suggestions.filter((s) => s.status === 'accepted').length,
    rejected: suggestions.filter((s) => s.status === 'rejected').length,
  };

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-panel-border bg-panel-surface">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-slate-900">
              Suggestions
            </h1>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Operator-submitted playbook edits. Accept rewrites the markdown on
              disk and creates a git commit; reject is a state change only.
            </p>
          </div>
          <div className="flex items-center gap-1">
            {(['all', 'pending', 'accepted', 'rejected'] as const).map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => setFilter(f)}
                className={`px-2.5 py-1 text-xs border rounded transition-colors ${
                  filter === f
                    ? 'bg-slate-100 border-slate-400 text-slate-900'
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {f} <span className="text-slate-400 font-mono">{counts[f]}</span>
              </button>
            ))}
          </div>
        </div>
      </header>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="max-w-4xl mx-auto px-8 py-6">
          {loading && <div className="text-sm text-slate-400">Loading…</div>}
          {error && <div className="text-sm text-red-600">{error}</div>}
          {!loading && !error && filtered.length === 0 && (
            <div className="text-sm text-slate-400">
              {filter === 'all'
                ? 'No suggestions yet. Open a playbook and click the pencil next to any step.'
                : `No ${filter} suggestions.`}
            </div>
          )}
          <ul className="space-y-4">
            {filtered.map((s) => (
              <SuggestionRow
                key={s.id}
                suggestion={s}
                playbookTitle={titleById.get(s.playbook_id)}
                busy={busyId === s.id}
                onAccept={() => handleAccept(s)}
                onReject={() => handleReject(s)}
              />
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Row
// ---------------------------------------------------------------------------

function SuggestionRow({
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
  const isPending = suggestion.status === 'pending';
  const kind = suggestion.type ?? 'edit';
  const isBullet = suggestion.section === 'when_applies';
  return (
    <li className="bg-panel-surface border border-panel-border rounded-lg p-4">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <Link
            to={`/knowledge/${suggestion.playbook_id}`}
            className="text-sm font-medium text-slate-900 hover:text-blue-700 leading-snug"
          >
            {playbookTitle ?? suggestion.playbook_id}
          </Link>
          <div className="mt-0.5 flex items-center gap-2 text-[11px] text-slate-500">
            <KindBadge kind={kind} isBullet={isBullet} />
            <span className="font-mono">{suggestion.playbook_id}</span>
            <span className="text-slate-300">·</span>
            <span>
              {suggestion.section}
              {suggestion.step_number != null && ` #${suggestion.step_number}`}
            </span>
            <span className="text-slate-300">·</span>
            <span>by {suggestion.author}</span>
            <span className="text-slate-300">·</span>
            <span className="font-mono">{formatTimestamp(suggestion.timestamp)}</span>
          </div>
        </div>
        <StatusPill status={suggestion.status} />
      </div>

      <SuggestionBody suggestion={suggestion} />

      {isPending && (
        <div className="mt-3 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onReject}
            disabled={busy}
            className="px-3 py-1.5 text-sm border border-red-200 text-red-700 bg-white rounded hover:bg-red-50 disabled:opacity-60"
          >
            Reject
          </button>
          <button
            type="button"
            onClick={onAccept}
            disabled={busy}
            className="px-4 py-1.5 text-sm font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-60"
          >
            {busy ? 'Working…' : 'Accept'}
          </button>
        </div>
      )}
    </li>
  );
}


function KindBadge({ kind, isBullet }: { kind: 'edit' | 'add' | 'remove'; isBullet: boolean }) {
  if (kind === 'edit') {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider border rounded bg-blue-50 text-blue-700 border-blue-200">
        edit
      </span>
    );
  }
  if (kind === 'add') {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider border rounded bg-emerald-50 text-emerald-700 border-emerald-200">
        {isBullet ? 'New condition' : 'New step'}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider border rounded bg-red-50 text-red-700 border-red-200">
      Removal
    </span>
  );
}


function SuggestionBody({ suggestion }: { suggestion: SuggestionRecord }) {
  const kind = suggestion.type ?? 'edit';
  if (kind === 'add') {
    return (
      <div className="flex items-start gap-2 bg-emerald-50 border-l-2 border-emerald-300 px-3 py-2 rounded">
        <span className="text-emerald-600 font-mono text-xs mt-0.5 select-none">+</span>
        <span className="text-sm text-emerald-900 whitespace-pre-wrap leading-relaxed flex-1">
          {suggestion.new_text}
        </span>
      </div>
    );
  }
  if (kind === 'remove') {
    return (
      <div className="flex items-start gap-2 bg-red-50 border-l-2 border-red-300 px-3 py-2 rounded">
        <span className="text-red-500 font-mono text-xs mt-0.5 select-none">−</span>
        <span className="text-sm text-red-900 line-through decoration-red-500/70 whitespace-pre-wrap leading-relaxed flex-1">
          {suggestion.old_text}
        </span>
      </div>
    );
  }
  // edit
  return (
    <div className="space-y-1">
      <div className="flex items-start gap-2 bg-red-50 border-l-2 border-red-300 px-3 py-2 rounded">
        <span className="text-red-500 font-mono text-xs mt-0.5 select-none">−</span>
        <span className="text-sm text-slate-700 line-through decoration-red-400/70 whitespace-pre-wrap leading-relaxed flex-1">
          {suggestion.old_text}
        </span>
      </div>
      <div className="flex items-start gap-2 bg-emerald-50 border-l-2 border-emerald-300 px-3 py-2 rounded">
        <span className="text-emerald-600 font-mono text-xs mt-0.5 select-none">+</span>
        <span className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed flex-1">
          {suggestion.new_text}
        </span>
      </div>
    </div>
  );
}


function StatusPill({ status }: { status: string }) {
  const map: Record<string, string> = {
    pending: 'bg-amber-50 text-amber-700 border-amber-200',
    accepted: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    rejected: 'bg-slate-50 text-slate-600 border-slate-200',
  };
  const tone = map[status] ?? map.pending;
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-[11px] font-medium border rounded ${tone}`}
    >
      {status}
    </span>
  );
}


function formatTimestamp(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}
