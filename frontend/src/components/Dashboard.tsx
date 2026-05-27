import { useMemo } from 'react';
import type { Ticket } from '../types';
import { Pill } from './Pills';
import { IconAlert, IconCheck, IconClock, IconInbox } from './Icons';

interface Props {
  tickets: Ticket[];
  loading: boolean;
  onOpen: (id: number) => void;
  onCreate: () => void;
}

export function Dashboard({ tickets, loading, onOpen, onCreate }: Props) {
  const stats = useMemo(() => {
    const total = tickets.length;
    const open = tickets.filter(
      (t) => !['resolved', 'closed'].includes(t.status),
    ).length;
    const resolved = tickets.filter((t) => t.status === 'resolved').length;
    const critical = tickets.filter((t) => t.priority === 'critical').length;
    return { total, open, resolved, critical };
  }, [tickets]);

  const recent = useMemo(() => tickets.slice(0, 6), [tickets]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="title-xl">
            <span className="gradient-text">Good to see you.</span>
          </h1>
          <p className="subtitle">
            Here is a snapshot of what your support inbox looks like today.
          </p>
        </div>
        <button className="btn btn-primary" onClick={onCreate}>
          + New ticket
        </button>
      </div>

      <div className="stat-grid">
        <div className="stat" style={{ ['--accent' as never]: 'radial-gradient(closest-side, rgba(124,92,255,0.5), transparent)' }}>
          <div className="label">
            <IconInbox width={14} height={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Total tickets
          </div>
          <div className="value">{loading ? '—' : stats.total}</div>
          <div className="delta">All time</div>
        </div>
        <div className="stat" style={{ ['--accent' as never]: 'radial-gradient(closest-side, rgba(245,158,11,0.45), transparent)' }}>
          <div className="label">
            <IconClock width={14} height={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Open
          </div>
          <div className="value">{loading ? '—' : stats.open}</div>
          <div className="delta">Awaiting action</div>
        </div>
        <div className="stat" style={{ ['--accent' as never]: 'radial-gradient(closest-side, rgba(46,204,113,0.45), transparent)' }}>
          <div className="label">
            <IconCheck width={14} height={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Resolved
          </div>
          <div className="value">{loading ? '—' : stats.resolved}</div>
          <div className="delta">Closed by AI or team</div>
        </div>
        <div className="stat" style={{ ['--accent' as never]: 'radial-gradient(closest-side, rgba(239,68,68,0.5), transparent)' }}>
          <div className="label">
            <IconAlert width={14} height={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
            Critical
          </div>
          <div className="value">{loading ? '—' : stats.critical}</div>
          <div className="delta">Needs immediate care</div>
        </div>
      </div>

      <div className="page-header" style={{ marginBottom: 14 }}>
        <h2 className="title">Recently created</h2>
      </div>

      {loading ? (
        <div className="ticket-grid">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="ticket-card" style={{ cursor: 'default' }}>
              <div className="skeleton" style={{ height: 14, width: '40%' }} />
              <div className="skeleton" style={{ height: 18, width: '80%' }} />
              <div className="skeleton" style={{ height: 14, width: '95%' }} />
              <div className="skeleton" style={{ height: 14, width: '70%' }} />
            </div>
          ))}
        </div>
      ) : recent.length === 0 ? (
        <div className="empty-state">
          <div className="ico">
            <IconInbox width={24} height={24} />
          </div>
          <p>No tickets yet.</p>
          <button
            className="btn btn-ghost"
            style={{ marginTop: 14 }}
            onClick={onCreate}
          >
            Submit your first ticket
          </button>
        </div>
      ) : (
        <div className="ticket-grid">
          {recent.map((t) => (
            <TicketTile key={t.id} ticket={t} onOpen={onOpen} />
          ))}
        </div>
      )}
    </div>
  );
}

function TicketTile({
  ticket,
  onOpen,
}: {
  ticket: Ticket;
  onOpen: (id: number) => void;
}) {
  return (
    <article className="ticket-card" onClick={() => onOpen(ticket.id)}>
      <div className="row-top">
        <span className="id">#{ticket.id}</span>
        <Pill value={ticket.status} kind="status" />
      </div>
      <h3>{ticket.title}</h3>
      <p className="desc">{ticket.description}</p>
      <div className="meta">
        {ticket.priority && <Pill value={ticket.priority} kind="priority" />}
        {ticket.category && <Pill value={ticket.category} kind="tag" />}
        {ticket.assigned_team && (
          <Pill value={ticket.assigned_team} kind="tag" />
        )}
      </div>
      <div className="footer">
        <span>{new Date(ticket.created_at).toLocaleDateString()}</span>
        <span>Open →</span>
      </div>
    </article>
  );
}
