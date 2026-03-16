'use client';

export function PriorityBadge({ priority }) {
  if (priority === null || priority === undefined) return null;
  const colors = {
    0: { bg: 'rgba(239,68,68,0.15)', color: '#ef4444', border: 'rgba(239,68,68,0.25)' },
    1: { bg: 'rgba(245,158,11,0.12)', color: '#f59e0b', border: 'rgba(245,158,11,0.2)' },
    2: { bg: 'rgba(77,142,255,0.1)', color: '#4d8eff', border: 'rgba(77,142,255,0.2)' },
    3: { bg: 'rgba(139,139,158,0.1)', color: '#8b8b9e', border: 'rgba(139,139,158,0.15)' },
  };
  const c = colors[priority] || colors[3];
  return (
    <span style={{
      fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4,
      background: c.bg, color: c.color, border: `1px solid ${c.border}`,
      letterSpacing: '0.02em',
    }}>
      P{priority}
    </span>
  );
}

export function StatusDot({ status }) {
  const colors = {
    open: '#55556a',
    'in-progress': '#f59e0b',
    done: '#34d399',
  };
  return (
    <span style={{
      width: 8, height: 8, borderRadius: '50%', display: 'inline-block',
      background: colors[status] || colors.open,
      boxShadow: status === 'in-progress' ? '0 0 6px #f59e0b' : 'none',
    }} />
  );
}

export function StatCard({ label, value, color }) {
  const colorMap = {
    blue: '#4d8eff', red: '#ef4444', amber: '#f59e0b',
    green: '#34d399', purple: '#a855f7', cyan: '#22d3ee',
  };
  return (
    <div className="stat-card-pm">
      <div className="stat-label-pm">{label}</div>
      <div className="stat-value-pm" style={{ color: colorMap[color] || colorMap.blue }}>{value}</div>
    </div>
  );
}
