//EmailList.tsx
//Renders emails as a table with column headers: Sender, Message, Channel, Time.

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
    <div style={{ backgroundColor: '#ffffff', borderRadius: 12, border: '1px solid #e5e7eb', overflow: 'hidden' }}>

      {/* Column header row */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '10px 16px',
        borderBottom: '1px solid #e5e7eb',
        backgroundColor: '#f9fafb',
      }}>
        {selectable && (
          <input
            type="checkbox"
            checked={selectedIds.size === emails.length && emails.length > 0}
            onChange={toggleAll}
            style={{ cursor: 'pointer', marginRight: 12, flexShrink: 0 }}
          />
        )}
        <div style={{ width: 220, fontSize: 12, fontWeight: 600, color: '#6b7280', flexShrink: 0 }}>Sender</div>
        <div style={{ flex: 1, fontSize: 12, fontWeight: 600, color: '#6b7280' }}>Message</div>
        <div style={{ width: 110, fontSize: 12, fontWeight: 600, color: '#6b7280', flexShrink: 0 }}>Channel</div>
        <div style={{ width: 80, fontSize: 12, fontWeight: 600, color: '#6b7280', textAlign: 'right', flexShrink: 0 }}>Time</div>
      </div>

      {/* Email rows */}
      {emails.map(email => (
        <EmailRow
          key={email.id}
          email={email}
          selectable={selectable}
          selected={selectedIds.has(email.id)}
          onSelect={toggleSelect}
        />
      ))}

      {/* Batch action bar — shown at the bottom when items are selected */}
      {selectable && selectedIds.size > 0 && onBatchAction && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '10px 16px',
          borderTop: '1px solid #e5e7eb',
          backgroundColor: '#f9fafb',
        }}>
          <span style={{ fontSize: 13, color: '#6b7280' }}>{selectedIds.size} selected</span>
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
        </div>
      )}
    </div>
  );
}
