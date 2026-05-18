/** Pill that renders an ``AgentStatus`` — used in the inbox list and the
 * detail header. Single source of color/label so a status flows consistently
 * through the UI.
 */
import type { AgentStatus } from '../lib/types';


const STATUS_META: Record<AgentStatus, { label: string; tone: string; dot: string }> = {
  pending: {
    label: 'pending',
    tone: 'bg-slate-50 text-slate-500 border-slate-200',
    dot: 'bg-slate-300',
  },
  in_progress: {
    label: 'processing',
    tone: 'bg-blue-50 text-blue-700 border-blue-200',
    dot: 'bg-blue-500',
  },
  needs_review: {
    label: 'needs review',
    tone: 'bg-amber-50 text-amber-700 border-amber-200',
    dot: 'bg-amber-500',
  },
  escalated: {
    label: 'escalated',
    tone: 'bg-red-50 text-red-700 border-red-200',
    dot: 'bg-red-500',
  },
  auto_drafted: {
    label: 'auto-drafted',
    tone: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    dot: 'bg-indigo-500',
  },
  auto_resolved: {
    label: 'auto-resolved',
    tone: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dot: 'bg-emerald-500',
  },
  approved: {
    label: 'approved',
    tone: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dot: 'bg-emerald-500',
  },
  rejected: {
    label: 'rejected',
    tone: 'bg-slate-50 text-slate-600 border-slate-200',
    dot: 'bg-slate-400',
  },
  skipped: {
    label: 'skipped',
    tone: 'bg-slate-50 text-slate-600 border-slate-200',
    dot: 'bg-slate-400',
  },
};


export function AgentStatusPill({
  status,
  size = 'sm',
}: {
  status: AgentStatus;
  size?: 'sm' | 'md';
}) {
  const meta = STATUS_META[status];
  const sizing =
    size === 'md'
      ? 'px-2 py-0.5 text-xs gap-1.5'
      : 'px-1.5 py-0 text-[10px] gap-1';
  return (
    <span
      className={`inline-flex items-center border rounded ${sizing} ${meta.tone}`}
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
