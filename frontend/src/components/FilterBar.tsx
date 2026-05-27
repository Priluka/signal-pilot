/** Horizontal dropdown filter bar for the Playbooks view.
 *
 * Each filter is a URL search param so the state is bookmarkable. The
 * dropdown options are derived from the full playbook corpus so the user
 * only ever sees values that exist in the data.
 */
import type { PlaybookSummary } from '../lib/types';
import { countryLabel, sourceLabel, ticketClassLabel } from './../lib/labels';


export interface PlaybookFilterState {
  ticket_class?: string;
  issue_category?: string;
  country?: string;
  source?: string;
}


function uniqSorted(values: Iterable<string>, drop: Set<string> = new Set()): string[] {
  const set = new Set<string>();
  for (const v of values) {
    if (!v || drop.has(v)) continue;
    set.add(v);
  }
  return Array.from(set).sort();
}


/** Resolve a friendly label for a given filter key. The dropdown <option>
 *  value stays the raw code (URL stability); only the visible text changes. */
function labelFor(filterKey: keyof PlaybookFilterState, raw: string): string {
  switch (filterKey) {
    case 'ticket_class':
      return ticketClassLabel(raw);
    case 'source':
      return sourceLabel(raw);
    case 'country': {
      const { flag, name } = countryLabel(raw);
      return flag ? `${flag} ${name}` : name;
    }
    default:
      return raw;
  }
}


export function deriveFilterOptions(playbooks: PlaybookSummary[]) {
  const tc = uniqSorted(playbooks.map((p) => p.ticket_class));
  const ic = uniqSorted(playbooks.map((p) => p.issue_category));
  const co = uniqSorted(
    playbooks.flatMap((p) => p.country_focus),
    new Set(['other']),
  );
  const src = uniqSorted(playbooks.flatMap((p) => p.project_keys));
  return { ticket_class: tc, issue_category: ic, country: co, source: src };
}


interface Props {
  filters: PlaybookFilterState;
  onChange: (next: PlaybookFilterState) => void;
  options: ReturnType<typeof deriveFilterOptions>;
}


function FilterSelect({
  label,
  filterKey,
  value,
  options,
  onChange,
}: {
  label: string;
  filterKey: keyof PlaybookFilterState;
  value: string | undefined;
  options: string[];
  onChange: (v: string | undefined) => void;
}) {
  return (
    <label className="flex flex-col gap-1 min-w-0">
      <span className="text-[10px] font-semibold tracking-wider uppercase text-ink-muted">
        {label}
      </span>
      <select
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value || undefined)}
        className="w-full px-2 py-1.5 text-xs bg-card border border-line rounded focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 truncate"
      >
        <option value="">All</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {labelFor(filterKey, opt)}
          </option>
        ))}
      </select>
    </label>
  );
}


export function FilterBar({ filters, onChange, options }: Props) {
  const anyActive = Object.values(filters).some(Boolean);
  return (
    <div className="px-4 pt-3 pb-2 border-b border-panel-border bg-panel-surface">
      <div className="grid grid-cols-2 gap-2">
        <FilterSelect
          label="Ticket class"
          filterKey="ticket_class"
          value={filters.ticket_class}
          options={options.ticket_class}
          onChange={(v) => onChange({ ...filters, ticket_class: v })}
        />
        <FilterSelect
          label="Category"
          filterKey="issue_category"
          value={filters.issue_category}
          options={options.issue_category}
          onChange={(v) => onChange({ ...filters, issue_category: v })}
        />
        <FilterSelect
          label="Country"
          filterKey="country"
          value={filters.country}
          options={options.country}
          onChange={(v) => onChange({ ...filters, country: v })}
        />
        <FilterSelect
          label="Source"
          filterKey="source"
          value={filters.source}
          options={options.source}
          onChange={(v) => onChange({ ...filters, source: v })}
        />
      </div>
      {anyActive && (
        <button
          type="button"
          onClick={() => onChange({})}
          className="mt-2 text-[11px] text-accent hover:text-accent"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}


/** Pure: returns the subset of playbooks that satisfies every active filter. */
export function applyFilters(
  playbooks: PlaybookSummary[],
  filters: PlaybookFilterState,
): PlaybookSummary[] {
  return playbooks.filter((pb) => {
    if (filters.ticket_class && pb.ticket_class !== filters.ticket_class) return false;
    if (filters.issue_category && pb.issue_category !== filters.issue_category) return false;
    if (filters.country && !pb.country_focus.includes(filters.country)) return false;
    if (filters.source && !pb.project_keys.includes(filters.source)) return false;
    return true;
  });
}
