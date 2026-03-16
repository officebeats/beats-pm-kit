'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';

const NAV = [
  { href: '/', label: 'Overview', icon: '◎' },
  { href: '/tasks', label: 'Tasks', icon: '⚡' },
  { href: '/bugs', label: 'Bugs', icon: '🐛' },
  { href: '/boss', label: 'Boss Asks', icon: '👔' },
  { href: '/projects', label: 'Projects', icon: '📦' },
  { href: '/eng', label: 'Engineering', icon: '⚙️' },
  { href: '/ux', label: 'UX', icon: '🎨' },
  { href: '/settings', label: 'Settings', icon: '⚙' },
  { href: '/files', label: 'Files', icon: '📁' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <span className="sidebar-logo-icon">⚛</span>
        <span className="sidebar-logo-text">Antigravity</span>
      </div>
      <ul className="sidebar-nav">
        {NAV.map(item => (
          <li key={item.href}>
            <Link
              href={item.href}
              className={`sidebar-link ${pathname === item.href ? 'active' : ''}`}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          </li>
        ))}
      </ul>
      <div className="sidebar-footer">
        PM Command Center
      </div>
    </nav>
  );
}
