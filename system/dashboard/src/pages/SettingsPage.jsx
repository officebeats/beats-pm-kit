import { useState, useEffect } from 'react';

export default function SettingsPage() {
  const [content, setContent] = useState('');

  useEffect(() => {
    fetch('/api/settings').then(r => r.json()).then(d => setContent(d.content));
  }, []);

  // Simple markdown-to-sections renderer
  const sections = content.split(/\n(?=## )/).filter(Boolean);

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">⚙ Settings</h1>
        <span className="item-count">SETTINGS.md (readonly)</span>
      </div>
      <div className="settings-grid">
        {sections.map((sec, i) => {
          const lines = sec.split('\n');
          const title = (lines[0] || '').replace(/^#+\s*/, '');
          const body = lines.slice(1).join('\n').trim();
          return (
            <div className="settings-card" key={i}>
              <h3 className="settings-card-title">{title}</h3>
              <pre className="settings-card-body">{body}</pre>
            </div>
          );
        })}
      </div>
    </div>
  );
}
