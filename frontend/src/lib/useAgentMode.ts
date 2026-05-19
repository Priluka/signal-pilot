/** Small hook for components that need to react to the operator's current
 * agent mode (Shadow / Assisted / Autonomous).
 *
 * Mode lives in SQLite via /agent/config — this hook fetches it on mount
 * and re-fetches whenever ``agent-config-changed`` fires on the window
 * event bus. The Agents page dispatches that event after a successful
 * PUT /agent/config, so the rest of the UI stays in sync without polling.
 *
 * Components consume this for two reasons:
 *   * Inbox renders a small mode badge so the operator always knows what
 *     pressing Approve will do.
 *   * AgentTicketDetail gates the Jira-side comment post on mode !== shadow,
 *     and adjusts the Approve button copy ('Approve' vs 'Approve & send').
 */
import { useEffect, useState } from 'react';

import { getAgentConfig } from './api';
import type { AgentMode } from './types';


export function useAgentMode(): AgentMode | null {
  const [mode, setMode] = useState<AgentMode | null>(null);

  useEffect(() => {
    let cancelled = false;
    function load() {
      getAgentConfig()
        .then((c) => {
          if (!cancelled) setMode(c.mode);
        })
        .catch(() => {
          // Surface absence rather than a stale value — the hook returning
          // null lets callers fall back to safe-by-default behaviour
          // (Shadow: no outbound writes).
          if (!cancelled) setMode(null);
        });
    }
    load();
    const handler = () => load();
    window.addEventListener('agent-config-changed', handler);
    return () => {
      cancelled = true;
      window.removeEventListener('agent-config-changed', handler);
    };
  }, []);

  return mode;
}
