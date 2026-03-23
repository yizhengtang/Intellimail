//InboxPage.tsx
//Main inbox view — shows the email list, or search results when a ?q= param is present.

import { useSearchParams } from 'react-router-dom';
import { useEmails } from '../hooks/useEmails';
import { useSearch } from '../hooks/useSearch';
import EmailList from '../components/EmailList';

//This page reads the ?q= search param from the URL.
//If a query is present, it uses useSearch to fetch matching emails.
//Otherwise, it uses useEmails to fetch the normal inbox.
export default function InboxPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  const inbox = useEmails();
  const search = useSearch(query);

  const isSearching = query.length > 0;
  const emails = isSearching ? search.results : inbox.emails;
  const loading = isSearching ? search.loading : inbox.loading;
  const error = isSearching ? search.error : inbox.error;

  if (error) return <p style={{ padding: 24 }}>{error}</p>;

  return (
    <div>
      {isSearching && (
        <p style={{ padding: '12px 24px 0', color: '#555' }}>
          Search results for &ldquo;{query}&rdquo;
        </p>
      )}
      <EmailList emails={emails} loading={loading} />
    </div>
  );
}
