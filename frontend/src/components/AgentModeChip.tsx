/** Small badge that renders an agent mode (shadow / assisted / autonomous)
 * with consistent colors + tooltip across the inbox row, the ticket detail
 * header, and any other place that wants to show "this ticket was handled
 * under mode X" or "the global default is mode Y".
 *
 * Variants:
 *   * size='sm' — compact pill for inbox rows.
 *   * size='md' — default, used in the ticket detail header.
 *   * prefix   — optional leading label such as "Default:" for the inbox
 *                top-bar info chip.
 */
import type { AgentMode } from '../lib/types';


const TONE: Record<AgentMode, { pill: string; dot: string; label: string; tip: string }> = {
  shadow: {
    pill: 'bg-slate-100 text-slate-700 border-slate-200',
    dot: 'bg-slate-400',
    label: 'Shadow',
    tip: 'Approve only logs feedback locally. Jira is not touched.',
  },
  assisted: {
    pill: 'bg-blue-50 text-blue-700 border-blue-200',
    dot: 'bg-blue-500',
    label: 'Assisted',
    tip: 'Approve posts the (clean) draft as a Jira comment.',
  },
  autonomous: {
    pill: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dot: 'bg-emerald-500',
    label: 'Autonomous',
    tip: 'Agent auto-posts when classifier confidence ≥ threshold.',
  },
};


interface Props {
  mode: AgentMode;
  size?: 'sm' | 'md';
  prefix?: string;
}


export function AgentModeChip({ mode, size = 'md', prefix }: Props) {
  const tone = TONE[mode];
  const sizing =
    size === 'sm'
      ? 'px-1.5 py-px text-[10px] gap-1'
      : 'px-2 py-0.5 text-[11px] gap-1.5';
  const dotSize = size === 'sm' ? 'w-1 h-1' : 'w-1.5 h-1.5';
  return (
    <span
      title={tone.tip}
      className={`inline-flex items-center ${sizing} font-medium border rounded ${tone.pill}`}
    >
      <span className={`rounded-full ${dotSize} ${tone.dot}`} />
      {prefix && <span className="opacity-70">{prefix}</span>}
      {tone.label}
    </span>
  );
}
