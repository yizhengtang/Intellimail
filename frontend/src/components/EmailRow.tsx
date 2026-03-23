//EmailRow.tsx
//Renders a single email row in the email list. Bold if unread, clickable to navigate to detail.
//Optionally shows a checkbox for batch selection when selectable is true.

import { useNavigate } from 'react-router-dom';
import type { EmailSummary } from '../types/email';
import { formatDate, truncate } from '../utils/format';

interface EmailRowProps {
  email: EmailSummary;
  selectable?: boolean;
  selected?: boolean;
  onSelect?: (id: string) => void;
}

//Each row shows: sender, subject, snippet, and date.
//Clicking the row navigates to /email/:provider/:id for the full email view.
//Unread emails are rendered bold so the user can tell them apart at a glance.
//When selectable is true, a checkbox appears on the left for batch operations.
export default function EmailRow({ email, selectable, selected, onSelect }: EmailRowProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/email/${email.provider}/${email.id}`);
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        padding: '10px 12px',
        cursor: 'pointer',
        borderBottom: '1px solid #e0e0e0',
        fontWeight: email.is_read ? 'normal' : 'bold',
      }}
    >
      {selectable && (
        <input
          type="checkbox"
          checked={selected || false}
          onChange={() => onSelect?.(email.id)}
          onClick={e => e.stopPropagation()}
          style={{ marginRight: 10, cursor: 'pointer' }}
        />
      )}
      <div onClick={handleClick} style={{ display: 'flex', flex: 1, justifyContent: 'space-between', minWidth: 0 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div>{email.from_name || email.from}</div>
          <div>{email.subject}</div>
          <div style={{ color: '#888' }}>{truncate(email.snippet, 80)}</div>
        </div>
        <div style={{ whiteSpace: 'nowrap', marginLeft: 12, color: '#888' }}>
          {formatDate(email.date)}
        </div>
      </div>
    </div>
  );
}
