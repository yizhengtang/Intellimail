//SlidePanel.tsx
//Slide-out panel that appears to the right of the sidebar when a provider icon is clicked.
//Shows Gmail labels, Outlook folders, or Teams chats depending on which provider is open.

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProvider } from '../context/ProviderContext';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';
import { listChats } from '../services/teamsService';
import type { Folder } from '../types/email';
import type { TeamsChat } from '../types/teams';
import { truncate } from '../utils/format';

//Gmail system labels worth showing — same list as useFolders.
const GMAIL_VISIBLE_SYSTEM_LABELS = ['INBOX', 'SENT', 'TRASH', 'DRAFT', 'STARRED'];

type PanelType = 'gmail' | 'outlook' | 'teams' | null;

interface Props {
  open: PanelType;
}

export default function SlidePanel({ open }: Props) {
  const { setProvider } = useProvider();
  const navigate = useNavigate();

  const [folders, setFolders] = useState<Folder[]>([]);
  const [chats, setChats] = useState<TeamsChat[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  //Fetch the correct data whenever the panel opens for a provider.
  useEffect(() => {
    if (!open) return;

    setFolders([]);
    setChats([]);
    setError(null);
    setLoading(true);

    if (open === 'gmail') {
      gmailService.getLabels()
        .then(data => setFolders(
          data.filter(f => f.type === 'user' || GMAIL_VISIBLE_SYSTEM_LABELS.includes(f.name))
        ))
        .catch(() => setError('Could not load Gmail labels. Make sure you are signed in.'))
        .finally(() => setLoading(false));

    } else if (open === 'outlook') {
      outlookService.getFolders()
        .then(data => setFolders(data))
        .catch(() => setError('Could not load Outlook folders. Make sure you are signed in.'))
        .finally(() => setLoading(false));

    } else if (open === 'teams') {
      listChats(20)
        .then(data => setChats(data))
        .catch(() => setError('Could not load Teams chats. Make sure you are signed in.'))
        .finally(() => setLoading(false));
    }
  }, [open]);

  //Navigate to a Gmail label — sets provider and navigates to inbox filtered by folder name.
  function handleGmailLabel(name: string) {
    setProvider('gmail');
    navigate(`/?folder=${encodeURIComponent(name)}`);
  }

  //Navigate to an Outlook folder.
  function handleOutlookFolder(name: string) {
    setProvider('outlook');
    navigate(`/?folder=${encodeURIComponent(name)}`);
  }

  //Navigate to a Teams chat.
  function handleTeamsChat(chatId: string) {
    navigate(`/teams/${chatId}`);
  }

  //Panel title for each provider.
  const title = open === 'gmail' ? 'Gmail' : open === 'outlook' ? 'Outlook' : 'Teams';

  //Accent colour per provider — matches the brand icon colours.
  const accent = open === 'gmail' ? '#EA4335' : open === 'outlook' ? '#0078D4' : '#6264A7';

  return (
    <>
      {/* The panel itself — sits in the flex row, not overlapping */}
      <div style={{
        height: '100vh',
        width: open ? 220 : 0,
        minWidth: open ? 220 : 0,
        overflow: 'hidden',
        backgroundColor: '#ffffff',
        borderRight: open ? '1px solid #e5e7eb' : 'none',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width 200ms ease, min-width 200ms ease',
        flexShrink: 0,
      }}>

        {/* Panel header */}
        <div style={{
          padding: '18px 16px 12px',
          borderBottom: '1px solid #f3f4f6',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}>
          <div style={{ width: 4, height: 18, borderRadius: 2, backgroundColor: accent, flexShrink: 0 }} />
          <span style={{ fontWeight: 600, fontSize: 14, color: '#111827' }}>{title}</span>
        </div>

        {/* Panel content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0' }}>
          {loading && (
            <p style={{ padding: '12px 16px', fontSize: 13, color: '#9ca3af', margin: 0 }}>Loading...</p>
          )}
          {!loading && error && (
            <p style={{ padding: '12px 16px', fontSize: 13, color: '#dc2626', margin: 0 }}>{error}</p>
          )}

          {/* Gmail labels */}
          {!loading && open === 'gmail' && folders.map(folder => (
            <button
              key={folder.id}
              onClick={() => handleGmailLabel(folder.name)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                width: '100%',
                padding: '9px 16px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: 13,
                color: '#374151',
                borderRadius: 0,
              }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#f9fafb')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
            >
              <span>{folder.name}</span>
              {folder.message_count !== undefined && folder.message_count > 0 && (
                <span style={{ fontSize: 11, color: '#9ca3af' }}>{folder.message_count}</span>
              )}
            </button>
          ))}

          {/* Outlook folders */}
          {!loading && open === 'outlook' && folders.map(folder => (
            <button
              key={folder.id}
              onClick={() => handleOutlookFolder(folder.name)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                width: '100%',
                padding: '9px 16px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: 13,
                color: '#374151',
                borderRadius: 0,
              }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#f9fafb')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
            >
              <span>{folder.name}</span>
              {folder.unread_count !== undefined && folder.unread_count > 0 && (
                <span style={{
                  fontSize: 11,
                  color: '#ffffff',
                  backgroundColor: '#0078D4',
                  borderRadius: 10,
                  padding: '1px 6px',
                }}>{folder.unread_count}</span>
              )}
            </button>
          ))}

          {/* Teams chats */}
          {!loading && open === 'teams' && chats.map(chat => (
            <button
              key={chat.id}
              onClick={() => handleTeamsChat(chat.id)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                width: '100%',
                padding: '10px 16px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left',
                borderRadius: 0,
                gap: 2,
              }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#f9fafb')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
            >
              <span style={{ fontSize: 13, fontWeight: 500, color: '#111827' }}>
                {truncate(chat.topic, 28)}
              </span>
              <span style={{ fontSize: 12, color: '#9ca3af' }}>
                {truncate(chat.last_message, 32)}
              </span>
            </button>
          ))}
        </div>

      </div>
    </>
  );
}
