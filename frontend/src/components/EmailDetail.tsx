//EmailDetail.tsx
//Renders the full detail view of a single email — headers, body, and attachment indicator.

//I decided to rename it to different name because the component is also called EmailDetail.
import type { EmailDetail as EmailDetailType } from '../types/email';
import { formatDate } from '../utils/format';

interface EmailDetailProps {
  email: EmailDetailType;
}

//This component receives the full EmailDetail object and renders it.
//The body is rendered as HTML or plain text depending on body_type.
export default function EmailDetail({ email }: EmailDetailProps) {
  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginBottom: 8 }}>{email.subject}</h2>

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
