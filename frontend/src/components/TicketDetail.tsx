import { useEffect, useRef, useState } from 'react';
import { getTicket } from '../api/tickets';
import type { Ticket } from '../types';
import { Pill } from './Pills';
import { IconArrowLeft, IconSpark, IconClock, IconUser } from './Icons';

interface Props {
  id: number;
  onBack: () => void;
}

const TERMINAL_STATUSES = new Set(['resolved', 'triaged', 'needs_info', 'closed']);

export function TicketDetail({ id, onBack }: Props) {
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load(initial = false) {
      try {
        const t = await getTicket(id);
        if (cancelled) return;
        setTicket(t);
        if (initial) setLoading(false);

        // Stop polling once the agent has settled OR a response is present.
        if (TERMINAL_STATUSES.has(t.status) && t.response_text) {
          if (pollRef.current) {
            clearInterval(pollRef.current);
            pollRef.current = null;
          }
        }
      } catch (e) {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : 'Failed to load ticket');
        if (initial) setLoading(false);
      }
    }

    load(true);
    pollRef.current = setInterval(() => load(false), 2500);

    return () => {
      cancelled = true;
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [id]);

  if (loading) {
    return (
      <div>
        <button className="btn btn-ghost" onClick={onBack} style={{ marginBottom: 18 }}>
          <IconArrowLeft width={16} height={16} /> Back
        </button>
        <div className="detail">
          <div className="detail-main">
            <div className="detail-head">
              <div className="skeleton" style={{ height: 18, width: '30%' }} />
              <div className="skeleton" style={{ height: 28, width: '70%' }} />
              <div className="skeleton" style={{ height: 14, width: '50%' }} />
            </div>
            <div className="block">
              <div className="skeleton" style={{ height: 12, width: '40%', marginBottom: 14 }} />
              <div className="skeleton" style={{ height: 14, marginBottom: 10 }} />
              <div className="skeleton" style={{ height: 14, marginBottom: 10 }} />
              <div className="skeleton" style={{ height: 14, width: '70%' }} />
            </div>
          </div>
          <div className="detail-aside">
            <div className="block">
              <div className="skeleton" style={{ height: 14, marginBottom: 12 }} />
              <div className="skeleton" style={{ height: 14, marginBottom: 12 }} />
              <div className="skeleton" style={{ height: 14, width: '70%' }} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div>
        <button className="btn btn-ghost" onClick={onBack} style={{ marginBottom: 18 }}>
          <IconArrowLeft width={16} height={16} /> Back
        </button>
        <div className="error-banner">{error || 'Ticket not found'}</div>
      </div>
    );
  }

  const isProcessing = !ticket.response_text && !TERMINAL_STATUSES.has(ticket.status);

  return (
    <div>
      <button className="btn btn-ghost" onClick={onBack} style={{ marginBottom: 18 }}>
        <IconArrowLeft width={16} height={16} /> Back to tickets
      </button>

      <div className="detail">
        <div className="detail-main">
          <div className="detail-head">
            <div className="top">
              <span className="mono" style={{ color: 'var(--text-faint)' }}>
                Ticket #{ticket.id}
              </span>
              {isProcessing && (
                <span className="pulse">
                  <span className="dot" /> AI is analysing…
                </span>
              )}
            </div>
            <h1>{ticket.title}</h1>
            <div className="meta">
              <Pill value={ticket.status} kind="status" />
              {ticket.priority && <Pill value={ticket.priority} kind="priority" />}
              {ticket.category && <Pill value={ticket.category} kind="tag" />}
              {ticket.assigned_team && (
                <Pill value={ticket.assigned_team} kind="tag" />
              )}
            </div>
          </div>

          <div className="block">
            <h3>Description</h3>
            <p>{ticket.description}</p>
          </div>

          {ticket.response_text ? (
            <div className="ai-response">
              <div className="ai-head">
                <span className="ai-badge">
                  <IconSpark width={12} height={12} /> AI Agent
                </span>
                <span className="ai-title">Suggested response</span>
              </div>
              <p>{ticket.response_text}</p>
            </div>
          ) : (
            <div className="ai-response">
              <div className="ai-head">
                <span className="ai-badge">
                  <IconSpark width={12} height={12} /> AI Agent
                </span>
                <span className="ai-title">Working on a response…</span>
              </div>
              <div className="skeleton" style={{ height: 14, marginBottom: 8 }} />
              <div className="skeleton" style={{ height: 14, marginBottom: 8 }} />
              <div className="skeleton" style={{ height: 14, width: '70%' }} />
            </div>
          )}
        </div>

        <div className="detail-aside">
          <div className="block">
            <h3>Activity</h3>
            <div className="aside-row">
              <span className="k">
                <IconClock width={12} height={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                Created
              </span>
              <span className="v">{new Date(ticket.created_at).toLocaleString()}</span>
            </div>
            <div className="aside-row">
              <span className="k">Updated</span>
              <span className="v">{new Date(ticket.updated_at).toLocaleString()}</span>
            </div>
            {ticket.resolved_at && (
              <div className="aside-row">
                <span className="k">Resolved</span>
                <span className="v">{new Date(ticket.resolved_at).toLocaleString()}</span>
              </div>
            )}
            <div className="aside-row">
              <span className="k">
                <IconUser width={12} height={12} style={{ marginRight: 4, verticalAlign: 'middle' }} />
                Created by
              </span>
              <span className="v mono">#{ticket.created_by}</span>
            </div>
          </div>

          <div className="block">
            <h3>Routing</h3>
            <div className="aside-row">
              <span className="k">Status</span>
              <Pill value={ticket.status} kind="status" />
            </div>
            <div className="aside-row">
              <span className="k">Priority</span>
              <span className="v">
                {ticket.priority ? <Pill value={ticket.priority} kind="priority" /> : '—'}
              </span>
            </div>
            <div className="aside-row">
              <span className="k">Category</span>
              <span className="v">{ticket.category || '—'}</span>
            </div>
            <div className="aside-row">
              <span className="k">Team</span>
              <span className="v">{ticket.assigned_team || '—'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
