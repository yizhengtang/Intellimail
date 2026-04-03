//Sidebar.tsx
//Navigation sidebar — provider switcher, compose link, and dynamic folder list.

import { Link, useSearchParams } from 'react-router-dom';
import { useProvider } from '../context/ProviderContext';
import { useFolders } from '../hooks/useFolders';
import type { Provider } from '../types/email';

//The sidebar has three sections:
//1. Provider switcher — three buttons that change the active email provider.
//2. Compose link — navigates to the compose page.
//3. Folder list — dynamically fetched from the active provider.
//   Gmail returns "labels" (INBOX, SENT, TRASH, etc.).
//   Outlook returns "folders" (Inbox, Sent Items, Deleted Items, etc.).
//   Clicking a folder navigates to /?folder=<folderId> which InboxPage reads.
export default function Sidebar() {
  const { provider, setProvider } = useProvider();
  const { folders, loading } = useFolders();
  const [searchParams] = useSearchParams();
  const activeFolder = searchParams.get('folder') || '';

  const providers: { label: string; value: Provider }[] = [
    { label: 'Gmail', value: 'gmail' },
    { label: 'Outlook', value: 'outlook' },
    { label: 'All', value: 'unified' },
  ];

  return (
    <div style={{ padding: 16 }}>
      <h4>Provider</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {providers.map(p => (
          <button
            key={p.value}
            onClick={() => setProvider(p.value)}
            style={{
              padding: '8px 12px',
              cursor: 'pointer',
              fontWeight: provider === p.value ? 'bold' : 'normal',
              backgroundColor: provider === p.value ? '#e0e0e0' : 'transparent',
              border: '1px solid #ccc',
              borderRadius: 4,
            }}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div style={{ marginTop: 24 }}>
        <Link
          to="/compose"
          style={{
            display: 'block',
            padding: '8px 12px',
            textDecoration: 'none',
            color: 'white',
            backgroundColor: '#2185d0',
            borderRadius: 4,
            textAlign: 'center',
          }}
        >
          Compose
        </Link>
        <Link
          to="/chat"
          style={{
            display: 'block',
            padding: '8px 12px',
            textDecoration: 'none',
            color: '#333',
            border: '1px solid #ccc',
            borderRadius: 4,
            textAlign: 'center',
            marginTop: 8,
          }}
        >
          AI Chat
        </Link>
        <Link
          to="/sync"
          style={{
            display: 'block',
            padding: '8px 12px',
            textDecoration: 'none',
            color: '#333',
            border: '1px solid #ccc',
            borderRadius: 4,
            textAlign: 'center',
            marginTop: 8,
          }}
        >
          Sync Inbox
        </Link>
      </div>

      <h4 style={{ marginTop: 24 }}>Folders</h4>
      {loading ? (
        <p style={{ color: '#888', fontSize: 14 }}>Loading...</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Link
            to="/"
            style={{
              padding: '6px 12px',
              textDecoration: 'none',
              color: !activeFolder ? '#333' : '#888',
              fontWeight: !activeFolder ? 'bold' : 'normal',
              fontSize: 14,
            }}
          >
            All Mail
          </Link>
          <Link
            to="/drafts"
            style={{
              padding: '6px 12px',
              textDecoration: 'none',
              color: '#888',
              fontSize: 14,
            }}
          >
            Drafts
          </Link>
          {folders.map(folder => (
            <Link
              key={`${folder.provider}-${folder.id}`}
              to={`/?folder=${encodeURIComponent(folder.name)}`}
              style={{
                padding: '6px 12px',
                textDecoration: 'none',
                color: activeFolder === folder.name ? '#333' : '#888',
                fontWeight: activeFolder === folder.name ? 'bold' : 'normal',
                fontSize: 14,
              }}
            >
              {folder.name}
              {provider === 'unified' && folder.provider && (
                <span style={{ color: '#bbb', marginLeft: 4, fontSize: 12 }}>
                  ({folder.provider})
                </span>
              )}
              {folder.unread_count !== undefined && folder.unread_count > 0 && (
                <span style={{ color: '#2185d0', marginLeft: 4, fontSize: 12 }}>
                  {folder.unread_count}
                </span>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
