//EmailDetail.tsx
//Renders the full detail view of a single email — headers, body, attachment indicator, and read/unread toggle.

import type { EmailDetail as EmailDetailType } from '../types/email';
import { formatDate } from '../utils/format';

interface EmailDetailProps {
  email: EmailDetailType;
  isRead: boolean;
  onToggleRead: () => void;
  onReply: () => void;
  onReplyAll: () => void;
}

const FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";

export default function EmailDetail({ email, isRead, onToggleRead, onReply, onReplyAll }: EmailDetailProps) {
  const senderName = email.from_name || email.from || 'Unknown';
  const senderEmail = email.from_name ? email.from : null;

  return (
    <div style={{ padding: '32px 40px', fontFamily: FONT, backgroundColor: '#ffffff' }}>

      {/* Subject */}
      <h1 style={{
        fontSize: 22,
        fontWeight: 700,
        color: '#111827',
        margin: '0 0 24px',
        letterSpacing: '-0.3px',
        lineHeight: 1.3,
      }}>
        {email.subject}
      </h1>

      {/* Sender row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>

        {/* Avatar + sender info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            backgroundColor: '#e5e7eb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 16,
            fontWeight: 600,
            color: '#374151',
            flexShrink: 0,
          }}>
            {senderName[0]?.toUpperCase()}
          </div>

          <div>
            <div style={{ fontSize: 14, fontWeight: 600, color: '#111827' }}>
              {senderName}
              {senderEmail && (
                <span style={{ fontWeight: 400, color: '#6b7280', marginLeft: 6 }}>
                  &lt;{senderEmail}&gt;
                </span>
              )}
            </div>
            <div style={{ fontSize: 13, color: '#6b7280', marginTop: 2 }}>
              To: {email.to}
              {email.cc && <span style={{ marginLeft: 8 }}>Cc: {email.cc}</span>}
            </div>
          </div>
        </div>

        {/* Date + actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
          <span style={{ fontSize: 13, color: '#9ca3af' }}>{formatDate(email.date)}</span>

          {/* Reply icon */}
          <button onClick={onReply} title="Reply" style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: '#6b7280', padding: 4, borderRadius: 6,
            display: 'flex', alignItems: 'center',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 17 4 12 9 7" />
              <path d="M20 18v-2a4 4 0 00-4-4H4" />
            </svg>
          </button>

          {/* Reply all icon */}
          <button onClick={onReplyAll} title="Reply All" style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: '#6b7280', padding: 4, borderRadius: 6,
            display: 'flex', alignItems: 'center',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="7 17 2 12 7 7" />
              <polyline points="13 17 8 12 13 7" />
              <path d="M22 18v-2a4 4 0 00-4-4H2" />
            </svg>
          </button>

          {/* Mark read/unread icon */}
          <button onClick={onToggleRead} title={isRead ? 'Mark as unread' : 'Mark as read'} style={{
            background: 'none', border: 'none', cursor: 'pointer',
            color: '#6b7280', padding: 4, borderRadius: 6,
            display: 'flex', alignItems: 'center',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {isRead
                ? <><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></>
                : <><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></>
              }
            </svg>
          </button>
        </div>
      </div>

      {/* Divider */}
      <hr style={{ border: 'none', borderTop: '1px solid #f3f4f6', margin: '0 0 24px' }} />

      {/* Body */}
      <div style={{
        backgroundColor: '#f9fafb',
        border: '1px solid #f3f4f6',
        borderRadius: 12,
        padding: '20px 24px',
        minHeight: 200,
      }}>
        {email.body_type === 'html' || email.body_type === 'HTML' ? (
          <iframe
            srcDoc={email.body}
            title="Email content"
            sandbox="allow-same-origin"
            style={{ width: '100%', border: 'none', minHeight: 200, display: 'block' }}
            onLoad={e => {
              try {
                const doc = e.currentTarget.contentDocument;
                if (doc?.body) e.currentTarget.style.height = `${doc.body.scrollHeight + 32}px`;
              } catch { /* sandbox may restrict access on some browsers */ }
            }}
          />
        ) : (
          <p style={{
            fontSize: 15,
            lineHeight: 1.7,
            color: '#374151',
            whiteSpace: 'pre-wrap',
            margin: 0,
          }}>
            {email.body}
          </p>
        )}
      </div>

      {/* Reply / Reply All buttons at bottom */}
      <div style={{ display: 'flex', gap: 8, marginTop: 32 }}>
        <button onClick={onReply} style={{
          padding: '8px 18px',
          fontSize: 13,
          fontWeight: 500,
          fontFamily: FONT,
          cursor: 'pointer',
          border: '1px solid #e5e7eb',
          borderRadius: 8,
          backgroundColor: '#f9fafb',
          color: '#374151',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="9 17 4 12 9 7" /><path d="M20 18v-2a4 4 0 00-4-4H4" />
          </svg>
          Reply
        </button>
        <button onClick={onReplyAll} style={{
          padding: '8px 18px',
          fontSize: 13,
          fontWeight: 500,
          fontFamily: FONT,
          cursor: 'pointer',
          border: '1px solid #e5e7eb',
          borderRadius: 8,
          backgroundColor: '#f9fafb',
          color: '#374151',
          display: 'flex',
          alignItems: 'center',
          gap: 6,
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="7 17 2 12 7 7" /><polyline points="13 17 8 12 13 7" /><path d="M22 18v-2a4 4 0 00-4-4H2" />
          </svg>
          Reply All
        </button>
      </div>
    </div>
  );
}
