/** Knowledge tab — filter bar + searchable list (left) + viewer (center) + metadata sidebar (right).
 *
 * URL state:
 *   /knowledge                                                → list with no filter
 *   /knowledge/:slug                                          → viewer + right rail
 *   ?ticket_class=&issue_category=&country=&source=           → narrows the list
 */
import { useEffect, useMemo, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';

import {
  applyFilters,
  deriveFilterOptions,
  FilterBar,
  type PlaybookFilterState,
} from '../components/FilterBar';
import { PlaybookList } from '../components/PlaybookList';
import { PlaybookSidebar } from '../components/PlaybookSidebar';
import { PlaybookViewer } from '../components/PlaybookViewer';
import { getPlaybook, listPlaybooks } from '../lib/api';
import type { PlaybookDetail, PlaybookSummary } from '../lib/types';


const FILTER_KEYS: (keyof PlaybookFilterState)[] = [
  'ticket_class',
  'issue_category',
  'country',
  'source',
];


export function KnowledgePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { slug } = useParams();

  // --- All playbooks fetched once; filtering is fully client-side --------
  const [allPlaybooks, setAllPlaybooks] = useState<PlaybookSummary[]>([]);
  const [listLoading, setListLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    let cancelled = false;
    setListLoading(true);
    setListError(null);
    listPlaybooks()
      .then((data) => {
        if (!cancelled) setAllPlaybooks(data);
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
  }, []);

  // Read filter state out of the URL.
  const filters: PlaybookFilterState = useMemo(() => {
    const out: PlaybookFilterState = {};
    for (const k of FILTER_KEYS) {
      const v = searchParams.get(k);
      if (v) out[k] = v;
    }
    return out;
  }, [searchParams]);

  const options = useMemo(() => deriveFilterOptions(allPlaybooks), [allPlaybooks]);

  const filtered = useMemo(
    () => applyFilters(allPlaybooks, filters),
    [allPlaybooks, filters],
  );

  function updateFilters(next: PlaybookFilterState) {
    const params = new URLSearchParams(searchParams);
    for (const k of FILTER_KEYS) {
      const v = next[k];
      if (v) params.set(k, v);
      else params.delete(k);
    }
    setSearchParams(params, { replace: true });
  }

  // --- Detail state (single fetch, fed to both viewer and sidebar) -------
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

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-panel-border bg-panel-surface">
        <h1 className="text-lg font-semibold tracking-tight text-slate-900">
          Knowledge Library
        </h1>
      </header>
      <div className="flex-1 flex overflow-hidden">
        <div className="flex flex-col w-[340px] shrink-0 border-r border-panel-border bg-panel-surface">
          <FilterBar
            filters={filters}
            onChange={updateFilters}
            options={options}
          />
          <PlaybookList
            playbooks={filtered}
            loading={listLoading}
            error={listError}
            search={search}
            onSearchChange={setSearch}
            totalCount={allPlaybooks.length}
            searchString={searchParams.toString() ? `?${searchParams.toString()}` : ''}
          />
        </div>
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
