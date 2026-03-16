import { useState, useEffect, useCallback } from 'react';

export default function ArchivePage() {
  const [archive, setArchive] = useState([]);

  const load = useCallback(async () => {
    const res = await fetch('/api/tasks');
    const data = await res.json();
    setArchive(data.archive || []);
  }, []);

  useEffect(() => { load(); }, [load]);

  const unarchive = async (id) => {
    await fetch(`/api/tasks/${id}/unarchive`, { method: 'POST' });
    load();
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">🗄 Archive</h1>
        <span className="item-count">{archive.length} archived</span>
      </div>

      {archive.length === 0 ? (
        <div className="archive-empty">
          <div className="archive-empty-icon">🗄</div>
          <div className="archive-empty-text">No archived tasks yet.</div>
          <div className="archive-empty-hint">Tasks marked Done can be archived from the Tasks or Kanban view.</div>
        </div>
      ) : (
        <div className="task-list">
          {archive.map(task => (
            <div className="task-card archived" key={task.id}>
              <div className="task-card-top">
                <span className={`priority-chip ${task.priority?.toLowerCase()}`}>{task.priority}</span>
                <span className="status-chip done">Archived</span>
                <span className="task-id">{task.id}</span>
              </div>
              <div className="task-card-body">
                <div className="task-title">{task.task}</div>
                <div className="task-meta">
                  <span className="meta-chip product-chip">{task.product}</span>
                  <span className="meta-chip project-chip">{task.project}</span>
                </div>
              </div>
              <div className="task-card-actions">
                <button className="unarchive-btn" onClick={() => unarchive(task.id)}>↑ Restore</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
