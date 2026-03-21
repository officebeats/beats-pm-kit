import { useState, useEffect, useCallback, useRef } from 'react';

const DEFAULT_COLUMNS = ['Now', 'Next', 'Later'];
const COL_COLORS = { 'Now': '#ef4444', 'Next': '#f59e0b', 'Later': '#4d8eff', 'Done': '#00a86b' };
function getColColor(col) { return COL_COLORS[col] || '#a855f7'; }

export default function KanbanPage() {
  const [tasks, setTasks] = useState([]);
  const [descs, setDescs] = useState({});
  const [columns, setColumns] = useState(DEFAULT_COLUMNS);
  const [dragId, setDragId] = useState(null);
  const [dragOver, setDragOver] = useState(null);
  const [detail, setDetail] = useState(null);
  const [editDesc, setEditDesc] = useState('');
  const [newColName, setNewColName] = useState('');
  const [showAddCol, setShowAddCol] = useState(false);
  const [showDone, setShowDone] = useState(false);
  const dragStartPos = useRef(null);

  const load = useCallback(async () => {
    try {
      const res = await fetch('/api/tasks');
      const data = await res.json();
      const active = data.active || [];
      setTasks(active);
      setDescs(data.descriptions || {});
      const statuses = [...new Set(active.map(t => t.status))];
      const custom = statuses.filter(s => s !== 'Done' && !DEFAULT_COLUMNS.includes(s));
      setColumns([...DEFAULT_COLUMNS, ...custom]);
    } catch (e) { /* silent */ }
  }, []);

  useEffect(() => { load(); const t = setInterval(load, 2000); return () => clearInterval(t); }, [load]);

  const updateStatus = async (id, status) => {
    await fetch(`/api/tasks/${id}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }) });
    load();
  };
  const markDone = async (id, e) => { e.stopPropagation(); await updateStatus(id, 'Done'); };
  const archiveTask = async (id, e) => { if (e) e.stopPropagation(); await fetch(`/api/tasks/${id}/archive`, { method: 'POST' }); load(); setDetail(null); };
  const saveDesc = async () => {
    if (!detail) return;
    await fetch(`/api/tasks/${detail.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ description: editDesc }) });
    load();
  };

  const openDetail = (task) => { setDetail(task); setEditDesc(descs[task.id] || ''); };
  const closeDetail = () => { saveDesc(); setDetail(null); };

  const addColumn = () => { const n = newColName.trim(); if (n && !columns.includes(n) && n !== 'Done') { setColumns([...columns, n]); setNewColName(''); setShowAddCol(false); } };
  const removeColumn = (col) => { if (DEFAULT_COLUMNS.includes(col)) return; tasks.filter(t => t.status === col).forEach(t => updateStatus(t.id, 'Later')); setColumns(columns.filter(c => c !== col)); };

  // Drag-and-drop: distinguish click from drag using mouse movement threshold
  const onMouseDown = (e) => { dragStartPos.current = { x: e.clientX, y: e.clientY }; };
  const onDragStart = (e, id) => { setDragId(id); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', id); };
  const onDragOver = (e, col) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; setDragOver(col); };
  const onDragLeave = () => setDragOver(null);
  const onDrop = (e, status) => { e.preventDefault(); setDragOver(null); if (dragId) { updateStatus(dragId, status); setDragId(null); } };
  const onDragEnd = () => { setDragId(null); setDragOver(null); };

  const onCardClick = (e, task) => {
    // Only open modal if mouse didn't move (not a drag)
    if (dragStartPos.current) {
      const dx = Math.abs(e.clientX - dragStartPos.current.x);
      const dy = Math.abs(e.clientY - dragStartPos.current.y);
      if (dx > 5 || dy > 5) return; // was a drag
    }
    openDetail(task);
  };

  // Touch drag support for mobile
  const touchRef = useRef(null);
  const onTouchStart = (e, id) => { touchRef.current = { id, el: e.currentTarget }; };
  const onTouchEnd = (e, task) => { touchRef.current = null; openDetail(task); };

  const doneTasks = tasks.filter(t => t.status === 'Done');

  return (
    <div className="page page-wide">
      <div className="page-header">
        <h1 className="page-title">◫ Kanban</h1>
        <span className="item-count">{tasks.length} tasks</span>
        <button className="add-col-trigger" onClick={() => setShowAddCol(!showAddCol)}>+ Column</button>
      </div>

      {showAddCol && (
        <div className="add-col-bar">
          <input className="add-col-input" placeholder="Column name..." value={newColName} onChange={e => setNewColName(e.target.value)} onKeyDown={e => e.key === 'Enter' && addColumn()} autoFocus />
          <button className="add-col-btn" onClick={addColumn}>Add</button>
          <button className="add-col-cancel" onClick={() => { setShowAddCol(false); setNewColName(''); }}>Cancel</button>
        </div>
      )}

      <div className="kanban-board" style={{ gridTemplateColumns: `repeat(${columns.length}, 1fr)` }}>
        {columns.map(col => {
          const colTasks = tasks.filter(t => t.status === col);
          const isCustom = !DEFAULT_COLUMNS.includes(col);
          const isOver = dragOver === col;
          return (
            <div className={`kanban-col ${isOver ? 'drag-over' : ''}`} key={col}
              onDragOver={e => onDragOver(e, col)} onDragLeave={onDragLeave} onDrop={e => onDrop(e, col)}>
              <div className="kanban-col-header">
                <span className="kanban-col-dot" style={{ background: getColColor(col), boxShadow: `0 0 8px ${getColColor(col)}60` }} />
                <span className="kanban-col-title">{col}</span>
                <span className="kanban-col-count">{colTasks.length}</span>
                {isCustom && <button className="kanban-col-remove" onClick={() => removeColumn(col)} title="Remove column">×</button>}
              </div>
              <div className="kanban-col-body">
                {colTasks.map(task => (
                  <div className={`kanban-card ${dragId === task.id ? 'dragging' : ''}`} key={task.id}
                    draggable
                    onMouseDown={onMouseDown}
                    onDragStart={e => onDragStart(e, task.id)}
                    onDragEnd={onDragEnd}
                    onClick={e => onCardClick(e, task)}
                    onTouchEnd={e => onTouchEnd(e, task)}>
                    <div className="kanban-card-top">
                      <span className={`priority-chip ${task.priority?.toLowerCase()}`}>{task.priority}</span>
                      <span className="task-id">{task.id}</span>
                      <button className="done-btn" onClick={e => markDone(task.id, e)} title="Mark complete">✓</button>
                    </div>
                    <div className="kanban-card-title">{task.task}</div>
                    <div className="kanban-card-meta">
                      {task.product && <span className="meta-chip product-chip">{task.product}</span>}
                      {task.project && <span className="meta-chip project-chip">{task.project}</span>}
                    </div>
                  </div>
                ))}
                {colTasks.length === 0 && <div className="kanban-empty">Drop here</div>}
              </div>
            </div>
          );
        })}
      </div>

      {doneTasks.length > 0 && (
        <div className="done-section">
          <h2 className="done-section-title" onClick={() => setShowDone(!showDone)} style={{ cursor: 'pointer', userSelect: 'none' }}>
            <span className={`accordion-chevron ${showDone ? 'open' : ''}`}>▸</span> Completed ({doneTasks.length})
          </h2>
          {showDone && (
            <div className="done-cards">
              {doneTasks.map(task => (
                <div className="kanban-card done-card" key={task.id} onClick={() => openDetail(task)}>
                  <div className="kanban-card-top"><span className="status-chip done">Done</span><span className="task-id">{task.id}</span></div>
                  <div className="kanban-card-title">{task.task}</div>
                  <button className="archive-btn-sm" onClick={e => archiveTask(task.id, e)}>Archive ↓</button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Detail Modal ──────────────── */}
      {detail && (
        <div className="modal-overlay" onClick={closeDetail}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <span className={`priority-chip ${detail.priority?.toLowerCase()}`}>{detail.priority}</span>
              <span className={`status-chip ${detail.status?.toLowerCase().replace(/ /g, '-')}`}>{detail.status}</span>
              <span className="task-id">{detail.id}</span>
              <button className="modal-close" onClick={closeDetail}>×</button>
            </div>
            <h2 className="modal-title">{detail.task}</h2>
            <div className="modal-meta-row">
              <div className="modal-meta-item"><span className="modal-meta-label">Product</span><span className="meta-chip product-chip">{detail.product}</span></div>
              <div className="modal-meta-item"><span className="modal-meta-label">Project</span><span className="meta-chip project-chip">{detail.project}</span></div>
              <div className="modal-meta-item"><span className="modal-meta-label">Owner</span><span>{detail.owner}</span></div>
              <div className="modal-meta-item"><span className="modal-meta-label">Due</span><span>{detail.due || '—'}</span></div>
            </div>
            {detail.tags?.length > 0 && <div className="modal-tags">{detail.tags.map(t => <span className="meta-chip tag-chip" key={t}>{t}</span>)}</div>}
            <div className="modal-desc-label">Description</div>
            <textarea className="modal-desc" value={editDesc} onChange={e => setEditDesc(e.target.value)} onBlur={saveDesc} placeholder="Add a description..." rows={5} />
            <div className="modal-actions">
              <select className="status-select" value={detail.status} onChange={e => { updateStatus(detail.id, e.target.value); setDetail({ ...detail, status: e.target.value }); }}>
                {columns.map(c => <option key={c} value={c}>{c}</option>)}
                <option value="Done">Done</option>
              </select>
              {detail.status === 'Done' && <button className="archive-btn" onClick={() => archiveTask(detail.id)}>Archive</button>}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
