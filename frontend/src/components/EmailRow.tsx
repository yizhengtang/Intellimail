//EmailRow.tsx
//Single email card — white rounded box with sender avatar, unread dot, subject, snippet, and date.

import { useNavigate } from 'react-router-dom';
import type { EmailSummary } from '../types/email';
import { formatDate, truncate } from '../utils/format';

//A fixed palette of soft colors for the sender avatar.
//The color is picked by the char code of the first letter of the sender name,
//so the same sender always gets the same color.
const AVATAR_COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#ef4444',
  '#f97316', '#22c55e', '#06b6d4', '#3b82f6', '#f59e0b',
];

function avatarColor(name: string): string {
  return AVATAR_COLORS[name.charCodeAt(0) % AVATAR_COLORS.length];
}

interface EmailRowProps {
  email: EmailSummary;
  selectable?: boolean;
  selected?: boolean;
  onSelect?: (id: string) => void;
}

export default function EmailRow({ email, selectable, selected, onSelect }: EmailRowProps) {
  const navigate = useNavigate();

  const senderName = email.from_name || email.from || '?';
  const initial = senderName[0].toUpperCase();
  const color = avatarColor(senderName);
  const isUnread = !email.is_read;

  return (
    <div
      onClick={() => navigate(`/email/${email.provider}/${email.id}`)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '12px 16px',
        backgroundColor: '#ffffff',
        borderRadius: 12,
        marginBottom: 8,
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        cursor: 'pointer',
        transition: 'box-shadow 150ms ease',
      }}
      onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.10)')}
      onMouseLeave={e => (e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.06)')}
    >
      {selectable && (
        <input
          type="checkbox"
          checked={selected || false}
          onChange={() => onSelect?.(email.id)}
          onClick={e => e.stopPropagation()}
          style={{ cursor: 'pointer', flexShrink: 0 }}
        />
      )}

      {/* Blue dot — visible only for unread emails */}
      <div style={{
        width: 8,
        height: 8,
        borderRadius: '50%',
        backgroundColor: isUnread ? '#3b82f6' : 'transparent',
        flexShrink: 0,
      }} />

      {/* Sender avatar — colored circle with first initial */}
      <div style={{
        width: 38,
        height: 38,
        borderRadius: '50%',
        backgroundColor: color,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#ffffff',
        fontWeight: 700,
        fontSize: 15,
        flexShrink: 0,
      }}>
        {initial}
      </div>

      {/* Email content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: 14,
          fontWeight: isUnread ? 700 : 500,
          color: '#111827',
          marginBottom: 2,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}>
          {senderName}
        </div>
        <div style={{
          fontSize: 13,
          fontWeight: isUnread ? 600 : 400,
          color: '#374151',
          marginBottom: 2,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}>
          {email.subject}
        </div>
        <div style={{
          fontSize: 12,
          color: '#9ca3af',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}>
          {truncate(email.snippet || '', 80)}
        </div>
      </div>

      {/* Date */}
      <div style={{ fontSize: 12, color: '#9ca3af', whiteSpace: 'nowrap', flexShrink: 0 }}>
        {formatDate(email.date)}
      </div>
    </div>
  );
}
