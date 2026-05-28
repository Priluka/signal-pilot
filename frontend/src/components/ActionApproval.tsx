/** ActionApproval — HITL panel for the planner's paused tool_use calls.
 *
 * Fetches pending actions for one ticket and renders each as a card:
 * skill name + params (formatted readably) + Approve / Reject buttons.
 * After a decision the panel re-fetches — if the planner produced another
 * pending action on the next loop iteration, it shows up here too.
 *
 * Placed in AgentTicketDetail BETWEEN the matched playbook card and the
 * drafted reply, so the operator sees "agent wants to do X" right next
 * to the playbook that justified the action.
 */
import { useCallback, useEffect, useState } from 'react';
import { Check, Loader2, X, Zap } from 'lucide-react';

import {
  approveAction,
  listPendingActionsForTicket,
  rejectAction,
} from '../lib/api';
import type { PendingAction, PlannerResultOut } from '../lib/types';

import { useToast } from './Toast';


interface Props {
  ticketKey: string;
  /** Bubble up planner outcomes so the parent (ticket detail) can
   *  refresh session state if the loop completed. */
  onPlannerResult?: (result: PlannerResultOut) => void;
}


export function ActionApproval({ ticketKey, onPlannerResult }: Props) {
  const toast = useToast();
  const [actions, setActions] = useState<PendingAction[] | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    listPendingActionsForTicket(ticketKey)
      .then(setActions)
      .catch((e: Error) => setError(e.message));
  }, [ticketKey]);

  useEffect(() => {
    refresh();
    // Poll every 3s so a planner that's iterating in the background
    // (e.g. another iteration produced a new pending action right after
    // the operator approved the previous one) surfaces without making
    // them refresh the browser. Cheap — one tiny GET against an
    // in-memory SQLite table.
    const id = setInterval(refresh, 3000);
    return () => clearInterval(id);
  }, [refresh]);

  async function handleApprove(action: PendingAction) {
    setBusyId(action.id);
    try {
      const result = await approveAction(action.id);
      toast.success(
        result.status === 'done'
          ? `${action.skill_name} executed · planner done`
          : `${action.skill_name} executed · ${result.status}`,
      );
      onPlannerResult?.(result);
      refresh();
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  async function handleReject(action: PendingAction) {
    setBusyId(action.id);
    try {
      const result = await rejectAction(
        action.id,
        'Operator rejected from inbox.',
      );
      toast.success(`${action.skill_name} rejected · ${result.status}`);
      onPlannerResult?.(result);
      refresh();
    } catch (e) {
      toast.error((e as Error).message);
    } finally {
      setBusyId(null);
    }
  }

  if (error) {
    return (
      <Wrapper>
        <p className="text-[12px] text-red-600 dark:text-red-400 px-4 py-3">
          Failed to load pending actions: {error}
        </p>
      </Wrapper>
    );
  }

  if (actions === null || actions.length === 0) {
    return null;
  }

  return (
    <Wrapper>
      <div className="px-4 pt-3 pb-1 flex items-center gap-2">
        <Zap
          width={14}
          height={14}
          strokeWidth={1.75}
          className="text-amber-600 dark:text-amber-400"
        />
        <h3 className="text-[13px] font-semibold text-ink">
          Agent action{actions.length > 1 ? 's' : ''} awaiting approval
          <span className="text-ink-muted font-normal ml-1.5">
            · {actions.length}
          </span>
        </h3>
      </div>
      <ul>
        {actions.map((a) => (
          <li
            key={a.id}
            className="px-4 py-3 border-t border-line-subtle first:border-t-0"
          >
            <ActionCard
              action={a}
              busy={busyId === a.id}
              onApprove={() => handleApprove(a)}
              onReject={() => handleReject(a)}
            />
          </li>
        ))}
      </ul>
    </Wrapper>
  );
}


function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <section className="border border-amber-200 dark:border-amber-800/60 bg-amber-50/40 dark:bg-amber-950/20 rounded-lg overflow-hidden">
      {children}
    </section>
  );
}


function ActionCard({
  action,
  busy,
  onApprove,
  onReject,
}: {
  action: PendingAction;
  busy: boolean;
  onApprove: () => void;
  onReject: () => void;
}) {
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3">
        <div className="font-mono text-[12px] text-ink font-semibold">
          {action.skill_name}
        </div>
        <div className="text-[10px] uppercase tracking-wider text-ink-muted font-mono">
          iter {action.iteration} · {action.mode}
        </div>
      </div>
      <ParamsBlock input={action.skill_input} />
      <div className="mt-3 flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onReject}
          disabled={busy}
          className="inline-flex items-center gap-1 px-3 h-8 text-[12px] font-medium rounded-md border border-red-200 text-red-600 hover:bg-red-50 dark:border-red-800/60 dark:text-red-400 dark:hover:bg-red-950/40 transition-colors duration-150 disabled:opacity-60"
        >
          <X width={12} height={12} strokeWidth={2} />
          Reject
        </button>
        <button
          type="button"
          onClick={onApprove}
          disabled={busy}
          className="inline-flex items-center gap-1 px-3 h-8 text-[12px] font-medium rounded-md bg-accent text-white hover:bg-accent-hover transition-colors duration-150 disabled:opacity-60"
        >
          {busy ? (
            <Loader2 width={12} height={12} className="animate-spin" />
          ) : (
            <Check width={12} height={12} strokeWidth={2} />
          )}
          {busy ? 'Working…' : 'Approve & run'}
        </button>
      </div>
    </div>
  );
}


function ParamsBlock({ input }: { input: Record<string, unknown> }) {
  const entries = Object.entries(input);
  if (entries.length === 0) {
    return (
      <p className="mt-2 text-[11px] text-ink-muted italic">no parameters</p>
    );
  }
  return (
    <dl className="mt-2 space-y-1">
      {entries.map(([k, v]) => (
        <div key={k} className="flex items-baseline gap-2 text-[12px]">
          <dt className="font-mono text-ink-muted shrink-0 min-w-[5rem]">
            {k}
          </dt>
          <dd className="text-ink-body break-words whitespace-pre-wrap font-mono">
            {formatValue(v)}
          </dd>
        </div>
      ))}
    </dl>
  );
}


function formatValue(v: unknown): string {
  if (v == null) return '—';
  if (typeof v === 'string') return v;
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  try {
    return JSON.stringify(v, null, 2);
  } catch {
    return String(v);
  }
}
