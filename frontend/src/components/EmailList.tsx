//EmailList.tsx
//Renders a list of EmailRow cards with a section header and batch selection bar.
//The grey container background is set by the parent page (InboxPage).

import { useState } from 'react';
import type { EmailSummary } from '../types/email';
import EmailRow from './EmailRow';

interface EmailListProps {
  emails: EmailSummary[];
  loading: boolean;
  selectable?: boolean;
  onBatchAction?: (selectedIds: string[]) => void;
  batchActionLabel?: string;
}

export default function EmailList({ emails, loading, selectable, onBatchAction, batchActionLabel }: EmailListProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleAll = () => {
    setSelectedIds(
      selectedIds.size === emails.length ? new Set() : new Set(emails.map(e => e.id))
    );
  };

  const handleBatchAction = () => {
    if (onBatchAction && selectedIds.size > 0) {
      onBatchAction([...selectedIds]);
      setSelectedIds(new Set());
    }
  };

  if (loading) {
    return <p style={{ padding: '24px 0', color: '#9ca3af', fontSize: 14 }}>Loading...</p>;
  }

  if (emails.length === 0) {
    return <p style={{ padding: '24px 0', color: '#9ca3af', fontSize: 14 }}>No emails found.</p>;
  }

  return (
    <div>
      {/* Batch selection bar — only shown when selectable is true */}
      {selectable && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '10px 4px',
          marginBottom: 8,
        }}>
          <input
            type="checkbox"
            checked={selectedIds.size === emails.length && emails.length > 0}
            onChange={toggleAll}
            style={{ cursor: 'pointer' }}
          />
          <span style={{ fontSize: 13, color: '#6b7280' }}>
            {selectedIds.size > 0 ? `${selectedIds.size} selected` : 'Select all'}
          </span>
          {selectedIds.size > 0 && onBatchAction && (
            <button
              onClick={handleBatchAction}
              style={{
                padding: '4px 14px',
                cursor: 'pointer',
                border: '1px solid #d1d5db',
                borderRadius: 6,
                backgroundColor: '#ffffff',
                fontSize: 13,
                color: '#374151',
              }}
            >
              {batchActionLabel || 'Action'}
            </button>
          )}
        </div>
      )}

      {emails.map(email => (
        <EmailRow
          key={email.id}
          email={email}
          selectable={selectable}
          selected={selectedIds.has(email.id)}
          onSelect={toggleSelect}
        />
      ))}
    </div>
  );
}
