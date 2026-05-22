/** /agents — agent runtime control surface.
 *
 * Premium settings-page feel: a single ``max-w-4xl`` column of flat
 * sections separated by hairline borders, no nested cards. Sections:
 *
 *   1. Header: name + Active status pill + subtitle.
 *   2. Stats grid: 6-up grid of metrics pulled from /agent/overview.
 *   3. Operating mode: three columned cards (shadow / assisted / autonomous).
 *      Switching opens a confirmation modal that persists to agent_config.
 *   4. Confidence threshold: a custom-styled slider that commits on
 *      mouseup / touchend so we don't spam PATCH requests during drag.
 *   5. Per-playbook overrides: filterable table with an inline mode
 *      dropdown that PATCHes /agent/playbook-modes/<id>.
 *   6. Jira connection: bordered card with masked credentials and a
 *      Test button that pings /rest/api/3/myself.
 */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown } from 'lucide-react';

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
      'Agent drafts in inbox. Approve posts a clean comment to Jira; Reject discards it. The customer never sees a draft.',
  },
  {
    key: 'autonomous',
    label: 'Autonomous',
    blurb:
      'Agent posts a comment to Jira immediately when classifier confidence ≥ threshold. Below threshold falls back to Assisted.',
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
      <div className="h-full flex items-center justify-center text-sm text-ink-muted">
        Loading agent control panel…
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="max-w-4xl mx-auto px-8 py-8">
        {overview && <Header overview={overview} />}
        {overview && <StatsGrid overview={overview} />}
        {config && (
          <ModeSection
            mode={config.mode}
            onModeRequest={(m) =>
              setPendingMode(m === config.mode ? null : m)
            }
          />
        )}
        {config && (
          <ThresholdSection
            value={thresholdDraft ?? config.confidence_threshold}
            saving={savingThreshold}
            onChange={(v) => setThresholdDraft(v)}
            onCommit={commitThreshold}
          />
        )}
        <OverridesSection
          rows={filteredModes}
          search={search}
          onSearchChange={setSearch}
          totalCount={playbookModes.length}
          onChangeMode={changePlaybookMode}
        />
        {jiraStatus && (
          <JiraSection
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
// Header
// ---------------------------------------------------------------------------

function Header({ overview }: { overview: AgentOverview }) {
  const isActive = (overview.status ?? '').toLowerCase() === 'active';
  return (
    <header>
      <div className="flex items-baseline justify-between gap-3 flex-wrap">
        <h1 className="text-xl font-semibold text-ink">{overview.name}</h1>
        {isActive && (
          <span className="inline-flex items-center gap-1.5 text-[12px] font-medium text-emerald-600">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            Active
          </span>
        )}
      </div>
      <p className="text-[13px] text-ink-body mt-1">
        Runtime controls for the support agent
      </p>
    </header>
  );
}


// ---------------------------------------------------------------------------
// Stats grid
// ---------------------------------------------------------------------------

function StatsGrid({ overview }: { overview: AgentOverview }) {
  const approvalPct =
    overview.approval_rate != null
      ? `${Math.round(overview.approval_rate * 100)}%`
      : '—';
  const approvalSub =
    overview.approval_rate != null
      ? `${overview.approved_count}/${
          overview.approved_count + overview.rejected_count
        }`
      : undefined;
  const sourceParts = overview.source_label.split('·').map((s) => s.trim());
  const sourceLabel = sourceParts[0] ?? overview.source_label;
  const sourceSub = sourceParts.slice(1).join(' · ') || undefined;

  return (
    <div className="grid grid-cols-3 lg:grid-cols-6 gap-4 pt-4 pb-6 border-b border-line-subtle">
      <Stat label="Source" value={sourceLabel} sub={sourceSub} />
      <Stat
        label="Playbooks"
        value={String(overview.playbooks_loaded)}
        sub="loaded"
      />
      <Stat label="Processed" value={String(overview.processed)} />
      <Stat label="Approval" value={approvalPct} sub={approvalSub} />
      <Stat
        label="Avg conf"
        value={
          overview.avg_confidence != null
            ? overview.avg_confidence.toFixed(2)
            : '—'
        }
      />
      <Stat
        label="Uptime"
        value={overview.uptime_since ? '' : '—'}
        sub={
          overview.uptime_since
            ? `since ${formatDate(overview.uptime_since)}`
            : undefined
        }
      />
    </div>
  );
}


function Stat({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="space-y-1 min-w-0">
      <div className="text-[11px] uppercase tracking-wider text-ink-muted font-medium">
        {label}
      </div>
      {value && (
        <div className="text-[16px] font-semibold font-mono text-ink truncate">
          {value}
        </div>
      )}
      {sub && (
        <div className="text-[11px] text-ink-muted font-mono truncate">
          {sub}
        </div>
      )}
    </div>
  );
}


// ---------------------------------------------------------------------------
// Operating mode
// ---------------------------------------------------------------------------

function ModeSection({
  mode,
  onModeRequest,
}: {
  mode: AgentMode;
  onModeRequest: (m: AgentMode) => void;
}) {
  return (
    <section className="pt-6">
      <h2 className="text-[14px] font-semibold text-ink">Operating mode</h2>
      <p className="text-[13px] text-ink-body mt-1 mb-4">
        Determines what the agent writes back to Jira after each ticket.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {MODES.map((m) => {
          const active = m.key === mode;
          return (
            <button
              key={m.key}
              type="button"
              onClick={() => onModeRequest(m.key)}
              className={`text-left border rounded-lg p-4 transition-all duration-150 ${
                active
                  ? 'border-accent bg-accent-subtle ring-1 ring-accent/20'
                  : 'border-line hover:border-line-strong hover:bg-hover'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[13px] font-semibold text-ink">
                  {m.label}
                </span>
                {active && (
                  <span className="w-2 h-2 rounded-full bg-accent" />
                )}
              </div>
              <p className="text-[12px] text-ink-body leading-relaxed">
                {m.blurb}
              </p>
            </button>
          );
        })}
      </div>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Confidence threshold — custom slider
// ---------------------------------------------------------------------------

function ThresholdSection({
  value,
  saving,
  onChange,
  onCommit,
}: {
  value: number;
  saving: boolean;
  onChange: (v: number) => void;
  onCommit: (v: number) => void;
}) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return (
    <section className="pt-6 pb-6 border-b border-line-subtle">
      <div className="flex items-center justify-between mb-1">
        <h2 className="text-[14px] font-semibold text-ink">
          Minimum confidence threshold
        </h2>
        <span className="text-[14px] font-semibold font-mono text-ink tabular-nums">
          {value.toFixed(2)}
        </span>
      </div>
      <p className="text-[12px] text-ink-body mb-4">
        Below this → escalate to human. In Autonomous mode, only tickets at or
        above this number are auto-sent.
      </p>

      <div className="relative h-4 flex items-center select-none">
        {/* Track */}
        <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-1.5 rounded-full bg-hover" />
        {/* Fill */}
        <div
          className="absolute top-1/2 -translate-y-1/2 h-1.5 rounded-full bg-accent"
          style={{ width: `${pct}%` }}
        />
        {/* Thumb */}
        <div
          className="absolute top-1/2 w-4 h-4 rounded-full bg-card border-2 border-accent shadow-sm pointer-events-none"
          style={{
            left: `${pct}%`,
            transform: 'translate(-50%, -50%)',
          }}
        />
        {/* Native input drives interaction, invisible on top */}
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={value}
          disabled={saving}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          onMouseUp={(e) =>
            onCommit(parseFloat((e.target as HTMLInputElement).value))
          }
          onTouchEnd={(e) =>
            onCommit(parseFloat((e.target as HTMLInputElement).value))
          }
          onKeyUp={(e) =>
            onCommit(parseFloat((e.target as HTMLInputElement).value))
          }
          className="absolute inset-0 w-full h-full appearance-none bg-transparent cursor-grab active:cursor-grabbing opacity-0"
          aria-label="Minimum confidence threshold"
        />
      </div>

      <div className="flex justify-between text-[11px] font-mono text-ink-muted mt-2">
        <span>0.0</span>
        <span>0.5</span>
        <span>1.0</span>
      </div>
    </section>
  );
}


// ---------------------------------------------------------------------------
// Per-playbook overrides
// ---------------------------------------------------------------------------

function OverridesSection({
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
    <section className="pt-6">
      <div className="flex items-center justify-between mb-1 gap-3">
        <h2 className="text-[14px] font-semibold text-ink">
          Per-playbook overrides
        </h2>
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Filter playbooks..."
          className="w-48 h-8 px-3 text-[12px] bg-app border border-line rounded-md text-ink placeholder:text-ink-muted focus:outline-none focus:border-accent"
        />
      </div>
      <p className="text-[12px] text-ink-body mb-4">
        Pin a specific playbook to a different mode. Empty selection follows
        the global mode.
      </p>

      <div className="border border-line rounded-lg overflow-hidden">
        <table className="w-full table-fixed">
          <thead className="bg-app">
            <tr>
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-left">
                Playbook
              </th>
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-left w-48">
                Mode
              </th>
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-center w-20">
                Approve %
              </th>
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-center w-20">
                Avg conf
              </th>
              <th className="px-4 py-2.5 text-[11px] uppercase tracking-wider font-semibold text-ink-muted text-center w-24">
                Processed
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td
                  colSpan={5}
                  className="text-center py-6 text-[13px] text-ink-muted border-t border-line-subtle"
                >
                  No playbooks match.
                </td>
              </tr>
            )}
            {rows.map((r) => (
              <tr
                key={r.playbook_id}
                className="border-t border-line-subtle hover:bg-hover transition-colors duration-150"
              >
                <td className="px-4 py-3 align-top min-w-0">
                  <Link
                    to={`/knowledge/${r.playbook_id}`}
                    className="text-[13px] font-medium text-ink hover:text-accent-fg leading-snug block truncate"
                  >
                    {r.title}
                  </Link>
                  <div className="text-[11px] font-mono text-ink-muted mt-0.5 truncate">
                    {r.playbook_id}
                  </div>
                </td>
                <td className="px-4 py-3 align-top">
                  <ModeSelect
                    row={r}
                    onChange={(mode) => onChangeMode(r.playbook_id, mode)}
                  />
                </td>
                <td className="px-4 py-3 align-top text-center">
                  {r.approve_rate != null ? (
                    <span className="text-[12px] font-mono text-ink-body">
                      {Math.round(r.approve_rate * 100)}%
                    </span>
                  ) : (
                    <span className="text-[12px] text-ink-muted">—</span>
                  )}
                </td>
                <td className="px-4 py-3 align-top text-center">
                  {r.avg_confidence != null ? (
                    <span className="text-[12px] font-mono text-ink-body">
                      {r.avg_confidence.toFixed(2)}
                    </span>
                  ) : (
                    <span className="text-[12px] text-ink-muted">—</span>
                  )}
                </td>
                <td className="px-4 py-3 align-top text-center">
                  {r.sample_count > 0 ? (
                    <span className="text-[12px] font-mono text-ink-body">
                      {r.sample_count}
                    </span>
                  ) : (
                    <span className="text-[12px] text-ink-muted">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="text-[11px] text-ink-muted px-4 py-2.5 border-t border-line-subtle bg-app">
          Showing {rows.length} of {totalCount} playbooks
        </div>
      </div>
    </section>
  );
}


function ModeSelect({
  row,
  onChange,
}: {
  row: PlaybookModeRow;
  onChange: (mode: AgentMode | null) => void;
}) {
  return (
    <div className="relative inline-block w-full max-w-[180px]">
      <select
        value={row.is_override ? row.mode : ''}
        onChange={(e) =>
          onChange(e.target.value === '' ? null : (e.target.value as AgentMode))
        }
        className="w-full h-8 pl-2.5 pr-7 text-[12px] bg-card border border-line rounded-md text-ink focus:outline-none focus:border-accent cursor-pointer appearance-none"
      >
        <option value="">Follow global ({row.mode})</option>
        <option value="shadow">Shadow</option>
        <option value="assisted">Assisted</option>
        <option value="autonomous">Autonomous</option>
      </select>
      <ChevronDown
        width={14}
        height={14}
        strokeWidth={1.75}
        className="absolute right-2 top-1/2 -translate-y-1/2 text-ink-muted pointer-events-none"
      />
    </div>
  );
}


// ---------------------------------------------------------------------------
// Jira connection
// ---------------------------------------------------------------------------

function JiraSection({
  status,
  testing,
  onTest,
}: {
  status: JiraConnectionStatus;
  testing: boolean;
  onTest: () => void;
}) {
  return (
    <section className="pt-6 mt-2">
      <div className="border border-line rounded-lg p-5">
        <div className="flex items-center justify-between mb-1 gap-3">
          <h2 className="text-[14px] font-semibold text-ink">Jira connection</h2>
          <button
            type="button"
            onClick={onTest}
            disabled={testing || !status.configured}
            className="bg-transparent border border-line text-ink hover:bg-hover rounded-md px-3 h-8 text-[12px] font-medium transition-colors duration-150 disabled:opacity-60"
          >
            {testing ? 'Testing…' : 'Test connection'}
          </button>
        </div>
        <p className="text-[12px] text-ink-body mb-4">
          Credentials are read from the backend <code>.env</code> at boot. Edit
          there to change the wired account.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <JiraField label="URL" value={status.url ?? '—'} />
          <JiraField label="Project" value={status.project ?? '—'} />
          <JiraField label="Email" value={status.email ?? '—'} />
          <JiraField label="API token" value={status.token_masked ?? '—'} />
        </div>
        {status.detail && (
          <p className="mt-4 text-[12px] font-mono text-ink-body">
            {status.detail}
          </p>
        )}
      </div>
    </section>
  );
}


function JiraField({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <div className="text-[11px] uppercase tracking-wider text-ink-muted font-medium mb-1">
        {label}
      </div>
      <div className="text-[13px] font-mono text-ink truncate">{value}</div>
    </div>
  );
}


// ---------------------------------------------------------------------------
// Mode switch confirmation modal
// ---------------------------------------------------------------------------

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
      <div className="bg-card rounded-lg shadow-md border border-line max-w-md w-full mx-4 p-6">
        <h2 className="text-base font-semibold text-ink">Confirm mode switch</h2>
        <p className="mt-2 text-[13px] text-ink-body leading-relaxed">
          {message}
        </p>
        <div className="mt-4 text-[11px] text-ink-muted font-mono">
          {from} → <strong className="text-ink">{to}</strong>
        </div>
        <div className="mt-5 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="text-[12px] text-ink-body hover:text-ink px-3 h-8 transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="bg-accent text-white hover:bg-accent-hover rounded-md px-4 h-8 text-[12px] font-medium transition-colors duration-150"
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
