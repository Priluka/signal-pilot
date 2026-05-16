/** /suggestions — list of operator-submitted playbook edits, newest first. */
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { listPlaybooks, listSuggestions } from '../lib/api';
import type { PlaybookSummary, SuggestionRecord } from '../lib/types';


export function SuggestionsPage() {
  const [suggestions, setSuggestions] = useState<SuggestionRecord[]>([]);
  const [playbooks, setPlaybooks] = useState<PlaybookSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([listSuggestions(), listPlaybooks()])
      .then(([s, p]) => {
        if (cancelled) return;
        setSuggestions(s);
        setPlaybooks(p);
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
  }, []);

  const titleById = useMemo(() => {
    const map = new Map<string, string>();
    for (const pb of playbooks) map.set(pb.id, pb.title);
    return map;
  }, [playbooks]);

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-panel-border bg-panel-surface">
        <h1 className="text-lg font-semibold tracking-tight text-slate-900">
          Suggestions
        </h1>
        <p className="text-[11px] text-slate-500 mt-0.5">
          Operator-submitted edits to playbooks, newest first. Status flow:
          pending → reviewed → merged | dismissed.
        </p>
      </header>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="max-w-4xl mx-auto px-8 py-6">
          {loading && <div className="text-sm text-slate-400">Loading…</div>}
          {error && <div className="text-sm text-red-600">{error}</div>}
          {!loading && !error && suggestions.length === 0 && (
            <div className="text-sm text-slate-400">
              No suggestions yet. Open a playbook and use the "Suggest an edit" form at the bottom.
            </div>
          )}
          <ul className="space-y-3">
            {suggestions.map((s) => (
              <SuggestionRow
                key={s.id}
                suggestion={s}
                playbookTitle={titleById.get(s.playbook_id)}
              />
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}


function SuggestionRow({
  suggestion,
  playbookTitle,
}: {
  suggestion: SuggestionRecord;
  playbookTitle: string | undefined;
}) {
  return (
    <li className="bg-panel-surface border border-panel-border rounded-lg p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <Link
            to={`/knowledge/${suggestion.playbook_id}`}
            className="text-sm font-medium text-slate-900 hover:text-blue-700 leading-snug"
          >
            {playbookTitle ?? suggestion.playbook_id}
          </Link>
          <div className="mt-0.5 text-[11px] font-mono text-slate-500">
            {suggestion.playbook_id}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <StatusPill status={suggestion.status} />
          <span className="text-[11px] text-slate-400 font-mono">
            {formatTimestamp(suggestion.timestamp)}
          </span>
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
        {suggestion.text}
      </p>
    </li>
  );
}


function StatusPill({ status }: { status: string }) {
  const map: Record<string, string> = {
    pending: 'bg-amber-50 text-amber-700 border-amber-200',
    reviewed: 'bg-blue-50 text-blue-700 border-blue-200',
    merged: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dismissed: 'bg-slate-50 text-slate-600 border-slate-200',
  };
  const tone = map[status] ?? map.pending;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-[11px] font-medium border rounded ${tone}`}>
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
