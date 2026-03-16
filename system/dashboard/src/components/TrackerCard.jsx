export default function TrackerCard({ name, tracker, meta }) {
  const { icon, label, color } = meta;
  const { items, type } = tracker;

  const iconBg = {
    blue: 'rgba(77,142,255,0.12)',
    red: 'rgba(239,68,68,0.12)',
    amber: 'rgba(245,158,11,0.12)',
    green: 'rgba(52,211,153,0.12)',
    purple: 'rgba(168,85,247,0.12)',
    cyan: 'rgba(34,211,238,0.12)',
  }[color] || 'rgba(77,142,255,0.12)';

  if (type === 'table') {
    return (
      <div className="tracker-card">
        <div className="tracker-card-header">
          <div className="tracker-card-title">
            <span className="icon" style={{ background: iconBg }}>{icon}</span>
            {label}
          </div>
          <span className="tracker-count">{items.length} items</span>
        </div>
        {items.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: 13, padding: '12px 0' }}>
            No items tracked.
          </div>
        ) : (
          <table className="tracker-table">
            <thead>
              <tr>
                {Object.keys(items[0]).map(h => (
                  <th key={h}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((row, i) => (
                <tr key={i}>
                  {Object.values(row).map((val, j) => (
                    <td key={j}>{val}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    );
  }

  // Checklist type
  let lastSection = '';
  return (
    <div className="tracker-card">
      <div className="tracker-card-header">
        <div className="tracker-card-title">
          <span className="icon" style={{ background: iconBg }}>{icon}</span>
          {label}
        </div>
        <span className="tracker-count">{items.length} items</span>
      </div>
      {items.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', fontSize: 13, padding: '12px 0' }}>
          No items tracked.
        </div>
      ) : (
        <ul className="checklist">
          {items.map((item, i) => {
            let sectionHeader = null;
            if (item.section && item.section !== lastSection) {
              lastSection = item.section;
              sectionHeader = <div className="section-header" key={`s-${i}`}>{item.section}</div>;
            }
            return (
              <li key={i}>
                {sectionHeader}
                <div className={`checklist-item ${item.status}`}>
                  <span className={`checklist-status ${item.status}`}>
                    {item.status === 'done' ? '✓' : item.status === 'in-progress' ? '›' : ''}
                  </span>
                  <span className="checklist-text">{item.text}</span>
                  {item.priority !== null && (
                    <span className={`priority-badge p${item.priority}`}>P{item.priority}</span>
                  )}
                </div>
                {item.tags.length > 0 && (
                  <div className="tags-row" style={{ marginLeft: 28 }}>
                    {item.tags.map(tag => (
                      <span className="tag" key={tag}>{tag}</span>
                    ))}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
