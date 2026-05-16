/**
 * Dark fixed sidebar with three navigation sections + a Chat link pinned at
 * the bottom. Category counts are fetched live from /categories so the
 * sidebar always reflects the actual corpus.
 */
import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';

import { getCategories } from '../lib/api';
import type { CategoriesResponse } from '../lib/types';


function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-4 pt-6 pb-2 text-[11px] font-semibold tracking-wider uppercase text-sidebar-heading">
      {children}
    </div>
  );
}

function NavRow({
  to,
  label,
  count,
}: {
  to: string;
  label: string;
  count?: number;
}) {
  return (
    <NavLink
      to={to}
      end
      className={({ isActive }) =>
        [
          'flex items-center justify-between px-4 py-1.5 mx-2 rounded-md text-sm transition-colors',
          isActive
            ? 'bg-sidebar-surface text-sidebar-textActive'
            : 'text-sidebar-text hover:bg-sidebar-surface/60 hover:text-sidebar-textActive',
        ].join(' ')
      }
    >
      <span>{label}</span>
      {typeof count === 'number' && (
        <span className="text-xs text-sidebar-muted font-mono tabular-nums">
          {count}
        </span>
      )}
    </NavLink>
  );
}

export function Sidebar() {
  const [categories, setCategories] = useState<CategoriesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getCategories()
      .then((data) => {
        if (!cancelled) setCategories(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <aside className="flex flex-col w-64 shrink-0 bg-sidebar-bg border-r border-sidebar-border text-sidebar-text">
      {/* Logo */}
      <div className="px-5 pt-6 pb-2">
        <div className="text-base font-semibold text-sidebar-textActive tracking-tight">
          Signal Pilot
        </div>
        <div className="text-[11px] text-sidebar-muted mt-0.5">
          Support triage prototype
        </div>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin pb-4">
        <SectionHeading>Knowledge Library</SectionHeading>
        <NavRow to="/knowledge" label="Playbooks" count={categories?.total} />
        <NavRow to="/knowledge/gaps" label="Gaps" count={
          categories?.issue_categories.find((c) => c.name === 'knowledge_gap')?.count
        } />
        <NavRow to="/knowledge/suggestions" label="Suggestions" />

        <SectionHeading>Categories</SectionHeading>
        {error && (
          <div className="px-4 text-[11px] text-red-400">{error}</div>
        )}
        {categories &&
          categories.issue_categories.map((cat) => (
            <NavRow
              key={cat.name}
              to={`/knowledge?issue_category=${cat.name}`}
              label={cat.name}
              count={cat.count}
            />
          ))}

        <SectionHeading>Agents</SectionHeading>
        <NavRow to="/agents/deployed" label="Deployed" />
        <NavRow to="/agents/shadow" label="Shadow mode" />
        <NavRow to="/agents/performance" label="Performance" />
      </div>

      {/* Pinned Chat link at the bottom */}
      <div className="border-t border-sidebar-border px-2 py-3">
        <NavLink
          to="/chat"
          className={({ isActive }) =>
            [
              'flex items-center justify-between px-3 py-2 rounded-md text-sm transition-colors',
              isActive
                ? 'bg-sidebar-surface text-sidebar-textActive'
                : 'text-sidebar-text hover:bg-sidebar-surface/60 hover:text-sidebar-textActive',
            ].join(' ')
          }
        >
          <span>Chat</span>
          <span className="text-xs text-sidebar-muted">Sonnet 4.6</span>
        </NavLink>
        <NavLink
          to="/agent"
          className={({ isActive }) =>
            [
              'flex items-center justify-between mt-1 px-3 py-2 rounded-md text-sm transition-colors',
              isActive
                ? 'bg-sidebar-surface text-sidebar-textActive'
                : 'text-sidebar-text hover:bg-sidebar-surface/60 hover:text-sidebar-textActive',
            ].join(' ')
          }
        >
          <span>Agent Feed</span>
          <span className="text-xs text-sidebar-muted">50 tickets</span>
        </NavLink>
      </div>
    </aside>
  );
}
