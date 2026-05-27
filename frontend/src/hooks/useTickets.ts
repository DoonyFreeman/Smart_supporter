import { useCallback, useEffect, useState } from 'react';
import { getTickets } from '../api/tickets';
import type { Ticket } from '../types';

interface UseTicketsResult {
  tickets: Ticket[];
  loading: boolean;
  error: string;
  refresh: () => Promise<void>;
}

export function useTickets(enabled: boolean): UseTicketsResult {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const list = await getTickets();
      list.sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      );
      setTickets(list);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load tickets');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (enabled) {
      refresh();
    }
  }, [enabled, refresh]);

  return { tickets, loading, error, refresh };
}
