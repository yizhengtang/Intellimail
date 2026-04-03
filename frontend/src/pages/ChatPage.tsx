//ChatPage.tsx
//Dedicated AI chat interface — sends messages to the backend chat endpoint and renders the conversation history.

import { useState, useRef, useEffect } from 'react';
import type { ChatMessage } from '../types/ai';
import { sendChatMessage } from '../services/aiService';

//ChatPage maintains a history array of { role, content } objects.
//On send, the user message is appended immediately, then the AI response is appended on success.
//The message list scrolls to the bottom after each new message using a ref on the last element.
export default function ChatPage() {
  const [history, setHistory] = useState<ChatMessage[]>([]);
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
    <div style={{ padding: 24 }}>
      <h2 style={{ marginBottom: 16 }}>AI Chat</h2>

      <div
        style={{
          height: 'calc(100vh - 280px)',
          overflowY: 'auto',
          border: '1px solid #e0e0e0',
          borderRadius: 4,
          padding: 16,
          marginBottom: 16,
          backgroundColor: '#fafafa',
        }}
      >
        {history.length === 0 && (
          <p style={{ color: '#aaa', fontSize: 14 }}>
            Ask me anything about your inbox. Try: "Summarise my emails" or "Find emails about the project deadline".
          </p>
        )}

        {history.map((msg, i) => (
          <div
            key={i}
            style={{
              marginBottom: 12,
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div
              style={{
                maxWidth: '75%',
                padding: '10px 14px',
                borderRadius: 8,
                backgroundColor: msg.role === 'user' ? '#2185d0' : '#e8e8e8',
                color: msg.role === 'user' ? 'white' : '#333',
                fontSize: 14,
                whiteSpace: 'pre-wrap',
              }}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 12 }}>
            <div
              style={{
                padding: '10px 14px',
                borderRadius: 8,
                backgroundColor: '#e8e8e8',
                color: '#888',
                fontSize: 14,
              }}
            >
              Thinking...
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {error && <p style={{ color: '#cc0000', fontSize: 13, marginBottom: 8 }}>{error}</p>}

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
          disabled={!input.trim() || loading}
          style={{
            padding: '0 20px',
            cursor: !input.trim() || loading ? 'not-allowed' : 'pointer',
            backgroundColor: '#2185d0',
            color: 'white',
            border: 'none',
            borderRadius: 4,
            fontSize: 14,
            opacity: !input.trim() || loading ? 0.6 : 1,
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
