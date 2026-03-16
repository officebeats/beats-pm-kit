import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Overview() {
  const [tasks, setTasks] = useState({ active: [], archive: [] });
  const [trackers, setTrackers] = useState({});
  const [version, setVersion] = useState('');
  const [expandedProducts, setExpandedProducts] = useState({});
  const [showProducts, setShowProducts] = useState(false);
  const [addingProduct, setAddingProduct] = useState(false);
  const [addingProject, setAddingProject] = useState(null); // product name or null
  const [newProductName, setNewProductName] = useState('');
  const [newProjectName, setNewProjectName] = useState('');
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const navigate = useNavigate();

  const load = useCallback(async () => {
    const [tRes, trRes] = await Promise.all([
      fetch('/api/tasks').then(r => r.json()),
      fetch('/api/trackers').then(r => r.json()),
    ]);
    setTasks(tRes);
    setTrackers(trRes.trackers || {});
    setVersion(trRes.version || '');
  }, []);

  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t); }, [load]);

  const active = tasks.active || [];
  const now = active.filter(t => t.status === 'Now').length;
  const next = active.filter(t => t.status === 'Next').length;
  const later = active.filter(t => t.status === 'Later').length;
  const critical = active.filter(t => t.priority === 'Critical').length;

  // Tracker counts
  const bugCount = active.filter(t => (t.tags || []).some(tag => tag.toLowerCase() === 'bug')).length;
  const bossCount = trackers['BOSS_REQUESTS']?.items?.length || 0;
  const delegatedCount = trackers['DELEGATED_TASKS']?.items?.length || 0;

  const products = [...new Set(active.map(t => t.product).filter(Boolean))];

  const toggleProduct = (prod) => {
    setExpandedProducts(prev => ({ ...prev, [prod]: !prev[prod] }));
  };

  const handleAddProduct = async () => {
    const name = newProductName.trim();
    const title = newTaskTitle.trim() || `Initial planning for ${name}`;
    if (!name) return;
    await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task: title, product: name, project: '', priority: 'Normal', tags: ['planning'] }),
    });
    setNewProductName('');
    setNewTaskTitle('');
    setAddingProduct(false);
    load();
  };

  const handleAddProject = async (product) => {
    const name = newProjectName.trim();
    const title = newTaskTitle.trim() || `Setup ${name}`;
    if (!name) return;
    await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task: title, product, project: name, priority: 'Normal', tags: ['setup'] }),
    });
    setNewProjectName('');
    setNewTaskTitle('');
    setAddingProject(null);
    load();
  };

  const statItems = [
    { n: now, label: 'Now', color: 'red', to: '/tasks' },
    { n: next, label: 'Next', color: 'amber', to: '/tasks' },
    { n: later, label: 'Later', color: 'blue', to: '/tasks' },
    { n: active.length, label: 'Total Active', color: 'green', to: '/tasks' },
    { n: bugCount, label: 'Bugs', color: 'red', to: '/tasks' },
    { n: bossCount, label: 'Boss Reqs', color: 'amber', to: '/tasks' },
    { n: delegatedCount, label: 'Delegated', color: 'purple', to: '/tasks' },
  ];

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">◎ Overview</h1>
        {version && <span className="version-badge">{version}</span>}
      </div>

      {/* Stats Grid */}
      <div className="overview-stats-grid">
        {statItems.map(s => (
          <div className="stat-tile stat-tile-interactive" key={s.label}
            onClick={() => navigate(s.to)} onKeyDown={e => e.key === 'Enter' && navigate(s.to)}
            role="button" tabIndex={0} aria-label={`${s.n} ${s.label}`}>
            <div className={`stat-num ${s.color}`}>{s.n}</div>
            <div className="stat-lbl">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Urgent — Top 5 Priority Items */}
      {active.length > 0 && (() => {
        const priRank = { Critical: 0, High: 1, Normal: 2, Low: 3 };
        const statusRank = { Now: 0, Next: 1, Later: 2 };
        const urgent = [...active]
          .sort((a, b) => (priRank[a.priority] ?? 9) - (priRank[b.priority] ?? 9) || (statusRank[a.status] ?? 9) - (statusRank[b.status] ?? 9))
          .slice(0, 5);
        return (
          <>
            <h2 className="overview-section-title" style={{ marginTop: 4 }}>🔥 Urgent</h2>
            <div className="urgent-table">
              <div className="urgent-header">
                <span className="urgent-col urgent-col-task">Task</span>
                <span className="urgent-col urgent-col-product">Product</span>
                <span className="urgent-col urgent-col-project">Project</span>
                <span className="urgent-col urgent-col-status">Status</span>
                <span className="urgent-col urgent-col-due">Due</span>
              </div>
              {urgent.map(t => (
                <div className="urgent-row overview-card overview-card-interactive" key={t.id}
                  onClick={() => navigate('/tasks')} role="button" tabIndex={0}>
                  <span className="urgent-col urgent-col-task">
                    <span className="urgent-task-id">{t.id}</span>
                    <span className="urgent-task-title">{t.task}</span>
                  </span>
                  <span className="urgent-col urgent-col-product">
                    {t.product && <span className="meta-chip product-chip">{t.product}</span>}
                  </span>
                  <span className="urgent-col urgent-col-project">
                    {t.project && <span className="meta-chip project-chip">{t.project}</span>}
                  </span>
                  <span className="urgent-col urgent-col-status">
                    <span className={`status-chip status-${t.status?.toLowerCase()}`}>{t.status}</span>
                  </span>
                  <span className="urgent-col urgent-col-due">{t.due || '—'}</span>
                </div>
              ))}
            </div>
          </>
        );
      })()}

      {/* Products & Projects — Collapsible */}
      <div className="overview-section-header" onClick={() => setShowProducts(p => !p)}
        role="button" tabIndex={0} style={{ cursor: 'pointer' }}>
        <h2 className="overview-section-title">
          <span className={`accordion-chevron ${showProducts ? 'open' : ''}`}>▸</span>{' '}
          Products & Projects
        </h2>
      </div>

      {showProducts && (<>

      {/* Add Product Form */}
      {addingProduct && (
        <div className="add-form overview-card" style={{ marginBottom: 8 }}>
          <input className="add-input" placeholder="Product name" value={newProductName}
            onChange={e => setNewProductName(e.target.value)} autoFocus
            onKeyDown={e => e.key === 'Enter' && handleAddProduct()} />
          <input className="add-input" placeholder="First task (optional)" value={newTaskTitle}
            onChange={e => setNewTaskTitle(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleAddProduct()} />
          <div className="add-form-actions">
            <button className="add-form-save" onClick={handleAddProduct}>Add to TaskMaster</button>
            <button className="add-form-cancel" onClick={() => { setAddingProduct(false); setNewProductName(''); setNewTaskTitle(''); }}>Cancel</button>
          </div>
        </div>
      )}

      <div className="accordion-list">
        {products.map(prod => {
          const prodTasks = active.filter(t => t.product === prod);
          const prodProjects = [...new Set(prodTasks.map(t => t.project).filter(Boolean))];
          const donePct = prodTasks.length ? Math.round(prodTasks.filter(t => t.status === 'Done').length / prodTasks.length * 100) : 0;
          const isOpen = expandedProducts[prod];

          return (
            <div className="accordion-item" key={prod}>
              <div className="accordion-header overview-card overview-card-interactive"
                onClick={() => toggleProduct(prod)} onKeyDown={e => e.key === 'Enter' && toggleProduct(prod)}
                role="button" tabIndex={0} aria-expanded={!!isOpen} aria-label={`${prod} — ${prodTasks.length} tasks`}>
                <span className={`accordion-chevron ${isOpen ? 'open' : ''}`}>▸</span>
                <span className="meta-chip product-chip">{prod}</span>
                <span className="overview-count">{prodTasks.length} tasks · {donePct}%</span>
                <div className="accordion-bar">
                  <div className="overview-bar-track" style={{ flex: 1 }}>
                    <div className="overview-bar-fill" style={{ width: `${donePct}%` }} />
                  </div>
                </div>
              </div>

              {isOpen && (
                <div className="accordion-body">
                  {/* Projects under this product */}
                  {prodProjects.map(prj => {
                    const prjTasks = prodTasks.filter(t => t.project === prj);
                    const prjDone = prjTasks.length ? Math.round(prjTasks.filter(t => t.status === 'Done').length / prjTasks.length * 100) : 0;
                    return (
                      <div className="project-row overview-card overview-card-interactive" key={prj}
                        onClick={() => navigate('/tasks')} role="button" tabIndex={0}>
                        <span className="meta-chip project-chip">{prj}</span>
                        <span className="overview-count">{prjTasks.length} tasks · {prjDone}%</span>
                        <div className="overview-bar-track" style={{ flex: 1, maxWidth: 120 }}>
                          <div className="overview-bar-fill" style={{ width: `${prjDone}%` }} />
                        </div>
                      </div>
                    );
                  })}

                  {/* Tasks without a project */}
                  {prodTasks.filter(t => !t.project).length > 0 && (
                    <div className="project-row overview-card" style={{ opacity: 0.7 }}>
                      <span className="overview-count">{prodTasks.filter(t => !t.project).length} unassigned tasks</span>
                    </div>
                  )}

                  {/* Add Project button */}
                  {addingProject === prod ? (
                    <div className="add-form project-row overview-card">
                      <input className="add-input" placeholder="Project name" value={newProjectName}
                        onChange={e => setNewProjectName(e.target.value)} autoFocus
                        onKeyDown={e => e.key === 'Enter' && handleAddProject(prod)} />
                      <input className="add-input" placeholder="First task (optional)" value={newTaskTitle}
                        onChange={e => setNewTaskTitle(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleAddProject(prod)} />
                      <div className="add-form-actions">
                        <button className="add-form-save" onClick={() => handleAddProject(prod)}>Add</button>
                        <button className="add-form-cancel" onClick={() => { setAddingProject(null); setNewProjectName(''); setNewTaskTitle(''); }}>✕</button>
                      </div>
                    </div>
                  ) : (
                    <button className="add-project-btn" onClick={(e) => { e.stopPropagation(); setAddingProject(prod); setAddingProduct(false); }}>
                      + Add Project to {prod}
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      </>)}

    </div>
  );
}
