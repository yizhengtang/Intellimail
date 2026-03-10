//EmailDetail.tsx
//Renders the full detail view of a single email — headers, body, attachment indicator, and read/unread toggle.

//I decided to rename it to different name because the component is also called EmailDetail.
import type { EmailDetail as EmailDetailType } from '../types/email';
import { formatDate } from '../utils/format';

interface EmailDetailProps {
  email: EmailDetailType;
  isRead: boolean;
  onToggleRead: () => void;
}

//This component receives the full EmailDetail object and renders it.
//The body is rendered as HTML or plain text depending on body_type.
//The read/unread toggle button calls onToggleRead which is handled by the page.
export default function EmailDetail({ email, isRead, onToggleRead }: EmailDetailProps) {
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
        <div dangerouslySetInnerHTML={{ __html: email.body }} />
      ) : (
        <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>{email.body}</pre>
      )}
    </div>
  );
}
