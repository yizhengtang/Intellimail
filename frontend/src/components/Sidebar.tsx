//Sidebar.tsx
//Navigation sidebar — provider switcher and folder navigation links.

import { Link } from 'react-router-dom';
import { useProvider } from '../context/ProviderContext';
import type { Provider } from '../types/email';

//The sidebar has two sections:
//1. Provider switcher — three buttons that change the active email provider.
//   When clicked, setProvider() updates the context, which causes useEmails
//   to re-fetch because its useEffect depends on the provider value.
//2. Nav links — navigate to different views. All point to / for now.
//   Folder-based filtering will be wired in commit 20.
export default function Sidebar() {
  const { provider, setProvider } = useProvider();

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

      <h4 style={{ marginTop: 24 }}>Navigation</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <Link to="/compose" style={{ padding: '8px 12px', textDecoration: 'none', color: '#333' }}>Compose</Link>
        <Link to="/" style={{ padding: '8px 12px', textDecoration: 'none', color: '#333' }}>Inbox</Link>
        <Link to="/" style={{ padding: '8px 12px', textDecoration: 'none', color: '#888' }}>Drafts</Link>
        <Link to="/" style={{ padding: '8px 12px', textDecoration: 'none', color: '#888' }}>Sent</Link>
        <Link to="/" style={{ padding: '8px 12px', textDecoration: 'none', color: '#888' }}>Trash</Link>
      </div>
    </div>
  );
}
