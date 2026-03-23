//EmailList.tsx
//Renders a list of EmailRow components. Handles loading, empty states, and batch selection.

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

//This component receives the email array and loading flag from the page.
//It does not fetch data — it only renders what it is given.
//When selectable is true, checkboxes appear and a batch action bar shows at the top.
export default function EmailList({ emails, loading, selectable, onBatchAction, batchActionLabel }: EmailListProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  //Toggle a single email's selection
  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  //Select all or deselect all
  const toggleAll = () => {
    if (selectedIds.size === emails.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(emails.map(e => e.id)));
    }
  };

  const handleBatchAction = () => {
    if (onBatchAction && selectedIds.size > 0) {
      onBatchAction([...selectedIds]);
      setSelectedIds(new Set());
    }
  };

  if (loading) return <p>Loading...</p>;
  if (emails.length === 0) return <p>No emails found.</p>;

  return (
    <div>
      {selectable && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '8px 12px',
          borderBottom: '1px solid #e0e0e0',
          backgroundColor: '#f9f9f9',
        }}>
          <input
            type="checkbox"
            checked={selectedIds.size === emails.length && emails.length > 0}
            onChange={toggleAll}
            style={{ cursor: 'pointer' }}
          />
          <span style={{ fontSize: 14, color: '#555' }}>
            {selectedIds.size > 0 ? `${selectedIds.size} selected` : 'Select all'}
          </span>
          {selectedIds.size > 0 && onBatchAction && (
            <button
              onClick={handleBatchAction}
              style={{
                padding: '4px 12px',
                cursor: 'pointer',
                border: '1px solid #ccc',
                borderRadius: 4,
                backgroundColor: 'transparent',
                fontSize: 14,
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
