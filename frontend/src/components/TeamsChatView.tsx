//TeamsChatView.tsx
//Renders a scrollable list of Teams chat messages as chat bubbles.
//Each message shows the sender name, content, and timestamp.

import type { TeamsMessage } from '../types/teams';
import { formatDate } from '../utils/format';

interface TeamsChatViewProps {
  messages: TeamsMessage[];
}

//Messages are displayed oldest-first (the API returns newest-first, so we reverse).
//Each bubble shows the sender name above the content and the timestamp below.
//HTML messages use dangerouslySetInnerHTML — Teams can send HTML-formatted content.
export default function TeamsChatView({ messages }: TeamsChatViewProps) {
  //API returns newest-first — reverse so the conversation reads top-to-bottom.
  const ordered = [...messages].reverse();

  if (ordered.length === 0) {
    return <p style={{ padding: 24, color: '#888' }}>No messages in this chat.</p>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, padding: 24 }}>
      {ordered.map(msg => (
        <div key={msg.id} style={{ display: 'flex', flexDirection: 'column', maxWidth: '75%' }}>

          <span style={{ fontSize: 12, fontWeight: 600, color: '#555', marginBottom: 2 }}>
            {msg.sender_name}
          </span>

          <div
            style={{
              padding: '10px 14px',
              borderRadius: 8,
              backgroundColor: '#f0f0f0',
              fontSize: 14,
              color: '#333',
              wordBreak: 'break-word',
            }}
          >
            {msg.content_type === 'html' ? (
              <div dangerouslySetInnerHTML={{ __html: msg.content }} />
            ) : (
              <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</p>
            )}
          </div>

          <span style={{ fontSize: 11, color: '#aaa', marginTop: 2 }}>
            {formatDate(msg.created_at)}
          </span>

        </div>
      ))}
    </div>
  );
}
