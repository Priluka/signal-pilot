/** /agents — agent runtime control surface.
 *
 * Four sections, top to bottom:
 *   1. Overview card: name + status + counts pulled from /agent/overview.
 *   2. Mode buttons (shadow / assisted / autonomous) with a confirmation
 *      modal on switch — and a confidence-threshold slider. Both persist
 *      to the agent_config SQLite table; the Jira processor reads them
 *      on every ticket.
 *   3. Per-playbook mode table with inline dropdown — operator can pin a
 *      specific playbook to a different mode than the global default.
 *   4. Jira connection card: shows the configured creds (token masked)
 *      and a Test button that pings /rest/api/3/myself.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { useToast } from '../components/Toast';
import {
  getAgentConfig,
  getAgentOverview,
  getJiraConnection,
  listPlaybookModes,
  updateAgentConfig,
  updatePlaybookMode,
} from '../lib/api';
import type {
  AgentConfig,
  AgentMode,
  AgentOverview,
  JiraConnectionStatus,
  PlaybookModeRow,
} from '../lib/types';


const MODES: { key: AgentMode; label: string; blurb: string }[] = [
  {
    key: 'shadow',
    label: 'Shadow',
    blurb:
      'Agent drafts only in the operator inbox. Jira is never touched — Approve just logs feedback, no comment is posted.',
  },
  {
    key: 'assisted',
    label: 'Assisted',
    blurb:
      'Agent drafts only in the operator inbox. Approve posts a clean comment to Jira; Reject discards it. The customer never sees a draft.',
  },
  {
    key: 'autonomous',
    label: 'Autonomous',
    blurb:
      'Agent posts a clean comment to Jira immediately when classifier confidence ≥ threshold. Below threshold falls back to Assisted (operator decides).',
  },
];


export function AgentsPage() {
  const toast = useToast();
  const [overview, setOverview] = useState<AgentOverview | null>(null);
  const [config, setConfig] = useState<AgentConfig | null>(null);
  const [playbookModes, setPlaybookModes] = useState<PlaybookModeRow[]>([]);
  const [jiraStatus, setJiraStatus] = useState<JiraConnectionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [pendingMode, setPendingMode] = useState<AgentMode | null>(null);
  const [savingThreshold, setSavingThreshold] = useState(false);
  const [thresholdDraft, setThresholdDraft] = useState<number | null>(null);
  const [testing, setTesting] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [o, c, pm, jc] = await Promise.all([
        getAgentOverview(),
        getAgentConfig(),
        listPlaybookModes(),
        getJiraConnection(false),
      ]);
      setOverview(o);
      setConfig(c);
      setPlaybookModes(pm);
      setJiraStatus(jc);
      setThresholdDraft(c.confidence_threshold);
    } catch (err) {
      toast.error((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function confirmModeSwitch(next: AgentMode) {
    setPendingMode(null);
    try {
      const updated = await updateAgentConfig({ mode: next });
      setConfig(updated);
      // Tell the rest of the UI (Inbox mode chip, AgentTicketDetail's
      // approve-posts-to-Jira gating) that the mode has changed.
      window.dispatchEvent(new Event('agent-config-changed'));
      toast.success(`Mode → ${next}`);
      // The overview's mode + the table's effective mode column both depend
      // on this — refresh so the UI doesn't disagree with the backend.
      refresh();
    } catch (err) {
      toast.error((err as Error).message);
    }
  }

  async function commitThreshold(value: number) {
    setSavingThreshold(true);
    try {
      const updated = await updateAgentConfig({ confidence_threshold: value });
      setConfig(updated);
      window.dispatchEvent(new Event('agent-config-changed'));
      toast.success(`Threshold → ${value.toFixed(2)}`);
    } catch (err) {
      toast.error((err as Error).message);
    } finally {
      setSavingThreshold(false);
    }
  }

  async function changePlaybookMode(pbId: string, mode: AgentMode | null) {
    try {
      const updated = await updatePlaybookMode(pbId, mode);
      setPlaybookModes((prev) =>
        prev.map((p) => (p.playbook_id === pbId ? updated : p)),
      );
    } catch (err) {
      toast.error((err as Error).message);
    }
  }

  async function testJira() {
    setTesting(true);
    try {
      const status = await getJiraConnection(true);
      setJiraStatus(status);
      if (status.reachable) toast.success('Jira: ' + (status.detail ?? 'OK'));
      else toast.error('Jira: ' + (status.detail ?? 'unreachable'));
    } catch (err) {
      toast.error((err as Error).message);
    } finally {
      setTesting(false);
    }
  }

  const filteredModes = useMemo(() => {
    if (!search.trim()) return playbookModes;
    const needle = search.toLowerCase();
    return playbookModes.filter(
      (p) =>
        p.playbook_id.toLowerCase().includes(needle) ||
        p.title.toLowerCase().includes(needle),
    );
  }, [playbookModes, search]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-slate-400">
        Loading agent control panel…
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="max-w-5xl mx-auto px-8 py-8 space-y-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Agents
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Runtime controls for the support agent. Mode + threshold apply
            globally; per-playbook overrides take precedence when set.
          </p>
        </div>

        {overview && <OverviewCard overview={overview} />}

        {config && (
          <ModeControls
            mode={config.mode}
            threshold={thresholdDraft ?? config.confidence_threshold}
            savingThreshold={savingThreshold}
            onModeRequest={(m) => setPendingMode(m === config.mode ? null : m)}
            onThresholdChange={(v) => setThresholdDraft(v)}
            onThresholdCommit={commitThreshold}
          />
        )}

        <PlaybookModeTable
          rows={filteredModes}
          search={search}
          onSearchChange={setSearch}
          totalCount={playbookModes.length}
          onChangeMode={changePlaybookMode}
        />

        {jiraStatus && (
          <JiraConnectionCard
            status={jiraStatus}
            testing={testing}
            onTest={testJira}
          />
        )}
      </div>

      {pendingMode && config && (
        <ModeSwitchModal
          from={config.mode}
          to={pendingMode}
          onConfirm={() => confirmModeSwitch(pendingMode)}
          onCancel={() => setPendingMode(null)}
        />
      )}
    </div>
  );
}


// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function OverviewCard({ overview }: { overview: AgentOverview }) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">{overview.name}</h2>
          <p className="mt-1 text-sm text-slate-500 flex items-center gap-2">
            <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            {overview.status} ·{' '}
            <ModeBadge mode={overview.mode} />
          </p>
        </div>
        <div className="text-[11px] text-slate-400 font-mono">
          conf ≥ {overview.confidence_threshold.toFixed(2)}
        </div>
      </div>
      <dl className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-3 text-sm">
        <Field label="Source" value={overview.source_label} mono />
        <Field
          label="Playbooks"
          value={`${overview.playbooks_loaded} loaded`}
        />
        <Field label="Processed" value={`${overview.processed}`} />
        <Field
          label="Approval"
          value={
            overview.approval_rate != null
              ? `${Math.round(overview.approval_rate * 100)}% (${overview.approved_count}/${
                  overview.approved_count + overview.rejected_count
                })`
              : '—'
          }
        />
        <Field
          label="Avg conf"
          value={
            overview.avg_confidence != null
              ? overview.avg_confidence.toFixed(2)
              : '—'
          }
        />
        <Field
          label="Uptime"
          value={overview.uptime_since ? `since ${formatDate(overview.uptime_since)}` : '—'}
        />
      </dl>
    </div>
  );
}


function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <dt className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
        {label}
      </dt>
      <dd className={`mt-0.5 text-slate-900 ${mono ? 'font-mono text-[13px]' : ''}`}>
        {value}
      </dd>
    </div>
  );
}


function ModeBadge({ mode }: { mode: AgentMode }) {
  const tone =
    mode === 'shadow'
      ? 'bg-slate-100 text-slate-700 border-slate-200'
      : mode === 'assisted'
      ? 'bg-blue-50 text-blue-700 border-blue-200'
      : 'bg-indigo-50 text-indigo-700 border-indigo-200';
  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider border rounded ${tone}`}>
      {mode}
    </span>
  );
}


function ModeControls({
  mode,
  threshold,
  savingThreshold,
  onModeRequest,
  onThresholdChange,
  onThresholdCommit,
}: {
  mode: AgentMode;
  threshold: number;
  savingThreshold: boolean;
  onModeRequest: (m: AgentMode) => void;
  onThresholdChange: (v: number) => void;
  onThresholdCommit: (v: number) => void;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 space-y-5">
      <div>
        <h3 className="text-sm font-semibold text-slate-900">Operating mode</h3>
        <p className="text-[12px] text-slate-500 mt-0.5">
          Determines what the agent writes back to Jira after each ticket.
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {MODES.map((m) => {
          const active = m.key === mode;
          return (
            <button
              key={m.key}
              type="button"
              onClick={() => onModeRequest(m.key)}
              className={`text-left p-4 border rounded-lg transition-colors ${
                active
                  ? 'border-blue-500 bg-blue-50/40 ring-2 ring-blue-500/15'
                  : 'border-slate-200 hover:border-slate-300 bg-white'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-900">{m.label}</span>
                {active && (
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-blue-500" />
                )}
              </div>
              <p className="mt-1 text-[12px] text-slate-600 leading-relaxed">{m.blurb}</p>
            </button>
          );
        })}
      </div>

      <div className="pt-4 border-t border-slate-100">
        <div className="flex items-center justify-between">
          <label htmlFor="conf" className="text-sm font-medium text-slate-900">
            Minimum confidence for drafting
          </label>
          <span className="text-sm font-mono tabular-nums text-slate-700">
            {threshold.toFixed(2)}
          </span>
        </div>
        <p className="text-[11px] text-slate-500 mt-0.5">
          Below this → escalate to human. In Autonomous mode, only tickets at
          or above this number are auto-sent.
        </p>
        <input
          id="conf"
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={threshold}
          disabled={savingThreshold}
          onChange={(e) => onThresholdChange(parseFloat(e.target.value))}
          onMouseUp={(e) =>
            onThresholdCommit(parseFloat((e.target as HTMLInputElement).value))
          }
          onTouchEnd={(e) =>
            onThresholdCommit(parseFloat((e.target as HTMLInputElement).value))
          }
          className="w-full mt-2 accent-blue-600"
        />
        <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-mono">
          <span>0.0</span>
          <span>0.5</span>
          <span>1.0</span>
        </div>
      </div>
    </div>
  );
}


function PlaybookModeTable({
  rows,
  search,
  onSearchChange,
  totalCount,
  onChangeMode,
}: {
  rows: PlaybookModeRow[];
  search: string;
  onSearchChange: (v: string) => void;
  totalCount: number;
  onChangeMode: (pbId: string, mode: AgentMode | null) => void;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Per-playbook overrides</h3>
          <p className="text-[12px] text-slate-500 mt-0.5">
            Pin a specific playbook to a different mode. Empty selection follows the global mode.
          </p>
        </div>
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Filter…"
          className="w-72 px-3 py-1.5 text-sm border border-slate-200 rounded-md focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15"
        />
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[10px] uppercase tracking-wider text-slate-500 border-b border-slate-200">
            <th className="text-left px-4 py-2 font-medium">Playbook</th>
            <th className="text-left py-2 font-medium">Mode</th>
            <th className="text-right py-2 font-medium">Approve %</th>
            <th className="text-right py-2 font-medium">Avg conf</th>
            <th className="text-right px-4 py-2 font-medium">Processed</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.length === 0 && (
            <tr>
              <td colSpan={5} className="text-center py-6 text-sm text-slate-400">
                No playbooks match.
              </td>
            </tr>
          )}
          {rows.map((r) => (
            <tr key={r.playbook_id} className="hover:bg-slate-50">
              <td className="px-4 py-2">
                <Link
                  to={`/knowledge/${r.playbook_id}`}
                  className="text-sm font-medium text-slate-900 hover:text-blue-700 leading-snug"
                >
                  {r.title}
                </Link>
                <div className="text-[11px] font-mono text-slate-500 truncate">
                  {r.playbook_id}
                </div>
              </td>
              <td className="py-2">
                <div className="flex items-center gap-2">
                  <select
                    value={r.is_override ? r.mode : ''}
                    onChange={(e) =>
                      onChangeMode(
                        r.playbook_id,
                        e.target.value === '' ? null : (e.target.value as AgentMode),
                      )
                    }
                    className="px-2 py-0.5 text-xs border border-slate-200 rounded bg-white"
                  >
                    <option value="">follow global ({r.mode})</option>
                    <option value="shadow">Shadow</option>
                    <option value="assisted">Assisted</option>
                    <option value="autonomous">Autonomous</option>
                  </select>
                  {r.is_override && <ModeBadge mode={r.mode} />}
                </div>
              </td>
              <td className="text-right py-2 font-mono tabular-nums">
                {r.approve_rate != null
                  ? `${Math.round(r.approve_rate * 100)}%`
                  : '—'}
              </td>
              <td className="text-right py-2 font-mono tabular-nums">
                {r.avg_confidence != null ? r.avg_confidence.toFixed(2) : '—'}
              </td>
              <td className="text-right px-4 py-2 font-mono tabular-nums text-slate-600">
                {r.sample_count > 0 ? r.sample_count : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="px-6 py-2 border-t border-slate-100 text-[11px] text-slate-500 font-mono">
        Showing {rows.length} of {totalCount} playbooks
      </div>
    </div>
  );
}


function JiraConnectionCard({
  status,
  testing,
  onTest,
}: {
  status: JiraConnectionStatus;
  testing: boolean;
  onTest: () => void;
}) {
  const tone = !status.configured
    ? 'border-amber-200 bg-amber-50/40'
    : status.reachable === false
    ? 'border-red-200 bg-red-50/40'
    : status.reachable === true
    ? 'border-emerald-200 bg-emerald-50/40'
    : 'border-slate-200 bg-white';
  return (
    <div className={`border rounded-lg p-6 ${tone}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Jira connection</h3>
          <p className="text-[12px] text-slate-500 mt-0.5">
            Credentials are read from the backend <code>.env</code> at boot. Edit
            them there to change the wired account.
          </p>
        </div>
        <button
          type="button"
          onClick={onTest}
          disabled={testing || !status.configured}
          className="px-3 py-1.5 text-xs font-medium border border-slate-200 bg-white rounded hover:bg-slate-50 disabled:opacity-60"
        >
          {testing ? 'Testing…' : 'Test connection'}
        </button>
      </div>
      <dl className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm">
        <Field label="URL" value={status.url ?? '—'} mono />
        <Field label="Project" value={status.project ?? '—'} mono />
        <Field label="Email" value={status.email ?? '—'} mono />
        <Field label="API token" value={status.token_masked ?? '—'} mono />
      </dl>
      {status.detail && (
        <p className="mt-4 text-[12px] font-mono text-slate-600">
          {status.detail}
        </p>
      )}
    </div>
  );
}


function ModeSwitchModal({
  from,
  to,
  onConfirm,
  onCancel,
}: {
  from: AgentMode;
  to: AgentMode;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const message =
    to === 'shadow'
      ? 'Switch to Shadow mode? Agent will draft only in the inbox; Approve will not post anything to Jira.'
      : to === 'assisted'
      ? 'Switch to Assisted mode? Agent will draft in the inbox; the operator decides per ticket whether the draft is posted to Jira. The customer never sees a draft.'
      : 'Switch to Autonomous mode? Agent will post the draft as the final reply for tickets where classifier confidence meets the threshold. Below threshold falls back to Assisted.';
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40">
      <div className="bg-white rounded-lg shadow-xl border border-slate-200 max-w-md w-full mx-4 p-6">
        <h2 className="text-base font-semibold text-slate-900">Confirm mode switch</h2>
        <p className="mt-2 text-sm text-slate-700 leading-relaxed">{message}</p>
        <div className="mt-4 text-[11px] text-slate-500 font-mono">
          {from} → <strong className="text-slate-700">{to}</strong>
        </div>
        <div className="mt-5 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="px-3 py-1.5 text-sm text-slate-600 rounded hover:bg-slate-100"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
          >
            Switch to {to}
          </button>
        </div>
      </div>
    </div>
  );
}


function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}
