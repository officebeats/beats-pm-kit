"use client";

import { useState, useMemo } from 'react';
import { 
  CheckSquare,
  Clock, 
  Search, 
  User, 
  RefreshCcw,
  Target,
  Kanban as KanbanIcon,
  List as ListIcon,
  ChevronUp,
  ChevronDown,
  Edit2,
  Save,
  X,
  Zap,
  Layers,
  Archive,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function TaskDashboard({ initialTasks }) {
  const [tasks, setTasks] = useState(initialTasks.active);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all'); 
  const [view, setView] = useState('active'); 
  const [layout, setLayout] = useState('kanban'); 
  const [stats] = useState(initialTasks.stats);
  const [isSyncing, setIsSyncing] = useState(false);
  
  const [editingId, setEditingId] = useState(null);
  const [editValue, setEditValue] = useState("");
  const [editField, setEditField] = useState(null);

  const [sortConfig, setSortConfig] = useState({ key: 'status', direction: 'asc' });

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') direction = 'desc';
    setSortConfig({ key, direction });
  };

  const SortIcon = ({ field }) => {
    if (sortConfig.key !== field) return null;
    return sortConfig.direction === 'asc' ? <ChevronUp size={10} /> : <ChevronDown size={10} />;
  };

  const currentTasksData = useMemo(() => {
    const list = view === 'active' ? tasks : initialTasks.completed;
    
    let filtered = list.filter(task => {
      const matchesSearch = 
        task.title.toLowerCase().includes(search.toLowerCase()) || 
        task.id.toLowerCase().includes(search.toLowerCase()) ||
        task.project.toLowerCase().includes(search.toLowerCase());
      const matchesFilter = filter === 'all' || task.priority.toLowerCase() === filter.toLowerCase();
      return matchesSearch && matchesFilter;
    });

    return filtered.sort((a, b) => {
      let aVal = a[sortConfig.key] || "";
      let bVal = b[sortConfig.key] || "";
      if (sortConfig.key === 'priority') {
        const pMap = { 'P0': 0, 'P1': 1, 'P2': 2 };
        aVal = pMap[a.priority]; bVal = pMap[b.priority];
      }
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [tasks, initialTasks.completed, view, search, filter, sortConfig]);

  const saveEdit = async (id, field) => {
    setIsSyncing(true);
    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, field, value: editValue })
      });
      if (response.ok) {
        setTasks(prev => prev.map(t => t.id === id ? { ...t, [field]: editValue } : t));
        setEditingId(null); setEditField(null);
      }
    } catch (err) { console.error(err); }
    finally { setIsSyncing(false); }
  };

  const EditableCell = ({ task, field, children }) => {
    const isEditing = editingId === task.id && editField === field;
    if (isEditing) {
      return (
        <span style={{ display: 'inline-flex', gap: '0.2rem', alignItems: 'center' }}>
          <input 
            className="search-input" 
            style={{ padding: '0.2rem 0.4rem', fontSize: '0.72rem', width: '80px', maxWidth: '80px' }}
            value={editValue} 
            onChange={(e) => setEditValue(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') saveEdit(task.id, field); if (e.key === 'Escape') setEditingId(null); }}
            autoFocus 
          />
          <Save size={11} style={{ cursor: 'pointer', color: 'var(--accent-green)' }} onClick={() => saveEdit(task.id, field)} />
          <X size={11} style={{ cursor: 'pointer', color: 'var(--fg-tertiary)' }} onClick={() => setEditingId(null)} />
        </span>
      );
    }
    return (
      <span 
        onClick={() => { setEditingId(task.id); setEditField(field); setEditValue(task[field]); }} 
        style={{ cursor: 'pointer' }}
        title="Click to edit"
      >
        {children}
      </span>
    );
  };

  const columnConfig = [
    { id: 'Now', title: 'Now / Today', icon: <Zap size={12} style={{ color: 'var(--accent-amber)' }} />, color: 'var(--accent-amber)' },
    { id: 'Next Week', title: 'Next Week', icon: <Clock size={12} style={{ color: 'var(--accent-blue)' }} />, color: 'var(--accent-blue)' },
    { id: 'Later', title: 'Later', icon: <Target size={12} style={{ color: 'var(--accent-green)' }} />, color: 'var(--accent-green)' }
  ];

  return (
    <div className="dashboard-container">
      {/* ─── Sidebar ─── */}
      <aside className="sidebar">
        <div className="sidebar-brand">NEO PM</div>

        <nav style={{ flex: 1 }}>
          <div className="nav-section-label">Views</div>
          <div className={`nav-item ${view === 'active' ? 'active' : ''}`} onClick={() => setView('active')}>
            <Layers size={13} /> Dashboard
          </div>
          <div className={`nav-item ${view === 'completed' ? 'active' : ''}`} onClick={() => setView('completed')}>
            <CheckSquare size={13} /> Archived
          </div>

          <div className="nav-section-label">Layout</div>
          <div className={`nav-item ${layout === 'kanban' ? 'active' : ''}`} onClick={() => setLayout('kanban')}>
            <KanbanIcon size={13} /> Board
          </div>
          <div className={`nav-item ${layout === 'list' ? 'active' : ''}`} onClick={() => setLayout('list')}>
            <ListIcon size={13} /> Table
          </div>
        </nav>
        
        <footer>
          <button className="sync-btn" onClick={async () => {
            setIsSyncing(true);
            try {
              const res = await fetch('/api/tasks');
              const data = await res.json();
              setTasks(data.active);
            } catch(e) { console.error(e); }
            finally { setTimeout(() => setIsSyncing(false), 500); }
          }}>
            <RefreshCcw size={12} className={isSyncing ? 'animate-spin' : ''} />
            Sync
          </button>
        </footer>
      </aside>

      {/* ─── Main ─── */}
      <main className="main-content">
        <header className="header">
          <h1>
            Antigravity Cockpit
            <span className="version">v7.5 (Neo)</span>
          </h1>
          <button className="sync-btn" onClick={() => window.location.reload()}>
            <RefreshCcw size={12} /> Sync
          </button>
        </header>

        {/* Stats */}
        <div className="stats-grid">
          {[
            { label: 'NOW', value: stats.p0, color: 'var(--accent-amber)' },
            { label: 'NEXT', value: stats.p1, color: 'var(--accent-blue)' },
            { label: 'FUTURE', value: stats.p2, color: 'var(--accent-green)' },
            { label: 'DONE', value: stats.done, color: 'var(--accent-purple)' },
          ].map(s => (
            <div className="stat-card" key={s.label}>
              <div className="stat-header">{s.label}</div>
              <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
            </div>
          ))}
        </div>

        {/* Toolbar */}
        <div className="toolbar">
          <input 
            type="text" 
            placeholder="Filter tasks..." 
            className="search-input" 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {['all', 'P0'].map(f => (
            <button 
              key={f}
              className={`filter-pill ${filter === f.toLowerCase() ? 'active' : ''}`}
              onClick={() => setFilter(f.toLowerCase() === filter ? 'all' : f.toLowerCase())}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>

        {/* Content */}
        <section style={{ overflowY: 'auto', maxHeight: 'calc(100vh - 250px)', paddingBottom: '1rem' }}>
          <AnimatePresence mode="wait">
            <motion.div 
              key={layout + view}
              initial={{ opacity: 0, y: 6 }} 
              animate={{ opacity: 1, y: 0 }} 
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            >
              {layout === 'list' ? (
                <div className="task-list-section">
                  <table>
                    <thead>
                      <tr>
                        {[
                          { key: 'status', label: 'Status' },
                          { key: 'project', label: 'Project' },
                          { key: 'title', label: 'Task' },
                          { key: 'stage', label: 'Stage' },
                          { key: 'owner', label: 'Owner' },
                        ].map(col => (
                          <th key={col.key} onClick={() => handleSort(col.key)}>
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.2rem' }}>
                              {col.label} <SortIcon field={col.key} />
                            </span>
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {currentTasksData.map(task => (
                        <tr key={task.id}>
                          <td>
                            <EditableCell task={task} field="status">
                              <span className="stage-badge">{task.status}</span>
                            </EditableCell>
                          </td>
                          <td><span className="project-tag">{task.project}</span></td>
                          <td>
                            <div className="task-title" style={{ margin: 0, fontSize: '0.75rem' }}>{task.title}</div>
                            <div className="task-id">{task.id}</div>
                          </td>
                          <td>
                            <EditableCell task={task} field="stage">
                              <span className="stage-badge">{task.stage}</span>
                            </EditableCell>
                          </td>
                          <td style={{ color: 'var(--fg-secondary)', fontSize: '0.72rem' }}>{task.owner}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                /* Kanban Board */
                <div className="kanban-grid">
                  {columnConfig.map(col => {
                    const colTasks = currentTasksData.filter(t => t.status === col.id);
                    return (
                      <div key={col.id} className="kanban-column">
                        <div className="kanban-column-header">
                          <div className="col-title">
                            {col.icon}
                            <span>{col.title}</span>
                          </div>
                          <span className="col-count">{colTasks.length}</span>
                        </div>
                        {colTasks.map(task => (
                          <motion.div 
                            key={task.id} 
                            layoutId={task.id}
                            className="kanban-card"
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.25rem' }}>
                              <span className="task-id">{task.id}</span>
                              <span className="project-tag">{task.project}</span>
                            </div>
                            <div className="task-title">{task.title}</div>
                            <div className="task-meta">
                              <span className="task-owner">
                                <User size={10} /> {task.owner.split('/')[0]}
                              </span>
                              <span className="stage-badge">{task.stage}</span>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    );
                  })}
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </section>
      </main>
    </div>
  );
}
