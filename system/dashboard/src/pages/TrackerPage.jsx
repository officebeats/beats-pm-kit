import { useState, useEffect } from 'react';

export default function TrackerPage({ trackerName, label, icon }) {
  const [tracker, setTracker] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`/api/tracker/${trackerName}`);
      if (res.ok) setTracker(await res.json());
    };
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, [trackerName]);

  if (!tracker) return <div className="page-loading">Loading {label}...</div>;

  const filtered = tracker.type === 'checklist'
    ? tracker.items.filter(i => filter === 'all' || i.status === filter)
    : tracker.items;

  let lastSection = '';

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">{icon} {label}</h1>
        <span className="item-count">{tracker.items.length} items</span>
      </div>

      {tracker.type === 'checklist' && (
        <div className="filter-bar">
          {['all', 'open', 'in-progress', 'done'].map(f => (
            <button key={f} onClick={() => setFilter(f)} className={`filter-btn ${filter === f ? 'active' : ''}`}>
              {f === 'all' ? 'All' : f === 'in-progress' ? 'In Progress' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      )}

      {tracker.type === 'table' ? (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                {Object.keys(tracker.items[0] || {}).map(h => <th key={h}>{h}</th>)}
              </tr>
            </thead>
            <tbody>
              {tracker.items.map((row, i) => (
                <tr key={i}>
                  {Object.values(row).map((v, j) => <td key={j}>{v}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="item-list">
          {filtered.map((item, i) => {
            let sectionEl = null;
            if (item.section && item.section !== lastSection) {
              lastSection = item.section;
              sectionEl = <div className="section-divider" key={`s-${i}`}>{item.section}</div>;
            }
            return (
              <div key={i}>
                {sectionEl}
                <div className={`item-row status-${item.status}`}>
                  <span className={`status-dot ${item.status}`} />
                  <span className="item-text">{item.text}</span>
                  {item.priority !== null && (
                    <span className={`priority-chip p${item.priority}`}>P{item.priority}</span>
                  )}
                  {item.tags?.length > 0 && (
                    <div className="tag-group">
                      {item.tags.map(t => <span className="tag" key={t}>{t}</span>)}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {filtered.length === 0 && (
            <div className="empty-msg">No items match the current filter.</div>
          )}
        </div>
      )}
    </div>
  );
}
