/** Left column of the Knowledge page — filterable, scrollable playbook list. */
import { useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';

import type { PlaybookSummary } from '../lib/types';


interface Props {
  playbooks: PlaybookSummary[];
  loading: boolean;
  error: string | null;
  search: string;
  onSearchChange: (v: string) => void;
  totalCount: number;
  /** Tells the list to preserve these query params when linking to a playbook. */
  searchString: string;
}

export function PlaybookList({
  playbooks,
  loading,
  error,
  search,
  onSearchChange,
  totalCount,
  searchString,
}: Props) {
  const { slug } = useParams();

  const filtered = useMemo(() => {
    if (!search.trim()) return playbooks;
    const needle = search.toLowerCase();
    return playbooks.filter(
      (pb) =>
        pb.title.toLowerCase().includes(needle) ||
        pb.description.toLowerCase().includes(needle),
    );
  }, [playbooks, search]);

  return (
    <div className="flex flex-col w-[340px] shrink-0 border-r border-panel-border bg-panel-surface">
      <div className="px-4 py-3 border-b border-panel-border">
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search playbooks…"
          className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15"
        />
        <div className="mt-2 text-[11px] text-slate-500 font-mono tabular-nums">
          {filtered.length} of {totalCount}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {loading && (
          <div className="px-4 py-6 text-sm text-slate-400">Loading…</div>
        )}
        {error && (
          <div className="px-4 py-6 text-sm text-red-600">{error}</div>
        )}
        {!loading && !error && filtered.length === 0 && (
          <div className="px-4 py-6 text-sm text-slate-400">
            No playbooks match the current filter.
          </div>
        )}
        <ul>
          {filtered.map((pb) => {
            const isActive = slug === pb.id;
            return (
              <li key={pb.id}>
                <Link
                  to={{ pathname: `/knowledge/${pb.id}`, search: searchString }}
                  className={`block px-4 py-3 border-b border-panel-divider transition-colors ${
                    isActive
                      ? 'bg-blue-50/60 border-l-2 border-l-blue-500'
                      : 'hover:bg-slate-50 border-l-2 border-l-transparent'
                  }`}
                >
                  <div className="text-sm font-medium text-slate-900 leading-snug line-clamp-2">
                    {pb.title}
                  </div>
                  <div className="mt-1.5 flex items-center gap-1.5 flex-wrap text-[11px] text-slate-500">
                    <StatusDot status={pb.status} />
                    <span>{pb.ticket_class}</span>
                    {pb.project_keys.map((k) => (
                      <span
                        key={k}
                        className="px-1 py-0 rounded bg-slate-100 text-slate-600 font-mono text-[10px]"
                      >
                        {k}
                      </span>
                    ))}
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}


function StatusDot({ status }: { status: string }) {
  const norm = (status || '').toLowerCase();
  const color =
    norm === 'active'
      ? 'bg-emerald-500'
      : norm === 'draft'
      ? 'bg-amber-500'
      : 'bg-slate-300';
  return <span className={`w-1.5 h-1.5 rounded-full ${color}`} />;
}
