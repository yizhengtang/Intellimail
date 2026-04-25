//Sidebar.tsx
//Icon-only navigation sidebar — nav links in the middle, Gmail/Outlook/Teams provider icons at the bottom.

import { useState } from 'react';
import type { CSSProperties } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useProvider } from '../context/ProviderContext';
import AccountPanel from './AccountPanel';

const ACTIVE_ICON = '#5c5fc4';
const INACTIVE_ICON = '#9ca3af';
const ACTIVE_NAV_BG = '#ede9fe';

//Grey rounded box that groups a section of icons.
const sectionBox: CSSProperties = {
  backgroundColor: '#f3f4f6',
  borderRadius: 16,
  padding: '8px 0',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: 4,
  width: 52,
};

//Envelope icon — Inbox
function EnvelopeIcon({ color }: { color: string }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  );
}

//Pencil icon — Compose
function PencilIcon({ color }: { color: string }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

//File icon — Drafts
function FileIcon({ color }: { color: string }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <polyline points="14,2 14,8 20,8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  );
}

//Chat bubble icon — AI Chat
function ChatIcon({ color }: { color: string }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
    </svg>
  );
}

//Person circle icon — Account
function PersonIcon({ color }: { color: string }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

//Calendar icon — Calendar page
function CalendarIcon({ color }: { color: string }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

//Refresh arrows icon — Sync Inbox
function SyncIcon({ color }: { color: string }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23,4 23,10 17,10" />
      <polyline points="1,20 1,14 7,14" />
      <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15" />
    </svg>
  );
}

//Gmail brand icon — red rounded square with white envelope M-shape
function GmailIcon({ active }: { active: boolean }) {
  return (
    <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="7" fill="#EA4335" opacity={active ? 1 : 0.55} />
      <rect x="6" y="10" width="20" height="13" rx="1" stroke="white" strokeWidth="1.8" fill="none" />
      <path d="M6 11l10 7 10-7" stroke="white" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

//Outlook brand icon — blue rounded square with O shape
function OutlookIcon({ active }: { active: boolean }) {
  return (
    <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="7" fill="#0078D4" opacity={active ? 1 : 0.55} />
      <rect x="16" y="9" width="10" height="14" rx="2" fill="white" opacity="0.95" />
      <ellipse cx="11.5" cy="16" rx="5.5" ry="6.5" fill="white" />
      <ellipse cx="11.5" cy="16" rx="3.2" ry="4.2" fill={active ? '#0078D4' : '#0060AA'} />
    </svg>
  );
}

//Teams brand icon — purple rounded square with T bar
function TeamsAppIcon({ active }: { active: boolean }) {
  return (
    <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="7" fill="#6264A7" opacity={active ? 1 : 0.55} />
      <line x1="9" y1="11" x2="23" y2="11" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
      <line x1="16" y1="11" x2="16" y2="22" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
    </svg>
  );
}

//Returns link/button style — highlighted if the nav item is active.
function navItemStyle(active: boolean): CSSProperties {
  return {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: active ? ACTIVE_NAV_BG : 'transparent',
    color: 'inherit',
    border: 'none',
    cursor: 'pointer',
    textDecoration: 'none',
    padding: 0,
  };
}

type OpenPanel = 'gmail' | 'outlook' | 'teams' | null;

interface Props {
  onPanelToggle: (panel: OpenPanel) => void;
  openPanel: OpenPanel;
}

export default function Sidebar({ onPanelToggle, openPanel }: Props) {
  const { setProvider } = useProvider();
  const location = useLocation();
  const path = location.pathname;
  const [accountOpen, setAccountOpen] = useState(false);

  //email-related paths all count as "inbox" being active
  const inboxActive = path === '/' || path.startsWith('/email/');

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      width: 64,
      backgroundColor: '#ffffff',
      borderRight: '1px solid #e5e7eb',
      alignItems: 'center',
      paddingTop: 16,
      paddingBottom: 20,
      boxSizing: 'border-box',
    }}>

      {/* App logo */}
      <div style={{
        width: 36,
        height: 36,
        borderRadius: 10,
        backgroundColor: '#5c5fc4',
        marginBottom: 28,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
          <polyline points="22,6 12,13 2,6" />
        </svg>
      </div>

      {/* APP section — grey rounded section box with Gmail, Outlook, Teams */}
      <div style={{ ...sectionBox, marginBottom: 12 }}>
        <button
          title="Gmail"
          onClick={() => { setProvider('gmail'); onPanelToggle('gmail'); }}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '6px 0' }}
        >
          <GmailIcon active={openPanel === 'gmail'} />
        </button>
        <button
          title="Outlook"
          onClick={() => { setProvider('outlook'); onPanelToggle('outlook'); }}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '6px 0' }}
        >
          <OutlookIcon active={openPanel === 'outlook'} />
        </button>
        <button
          title="Microsoft Teams"
          onClick={() => onPanelToggle('teams')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '6px 0' }}
        >
          <TeamsAppIcon active={openPanel === 'teams'} />
        </button>
      </div>

      {/* Navigation icons — grey rounded section box */}
      <div style={{ ...sectionBox, flex: 1, justifyContent: 'flex-start' }}>
        <Link to="/" title="Inbox" style={navItemStyle(inboxActive)} onClick={() => setProvider('unified')}>
          <EnvelopeIcon color={inboxActive ? ACTIVE_ICON : INACTIVE_ICON} />
        </Link>
        <Link to="/compose" title="Compose" style={navItemStyle(path === '/compose')}>
          <PencilIcon color={path === '/compose' ? ACTIVE_ICON : INACTIVE_ICON} />
        </Link>
        <Link to="/drafts" title="Drafts" style={navItemStyle(path === '/drafts')}>
          <FileIcon color={path === '/drafts' ? ACTIVE_ICON : INACTIVE_ICON} />
        </Link>
        <Link to="/chat" title="AI Chat" style={navItemStyle(path === '/chat')}>
          <ChatIcon color={path === '/chat' ? ACTIVE_ICON : INACTIVE_ICON} />
        </Link>
        <Link to="/sync" title="Sync Inbox" style={navItemStyle(path === '/sync')}>
          <SyncIcon color={path === '/sync' ? ACTIVE_ICON : INACTIVE_ICON} />
        </Link>
        <Link to="/calendar" title="Calendar" style={navItemStyle(path === '/calendar')}>
          <CalendarIcon color={path === '/calendar' ? ACTIVE_ICON : INACTIVE_ICON} />
        </Link>

        {/* Account button — pushed to the bottom of the nav box */}
        <div style={{ marginTop: 'auto', position: 'relative' }}>
          <button
            title="Account"
            onMouseDown={e => e.stopPropagation()}
            onClick={() => setAccountOpen(o => !o)}
            style={navItemStyle(accountOpen)}
          >
            <PersonIcon color={accountOpen ? ACTIVE_ICON : INACTIVE_ICON} />
          </button>
          {accountOpen && <AccountPanel onClose={() => setAccountOpen(false)} />}
        </div>
      </div>

    </div>
  );
}
