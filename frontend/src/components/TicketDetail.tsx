import { useEffect, useState } from 'react';
import { getTicket } from '../api/tickets';
import type { Ticket } from '../types';

export function TicketDetail({ id, onBack }: { id: number; onBack: () => void }) {
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getTicket(id)
      .then(setTicket)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!ticket) return <div className="error">Ticket not found</div>;

  return (
    <div className="ticket-detail">
      <button className="link back" onClick={onBack}>← Back to tickets</button>

      <h2>{ticket.title}</h2>

      <div className="meta">
        <span className="badge">{ticket.status}</span>
        {ticket.priority && <span className="badge">{ticket.priority}</span>}
        {ticket.category && <span className="badge">{ticket.category}</span>}
        {ticket.assigned_team && <span className="badge">{ticket.assigned_team}</span>}
      </div>

      <div className="field">
        <label>Description</label>
        <p>{ticket.description}</p>
      </div>

      {ticket.response_text && (
        <div className="field">
          <label>AI Response</label>
          <p>{ticket.response_text}</p>
        </div>
      )}

      <div className="field">
        <label>Created</label>
        <p>{new Date(ticket.created_at).toLocaleString()}</p>
      </div>
    </div>
  );
}
