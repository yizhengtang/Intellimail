//EmailPage.tsx
//This is responsible for displaying the full detail of a single email and its conversation thread.

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import type { EmailDetail as EmailDetailType } from '../types/email';
import { useEmailDetail } from '../hooks/useEmailDetail';
import EmailDetail from '../components/EmailDetail';
import { formatDate } from '../utils/format';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';

//This page extracts the provider and id from the URL using useParams().
//It fetches the main email via useEmailDetail and the conversation thread separately.
//Thread messages are displayed below the main email with expand/collapse.
export default function EmailPage() {
  const { provider, id } = useParams<{ provider: string; id: string }>();

  const { email, loading, error } = useEmailDetail(provider || '', id || '');

  const [thread, setThread] = useState<EmailDetailType[]>([]);
  const [threadLoading, setThreadLoading] = useState(true);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  //Fetch the conversation thread for this email
  const fetchThread = useCallback(async () => {
    if (!provider || !id) return;
    setThreadLoading(true);

    try {
      if (provider === 'gmail') {
        const data = await gmailService.getConversations(id);
        setThread(data);
      } else if (provider === 'outlook') {
        const data = await outlookService.getConversations(id);
        setThread(data);
      }
    } catch {
      setThread([]);
    } finally {
      setThreadLoading(false);
    }
  }, [provider, id]);

  useEffect(() => {
    fetchThread();
  }, [fetchThread]);

  //Toggle expand/collapse for a thread message
  const toggleMessage = (messageId: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;
  if (!email) return <p>Email not found.</p>;

  //Filter out the current email from the thread so it is not shown twice
  const otherMessages = thread.filter(msg => msg.id !== id);

  return (
    <div>
      <EmailDetail email={email} />

      {otherMessages.length > 0 && (
        <div style={{ padding: '0 24px 24px' }}>
          <h4 style={{ marginBottom: 8 }}>Conversation ({otherMessages.length} other messages)</h4>

          {otherMessages.map(msg => (
            <div
              key={msg.id}
              style={{
                border: '1px solid #e0e0e0',
                borderRadius: 4,
                marginBottom: 8,
              }}
            >
              <div
                onClick={() => toggleMessage(msg.id)}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '10px 12px',
                  cursor: 'pointer',
                  backgroundColor: '#f9f9f9',
                }}
              >
                <div>
                  <strong>{msg.from_name || msg.from}</strong>
                  <span style={{ color: '#888', marginLeft: 8 }}>{msg.subject}</span>
                </div>
                <div style={{ color: '#888', whiteSpace: 'nowrap' }}>
                  {formatDate(msg.date)}
                </div>
              </div>

              {expandedIds.has(msg.id) && (
                <div style={{ padding: '12px', borderTop: '1px solid #e0e0e0' }}>
                  <div style={{ color: '#555', marginBottom: 8 }}>
                    <div><strong>From:</strong> {msg.from}</div>
                    <div><strong>To:</strong> {msg.to}</div>
                    {msg.cc && <div><strong>Cc:</strong> {msg.cc}</div>}
                  </div>
                  {msg.body_type === 'html' || msg.body_type === 'HTML' ? (
                    <div dangerouslySetInnerHTML={{ __html: msg.body }} />
                  ) : (
                    <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{msg.body}</pre>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {threadLoading && <p style={{ padding: '0 24px' }}>Loading conversation...</p>}
    </div>
  );
}
