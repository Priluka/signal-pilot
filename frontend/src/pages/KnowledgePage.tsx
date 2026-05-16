/** Knowledge tab — playbook list (left) + viewer (right).
 *
 * URL state:
 *   /knowledge                            → list visible, viewer shows empty state
 *   /knowledge/:slug                      → viewer shows the selected playbook
 *   ?issue_category=billing&ticket_class=end_user&q=...   → narrows the list
 */
import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { PlaybookList } from '../components/PlaybookList';
import { PlaybookViewer } from '../components/PlaybookViewer';
import { listPlaybooks, type PlaybookFilters } from '../lib/api';
import type { PlaybookSummary } from '../lib/types';


export function KnowledgePage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters: PlaybookFilters = useMemo(
    () => ({
      ticket_class: searchParams.get('ticket_class') ?? undefined,
      issue_category: searchParams.get('issue_category') ?? undefined,
      country: searchParams.get('country') ?? undefined,
      language: searchParams.get('language') ?? undefined,
    }),
    [searchParams],
  );

  const [playbooks, setPlaybooks] = useState<PlaybookSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    listPlaybooks(filters)
      .then((data) => {
        if (!cancelled) setPlaybooks(data);
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
  }, [filters]);

  const activeFilters = Object.entries(filters).filter(([, v]) => v) as [string, string][];

  function clearFilter(key: string) {
    const next = new URLSearchParams(searchParams);
    next.delete(key);
    setSearchParams(next, { replace: true });
  }

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-panel-border bg-panel-surface">
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-semibold tracking-tight text-slate-900">
            Knowledge Library
          </h1>
          {activeFilters.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              {activeFilters.map(([k, v]) => (
                <button
                  key={k}
                  type="button"
                  onClick={() => clearFilter(k)}
                  className="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded hover:bg-blue-100"
                >
                  <span className="font-mono">{k}</span>: {v}
                  <span className="text-blue-400">×</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </header>
      <div className="flex-1 flex overflow-hidden">
        <PlaybookList
          playbooks={playbooks}
          loading={loading}
          error={error}
          search={search}
          onSearchChange={setSearch}
          totalCount={playbooks.length}
          searchString={searchParams.toString() ? `?${searchParams.toString()}` : ''}
        />
        <PlaybookViewer />
      </div>
    </div>
  );
}
