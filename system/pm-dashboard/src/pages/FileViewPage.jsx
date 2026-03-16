import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

export default function FileViewPage() {
  const [content, setContent] = useState('');
  const [error, setError] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const filePath = location.pathname.replace('/files/', '');

  useEffect(() => {
    fetch(`/api/file?path=${encodeURIComponent(filePath)}`)
      .then(r => {
        if (!r.ok) throw new Error('Not found');
        return r.json();
      })
      .then(d => setContent(d.content))
      .catch(() => setError(true));
  }, [filePath]);

  if (error) {
    return (
      <div className="page">
        <div className="page-header">
          <h1 className="page-title">File Not Found</h1>
        </div>
        <button className="back-btn" onClick={() => navigate('/files')}>← Back to Files</button>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">📄 {filePath.split('/').pop()}</h1>
        <span className="item-count">{filePath}</span>
      </div>
      <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>
      <div className="markdown-preview">
        <pre className="file-content">{content}</pre>
      </div>
    </div>
  );
}
