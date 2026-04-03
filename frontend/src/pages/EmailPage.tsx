//EmailPage.tsx
//This is responsible for displaying the full detail of a single email and its conversation thread.

import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import type { EmailDetail as EmailDetailType } from '../types/email';
import { useEmailDetail } from '../hooks/useEmailDetail';
import EmailDetail from '../components/EmailDetail';
import AiPanel from '../components/AiPanel';
import { formatDate } from '../utils/format';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';

//This page extracts the provider and id from the URL using useParams().
//It fetches the main email via useEmailDetail and the conversation thread separately.
//Thread messages are displayed below the main email with expand/collapse.
export default function EmailPage() {
  const { provider, id } = useParams<{ provider: string; id: string }>();

  const { email, loading, error } = useEmailDetail(provider || '', id || '');

  const [isRead, setIsRead] = useState(true);
  const [thread, setThread] = useState<EmailDetailType[]>([]);
  const [threadLoading, setThreadLoading] = useState(true);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  //Reply state — tracks whether the reply form is visible, the mode, body text, and sending status
  const [replyMode, setReplyMode] = useState<'reply' | 'reply-all' | null>(null);
  const [replyBody, setReplyBody] = useState('');
  const [replySending, setReplySending] = useState(false);
  const [replyError, setReplyError] = useState<string | null>(null);

  //Auto-mark as read when the email is opened and it is currently unread
  useEffect(() => {
    if (!email || !provider || !id) return;
    if (email.is_read) {
      setIsRead(true);
      return;
    }
    setIsRead(false);

    if (provider === 'gmail') {
      gmailService.modifyEmailLabels(id, undefined, ['UNREAD']).then(() => setIsRead(true)).catch(() => {});
    } else if (provider === 'outlook') {
      outlookService.markAsRead(id).then(() => setIsRead(true)).catch(() => {});
    }
  }, [email, provider, id]);

  //Toggle read/unread status
  const handleToggleRead = async () => {
    if (!provider || !id) return;

    try {
      if (isRead) {
        if (provider === 'gmail') {
          await gmailService.modifyEmailLabels(id, ['UNREAD']);
        } else if (provider === 'outlook') {
          await outlookService.markAsUnread(id);
        }
        setIsRead(false);
      } else {
        if (provider === 'gmail') {
          await gmailService.modifyEmailLabels(id, undefined, ['UNREAD']);
        } else if (provider === 'outlook') {
          await outlookService.markAsRead(id);
        }
        setIsRead(true);
      }
    } catch {
      //Toggle failed — state stays unchanged
    }
  };

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

  //Send reply or reply-all using the correct service based on provider
  const handleReplySend = async () => {
    if (!provider || !id || !replyMode) return;
    setReplySending(true);
    setReplyError(null);

    try {
      const payload = { body: replyBody };

      if (replyMode === 'reply') {
        if (provider === 'gmail') {
          await gmailService.replyEmail(id, payload);
        } else {
          await outlookService.replyEmail(id, payload);
        }
      } else {
        if (provider === 'gmail') {
          await gmailService.replyAllEmail(id, payload);
        } else {
          await outlookService.replyAllEmail(id, payload);
        }
      }

      setReplyMode(null);
      setReplyBody('');
      fetchThread();
    } catch (err) {
      setReplyError(err instanceof Error ? err.message : 'Failed to send reply');
    } finally {
      setReplySending(false);
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;
  if (!email) return <p>Email not found.</p>;

  //Filter out the current email from the thread so it is not shown twice
  const otherMessages = thread.filter(msg => msg.id !== id);

  return (
    <div>
      <EmailDetail
        email={email}
        isRead={isRead}
        onToggleRead={handleToggleRead}
        onReply={() => { setReplyMode('reply'); setReplyBody(''); setReplyError(null); }}
        onReplyAll={() => { setReplyMode('reply-all'); setReplyBody(''); setReplyError(null); }}
      />

      <AiPanel provider={provider || ''} messageId={id || ''} />

      {replyMode && (
        <div style={{ padding: '0 24px 24px' }}>
          <h4>{replyMode === 'reply' ? 'Reply' : 'Reply All'} to {email.from_name || email.from}</h4>

          {replyError && <p style={{ color: 'red' }}>{replyError}</p>}

          <textarea
            placeholder="Write your reply..."
            value={replyBody}
            onChange={e => setReplyBody(e.target.value)}
            rows={6}
            style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box', resize: 'vertical', marginBottom: 8 }}
          />

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={handleReplySend}
              disabled={replySending || !replyBody.trim()}
              style={{
                padding: '8px 16px',
                cursor: replySending ? 'not-allowed' : 'pointer',
                backgroundColor: '#2185d0',
                color: 'white',
                border: 'none',
                borderRadius: 4,
              }}
            >
              {replySending ? 'Sending...' : 'Send'}
            </button>
            <button
              onClick={() => { setReplyMode(null); setReplyBody(''); setReplyError(null); }}
              style={{
                padding: '8px 16px',
                cursor: 'pointer',
                border: '1px solid #ccc',
                borderRadius: 4,
                backgroundColor: 'transparent',
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

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
