/** Left pane of the Knowledge Library — Linear-style.
 *
 * Owns the inbox-mirror chrome for the playbooks view: a flat header row
 * with title + filter/more icons, an inset search input, the result count,
 * and the scrollable list of playbook rows. Filters live behind the
 * ListFilter icon as a nested dropdown so the rail isn't cluttered with
 * four large select boxes the way it used to be.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ChevronRight, ListFilter } from 'lucide-react';

import type { PlaybookSummary } from '../lib/types';
import { sourceLabel, ticketClassLabel } from '../lib/labels';

import {
  applyFilters,
  deriveFilterOptions,
  type PlaybookFilterState,
} from './FilterBar';


interface Props {
  playbooks: PlaybookSummary[];
  loading: boolean;
  error: string | null;
  search: string;
  onSearchChange: (v: string) => void;
  filters: PlaybookFilterState;
  onFiltersChange: (next: PlaybookFilterState) => void;
  totalCount: number;
  /** Preserved on every list → detail navigation so filter state survives. */
  searchString: string;
}


const FILTER_CATEGORIES: Array<{
  key: keyof PlaybookFilterState;
  label: string;
}> = [
  { key: 'ticket_class', label: 'Ticket class' },
  { key: 'issue_category', label: 'Category' },
  { key: 'country', label: 'Country' },
  { key: 'source', label: 'Source' },
];


export function PlaybookList({
  playbooks,
  loading,
  error,
  search,
  onSearchChange,
  filters,
  onFiltersChange,
  totalCount,
  searchString,
}: Props) {
  const { slug } = useParams();
  const activeRowRef = useRef<HTMLLIElement | null>(null);

  // Auto-scroll the highlighted playbook into view whenever ``slug``
  // changes — e.g. when the operator clicks a Related-playbook chip
  // from another playbook's detail. ``block: 'nearest'`` so already-
  // visible rows stay put and only off-screen targets get a scroll.
  useEffect(() => {
    if (!slug) return;
    const el = activeRowRef.current;
    if (!el) return;
    el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [slug, playbooks]);

  const options = useMemo(() => deriveFilterOptions(playbooks), [playbooks]);

  const filteredByFacets = useMemo(
    () => applyFilters(playbooks, filters),
    [playbooks, filters],
  );

  const filtered = useMemo(() => {
    if (!search.trim()) return filteredByFacets;
    const needle = search.toLowerCase();
    return filteredByFacets.filter(
      (pb) =>
        pb.title.toLowerCase().includes(needle) ||
        pb.description.toLowerCase().includes(needle),
    );
  }, [filteredByFacets, search]);

  const activeFilterCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="flex flex-col flex-1 min-h-0">
      {/* Header */}
      <header className="h-12 px-4 flex items-center border-b border-line-subtle shrink-0">
        <h1 className="text-base font-semibold text-ink tracking-tight flex items-center gap-2">
          <span>Playbooks</span>
          {activeFilterCount > 0 && (
            <span className="text-ink-muted font-normal">
              · {activeFilterCount} filter{activeFilterCount === 1 ? '' : 's'}
            </span>
          )}
        </h1>
        <div className="ml-auto flex items-center gap-1">
          <FilterMenu
            filters={filters}
            options={options}
            onChange={onFiltersChange}
            activeCount={activeFilterCount}
          />
        </div>
      </header>

      {/* Search */}
      <div className="px-3 py-2">
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search playbooks..."
          className="w-full h-8 px-3 text-[13px] bg-app border border-line rounded-md text-ink placeholder:text-ink-muted focus:outline-none focus:ring-1 focus:ring-accent/30 focus:border-accent transition-colors duration-150"
        />
      </div>

      {/* Count */}
      <div className="px-4 py-1.5 text-[11px] text-ink-muted">
        {filtered.length === totalCount
          ? `${totalCount} playbook${totalCount === 1 ? '' : 's'}`
          : `${filtered.length} of ${totalCount}`}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin pb-2">
        {loading && (
          <div className="px-4 py-6 text-sm text-ink-muted">Loading…</div>
        )}
        {error && (
          <div className="px-4 py-6 text-sm text-red-600">{error}</div>
        )}
        {!loading && !error && filtered.length === 0 && (
          <div className="px-4 py-6 text-sm text-ink-muted">
            No playbooks match the current filter.
          </div>
        )}
        <ul>
          {filtered.map((pb) => {
            const isActive = slug === pb.id;
            return (
              <li
                key={pb.id}
                ref={isActive ? activeRowRef : undefined}
              >
                <Link
                  to={{ pathname: `/knowledge/${pb.id}`, search: searchString }}
                  className={`block mx-2 px-3 py-3 rounded-lg transition-colors duration-150 ${
                    isActive ? 'bg-hover' : 'hover:bg-hover'
                  }`}
                >
                  <div
                    className={`text-[13px] leading-snug line-clamp-2 ${
                      isActive ? 'font-semibold text-ink' : 'font-medium text-ink'
                    }`}
                  >
                    {pb.title}
                  </div>
                  <div className="mt-1 flex items-center gap-1.5 flex-wrap text-[11px] text-ink-muted">
                    <span>{ticketClassLabel(pb.ticket_class)}</span>
                    {pb.project_keys.map((k) => (
                      <span
                        key={k}
                        className="bg-app border border-line rounded px-1.5 py-0.5 text-[10px] text-ink-muted"
                      >
                        {sourceLabel(k)}
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


// ---------------------------------------------------------------------------
// Filter dropdown
// ---------------------------------------------------------------------------

function FilterMenu({
  filters,
  options,
  onChange,
  activeCount,
}: {
  filters: PlaybookFilterState;
  options: ReturnType<typeof deriveFilterOptions>;
  onChange: (next: PlaybookFilterState) => void;
  activeCount: number;
}) {
  const [open, setOpen] = useState(false);
  // Which row is currently "armed" — drives the side-by-side sub-popover.
  // Hovering a row sets it, moving the mouse off the whole dropdown
  // clears it. Stays open as long as the mouse is over main OR sub.
  const [hoveredCategory, setHoveredCategory] = useState<
    keyof PlaybookFilterState | null
  >(null);
  const rootRef = useRef<HTMLDivElement | null>(null);

  // Click-outside closes the entire dropdown (main + sub).
  useEffect(() => {
    if (!open) return;
    function onClickAway(e: MouseEvent) {
      const target = e.target as Node | null;
      if (target && rootRef.current && !rootRef.current.contains(target)) {
        setOpen(false);
        setHoveredCategory(null);
      }
    }
    document.addEventListener('mousedown', onClickAway);
    return () => document.removeEventListener('mousedown', onClickAway);
  }, [open]);

  useEffect(() => {
    if (!open) setHoveredCategory(null);
  }, [open]);

  const highlighted = open || activeCount > 0;

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
        // Main menu is fixed-position relative to the filter icon. The
        // sub-menu is rendered INSIDE the hovered row as an absolute
        // descendant — flush against the row's right edge with no gap,
        // so the mouse can travel from row → sub without exiting the
        // main menu's DOM subtree (which would fire onMouseLeave and
        // collapse the sub). Each row is ``position: relative`` so the
        // sub anchors to the row, not to the menu.
        <div
          className="absolute top-full right-0 mt-1 w-52 bg-card border border-line rounded-md shadow-md py-1 z-20"
          onMouseLeave={() => setHoveredCategory(null)}
        >
          <div className="px-3 py-2 text-[12px] text-ink-muted border-b border-line-subtle">
            Add filter
          </div>
          {FILTER_CATEGORIES.map((cat) => {
            const current = filters[cat.key];
            const isHovered = hoveredCategory === cat.key;
            return (
              <div key={cat.key} className="relative">
                <button
                  type="button"
                  onMouseEnter={() => setHoveredCategory(cat.key)}
                  onFocus={() => setHoveredCategory(cat.key)}
                  className={`w-full text-left px-3 py-1.5 text-[13px] text-ink flex items-center justify-between gap-2 transition-colors duration-150 ${
                    isHovered ? 'bg-hover' : 'hover:bg-hover'
                  }`}
                >
                  <span className="flex items-center gap-2 min-w-0">
                    <span className="truncate">{cat.label}</span>
                    {current && (
                      <span className="text-[11px] font-mono text-accent-fg bg-accent-subtle rounded px-1.5 py-0.5 shrink-0">
                        {current}
                      </span>
                    )}
                  </span>
                  <ChevronRight
                    width={13}
                    height={13}
                    strokeWidth={1.75}
                    className="text-ink-muted shrink-0"
                  />
                </button>
                {isHovered && (
                  // Flush against the row's right edge (no margin) so the
                  // mouse never crosses dead pixels and triggers leave.
                  <div className="absolute left-full top-0 w-48 bg-card border border-line rounded-md shadow-md py-1 z-30">
                    <SubMenuValues
                      category={cat.key}
                      currentValue={filters[cat.key]}
                      values={options[cat.key]}
                      onPick={(value) => {
                        // Apply the chosen value and collapse only the
                        // sub-menu — the main menu stays open so the
                        // operator can pile on another filter or pick a
                        // different value without re-opening it.
                        onChange({ ...filters, [cat.key]: value });
                        setHoveredCategory(null);
                      }}
                    />
                  </div>
                )}
              </div>
            );
          })}
          {activeCount > 0 && (
            <>
              <div className="my-1 border-t border-line-subtle" />
              <button
                type="button"
                onMouseEnter={() => setHoveredCategory(null)}
                onClick={() => {
                  onChange({});
                  setOpen(false);
                  setHoveredCategory(null);
                }}
                className="w-full text-left px-3 py-1.5 text-[12px] text-ink-muted hover:text-ink-body hover:bg-hover transition-colors duration-150"
              >
                Clear all filters
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}


function SubMenuValues({
  category,
  currentValue,
  values,
  onPick,
}: {
  category: keyof PlaybookFilterState;
  currentValue: string | undefined;
  values: string[];
  onPick: (value: string | undefined) => void;
}) {
  const label = FILTER_CATEGORIES.find((c) => c.key === category)?.label ?? category;
  return (
    <>
      <div className="px-3 py-2 text-[12px] font-medium text-ink-muted border-b border-line-subtle">
        {label}
      </div>
      <div className="max-h-72 overflow-y-auto scrollbar-thin py-1">
        <FilterOption
          label="All"
          active={!currentValue}
          onClick={() => onPick(undefined)}
        />
        {values.map((v) => (
          <FilterOption
            key={v}
            label={v}
            active={currentValue === v}
            onClick={() => onPick(v)}
          />
        ))}
      </div>
    </>
  );
}


function FilterOption({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left px-3 py-1 text-[13px] flex items-center justify-between gap-2 transition-colors duration-150 ${
        active
          ? 'text-ink font-medium'
          : 'text-ink-body hover:bg-hover hover:text-ink'
      }`}
    >
      <span className="truncate">{label}</span>
      {active && <span className="text-xs text-accent">✓</span>}
    </button>
  );
}


