//TeamsPage.tsx
//Teams chat list page — shows all chats the user is part of.
//Each row shows the chat topic, last sender, last message preview, and timestamp.

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { TeamsChat } from '../types/teams';
import { listChats } from '../services/teamsService';
import { formatDate, truncate } from '../utils/format';

//TeamsPage fetches the list of chats on mount and renders them as clickable rows.
//Clicking a row navigates to /teams/:chatId where the full conversation is shown.
export default function TeamsPage() {
  const [chats, setChats] = useState<TeamsChat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchChats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listChats(20);
      setChats(data);
    } catch {
      setError('Failed to load chats. Make sure you are signed in to Teams.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  if (loading) return <p style={{ padding: 24 }}>Loading chats...</p>;
  if (error) return <p style={{ padding: 24, color: '#cc0000' }}>{error}</p>;
  if (chats.length === 0) return <p style={{ padding: 24, color: '#888' }}>No chats found.</p>;

  return (
    <div>
      <div style={{ padding: '16px 24px', borderBottom: '1px solid #e0e0e0' }}>
        <h2 style={{ margin: 0, fontSize: 18 }}>Teams Chats</h2>
      </div>

      <div>
        {chats.map(chat => (
          <div
            key={chat.id}
            onClick={() => navigate(`/teams/${chat.id}`)}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              padding: '14px 24px',
              borderBottom: '1px solid #f0f0f0',
              cursor: 'pointer',
            }}
            onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#f9f9f9')}
            onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
          >
            <div style={{ flex: 1, minWidth: 0 }}>

              <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 2 }}>
                {chat.topic}
              </div>

              <div style={{ fontSize: 13, color: '#555' }}>
                <span style={{ fontWeight: 500 }}>{chat.last_sender}: </span>
                <span style={{ color: '#888' }}>{truncate(chat.last_message, 80)}</span>
              </div>

            </div>

            <div style={{ fontSize: 12, color: '#aaa', whiteSpace: 'nowrap', marginLeft: 16, paddingTop: 2 }}>
              {chat.last_message_time ? formatDate(chat.last_message_time) : ''}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
