import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export default function PeoplePage() {
  const [tasks, setTasks] = useState([]);
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    const res = await fetch('/api/tasks');
    const data = await res.json();
    setTasks(data.active || []);
  }, []);

  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t); }, [load]);

  // Extract unique stakeholders from owner field
  const people = [...new Set(tasks.map(t => t.owner).filter(Boolean))];
  const selectedTasks = selected ? tasks.filter(t => t.owner === selected) : [];

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">👥 People</h1>
        <span className="item-count">{people.length} stakeholders</span>
      </div>

      {/* Stakeholder cards */}
      <div className="entity-grid">
        {people.map(person => {
          const pTasks = tasks.filter(t => t.owner === person);
          const nowCount = pTasks.filter(t => t.status === 'Now').length;
          const doneCount = pTasks.filter(t => t.status === 'Done').length;
          const isActive = selected === person;
          return (
            <div className={`entity-card overview-card overview-card-interactive ${isActive ? 'entity-active' : ''}`}
              key={person} onClick={() => setSelected(isActive ? null : person)}
              onKeyDown={e => e.key === 'Enter' && setSelected(isActive ? null : person)}
              role="button" tabIndex={0} aria-expanded={isActive}>
              <div className="entity-icon">👤</div>
              <div className="entity-info">
                <div className="entity-name">{person}</div>
                <div className="entity-stats">
                  <span>{pTasks.length} tasks</span>
                  {nowCount > 0 && <span className="entity-badge red">{nowCount} Now</span>}
                  {doneCount > 0 && <span className="entity-badge green">{doneCount} Done</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Drill-down task list */}
      {selected && (
        <div className="entity-drilldown">
          <h2 className="overview-section-title" style={{ marginTop: 16 }}>
            Tasks for {selected} <span className="item-count">{selectedTasks.length}</span>
          </h2>
          <div className="task-list">
            {selectedTasks.map(task => (
              <div className="task-card" key={task.id} onClick={() => navigate('/kanban')}
                role="button" tabIndex={0} style={{ cursor: 'pointer' }}>
                <div className="task-card-top">
                  <span className={`priority-chip ${task.priority?.toLowerCase()}`}>{task.priority}</span>
                  <span className={`status-chip ${task.status?.toLowerCase().replace(/ /g, '-')}`}>{task.status}</span>
                  <span className="task-id">{task.id}</span>
                </div>
                <div className="task-card-body">
                  <div className="task-title">{task.task}</div>
                  <div className="task-meta">
                    <span className="meta-chip product-chip">{task.product}</span>
                    <span className="meta-chip project-chip">{task.project}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {people.length === 0 && (
        <div className="empty-msg" style={{ padding: '40px 0', textAlign: 'center' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>👥</div>
          <div>No stakeholders found.</div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
            Add tasks with an owner field to see stakeholder cards here.
          </div>
        </div>
      )}
    </div>
  );
}
