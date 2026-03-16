import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function FilesPage() {
  const [entries, setEntries] = useState([]);
  const [currentDir, setCurrentDir] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`/api/files?dir=${encodeURIComponent(currentDir)}`)
      .then(r => r.json())
      .then(d => setEntries(d.entries || []));
  }, [currentDir]);

  const handleClick = (entry) => {
    if (entry.isDir) {
      setCurrentDir(entry.path);
    } else {
      navigate(`/files/${entry.path}`);
    }
  };

  const goUp = () => {
    const parts = currentDir.split('/').filter(Boolean);
    parts.pop();
    setCurrentDir(parts.join('/'));
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">📁 File Browser</h1>
        <span className="item-count">/{currentDir || 'root'}</span>
      </div>

      {currentDir && (
        <button className="back-btn" onClick={goUp}>← Back</button>
      )}

      <div className="file-list">
        {entries.map(entry => (
          <div
            key={entry.path}
            className="file-entry"
            onClick={() => handleClick(entry)}
          >
            <span className="file-icon">{entry.isDir ? '📁' : '📄'}</span>
            <span className="file-name">{entry.name}</span>
          </div>
        ))}
        {entries.length === 0 && (
          <div className="empty-msg">This directory is empty.</div>
        )}
      </div>
    </div>
  );
}
