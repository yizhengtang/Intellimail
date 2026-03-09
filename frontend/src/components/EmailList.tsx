//EmailList.tsx
//Renders a list of EmailRow components. Handles loading and empty states.

import type { EmailSummary } from '../types/email';
import EmailRow from './EmailRow';

interface EmailListProps {
  emails: EmailSummary[];
  loading: boolean;
}

//This component receives the email array and loading flag from the page.
//It does not fetch data — it only renders what it is given.
export default function EmailList({ emails, loading }: EmailListProps) {
  if (loading) return <p>Loading...</p>;
  if (emails.length === 0) return <p>No emails found.</p>;

  return (
    <div>
      {emails.map(email => (
        <EmailRow key={email.id} email={email} />
      ))}
    </div>
  );
}
