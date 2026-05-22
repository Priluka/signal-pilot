/** Top-of-page metrics strip for the Agent Feed inbox. */
import type { AgentMetrics, BatchStatus } from '../lib/types';


export function AgentMetricsBar({
  metrics,
  batch,
}: {
  metrics: AgentMetrics | null;
  batch: BatchStatus | null;
}) {
  if (!metrics) {
    return (
      <div className="text-[11px] text-ink-muted font-mono">Loading metrics…</div>
    );
  }
  const cells: Array<[string, string | number, string?]> = [
    ['Processed', `${metrics.processed} / ${metrics.total}`],
    ['Needs review', metrics.needs_review, 'text-amber-700'],
    ['Auto-drafted', metrics.auto_drafted, 'text-indigo-700'],
    ['Auto-resolved', metrics.auto_resolved, 'text-emerald-700'],
    ['Escalated', metrics.escalated, 'text-red-700'],
    ['Skipped', metrics.skipped, 'text-ink-muted'],
    ['Approved', metrics.approved, 'text-emerald-700'],
    ['Rejected', metrics.rejected, 'text-ink-muted'],
    [
      'Approval rate',
      metrics.approval_rate
        ? `${Math.round(metrics.approval_rate * 100)}%`
        : '—',
    ],
    [
      'Avg confidence',
      metrics.avg_confidence ? metrics.avg_confidence.toFixed(2) : '—',
    ],
  ];

  return (
    <div className="flex items-center gap-x-5 gap-y-2 flex-wrap">
      {cells.map(([label, value, tone]) => (
        <div key={label} className="flex items-baseline gap-1.5">
          <span className="text-[10px] uppercase tracking-wider text-ink-muted font-semibold">
            {label}
          </span>
          <span
            className={`text-sm font-mono tabular-nums font-medium ${
              tone ?? 'text-ink'
            }`}
          >
            {value}
          </span>
        </div>
      ))}
      {batch?.running && (
        <div className="ml-auto flex items-center gap-2 text-[11px] text-accent">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
          Processing {batch.processed} / {batch.total}
          {batch.current_ticket && (
            <span className="font-mono text-ink-muted">{batch.current_ticket}</span>
          )}
        </div>
      )}
    </div>
  );
}
