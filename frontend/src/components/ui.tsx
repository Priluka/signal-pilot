/** Small presentational primitives shared across pages. */
import { Link } from 'react-router-dom';


/** Status pill — green for active, amber for draft, slate for anything else. */
export function StatusBadge({ status }: { status: string }) {
  const norm = (status || '').toLowerCase();
  const tone =
    norm === 'active'
      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
      : norm === 'draft'
      ? 'bg-amber-50 text-amber-700 border-amber-200'
      : 'bg-slate-50 text-slate-600 border-slate-200';
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-medium border rounded ${tone}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          norm === 'active'
            ? 'bg-emerald-500'
            : norm === 'draft'
            ? 'bg-amber-500'
            : 'bg-slate-400'
        }`}
      />
      {status || 'unknown'}
    </span>
  );
}


/** Colored progress bar — green ≥0.7, amber ≥0.4, red below. */
export function ConfidenceBar({ score }: { score: number | null }) {
  if (score == null) return <span className="text-xs text-slate-400">—</span>;
  const pct = Math.max(0, Math.min(1, score)) * 100;
  const tone =
    score >= 0.7
      ? 'bg-emerald-500'
      : score >= 0.4
      ? 'bg-amber-500'
      : 'bg-red-500';
  return (
    <div className="flex items-center gap-2 min-w-[120px]">
      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-slate-600 font-mono tabular-nums w-9 text-right">
        {score.toFixed(2)}
      </span>
    </div>
  );
}


/** Small monospace chip — used for ticket IDs (BS-42708) and playbook ids. */
export function TicketChip({ id, href }: { id: string; href?: string }) {
  const body = (
    <span className="inline-flex items-center px-1.5 py-0.5 text-[11px] font-mono rounded border border-slate-200 bg-slate-50 text-slate-700">
      {id}
    </span>
  );
  return href ? <Link to={href}>{body}</Link> : body;
}


/** Generic non-monospace pill — used for languages, countries, ticket_class. */
export function Chip({
  children,
  tone = 'neutral',
}: {
  children: React.ReactNode;
  tone?: 'neutral' | 'blue';
}) {
  const toneClass =
    tone === 'blue'
      ? 'bg-blue-50 text-blue-700 border-blue-200'
      : 'bg-slate-50 text-slate-600 border-slate-200';
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-[11px] rounded border ${toneClass}`}
    >
      {children}
    </span>
  );
}


/** Blue numbered circle — used for resolution steps. */
export function StepCircle({ n }: { n: number }) {
  return (
    <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-blue-50 text-blue-700 font-semibold text-xs border border-blue-200 shrink-0">
      {n}
    </span>
  );
}


/** Section heading inside a viewer card. */
export function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-[11px] font-semibold tracking-wider uppercase text-slate-500 mb-3">
      {children}
    </h3>
  );
}
