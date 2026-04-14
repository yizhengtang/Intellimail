//ChatPage.tsx
//Dedicated AI chat interface — sends messages to the backend chat endpoint and renders the conversation history.

import { useState, useRef, useEffect } from 'react';
import type { ChatMessage } from '../types/ai';
import { sendChatMessage } from '../services/aiService';
import { useChat } from '../context/ChatContext';

//ChatPage maintains a history array of { role, content } objects.
//On send, the user message is appended immediately, then the AI response is appended on success.
//The message list scrolls to the bottom after each new message using a ref on the last element.
export default function ChatPage() {
  const { history, setHistory } = useChat();
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  //Scroll to the bottom whenever history updates — runs after every render where history changes.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMessage: ChatMessage = { role: 'user', content: text };
    //Append the user message first so it appears immediately in the UI.
    const updatedHistory = [...history, userMessage];
    setHistory(updatedHistory);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      //Pass history BEFORE the current message — the backend treats message and history separately.
      const data = await sendChatMessage(text, history);
      setHistory([...updatedHistory, { role: 'assistant', content: data.response }]);
    } catch {
      setError('Failed to get a response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  //Enter sends the message. Shift+Enter inserts a new line.
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#ffffff' }}>

      {/* Message history — fills remaining space, scrolls independently */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '32px 40px 16px' }}>

        {history.map((msg, i) => (
          <div
            key={i}
            style={{
              marginBottom: 28,
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            {msg.role === 'assistant' && (
              <div style={{ maxWidth: '72%' }}>
                {/* "Chat AI" label above AI messages */}
                <div style={{
                  fontSize: 11,
                  fontWeight: 700,
                  color: '#9ca3af',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  marginBottom: 8,
                }}>
                  Chat AI
                </div>
                <div style={{
                  fontSize: 14,
                  color: '#374151',
                  lineHeight: 1.75,
                  whiteSpace: 'pre-wrap',
                }}>
                  {msg.content}
                </div>
              </div>
            )}

            {msg.role === 'user' && (
              <div style={{
                maxWidth: '65%',
                padding: '12px 18px',
                borderRadius: 20,
                backgroundColor: '#111827',
                color: '#ffffff',
                fontSize: 14,
                lineHeight: 1.55,
                whiteSpace: 'pre-wrap',
              }}>
                {msg.content}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ marginBottom: 28, display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{ maxWidth: '72%' }}>
              <div style={{
                fontSize: 11,
                fontWeight: 700,
                color: '#9ca3af',
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                marginBottom: 8,
              }}>
                Chat AI
              </div>
              <div style={{ fontSize: 14, color: '#9ca3af', fontStyle: 'italic' }}>Thinking...</div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input area — pinned to the bottom */}
      <div style={{ padding: '12px 40px 28px', flexShrink: 0 }}>
        {error && <p style={{ color: '#dc2626', fontSize: 13, marginBottom: 10 }}>{error}</p>}

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          backgroundColor: '#ffffff',
          border: '1px solid #e5e7eb',
          borderRadius: 50,
          padding: '10px 10px 10px 22px',
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
        }}>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What's in your mind?"
            rows={1}
            style={{
              flex: 1,
              border: 'none',
              outline: 'none',
              resize: 'none',
              fontSize: 14,
              color: '#111827',
              backgroundColor: 'transparent',
              lineHeight: '22px',
              padding: 0,
              overflow: 'hidden',
            }}
          />

          {/* Blue circle send button */}
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            style={{
              width: 38,
              height: 38,
              borderRadius: '50%',
              backgroundColor: !input.trim() || loading ? '#d1d5db' : '#3b82f6',
              border: 'none',
              cursor: !input.trim() || loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              transition: 'background-color 150ms ease',
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" fill="white" stroke="none" />
            </svg>
          </button>
        </div>
      </div>

    </div>
  );
}
