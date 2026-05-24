import { useState } from 'react';
import { useAuth } from './context/AuthContext';
import { LoginPage } from './components/LoginPage';
import { TicketList } from './components/TicketList';
import { TicketCreate } from './components/TicketCreate';
import { TicketDetail } from './components/TicketDetail';

type View = { page: 'list' } | { page: 'detail'; id: number };

export default function App() {
  const { isAuthenticated, logout } = useAuth();
  const [view, setView] = useState<View>({ page: 'list' });
  const [refreshKey, setRefreshKey] = useState(0);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <div className="app">
      <header>
        <h1>Support Triager</h1>
        <nav>
          <button className="link" onClick={() => { setView({ page: 'list' }); setRefreshKey(k => k + 1); }}>
            Tickets
          </button>
          <button className="link" onClick={() => setView({ page: 'list' })}>
            New Ticket
          </button>
          <button className="link" onClick={logout}>Log out</button>
        </nav>
      </header>

      <main>
        {view.page === 'list' && (
          <>
            <TicketCreate onCreated={() => setRefreshKey(k => k + 1)} />
            <TicketList key={refreshKey} onSelect={(id) => setView({ page: 'detail', id })} />
          </>
        )}
        {view.page === 'detail' && (
          <TicketDetail id={view.id} onBack={() => setView({ page: 'list' })} />
        )}
      </main>
    </div>
  );
}
