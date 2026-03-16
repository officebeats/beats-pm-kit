import { useState, useEffect, useCallback } from 'react';
import Header from './components/Header.jsx';
import StatCard from './components/StatCard.jsx';
import TrackerCard from './components/TrackerCard.jsx';

const TRACKER_META = {
  TASK_MASTER: { icon: '⚡', label: 'Tasks', color: 'blue' },
  BUG_TRACKER: { icon: '🐛', label: 'Bugs', color: 'red' },
  BOSS_REQUESTS: { icon: '👔', label: 'Boss Asks', color: 'amber' },
  PROJECT_TRACKER: { icon: '📦', label: 'Projects', color: 'purple' },
  ENG_TASKS: { icon: '⚙️', label: 'Engineering', color: 'cyan' },
  UX_TASKS: { icon: '🎨', label: 'UX', color: 'green' },
  DECISION_LOG: { icon: '📝', label: 'Decisions', color: 'blue' },
  DELEGATED_TASKS: { icon: '📤', label: 'Delegated', color: 'amber' },
};

function countByStatus(items, type) {
  if (type === 'table') {
    return {
      total: items.length,
      done: items.filter(i => (i.Status || '').includes('Done') || (i.Status || '').includes('✅')).length,
      open: items.filter(i => !(i.Status || '').includes('Done') && !(i.Status || '').includes('✅')).length,
    };
  }
  return {
    total: items.length,
    done: items.filter(i => i.status === 'done').length,
    open: items.filter(i => i.status === 'open').length,
    inProgress: items.filter(i => i.status === 'in-progress').length,
  };
}

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (!data && !error) {
    return (
      <div className="loading">
        <div className="loading-spinner" />
        Connecting to brain...
      </div>
    );
  }

  const trackerEntries = data ? Object.entries(data.trackers) : [];

  // Aggregate stats
  let totalOpen = 0, totalDone = 0, totalInProgress = 0, totalP0 = 0;
  trackerEntries.forEach(([, tracker]) => {
    const counts = countByStatus(tracker.items, tracker.type);
    totalOpen += counts.open || 0;
    totalDone += counts.done || 0;
    totalInProgress += counts.inProgress || 0;
    if (tracker.type === 'checklist') {
      totalP0 += tracker.items.filter(i => i.priority === 0 && i.status !== 'done').length;
    }
  });

  return (
    <div className="dashboard">
      <Header version={data?.version} lastUpdate={lastUpdate} />

      {error && <div className="error-banner">⚠ API Error: {error}</div>}

      <div className="summary-row">
        <StatCard label="Open Items" value={totalOpen} color="blue" />
        <StatCard label="In Progress" value={totalInProgress} color="amber" />
        <StatCard label="Completed" value={totalDone} color="green" />
        <StatCard label="P0 Critical" value={totalP0} color="red" />
        <StatCard label="Trackers" value={trackerEntries.length} color="purple" />
        <StatCard label="Refresh" value="5s" color="cyan" />
      </div>

      <div className="tracker-grid">
        {trackerEntries.map(([key, tracker]) => (
          <TrackerCard
            key={key}
            name={key}
            tracker={tracker}
            meta={TRACKER_META[key] || { icon: '📄', label: key, color: 'blue' }}
          />
        ))}
      </div>
    </div>
  );
}
