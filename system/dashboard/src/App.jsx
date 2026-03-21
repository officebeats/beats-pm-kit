import { Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import TasksPage from './pages/TasksPage';
import ArchivePage from './pages/ArchivePage';
import TrackerPage from './pages/TrackerPage';
import SettingsPage from './pages/SettingsPage';
import FilesPage from './pages/FilesPage';
import FileViewPage from './pages/FileViewPage';
import MeetingsPage from './pages/MeetingsPage';
import PeoplePage from './pages/PeoplePage';
import ProductsPage from './pages/ProductsPage';

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      {/* Mobile hamburger */}
      <button className="mobile-hamburger" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Menu">
        {sidebarOpen ? '✕' : '☰'}
      </button>

      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Overlay for mobile */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

      <div className="main-content" onClick={() => sidebarOpen && setSidebarOpen(false)}>
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/archive" element={<ArchivePage />} />
          <Route path="/meetings" element={<MeetingsPage />} />
          <Route path="/people" element={<PeoplePage />} />
          <Route path="/products-hub" element={<ProductsPage />} />
          <Route path="/projects" element={<TrackerPage file="PROJECT_TRACKER.md" title="📦 Projects" />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/files" element={<FilesPage />} />
          <Route path="/files/*" element={<FileViewPage />} />
        </Routes>
      </div>
    </div>
  );
}
