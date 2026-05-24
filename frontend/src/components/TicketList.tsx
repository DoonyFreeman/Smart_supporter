import { useEffect, useState } from 'react';
import { getTickets } from '../api/tickets';
import type { Ticket } from '../types';

const PRIORITY_COLORS: Record<string, string> = {
  critical: '#dc3545',
  high: '#fd7e14',
  medium: '#ffc107',
  low: '#28a745',
};

export function TicketList({ onSelect }: { onSelect: (id: number) => void }) {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getTickets()
      .then(setTickets)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">Loading tickets...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="ticket-list">
      <h2>Tickets ({tickets.length})</h2>
      {tickets.length === 0 ? (
        <p className="empty">No tickets yet</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Category</th>
              <th>Team</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.id} onClick={() => onSelect(t.id)} className="clickable">
                <td>{t.id}</td>
                <td>{t.title}</td>
                <td><span className="badge">{t.status}</span></td>
                <td>
                  {t.priority && (
                    <span className="badge" style={{ backgroundColor: PRIORITY_COLORS[t.priority] || '#6c757d' }}>
                      {t.priority}
                    </span>
                  )}
                </td>
                <td>{t.category || '-'}</td>
                <td>{t.assigned_team || '-'}</td>
                <td>{new Date(t.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
