import { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

// Simple fuzzy match — checks if all chars of query appear in order in target
function fuzzyMatch(query, target) {
  const q = query.toLowerCase();
  const t = target.toLowerCase();
  let qi = 0;
  for (let ti = 0; ti < t.length && qi < q.length; ti++) {
    if (t[ti] === q[qi]) qi++;
  }
  return qi === q.length;
}

// Highlight fuzzy matched characters
function FuzzyHighlight({ text, query }) {
  if (!query) return <>{text}</>;
  const q = query.toLowerCase();
  const chars = text.split('');
  const result = [];
  let qi = 0;
  for (let i = 0; i < chars.length; i++) {
    if (qi < q.length && chars[i].toLowerCase() === q[qi]) {
      result.push(<mark key={i} className="fuzzy-hl">{chars[i]}</mark>);
      qi++;
    } else {
      result.push(chars[i]);
    }
  }
  return <>{result}</>;
}

const CATEGORY_ICONS = {
  'General': '📄', '1 On 1s': '👥', 'Customer Calls': '📞',
  'Daily Briefs': '☀️', 'Standups': '🧍', 'Transcripts': '🎙️',
  'Summaries': '📋', 'Notes': '📝', 'Weekly Digests': '📆',
  'Monthly Digests': '📊', 'Stakeholder Reviews': '🏛️', 'Archive': '🗄️',
};

export default function MeetingsPage() {
  const [notes, setNotes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [catFilter, setCatFilter] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const navigate = useNavigate();

  const load = useCallback(async () => {
    try {
      const res = await fetch('/api/meetings');
      const data = await res.json();
      setNotes(data.notes || []);
      setCategories(data.categories || []);
    } catch { setNotes([]); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = useMemo(() => {
    return notes.filter(n => {
      // Fuzzy text search across title, preview, category, filename
      if (search) {
        const haystack = `${n.title} ${n.preview} ${n.category} ${n.filename}`;
        if (!fuzzyMatch(search, haystack)) return false;
      }
      // Category filter
      if (catFilter !== 'all' && n.category !== catFilter) return false;
      // Date range
      const d = n.date || n.modified?.slice(0, 10);
      if (dateFrom && d && d < dateFrom) return false;
      if (dateTo && d && d > dateTo) return false;
      return true;
    });
  }, [notes, search, catFilter, dateFrom, dateTo]);

  const clearFilters = () => { setSearch(''); setCatFilter('all'); setDateFrom(''); setDateTo(''); };
  const hasFilters = search || catFilter !== 'all' || dateFrom || dateTo;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title">📝 Meeting Notes</h1>
        <span className="item-count">{filtered.length} of {notes.length} notes</span>
      </div>

      {/* Search + Filters Bar */}
      <div className="meetings-search-bar">
        <div className="search-input-wrap">
          <span className="search-icon">⌕</span>
          <input
            className="search-input"
            type="text"
            placeholder="Fuzzy search notes..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {search && <button className="search-clear" onClick={() => setSearch('')}>×</button>}
        </div>

        <div className="filter-row">
          <select className="filter-select" value={catFilter} onChange={e => setCatFilter(e.target.value)}>
            <option value="all">All Categories</option>
            {categories.map(c => <option key={c} value={c}>{CATEGORY_ICONS[c] || '📁'} {c}</option>)}
          </select>

          <div className="date-range">
            <label className="date-label">From</label>
            <input type="date" className="date-input" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
            <label className="date-label">To</label>
            <input type="date" className="date-input" value={dateTo} onChange={e => setDateTo(e.target.value)} />
          </div>

          {hasFilters && (
            <button className="filter-clear-btn" onClick={clearFilters}>Clear All</button>
          )}
        </div>
      </div>

      {/* Results */}
      {filtered.length === 0 ? (
        <div className="empty-msg" style={{ padding: '40px 0', textAlign: 'center' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>📝</div>
          {notes.length === 0 ? (
            <>
              <div>No meeting notes yet.</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                Use <code>/transcript</code> or <code>/meet</code> in Antigravity to process a meeting.
              </div>
            </>
          ) : (
            <div>No notes match your search.</div>
          )}
        </div>
      ) : (
        <div className="meeting-notes-list">
          {filtered.map((note, i) => (
            <div className="meeting-note-card" key={i}
              onClick={() => navigate(`/files/${note.path}`)}
              onKeyDown={e => e.key === 'Enter' && navigate(`/files/${note.path}`)}
              role="button" tabIndex={0}>
              <div className="note-card-left">
                <span className="note-category-icon">{CATEGORY_ICONS[note.category] || '📁'}</span>
              </div>
              <div className="note-card-body">
                <div className="note-card-header">
                  <span className="note-title">
                    <FuzzyHighlight text={note.title} query={search} />
                  </span>
                  <span className="note-category-chip">{note.category}</span>
                </div>
                {note.preview && (
                  <div className="note-preview">{note.preview}</div>
                )}
                <div className="note-meta">
                  {note.date && <span className="note-date">{note.date}</span>}
                  {!note.date && note.modified && <span className="note-date">{note.modified.slice(0, 10)}</span>}
                  <span className="note-filename">{note.filename}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
