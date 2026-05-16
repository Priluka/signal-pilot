/** Agent tab — pick a ticket, run classify → retrieve → draft, approve/edit/reject. */
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { AgentWorkflow } from '../components/AgentWorkflow';
import { TicketList } from '../components/TicketList';
import { getTicket, listTickets } from '../lib/api';
import type { TicketDetail, TicketSummary } from '../lib/types';


export function AgentPage() {
  const { ticketKey } = useParams();
  const navigate = useNavigate();

  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [ticketsLoading, setTicketsLoading] = useState(true);
  const [ticketsError, setTicketsError] = useState<string | null>(null);

  const [activeTicket, setActiveTicket] = useState<TicketDetail | null>(null);
  const [activeLoading, setActiveLoading] = useState(false);
  const [activeError, setActiveError] = useState<string | null>(null);

  // Load the ticket sample once.
  useEffect(() => {
    let cancelled = false;
    setTicketsLoading(true);
    listTickets()
      .then((data) => {
        if (cancelled) return;
        setTickets(data);
        // If the URL has no ticketKey yet, redirect to the first one so the
        // workflow has something to show.
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
    return () => {
      cancelled = true;
    };
    // ticketKey/navigate intentionally excluded — we only redirect once on load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Load the active ticket detail when the URL changes.
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

  return (
    <div className="h-full flex flex-col">
      <header className="px-6 py-4 border-b border-panel-border bg-panel-surface">
        <h1 className="text-lg font-semibold tracking-tight text-slate-900">Agent Feed</h1>
      </header>
      <div className="flex-1 flex overflow-hidden">
        <TicketList tickets={tickets} loading={ticketsLoading} error={ticketsError} />
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
