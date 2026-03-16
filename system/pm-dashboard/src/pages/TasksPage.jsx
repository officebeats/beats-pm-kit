import { useState, useEffect, useCallback, useRef } from 'react';

const TRACKER_TABS = [
  { key: 'tasks', label: 'Tasks', icon: '⚡' },
  { key: 'bugs', label: 'Bugs', icon: '🐛', tags: ['bug'] },
  { key: 'boss', label: 'Boss Asks', icon: '👔', tags: ['boss', 'boss-ask'] },
  { key: 'eng', label: 'Engineering', icon: '⚙️', tags: ['eng', 'engineering'] },
  { key: 'ux', label: 'UX', icon: '🎨', tags: ['ux', 'design'] },
];

const DEFAULT_COLUMNS = ['Now', 'Next', 'Later'];
const COL_COLORS = { 'Now': '#ef4444', 'Next': '#f59e0b', 'Later': '#4d8eff', 'Done': '#00a86b' };
function getColColor(col) { return COL_COLORS[col] || '#a855f7'; }

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [descs, setDescs] = useState({});
  const [filter, setFilter] = useState({ status: 'all', product: 'all', project: 'all' });
  const [activeTab, setActiveTab] = useState('tasks');
  const [viewMode, setViewMode] = useState(() => localStorage.getItem('taskViewMode') || 'list');

  // Kanban state
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
    const res = await fetch('/api/tasks');
    const data = await res.json();
    const active = data.active || [];
    setTasks(active);
    setDescs(data.descriptions || {});
    const statuses = [...new Set(active.map(t => t.status))];
    const custom = statuses.filter(s => s !== 'Done' && !DEFAULT_COLUMNS.includes(s));
    setColumns([...DEFAULT_COLUMNS, ...custom]);
  }, []);

  useEffect(() => { load(); const t = setInterval(load, 2000); return () => clearInterval(t); }, [load]);

  // Persist view mode
  useEffect(() => { localStorage.setItem('taskViewMode', viewMode); }, [viewMode]);

  const updateStatus = async (id, status) => {
    await fetch(`/api/tasks/${id}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }) });
    load();
  };
  const archiveTask = async (id, e) => { if (e) e.stopPropagation(); await fetch(`/api/tasks/${id}/archive`, { method: 'POST' }); load(); setDetail(null); };
  const markDone = async (id, e) => { e.stopPropagation(); await updateStatus(id, 'Done'); };
  const saveDesc = async () => {
    if (!detail) return;
    await fetch(`/api/tasks/${detail.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ description: editDesc }) });
    load();
  };
  const openDetail = (task) => { setDetail(task); setEditDesc(descs[task.id] || ''); };
  const closeDetail = () => { saveDesc(); setDetail(null); };
  const addColumn = () => { const n = newColName.trim(); if (n && !columns.includes(n) && n !== 'Done') { setColumns([...columns, n]); setNewColName(''); setShowAddCol(false); } };
  const removeColumn = (col) => { if (DEFAULT_COLUMNS.includes(col)) return; tasks.filter(t => t.status === col).forEach(t => updateStatus(t.id, 'Later')); setColumns(columns.filter(c => c !== col)); };

  // Drag-and-drop
  const onMouseDown = (e) => { dragStartPos.current = { x: e.clientX, y: e.clientY }; };
  const onDragStart = (e, id) => { setDragId(id); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', id); };
  const onDragOver = (e, col) => { e.preventDefault(); e.dataTransfer.dropEffect = 'move'; setDragOver(col); };
  const onDragLeave = () => setDragOver(null);
  const onDrop = (e, status) => { e.preventDefault(); setDragOver(null); if (dragId) { updateStatus(dragId, status); setDragId(null); } };
  const onDragEnd = () => { setDragId(null); setDragOver(null); };
  const onCardClick = (e, task) => {
    if (dragStartPos.current) {
      const dx = Math.abs(e.clientX - dragStartPos.current.x);
      const dy = Math.abs(e.clientY - dragStartPos.current.y);
      if (dx > 5 || dy > 5) return;
    }
    openDetail(task);
  };

  const currentTab = TRACKER_TABS.find(t => t.key === activeTab);

  // Pre-filter by active tab's tags
  const tabFiltered = currentTab?.tags
    ? tasks.filter(t => (t.tags || []).some(tag => currentTab.tags.includes(tag.toLowerCase())))
    : tasks;

  const products = [...new Set(tabFiltered.map(t => t.product).filter(Boolean))];
  const projects = [...new Set(tabFiltered.map(t => t.project).filter(Boolean))];
  const filtered = tabFiltered.filter(t => {
    if (filter.status !== 'all' && t.status !== filter.status) return false;
    if (filter.product !== 'all' && t.product !== filter.product) return false;
    if (filter.project !== 'all' && t.project !== filter.project) return false;
    return true;
  });
  const statusOrder = { 'Critical': 0, 'High': 1, 'Normal': 2, 'Low': 3 };
  filtered.sort((a, b) => (statusOrder[a.priority] ?? 9) - (statusOrder[b.priority] ?? 9));

  const doneTasks = tasks.filter(t => t.status === 'Done');


  // ── Kanban board rendering ──
  const renderBoard = () => (
    <>
      {showAddCol && (
        <div className="add-col-bar">
          <input className="add-col-input" placeholder="Column name..." value={newColName} onChange={e => setNewColName(e.target.value)} onKeyDown={e => e.key === 'Enter' && addColumn()} autoFocus />
          <button className="add-col-btn" onClick={addColumn}>Add</button>
          <button className="add-col-cancel" onClick={() => { setShowAddCol(false); setNewColName(''); }}>Cancel</button>
        </div>
      )}
      <div className="kanban-board" style={{ gridTemplateColumns: `repeat(${columns.length}, 1fr) 48px` }}>
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
                    draggable onMouseDown={onMouseDown} onDragStart={e => onDragStart(e, task.id)}
                    onDragEnd={onDragEnd} onClick={e => onCardClick(e, task)}>
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
        {/* Ghost add-column */}
        <div className="kanban-col-add">
          {showAddCol ? (
            <div className="add-col-inline">
              <input className="add-col-input" placeholder="Name…" value={newColName} onChange={e => setNewColName(e.target.value)} onKeyDown={e => e.key === 'Enter' && addColumn()} autoFocus />
              <button className="add-col-btn" onClick={addColumn}>✓</button>
              <button className="add-col-cancel" onClick={() => { setShowAddCol(false); setNewColName(''); }}>×</button>
            </div>
          ) : (
            <button className="kanban-add-col-btn" onClick={() => setShowAddCol(true)} title="Add column">+</button>
          )}
        </div>
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
    </>
  );

  // ── List view rendering ──
  const renderList = () => (
    <>
      <div className="filter-bar">
        <select className="filter-select" value={filter.status} onChange={e => setFilter(f => ({ ...f, status: e.target.value }))}>
          <option value="all">All Statuses</option>
          <option value="Now">Now</option>
          <option value="Next">Next</option>
          <option value="Later">Later</option>
          <option value="Done">Done</option>
        </select>
        <select className="filter-select" value={filter.product} onChange={e => setFilter(f => ({ ...f, product: e.target.value }))}>
          <option value="all">All Products</option>
          {products.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
        <select className="filter-select" value={filter.project} onChange={e => setFilter(f => ({ ...f, project: e.target.value }))}>
          <option value="all">All Projects</option>
          {projects.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>
      <div className="task-list">
        {filtered.map(task => (
          <div className="task-card" key={task.id}>
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
            <div className="task-card-actions">
              <select className="status-select" value={task.status} onChange={e => updateStatus(task.id, e.target.value)}>
                <option value="Now">Now</option>
                <option value="Next">Next</option>
                <option value="Later">Later</option>
                <option value="Done">Done</option>
              </select>
              {task.status === 'Done' && <button className="archive-btn" onClick={() => archiveTask(task.id)}>Archive</button>}
            </div>
          </div>
        ))}
        {filtered.length === 0 && <div className="empty-msg">No tasks match the current filters.</div>}
      </div>
    </>
  );

  return (
    <div className={`page ${activeTab === 'tasks' && viewMode === 'board' ? 'page-wide' : ''}`}>
      <div className="page-header">
        <h1 className="page-title">
          {currentTab?.icon} {currentTab?.label || 'Tasks'}
        </h1>
        <span className="item-count">
          {`${filtered.length} tasks`}
        </span>

        {/* Notion-style view toggle */}
        <div className="view-toggle">
            <button className={`view-toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')} title="List view">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="1" y="2" width="14" height="2" rx="1" fill="currentColor"/><rect x="1" y="7" width="14" height="2" rx="1" fill="currentColor"/><rect x="1" y="12" width="14" height="2" rx="1" fill="currentColor"/></svg>
            </button>
            <button className={`view-toggle-btn ${viewMode === 'board' ? 'active' : ''}`}
              onClick={() => setViewMode('board')} title="Board view">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="4" height="14" rx="1" fill="currentColor"/><rect x="6" y="1" width="4" height="10" rx="1" fill="currentColor"/><rect x="11" y="1" width="4" height="12" rx="1" fill="currentColor"/></svg>
            </button>
          </div>
      </div>

      {/* Sub-tabs */}
      <div className="sub-tabs">
        {TRACKER_TABS.map(tab => (
          <button key={tab.key}
            className={`sub-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}>
            <span className="sub-tab-icon">{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tasks content — list or board (all tabs) */}
      {viewMode === 'list' && renderList()}
      {viewMode === 'board' && renderBoard()}

      {/* Detail Modal */}
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
