/** Status chip rendered everywhere a ticket's derived status appears.
 *
 * Linear-style: barely-tinted background (-50), medium text (-600), subtle
 * border (-200), with a leading status dot. Single source of truth for
 * colour + label across inbox row, ticket detail header, and the activity
 * log groups.
 */
import type { AgentStatus } from '../lib/types';


const STATUS_META: Record<AgentStatus, { label: string; tone: string; dot: string }> = {
  pending: {
    label: 'pending',
    tone: 'bg-hover text-ink-muted border-line',
    dot: 'bg-slate-300',
  },
  in_progress: {
    label: 'processing',
    tone: 'bg-accent-subtle text-accent-fg border-accent/20',
    dot: 'bg-accent',
  },
  needs_review: {
    label: 'needs review',
    tone: 'bg-amber-50 text-amber-600 border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800/60',
    dot: 'bg-amber-500',
  },
  escalated: {
    label: 'escalated',
    tone: 'bg-red-50 text-red-600 border-red-200 dark:bg-red-950/40 dark:text-red-300 dark:border-red-800/60',
    dot: 'bg-red-500',
  },
  auto_drafted: {
    label: 'auto-drafted',
    tone: 'bg-blue-50 text-blue-600 border-blue-200 dark:bg-blue-950/40 dark:text-blue-300 dark:border-blue-800/60',
    dot: 'bg-blue-500',
  },
  auto_resolved: {
    label: 'auto-sent',
    tone: 'bg-emerald-50 text-emerald-600 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60',
    dot: 'bg-emerald-500',
  },
  approved: {
    label: 'approved',
    tone: 'bg-emerald-50 text-emerald-600 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800/60',
    dot: 'bg-emerald-500',
  },
  rejected: {
    label: 'rejected',
    tone: 'bg-hover text-ink-body border-line',
    dot: 'bg-slate-400',
  },
  skipped: {
    label: 'skipped',
    tone: 'bg-hover text-ink-body border-line',
    dot: 'bg-slate-400',
  },
};


export function AgentStatusPill({
  status,
  size = 'sm',
}: {
  status: AgentStatus;
  /** ``sm`` → bare dot for list rows; ``md`` → full chip for detail headers. */
  size?: 'sm' | 'md';
}) {
  const meta = STATUS_META[status];

  // List variant: a single status dot. Title attribute keeps the label
  // accessible on hover / for screen readers without taking row width.
  if (size === 'sm') {
    return (
      <span
        title={meta.label}
        aria-label={meta.label}
        className={`inline-block w-1.5 h-1.5 rounded-full shrink-0 ${meta.dot}`}
      />
    );
  }

  // Detail variant: full chip with label.
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium border ${meta.tone}`}
    >
      <span className={`inline-block w-1.5 h-1.5 rounded-full ${meta.dot}`} />
      {meta.label}
    </span>
  );
}


/** Numeric priority for sorting: lowest first appears at the top of the inbox. */
export function statusPriority(status: AgentStatus | undefined): number {
  switch (status) {
    case 'escalated':
      return 0;
    case 'needs_review':
      return 1;
    case 'in_progress':
      return 2;
    case 'auto_drafted':
      return 3;
    case 'auto_resolved':
      return 4;
    case 'approved':
      return 5;
    case 'rejected':
      return 6;
    case 'skipped':
      return 7;
    case 'pending':
    default:
      return 8;
  }
}
