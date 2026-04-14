//EmailDetail.tsx
//Renders the full detail view of a single email — headers, body, attachment indicator, and read/unread toggle.

//I decided to rename it to different name because the component is also called EmailDetail.
import type { EmailDetail as EmailDetailType } from '../types/email';
import { formatDate } from '../utils/format';

interface EmailDetailProps {
  email: EmailDetailType;
  isRead: boolean;
  onToggleRead: () => void;
  onReply: () => void;
  onReplyAll: () => void;
}

//This component receives the full EmailDetail object and renders it.
//The body is rendered as HTML or plain text depending on body_type.
//The read/unread toggle button calls onToggleRead which is handled by the page.
//Reply and Reply All buttons call their callbacks — the page handles the logic.
export default function EmailDetail({ email, isRead, onToggleRead, onReply, onReplyAll }: EmailDetailProps) {
  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <h2 style={{ margin: 0 }}>{email.subject}</h2>
        <button
          onClick={onToggleRead}
          style={{
            padding: '6px 12px',
            cursor: 'pointer',
            border: '1px solid #ccc',
            borderRadius: 4,
            backgroundColor: 'transparent',
          }}
        >
          {isRead ? 'Mark as unread' : 'Mark as read'}
        </button>
      </div>

      <div style={{ color: '#555', marginBottom: 16 }}>
        <div><strong>From:</strong> {email.from_name ? `${email.from_name} <${email.from}>` : email.from}</div>
        <div><strong>To:</strong> {email.to}</div>
        {email.cc && <div><strong>Cc:</strong> {email.cc}</div>}
        <div><strong>Date:</strong> {formatDate(email.date)}</div>
        {email.has_attachments && <div style={{ marginTop: 4, color: '#888' }}>📎 This email has attachments</div>}
      </div>

      <hr style={{ border: 'none', borderTop: '1px solid #e0e0e0', marginBottom: 16 }} />

      {email.body_type === 'html' || email.body_type === 'HTML' ? (
        //Sandboxed iframe isolates the email HTML from the app.
        //sandbox without allow-scripts means no JavaScript in the email can execute.
        //allow-same-origin lets us read scrollHeight to auto-fit the iframe height.
        <iframe
          srcDoc={email.body}
          title="Email content"
          sandbox="allow-same-origin"
          style={{ width: '100%', border: 'none', minHeight: 300, display: 'block' }}
          onLoad={e => {
            try {
              const doc = e.currentTarget.contentDocument;
              if (doc?.body) {
                e.currentTarget.style.height = `${doc.body.scrollHeight + 32}px`;
              }
            } catch { /* sandbox may restrict access on some browsers */ }
          }}
        />
      ) : (
        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{email.body}</pre>
      )}

      <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
        <button
          onClick={onReply}
          style={{
            padding: '8px 16px',
            cursor: 'pointer',
            border: '1px solid #ccc',
            borderRadius: 4,
            backgroundColor: '#2185d0',
            color: 'white',
          }}
        >
          Reply
        </button>
        <button
          onClick={onReplyAll}
          style={{
            padding: '8px 16px',
            cursor: 'pointer',
            border: '1px solid #ccc',
            borderRadius: 4,
            backgroundColor: 'transparent',
          }}
        >
          Reply All
        </button>
      </div>
    </div>
  );
}
