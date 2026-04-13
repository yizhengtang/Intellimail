//InboxPage.tsx
//Main inbox view — shows the email list, search results, or trash view with batch actions.

import { useSearchParams } from 'react-router-dom';
import { useEmails } from '../hooks/useEmails';
import { useSearch } from '../hooks/useSearch';
import { useProvider } from '../context/ProviderContext';
import { useAuth } from '../context/AuthContext';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';
import EmailList from '../components/EmailList';

//This page reads two URL search params:
//  ?q=     — search query (shows search results instead of normal inbox)
//  ?folder= — folder/label name (filters emails by that folder)
//When the folder is TRASH or Deleted Items, the page enables batch selection
//with a "Restore" button that calls untrash for the selected emails.
//In all other folder views, batch selection shows a "Trash" button instead.
export default function InboxPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const folder = searchParams.get('folder') || undefined;
  const { provider } = useProvider();
  const { authStatus } = useAuth();

  const inbox = useEmails(folder);
  const search = useSearch(query);

  const isSearching = query.length > 0;
  const emails = isSearching ? search.results : inbox.emails;
  const loading = isSearching ? search.loading : inbox.loading;
  const error = isSearching ? search.error : inbox.error;

  //Detect if we are viewing the trash folder
  //Gmail uses "TRASH", Outlook uses "Deleted Items"
  const isTrash = folder === 'TRASH' || folder === 'Deleted Items';

  //Batch trash — moves selected emails to trash, then refreshes the list
  const handleBatchTrash = async (selectedIds: string[]) => {
    try {
      if (provider === 'gmail') {
        await gmailService.batchTrash(selectedIds);
      } else if (provider === 'outlook') {
        await outlookService.batchTrash(selectedIds);
      }
      inbox.refetch();
    } catch {
      //Batch action failed — list stays unchanged
    }
  };

  //Batch restore — moves selected emails out of trash, then refreshes the list
  const handleBatchRestore = async (selectedIds: string[]) => {
    try {
      if (provider === 'gmail') {
        await gmailService.batchUntrash(selectedIds);
      } else if (provider === 'outlook') {
        await outlookService.batchUntrash(selectedIds);
      }
      inbox.refetch();
    } catch {
      //Batch action failed — list stays unchanged
    }
  };

  //Guard — show a not-connected message instead of calling the email API.
  //Only checked once authStatus has loaded (null means still loading — let through to avoid flicker).
  if (authStatus) {
    if (provider === 'gmail' && !authStatus.gmail.connected) {
      return (
        <p style={{ padding: 24, color: '#888' }}>
          Gmail is not connected. Open the Account panel to connect.
        </p>
      );
    }
    if (provider === 'outlook' && !authStatus.outlook.connected) {
      return (
        <p style={{ padding: 24, color: '#888' }}>
          Outlook is not connected. Open the Account panel to connect.
        </p>
      );
    }
  }

  if (error) return <p style={{ padding: 24 }}>{error}</p>;

  return (
    <div>
      {isSearching && (
        <p style={{ padding: '12px 24px 0', color: '#555' }}>
          Search results for &ldquo;{query}&rdquo;
        </p>
      )}
      <EmailList
        emails={emails}
        loading={loading}
        selectable={!isSearching}
        onBatchAction={isTrash ? handleBatchRestore : handleBatchTrash}
        batchActionLabel={isTrash ? 'Restore' : 'Trash'}
      />
    </div>
  );
}
