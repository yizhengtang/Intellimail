//EmailRow.tsx
//Single table row — columns are Sender, Message, Channel, Time.

import { useNavigate } from 'react-router-dom';
import type { EmailSummary } from '../types/email';
import { formatDate, truncate } from '../utils/format';

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

  const rawSender = email.from_name || email.from || '?';
  const senderName = rawSender.replace(/<[^>]*>/g, '').trim() || rawSender;
  const initial = senderName[0].toUpperCase();
  const color = avatarColor(senderName);
  const isUnread = !email.is_read;

  return (
    <div
      onClick={() => navigate(`/email/${email.provider}/${email.id}`)}
      style={{
        display: 'flex',
        alignItems: 'center',
        padding: '12px 16px',
        borderBottom: '1px solid #f3f4f6',
        cursor: 'pointer',
        backgroundColor: '#ffffff',
        transition: 'background-color 120ms ease',
      }}
      onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#f9fafb')}
      onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#ffffff')}
    >
      {selectable && (
        <input
          type="checkbox"
          checked={selected || false}
          onChange={() => onSelect?.(email.id)}
          onClick={e => e.stopPropagation()}
          style={{ cursor: 'pointer', marginRight: 12, flexShrink: 0 }}
        />
      )}

      {/* Sender column — 220px */}
      <div style={{ width: 220, display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0, minWidth: 0 }}>
        {/* Unread dot */}
        <div style={{
          width: 7,
          height: 7,
          borderRadius: '50%',
          backgroundColor: isUnread ? '#3b82f6' : 'transparent',
          flexShrink: 0,
        }} />
        {/* Avatar */}
        <div style={{
          width: 32,
          height: 32,
          borderRadius: '50%',
          backgroundColor: color,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          fontWeight: 700,
          fontSize: 13,
          flexShrink: 0,
        }}>
          {initial}
        </div>
        {/* Name */}
        <span style={{
          fontSize: 13,
          fontWeight: isUnread ? 700 : 500,
          color: '#111827',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}>
          {senderName}
        </span>
      </div>

      {/* Message column — flex:1 */}
      <div style={{ flex: 1, minWidth: 0, padding: '0 16px', display: 'flex', alignItems: 'baseline', gap: 6 }}>
        <span style={{
          fontSize: 13,
          fontWeight: isUnread ? 600 : 400,
          color: '#374151',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          flexShrink: 0,
          maxWidth: '40%',
        }}>
          {email.subject}
        </span>
        <span style={{
          fontSize: 12,
          color: '#9ca3af',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}>
          {truncate(email.snippet || '', 80)}
        </span>
      </div>

      {/* Channel column — 110px */}
      <div style={{ width: 110, flexShrink: 0 }}>
        {email.provider && (
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 5,
            fontSize: 11,
            fontWeight: 600,
            color: '#ffffff',
            backgroundColor: email.provider === 'gmail' ? '#EA4335' : '#0078D4',
            borderRadius: 6,
            padding: '3px 9px',
          }}>
            {email.provider === 'gmail' ? 'Gmail' : 'Outlook'}
          </div>
        )}
      </div>

      {/* Time column — 80px */}
      <div style={{ width: 80, fontSize: 12, color: '#9ca3af', textAlign: 'right', flexShrink: 0 }}>
        {formatDate(email.date)}
      </div>
    </div>
  );
}
