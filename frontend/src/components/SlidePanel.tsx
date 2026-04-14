//SlidePanel.tsx
//Slide-out panel that appears to the right of the sidebar when a provider icon is clicked.
//Shows Gmail labels, Outlook folders, or Teams chats depending on which provider is open.
//Each provider's data is fetched once and cached for the lifetime of the component.
//Re-fetching only happens if a previous attempt for that provider failed.

import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProvider } from '../context/ProviderContext';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';
import { listChats } from '../services/teamsService';
import type { Folder } from '../types/email';
import type { TeamsChat } from '../types/teams';
import { truncate } from '../utils/format';

const GMAIL_VISIBLE_SYSTEM_LABELS = ['INBOX', 'SENT', 'TRASH', 'DRAFT', 'STARRED'];

type PanelType = 'gmail' | 'outlook' | 'teams' | null;

//A parent label and its direct children, derived from Gmail's flat label list.
//Gmail encodes nesting with a "/" in the label name — "Course/FYP" is a child of "Course".
interface LabelNode {
  folder: Folder;
  children: Folder[];
}

//Groups a flat Gmail label list into a parent → children tree.
//Labels whose name contains "/" are children of the segment before the first slash.
//If a parent label does not exist in the list as its own entry, it is not shown.
function buildLabelTree(folders: Folder[]): LabelNode[] {
  const roots = folders.filter(f => !f.name.includes('/'));
  const children = folders.filter(f => f.name.includes('/'));
  return roots.map(root => ({
    folder: root,
    children: children.filter(c => c.name.startsWith(root.name + '/')),
  }));
}

//Chevron pointing right — used for a collapsed parent label.
function ChevronRight() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  );
}

//Chevron pointing down — used for an expanded parent label.
function ChevronDown() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

interface Props {
  open: PanelType;
}

export default function SlidePanel({ open }: Props) {
  const { setProvider } = useProvider();
  const navigate = useNavigate();

  //Separate state per provider so switching panels does not wipe the other's cached data.
  const [gmailFolders, setGmailFolders] = useState<Folder[]>([]);
  const [outlookFolders, setOutlookFolders] = useState<Folder[]>([]);
  const [teamsChats, setTeamsChats] = useState<TeamsChat[]>([]);

  //loading tracks which provider is currently being fetched. null means idle.
  const [loading, setLoading] = useState<PanelType>(null);

  //errors holds the error message per provider so each provider's error is independent.
  const [errors, setErrors] = useState<Partial<Record<NonNullable<PanelType>, string>>>({});

  //fetched tracks which providers have already loaded successfully.
  //A ref is used because updating it must not trigger a re-render — it is bookkeeping only.
  const fetched = useRef(new Set<string>());

  //expandedLabels tracks which Gmail parent label IDs are currently expanded.
  const [expandedLabels, setExpandedLabels] = useState<Set<string>>(new Set());

  //Only fetch when the panel opens for a provider that has not been fetched yet,
  //or when a previous fetch for that provider ended in an error.
  useEffect(() => {
    if (!open) return;
    if (fetched.current.has(open) && !errors[open]) return;

    setLoading(open);
    setErrors(prev => ({ ...prev, [open]: undefined }));

    if (open === 'gmail') {
      gmailService.getLabels()
        .then(data => {
          setGmailFolders(data.filter(f => f.type === 'user' || GMAIL_VISIBLE_SYSTEM_LABELS.includes(f.name)));
          fetched.current.add('gmail');
        })
        .catch(() => setErrors(prev => ({ ...prev, gmail: 'Could not load Gmail labels. Make sure you are signed in.' })))
        .finally(() => setLoading(null));

    } else if (open === 'outlook') {
      outlookService.getFolders()
        .then(data => {
          setOutlookFolders(data);
          fetched.current.add('outlook');
        })
        .catch(() => setErrors(prev => ({ ...prev, outlook: 'Could not load Outlook folders. Make sure you are signed in.' })))
        .finally(() => setLoading(null));

    } else if (open === 'teams') {
      listChats(20)
        .then(data => {
          setTeamsChats(data);
          fetched.current.add('teams');
        })
        .catch(() => setErrors(prev => ({ ...prev, teams: 'Could not load Teams chats. Make sure you are signed in.' })))
        .finally(() => setLoading(null));
    }
  }, [open]);

  //Toggles a Gmail parent label open or closed.
  function toggleLabel(id: string) {
    setExpandedLabels(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  function handleGmailLabel(name: string) {
    setProvider('gmail');
    navigate(`/?folder=${encodeURIComponent(name)}`);
  }

  function handleOutlookFolder(name: string) {
    setProvider('outlook');
    navigate(`/?folder=${encodeURIComponent(name)}`);
  }

  function handleTeamsChat(chatId: string) {
    navigate(`/teams/${chatId}`);
  }

  const isLoading = loading === open;
  const activeError = open ? errors[open] : undefined;
  const title = open === 'gmail' ? 'Gmail' : open === 'outlook' ? 'Outlook' : 'Teams';
  const accent = open === 'gmail' ? '#EA4335' : open === 'outlook' ? '#0078D4' : '#6264A7';

  return (
    <>
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

        <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0' }}>
          {isLoading && (
            <p style={{ padding: '12px 16px', fontSize: 13, color: '#9ca3af', margin: 0 }}>Loading...</p>
          )}
          {!isLoading && activeError && (
            <p style={{ padding: '12px 16px', fontSize: 13, color: '#dc2626', margin: 0 }}>{activeError}</p>
          )}

          {/* Gmail labels — grouped into a collapsible tree */}
          {!isLoading && open === 'gmail' && buildLabelTree(gmailFolders).map(({ folder, children }) => (
            <div key={folder.id}>

              {/* Parent label row */}
              <div style={{ display: 'flex', alignItems: 'center' }}>
                {children.length > 0 ? (
                  <>
                    {/* Chevron toggle — expands/collapses the children */}
                    <button
                      onClick={() => toggleLabel(folder.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: 28,
                        flexShrink: 0,
                        padding: '9px 0 9px 12px',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#9ca3af',
                      }}
                    >
                      {expandedLabels.has(folder.id) ? <ChevronDown /> : <ChevronRight />}
                    </button>

                    {/* Label name — navigates to this label */}
                    <button
                      onClick={() => handleGmailLabel(folder.name)}
                      style={{
                        flex: 1,
                        padding: '9px 16px 9px 4px',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        textAlign: 'left',
                        fontSize: 13,
                        color: '#374151',
                      }}
                      onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#f9fafb')}
                      onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      {folder.name}
                    </button>
                  </>
                ) : (
                  // No children — full-width navigation button
                  <button
                    onClick={() => handleGmailLabel(folder.name)}
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      padding: '9px 16px',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      textAlign: 'left',
                      fontSize: 13,
                      color: '#374151',
                    }}
                    onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#f9fafb')}
                    onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    {folder.name}
                  </button>
                )}
              </div>

              {/* Child labels — only rendered when the parent is expanded */}
              {expandedLabels.has(folder.id) && children.map(child => (
                <button
                  key={child.id}
                  onClick={() => handleGmailLabel(child.name)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    width: '100%',
                    padding: '8px 16px 8px 40px',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: 13,
                    color: '#6b7280',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#f9fafb')}
                  onMouseLeave={e => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  {/* Show only the part after the last slash */}
                  {child.name.split('/').pop()}
                </button>
              ))}

            </div>
          ))}

          {/* Outlook folders */}
          {!isLoading && open === 'outlook' && outlookFolders.map(folder => (
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
          {!isLoading && open === 'teams' && teamsChats.map(chat => (
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
