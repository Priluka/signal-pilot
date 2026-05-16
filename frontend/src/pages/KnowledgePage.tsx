/** Knowledge tab — playbook list (left) + viewer (center) + metadata sidebar (right).
 *
 * URL state:
 *   /knowledge                            → list visible, viewer empty, no right rail
 *   /knowledge/:slug                      → viewer + right rail show the selected playbook
 *   ?issue_category=billing&...           → narrows the list
 */
import { useEffect, useMemo, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';

import { PlaybookList } from '../components/PlaybookList';
import { PlaybookSidebar } from '../components/PlaybookSidebar';
import { PlaybookViewer } from '../components/PlaybookViewer';
import { getPlaybook, listPlaybooks, type PlaybookFilters } from '../lib/api';
import type { PlaybookDetail, PlaybookSummary } from '../lib/types';


export function KnowledgePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { slug } = useParams();

  const filters: PlaybookFilters = useMemo(
    () => ({
      ticket_class: searchParams.get('ticket_class') ?? undefined,
      issue_category: searchParams.get('issue_category') ?? undefined,
      country: searchParams.get('country') ?? undefined,
      language: searchParams.get('language') ?? undefined,
    }),
    [searchParams],
  );

  // --- List state ---------------------------------------------------------
  const [playbooks, setPlaybooks] = useState<PlaybookSummary[]>([]);
  const [listLoading, setListLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    let cancelled = false;
    setListLoading(true);
    setListError(null);
    listPlaybooks(filters)
      .then((data) => {
        if (!cancelled) setPlaybooks(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setListError(err.message);
      })
      .finally(() => {
        if (!cancelled) setListLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [filters]);

  // --- Detail state (single fetch, fed to both viewer and sidebar) --------
  const [detail, setDetail] = useState<PlaybookDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) {
      setDetail(null);
      setDetailError(null);
      return;
    }
    let cancelled = false;
    setDetailLoading(true);
    setDetailError(null);
    setDetail(null);
    getPlaybook(slug)
      .then((data) => {
        if (!cancelled) setDetail(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setDetailError(err.message);
      })
      .finally(() => {
        if (!cancelled) setDetailLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [slug]);

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
          loading={listLoading}
          error={listError}
          search={search}
          onSearchChange={setSearch}
          totalCount={playbooks.length}
          searchString={searchParams.toString() ? `?${searchParams.toString()}` : ''}
        />
        <PlaybookViewer
          playbook={detail}
          loading={detailLoading}
          error={detailError}
          hasSelection={Boolean(slug)}
        />
        {detail && <PlaybookSidebar playbook={detail} />}
      </div>
    </div>
  );
}
