import { useAuth } from '../context/AuthContext';
import { IconChart, IconInbox, IconLogout, IconPlus, IconSpark } from './Icons';

export type Section = 'dashboard' | 'tickets' | 'new';

interface Props {
  section: Section;
  onSelect: (s: Section) => void;
}

export function Sidebar({ section, onSelect }: Props) {
  const { logout, user } = useAuth();
  const initials = (user?.email || 'U').slice(0, 1).toUpperCase();

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="logo">
          <IconSpark width={20} height={20} />
        </div>
        <div className="name">
          Triage
          <small>AI support workspace</small>
        </div>
      </div>

      <nav className="nav">
        <button
          className={section === 'dashboard' ? 'active' : ''}
          onClick={() => onSelect('dashboard')}
        >
          <IconChart /> Dashboard
        </button>
        <button
          className={section === 'tickets' ? 'active' : ''}
          onClick={() => onSelect('tickets')}
        >
          <IconInbox /> All tickets
        </button>
        <button
          className={section === 'new' ? 'active' : ''}
          onClick={() => onSelect('new')}
        >
          <IconPlus /> New ticket
        </button>
      </nav>

      <div className="sidebar-footer">
        <div className="avatar">{initials}</div>
        <div className="who">
          <strong>{user?.full_name || user?.email || 'You'}</strong>
          <span>{user?.role || 'member'}</span>
        </div>
        <button className="btn btn-ghost btn-icon" title="Log out" onClick={logout}>
          <IconLogout width={16} height={16} />
        </button>
      </div>
    </aside>
  );
}
