import { Suspense, lazy, useState } from 'react';
import { useAuth } from './context/AuthContext';
import { LoginPage } from './components/LoginPage';
import { Sidebar, type Section } from './components/Sidebar';
import { PageSkeleton } from './components/PageSkeleton';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useTickets } from './hooks/useTickets';

const Dashboard = lazy(() =>
  import('./components/Dashboard').then((m) => ({ default: m.Dashboard })),
);
const TicketList = lazy(() =>
  import('./components/TicketList').then((m) => ({ default: m.TicketList })),
);
const TicketCreate = lazy(() =>
  import('./components/TicketCreate').then((m) => ({ default: m.TicketCreate })),
);
const TicketDetail = lazy(() =>
  import('./components/TicketDetail').then((m) => ({ default: m.TicketDetail })),
);

type View =
  | { kind: 'section'; section: Section }
  | { kind: 'detail'; id: number };

export default function App() {
  const { isAuthenticated } = useAuth();
  const [view, setView] = useState<View>({ kind: 'section', section: 'dashboard' });
  const { tickets, loading, error, refresh } = useTickets(isAuthenticated);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  const section = view.kind === 'section' ? view.section : 'tickets';

  return (
    <div className="shell">
      <Sidebar
        section={section}
        onSelect={(s) => setView({ kind: 'section', section: s })}
      />

      <main className="main">
        <ErrorBoundary>
          <Suspense fallback={<PageSkeleton />}>
            {view.kind === 'detail' ? (
              <TicketDetail
                id={view.id}
                onBack={() => {
                  setView({ kind: 'section', section: 'tickets' });
                  refresh();
                }}
              />
            ) : section === 'dashboard' ? (
              <Dashboard
                tickets={tickets}
                loading={loading}
                onOpen={(id) => setView({ kind: 'detail', id })}
                onCreate={() => setView({ kind: 'section', section: 'new' })}
              />
            ) : section === 'tickets' ? (
              <TicketList
                tickets={tickets}
                loading={loading}
                error={error}
                onOpen={(id) => setView({ kind: 'detail', id })}
                onRefresh={refresh}
              />
            ) : (
              <TicketCreate
                onCreated={(ticket) => {
                  refresh();
                  setView({ kind: 'detail', id: ticket.id });
                }}
              />
            )}
          </Suspense>
        </ErrorBoundary>
      </main>
    </div>
  );
}
