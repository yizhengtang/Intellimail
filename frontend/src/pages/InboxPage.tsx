//InboxPage.tsx
//Main inbox view — fetches emails using the useEmails hook and renders them with EmailList.

import { useEmails } from '../hooks/useEmails';
import EmailList from '../components/EmailList';

//This page is the first screen the user sees.
//It calls useEmails() which reads the active provider from context
//and fetches the correct emails. The results are passed to EmailList for rendering.
export default function InboxPage() {
  const { emails, loading, error } = useEmails();

  if (error) return <p>{error}</p>;

  return <EmailList emails={emails} loading={loading} />;
}
