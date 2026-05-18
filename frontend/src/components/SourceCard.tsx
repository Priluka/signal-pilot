/** Footnote-style source row at the bottom of the Chat tab.
 *
 * Just the number, the playbook title (linked to the viewer), and a short
 * description. No 'cited' pill and no score bar — the inline citation
 * superscripts already convey which sources the answer leans on.
 */
import { Link } from 'react-router-dom';

import type { RetrievalHitOut } from '../lib/types';


export function SourceCard({
  hit,
  number,
}: {
  hit: RetrievalHitOut;
  number: number;
}) {
  return (
    <li
      id={`source-${number}`}
      className="flex gap-3 scroll-mt-4 bg-panel-surface border border-panel-border rounded-lg px-4 py-3 hover:border-blue-300 transition-colors"
    >
      <span className="text-sm font-semibold text-blue-700 font-mono tabular-nums w-6 shrink-0 pt-0.5">
        {number}.
      </span>
      <div className="flex-1 min-w-0">
        <Link
          to={`/knowledge/${hit.playbook_id}`}
          className="text-sm font-medium text-slate-900 hover:text-blue-700 leading-snug"
        >
          {hit.title}
        </Link>
        <p className="mt-1 text-xs text-slate-600 leading-relaxed line-clamp-2">
          {hit.description}
        </p>
      </div>
    </li>
  );
}
