import { NavLink, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  LayoutDashboard, Zap, Columns3, Archive, Bug,
  Briefcase, FolderKanban, Cog, Palette, Settings,
  FolderOpen, Sun, Moon, CalendarDays, Users, Package
} from 'lucide-react';

const ICON_SIZE = 16;
const NAV = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/tasks', label: 'Tasks', icon: Zap },
  { to: '/archive', label: 'Archive', icon: Archive },
  { divider: true },
  { to: '/meetings', label: 'Meeting Notes', icon: CalendarDays },
  { to: '/people', label: 'People', icon: Users },
  { to: '/products-hub', label: 'Products', icon: Package },
  { divider: true },
  { to: '/settings', label: 'Settings', icon: Settings },
  { to: '/files', label: 'Files', icon: FolderOpen },
];

export default function Sidebar({ open, onClose }) {
  const [dark, setDark] = useState(() => localStorage.getItem('theme') === 'dark');
  const location = useLocation();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
    localStorage.setItem('theme', dark ? 'dark' : 'light');
  }, [dark]);

  useEffect(() => { if (onClose) onClose(); }, [location.pathname]);

  return (
    <aside className={`sidebar ${open ? 'sidebar-open' : ''}`}>
      <div className="sidebar-brand">
        <span className="sidebar-logo">B</span>
        <div>
          <div className="sidebar-title">BeatsPM Kit</div>
          <div className="sidebar-subtitle">Command Center</div>
        </div>
      </div>
      <nav className="sidebar-nav">
        {NAV.map((item, i) =>
          item.divider ? (
            <div className="sidebar-divider" key={`d-${i}`} />
          ) : (
            <NavLink key={item.to} to={item.to} end={item.to === '/'} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <item.icon size={ICON_SIZE} strokeWidth={1.8} className="sidebar-icon-svg" />
              <span>{item.label}</span>
            </NavLink>
          )
        )}
        <div className="sidebar-divider" />
        <button className="theme-toggle" onClick={() => setDark(!dark)} aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}>
          {dark ? <Sun size={ICON_SIZE} strokeWidth={1.8} /> : <Moon size={ICON_SIZE} strokeWidth={1.8} />}
          <span>{dark ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
      </nav>
      <div className="sidebar-footer">
        <span className="pulse-dot" />
        <span>Live · 2s sync</span>
      </div>
    </aside>
  );
}
