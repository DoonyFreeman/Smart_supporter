import { useMemo, useState } from 'react';
import type { Ticket } from '../types';
import { Pill } from './Pills';
import { IconInbox, IconSearch, IconRefresh } from './Icons';

interface Props {
  tickets: Ticket[];
  loading: boolean;
  error: string;
  onOpen: (id: number) => void;
  onRefresh: () => void;
}

type StatusFilter = 'all' | 'open' | 'resolved' | 'triaged' | 'needs_info';

export function TicketList({
  tickets,
  loading,
  error,
  onOpen,
  onRefresh,
}: Props) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<StatusFilter>('all');

  const filtered = useMemo(() => {
    let list = tickets;
    if (filter === 'open') {
      list = list.filter((t) => !['resolved', 'closed'].includes(t.status));
    } else if (filter !== 'all') {
      list = list.filter((t) => t.status === filter);
    }
    if (query.trim()) {
      const q = query.toLowerCase();
      list = list.filter(
        (t) =>
          t.title.toLowerCase().includes(q) ||
          t.description.toLowerCase().includes(q) ||
          String(t.id).includes(q),
      );
    }
    return list;
  }, [tickets, filter, query]);

  const filters: { key: StatusFilter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'open', label: 'Open' },
    { key: 'triaged', label: 'Triaged' },
    { key: 'resolved', label: 'Resolved' },
    { key: 'needs_info', label: 'Needs info' },
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="title-xl">Tickets</h1>
          <p className="subtitle">
            {loading
              ? 'Loading…'
              : `${filtered.length} of ${tickets.length} ${tickets.length === 1 ? 'ticket' : 'tickets'}`}
          </p>
        </div>
        <button className="btn btn-ghost" onClick={onRefresh}>
          <IconRefresh width={16} height={16} /> Refresh
        </button>
      </div>

      <div className="toolbar">
        <div className="search">
          <IconSearch />
          <input
            placeholder="Search by title, description or #id…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="chip-group">
          {filters.map((f) => (
            <button
              key={f.key}
              className={`chip ${filter === f.key ? 'active' : ''}`}
              onClick={() => setFilter(f.key)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-banner" style={{ marginBottom: 14 }}>{error}</div>}

      {loading ? (
        <div className="ticket-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="ticket-card" style={{ cursor: 'default' }}>
              <div className="skeleton" style={{ height: 14, width: '35%' }} />
              <div className="skeleton" style={{ height: 18, width: '85%' }} />
              <div className="skeleton" style={{ height: 14, width: '95%' }} />
              <div className="skeleton" style={{ height: 14, width: '60%' }} />
            </div>
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="ico">
            <IconInbox width={24} height={24} />
          </div>
          <p>No tickets match the current filters.</p>
        </div>
      ) : (
        <div className="ticket-grid">
          {filtered.map((t) => (
            <article
              key={t.id}
              className="ticket-card"
              onClick={() => onOpen(t.id)}
            >
              <div className="row-top">
                <span className="id">#{t.id}</span>
                <Pill value={t.status} kind="status" />
              </div>
              <h3>{t.title}</h3>
              <p className="desc">{t.description}</p>
              <div className="meta">
                {t.priority && <Pill value={t.priority} kind="priority" />}
                {t.category && <Pill value={t.category} kind="tag" />}
                {t.assigned_team && <Pill value={t.assigned_team} kind="tag" />}
              </div>
              <div className="footer">
                <span>{new Date(t.created_at).toLocaleString()}</span>
                <span>Open →</span>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
