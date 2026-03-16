import { useState, useEffect } from 'react';

export default function Header({ version, lastUpdate }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const fmt = time.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });

  const dateFmt = time.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  return (
    <header className="header">
      <div className="header-left">
        <div className="logo">⚛</div>
        <div>
          <h1>Antigravity Brain</h1>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
            Live Dashboard — PM Command Center
          </div>
        </div>
      </div>
      <div className="header-meta">
        <span className="pulse-dot" />
        {version && <span className="version-badge">v{version}</span>}
        <span className="clock">{dateFmt} · {fmt}</span>
      </div>
    </header>
  );
}
