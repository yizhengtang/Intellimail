//TeamsChatPage.tsx
//Single Teams chat view — shows the full message thread and a send box at the bottom.

import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom';
import type { TeamsMessage } from '../types/teams';
import { getChatMessages, sendChatMessage } from '../services/teamsService';
import TeamsChatView from '../components/TeamsChatView';
import TeamsAiPanel from '../components/TeamsAiPanel';

//TeamsChatPage reads the chatId from the URL, fetches all messages, and renders the thread.
//A send box at the bottom lets the user send a new message to the chat.
//The message list re-fetches after a successful send so the new message appears immediately.
export default function TeamsChatPage() {
  const { chatId } = useParams<{ chatId: string }>();
  const [messages, setMessages] = useState<TeamsMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchMessages = useCallback(async () => {
    if (!chatId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getChatMessages(chatId);
      setMessages(data);
    } catch {
      setError('Failed to load messages.');
    } finally {
      setLoading(false);
    }
  }, [chatId]);

  useEffect(() => {
    fetchMessages();
  }, [fetchMessages]);

  //Scroll to the bottom whenever messages update.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || !chatId || sending) return;

    setSending(true);
    setSendError(null);
    try {
      await sendChatMessage(chatId, text);
      setInput('');
      //Re-fetch so the sent message appears in the thread.
      await fetchMessages();
    } catch {
      setSendError('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  //Enter sends, Shift+Enter inserts a new line.
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (loading) return <p style={{ padding: 24 }}>Loading messages...</p>;
  if (error) return <p style={{ padding: 24, color: '#cc0000' }}>{error}</p>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 57px)' }}>

      {/* Scrollable message thread */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        <TeamsChatView messages={messages} />
        <div ref={bottomRef} />
      </div>

      {/* AI panel */}
      <TeamsAiPanel chatId={chatId || ''} onReplyDraft={setInput} />

      {/* Send box */}
      <div style={{ borderTop: '1px solid #e0e0e0', padding: 16 }}>
        {sendError && <p style={{ color: '#cc0000', fontSize: 13, marginBottom: 8 }}>{sendError}</p>}
        <div style={{ display: 'flex', gap: 8 }}>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
            rows={2}
            style={{
              flex: 1,
              padding: '10px 12px',
              boxSizing: 'border-box',
              resize: 'none',
              border: '1px solid #ccc',
              borderRadius: 4,
              fontSize: 14,
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            style={{
              padding: '0 20px',
              cursor: !input.trim() || sending ? 'not-allowed' : 'pointer',
              backgroundColor: '#6264a7',
              color: 'white',
              border: 'none',
              borderRadius: 4,
              fontSize: 14,
              opacity: !input.trim() || sending ? 0.6 : 1,
            }}
          >
            {sending ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>

    </div>
  );
}
