import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ProductsPage() {
  const [tasks, setTasks] = useState([]);
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    const res = await fetch('/api/tasks');
    const data = await res.json();
    setTasks(data.active || []);
  }, []);

  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t); }, [load]);

  const products = [...new Set(tasks.map(t => t.product).filter(Boolean))];
  const selectedTasks = selected ? tasks.filter(t => t.product === selected) : [];
  const selectedProjects = selected ? [...new Set(selectedTasks.map(t => t.project).filter(Boolean))] : [];

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">📦 Products</h1>
        <span className="item-count">{products.length} products</span>
      </div>

      {/* Product cards */}
      <div className="entity-grid">
        {products.map(prod => {
          const pTasks = tasks.filter(t => t.product === prod);
          const projects = [...new Set(pTasks.map(t => t.project).filter(Boolean))];
          const donePct = pTasks.length ? Math.round(pTasks.filter(t => t.status === 'Done').length / pTasks.length * 100) : 0;
          const criticalCount = pTasks.filter(t => t.priority === 'Critical').length;
          const isActive = selected === prod;
          return (
            <div className={`entity-card overview-card overview-card-interactive ${isActive ? 'entity-active' : ''}`}
              key={prod} onClick={() => setSelected(isActive ? null : prod)}
              onKeyDown={e => e.key === 'Enter' && setSelected(isActive ? null : prod)}
              role="button" tabIndex={0} aria-expanded={isActive}>
              <div className="entity-icon">📦</div>
              <div className="entity-info">
                <div className="entity-name">{prod}</div>
                <div className="entity-stats">
                  <span>{pTasks.length} tasks</span>
                  <span>{projects.length} projects</span>
                  {criticalCount > 0 && <span className="entity-badge red">{criticalCount} Critical</span>}
                </div>
                <div className="overview-bar-track" style={{ marginTop: 4 }}>
                  <div className="overview-bar-fill" style={{ width: `${donePct}%` }} />
                </div>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2 }}>{donePct}% complete</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Drill-down: projects + tasks under selected product */}
      {selected && (
        <div className="entity-drilldown">
          <h2 className="overview-section-title" style={{ marginTop: 16 }}>
            {selected} <span className="item-count">{selectedTasks.length} tasks · {selectedProjects.length} projects</span>
          </h2>

          {/* Projects under this product */}
          {selectedProjects.length > 0 && (
            <div className="entity-grid" style={{ marginBottom: 12 }}>
              {selectedProjects.map(prj => {
                const prjTasks = selectedTasks.filter(t => t.project === prj);
                const prjDone = prjTasks.length ? Math.round(prjTasks.filter(t => t.status === 'Done').length / prjTasks.length * 100) : 0;
                return (
                  <div className="overview-card" key={prj} style={{ padding: '8px 12px' }}>
                    <span className="meta-chip project-chip">{prj}</span>
                    <span className="overview-count" style={{ marginLeft: 8 }}>{prjTasks.length} tasks · {prjDone}%</span>
                    <div className="overview-bar-track" style={{ marginTop: 4 }}>
                      <div className="overview-bar-fill" style={{ width: `${prjDone}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Task list */}
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
                    <span className="meta-chip project-chip">{task.project}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {products.length === 0 && (
        <div className="empty-msg" style={{ padding: '40px 0', textAlign: 'center' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📦</div>
          <div>No products found.</div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
            Add tasks with a product field to see product cards here.
          </div>
        </div>
      )}
    </div>
  );
}
