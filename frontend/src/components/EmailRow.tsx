//EmailRow.tsx
//Renders a single email row in the email list. Bold if unread, clickable to navigate to detail.

import { useNavigate } from 'react-router-dom';
import type { EmailSummary } from '../types/email';
import { formatDate, truncate } from '../utils/format';

interface EmailRowProps {
  email: EmailSummary;
}

//Each row shows: sender, subject, snippet, and date.
//Clicking the row navigates to /email/:provider/:id for the full email view.
//Unread emails are rendered bold so the user can tell them apart at a glance.
export default function EmailRow({ email }: EmailRowProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/email/${email.provider}/${email.id}`);
  };

  return (
    <div
      onClick={handleClick}
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        padding: '10px 12px',
        cursor: 'pointer',
        borderBottom: '1px solid #e0e0e0',
        fontWeight: email.is_read ? 'normal' : 'bold',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div>{email.from_name || email.from}</div>
        <div>{email.subject}</div>
        <div style={{ color: '#888' }}>{truncate(email.snippet, 80)}</div>
      </div>
      <div style={{ whiteSpace: 'nowrap', marginLeft: 12, color: '#888' }}>
        {formatDate(email.date)}
      </div>
    </div>
  );
}
