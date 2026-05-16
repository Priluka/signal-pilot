/** One retrieved playbook surfaced as a Chat source. */
import { Link } from 'react-router-dom';

import type { RetrievalHitOut } from '../lib/types';

import { Chip, ConfidenceBar } from './ui';


export function SourceCard({
  hit,
  cited,
}: {
  hit: RetrievalHitOut;
  cited: boolean;
}) {
  return (
    <Link
      to={`/knowledge/${hit.playbook_id}`}
      className="block bg-panel-surface border border-panel-border rounded-lg p-4 hover:border-blue-300 transition-colors"
    >
      <div className="flex items-start gap-2 mb-1.5">
        <span className="text-[11px] font-mono text-slate-400 w-6 shrink-0 pt-0.5">
          #{hit.rank + 1}
        </span>
        <div className="flex-1">
          <h4 className="text-sm font-medium text-slate-900 leading-snug">
            {hit.title}
          </h4>
          <div className="mt-0.5 text-[11px] text-slate-500 font-mono">{hit.playbook_id}</div>
        </div>
        {cited && (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-200 rounded">
            cited
          </span>
        )}
      </div>
      <div className="ml-8 mt-2">
        <ConfidenceBar score={hit.score} />
      </div>
      <div className="ml-8 mt-2 flex flex-wrap gap-1.5">
        <Chip tone="blue">{hit.ticket_class}</Chip>
        <Chip>{hit.issue_category}</Chip>
        {hit.country_focus.filter((c) => c !== 'other').map((c) => (
          <Chip key={c}>{c}</Chip>
        ))}
        {hit.project_keys.map((k) => (
          <Chip key={k}>{k}</Chip>
        ))}
      </div>
      <p className="ml-8 mt-2 text-sm text-slate-600 leading-relaxed line-clamp-2">
        {hit.description}
      </p>
    </Link>
  );
}
