//AccountPanel.tsx
//Dropdown panel showing connection status for Gmail, Outlook, and Teams.
//Each provider row shows the logged-in email, a connected/disconnected indicator,
//and either a Sign out button (when connected) or a Connect button (when not connected).

import { useState, useEffect, useRef } from 'react';
import type { AuthStatus } from '../types/auth';
import { getAuthStatus, signOut, connect } from '../services/authService';

interface AccountPanelProps {
  onClose: () => void;
}

//Label and display order for the three providers.
const PROVIDERS: { key: keyof AuthStatus; label: string }[] = [
  { key: 'gmail',   label: 'Gmail' },
  { key: 'outlook', label: 'Outlook' },
  { key: 'teams',   label: 'Teams' },
];

const btnStyle: React.CSSProperties = {
  padding: '4px 10px',
  fontSize: 12,
  cursor: 'pointer',
  border: '1px solid #ccc',
  borderRadius: 4,
  backgroundColor: 'transparent',
};

//AccountPanel fetches auth status on mount and renders one row per provider.
//The parent (Layout.tsx) controls whether this component is rendered — it has no open/close state of its own.
//Clicking outside the panel calls onClose() so the parent can unmount it.
export default function AccountPanel({ onClose }: AccountPanelProps) {
  const [status, setStatus] = useState<AuthStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  //Fetch auth status as soon as the panel opens.
  useEffect(() => {
    setLoading(true);
    getAuthStatus()
      .then(data => setStatus(data))
      .finally(() => setLoading(false));
  }, []);

  //Close the panel when the user clicks anywhere outside it.
  useEffect(() => {
    function handleMouseDown(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener('mousedown', handleMouseDown);
    return () => document.removeEventListener('mousedown', handleMouseDown);
  }, [onClose]);

  //Sign out of a provider — deletes its token file, then re-fetches status.
  async function handleSignOut(provider: string) {
    setActionInProgress(provider);
    try {
      await signOut(provider);
      const updated = await getAuthStatus();
      setStatus(updated);
    } finally {
      setActionInProgress(null);
    }
  }

  //Connect a provider — triggers the OAuth browser flow, then re-fetches status.
  async function handleConnect(provider: string) {
    setActionInProgress(provider);
    try {
      await connect(provider);
      const updated = await getAuthStatus();
      setStatus(updated);
    } finally {
      setActionInProgress(null);
    }
  }

  return (
    <div
      ref={panelRef}
      style={{
        position: 'absolute',
        top: '100%',
        right: 0,
        width: 320,
        backgroundColor: 'white',
        border: '1px solid #e0e0e0',
        borderRadius: 6,
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        padding: 16,
        zIndex: 100,
        marginTop: 4,
      }}
    >
      <p style={{ fontWeight: 600, fontSize: 13, marginBottom: 12, marginTop: 0 }}>
        Connected Accounts
      </p>

      {loading && <p style={{ fontSize: 13, color: '#888' }}>Loading...</p>}

      {!loading && status && PROVIDERS.map(({ key, label }) => {
        const info = status[key];
        const isActing = actionInProgress === key;

        return (
          <div
            key={key}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '10px 0',
              borderTop: '1px solid #f0f0f0',
            }}
          >
            {/* Left: indicator dot + provider name + email */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 0 }}>
              <span style={{
                fontSize: 16,
                color: info.connected ? '#22a55b' : '#aaa',
                lineHeight: 1,
              }}>
                {info.connected ? '●' : '○'}
              </span>
              <div style={{ minWidth: 0 }}>
                <p style={{ margin: 0, fontSize: 13, fontWeight: 500 }}>{label}</p>
                <p style={{ margin: 0, fontSize: 12, color: '#888', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 160 }}>
                  {info.connected ? info.email : 'Not connected'}
                </p>
              </div>
            </div>

            {/* Right: Sign out or Connect button */}
            {info.connected ? (
              <button
                style={{ ...btnStyle, color: '#cc0000', borderColor: '#cc0000' }}
                disabled={isActing}
                onClick={() => handleSignOut(key)}
              >
                {isActing ? 'Signing out...' : 'Sign out'}
              </button>
            ) : (
              <button
                style={{ ...btnStyle, color: '#2185d0', borderColor: '#2185d0' }}
                disabled={isActing}
                onClick={() => handleConnect(key)}
              >
                {isActing ? 'Connecting...' : 'Connect'}
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
