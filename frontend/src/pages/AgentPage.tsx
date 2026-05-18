/** Agent tab — pick a ticket, run classify → retrieve → draft, approve/edit/reject. */
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { AgentWorkflow } from '../components/AgentWorkflow';
import { TicketList } from '../components/TicketList';
import { getTicket, listAgentSessions, listTickets } from '../lib/api';
import type {
  AgentSessionSummary,
  TicketDetail,
  TicketSummary,
} from '../lib/types';


export function AgentPage() {
  const { ticketKey } = useParams();
  const navigate = useNavigate();

  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(true);
  const [ticketsError, setTicketsError] = useState<string | null>(null);

  const [activeTicket, setActiveTicket] = useState<TicketDetail | null>(null);
  const [activeLoading, setActiveLoading] = useState(false);
  const [activeError, setActiveError] = useState<string | null>(null);

  // Per-ticket workflow state — fetched in one shot and refreshed whenever
  // an AgentWorkflow step finishes (custom 'agent-sessions-changed' event).
  const [sessions, setSessions] = useState<AgentSessionSummary[]>([]);

  const refreshSessions = useCallback(() => {
    listAgentSessions()
      .then(setSessions)
      .catch(() => setSessions([]));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setTicketsLoading(true);
    listTickets()
      .then((data) => {
        if (cancelled) return;
        setTickets(data);
        if (!ticketKey && data.length > 0) {
          navigate(`/agent/${data[0].key}`, { replace: true });
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setTicketsError(err.message);
      })
      .finally(() => {
        if (!cancelled) setTicketsLoading(false);
      });
    refreshSessions();
    const handler = () => refreshSessions();
    window.addEventListener('agent-sessions-changed', handler);
    return () => {
      cancelled = true;
      window.removeEventListener('agent-sessions-changed', handler);
    };
    // ticketKey/navigate intentionally excluded — we only redirect once on load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!ticketKey) {
      setActiveTicket(null);
      return;
    }
    let cancelled = false;
    setActiveLoading(true);
    setActiveError(null);
    getTicket(ticketKey)
      .then((data) => {
        if (!cancelled) setActiveTicket(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setActiveError(err.message);
      })
      .finally(() => {
        if (!cancelled) setActiveLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [ticketKey]);

  const sessionByTicketId = useMemo(() => {
    const m = new Map<string, AgentSessionSummary>();
    for (const s of sessions) m.set(s.ticket_id, s);
    return m;
  }, [sessions]);

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-panel-border bg-panel-surface">
        <h1 className="text-lg font-semibold tracking-tight text-slate-900">Agent Feed</h1>
      </header>
      <div className="flex-1 flex overflow-hidden">
        <TicketList
          tickets={tickets}
          loading={ticketsLoading}
          error={ticketsError}
          sessionByTicketId={sessionByTicketId}
        />
        {activeError ? (
          <div className="flex-1 flex items-center justify-center text-sm text-red-600">
            {activeError}
          </div>
        ) : activeLoading || !activeTicket ? (
          <div className="flex-1 flex items-center justify-center text-sm text-slate-400">
            {ticketKey ? 'Loading ticket…' : 'Pick a ticket from the list.'}
          </div>
        ) : (
          <AgentWorkflow ticket={activeTicket} tickets={tickets} />
        )}
      </div>
    </div>
  );
}
