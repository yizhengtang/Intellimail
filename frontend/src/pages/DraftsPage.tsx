//DraftsPage.tsx
//Displays the list of draft emails with send and delete actions.

import { useState } from 'react';
import { useDrafts } from '../hooks/useDrafts';
import { formatDate } from '../utils/format';

//This page uses the useDrafts hook to fetch drafts from the active provider.
//Each draft row shows the recipient, subject, snippet, and date.
//Send and Delete buttons let the user act on each draft.
export default function DraftsPage() {
  const { drafts, loading, error, sendDraft, deleteDraft } = useDrafts();
  const [actionError, setActionError] = useState<string | null>(null);

  const handleSend = async (draftId: string, draftProvider: string) => {
    try {
      setActionError(null);
      await sendDraft(draftId, draftProvider);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to send draft');
    }
  };

  const handleDelete = async (draftId: string, draftProvider: string) => {
    try {
      setActionError(null);
      await deleteDraft(draftId, draftProvider);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to delete draft');
    }
  };

  if (error) return <p style={{ padding: 24 }}>{error}</p>;
  if (loading) return <p style={{ padding: 24 }}>Loading drafts...</p>;

  return (
    <div>
      <h2 style={{ padding: '24px 24px 0' }}>Drafts</h2>

      {actionError && <p style={{ color: 'red', padding: '0 24px' }}>{actionError}</p>}

      {drafts.length === 0 && <p style={{ padding: 24 }}>No drafts.</p>}

      {drafts.map(draft => (
        <div
          key={draft.id}
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 24px',
            borderBottom: '1px solid #e0e0e0',
          }}
        >
          <div style={{ flex: 1, minWidth: 0 }}>
            <div>
              <strong>To:</strong> {draft.to || '(no recipient)'}
              {draft.provider && (
                <span style={{ color: '#888', marginLeft: 8, fontSize: '0.85em' }}>
                  ({draft.provider})
                </span>
              )}
            </div>
            <div style={{ fontWeight: 'bold' }}>{draft.subject || '(no subject)'}</div>
            <div style={{ color: '#888', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {draft.snippet || ''}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginLeft: 16 }}>
            <span style={{ color: '#888', whiteSpace: 'nowrap' }}>
              {draft.date ? formatDate(draft.date) : ''}
            </span>
            <button
              onClick={() => handleSend(draft.id, draft.provider || '')}
              style={{
                padding: '4px 12px',
                cursor: 'pointer',
                backgroundColor: '#2185d0',
                color: 'white',
                border: 'none',
                borderRadius: 4,
              }}
            >
              Send
            </button>
            <button
              onClick={() => handleDelete(draft.id, draft.provider || '')}
              style={{
                padding: '4px 12px',
                cursor: 'pointer',
                backgroundColor: 'transparent',
                border: '1px solid #ccc',
                borderRadius: 4,
              }}
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
