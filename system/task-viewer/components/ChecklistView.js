'use client';

import { PriorityBadge, StatusDot } from './UIComponents';

export default function ChecklistView({ items, title }) {
  if (!items || items.length === 0) {
    return <p style={{ color: '#55556a', padding: '20px 0' }}>No items found.</p>;
  }

  let lastSection = '';
  return (
    <div className="checklist-view">
      {title && <h2 className="page-title">{title}</h2>}
      <div className="item-list">
        {items.map((item, i) => {
          let sectionEl = null;
          if (item.section && item.section !== lastSection) {
            lastSection = item.section;
            sectionEl = <div className="section-divider" key={`s-${i}`}>{item.section}</div>;
          }
          return (
            <div key={i}>
              {sectionEl}
              <div className={`item-row ${item.status}`}>
                <StatusDot status={item.status} />
                <span className="item-text">{item.text}</span>
                <PriorityBadge priority={item.priority} />
                {item.tags?.length > 0 && (
                  <div className="item-tags">
                    {item.tags.map(t => <span className="item-tag" key={t}>{t}</span>)}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
