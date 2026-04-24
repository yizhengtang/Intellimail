//InboxPage.tsx
//Main inbox view — fills the viewport exactly, with a scrollable email list that fades at the bottom.

import { useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
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
export default function InboxPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const query = searchParams.get('q') || '';
  const folderParam = searchParams.get('folder');
  //Guard against stale "undefined" string that can appear in the URL from old navigation bugs.
  const folder = folderParam && folderParam !== 'undefined' ? folderParam : undefined;

  const { provider } = useProvider();
  const { authStatus } = useAuth();

  //Local state for the search input — keeps the input in sync with the ?q= URL param.
  const [searchInput, setSearchInput] = useState(query);

  const inbox = useEmails(folder);
  const search = useSearch(query);

  const isSearching = query.length > 0;
  const emails = isSearching ? search.results : inbox.emails;
  const loading = isSearching ? search.loading : inbox.loading;
  const error = isSearching ? search.error : inbox.error;

  const isTrash = folder === 'TRASH' || folder === 'Deleted Items';

  function handleSearch(e: { preventDefault(): void }) {
    e.preventDefault();
    const trimmed = searchInput.trim();
    navigate(trimmed ? `/?q=${encodeURIComponent(trimmed)}` : '/');
  }

  const handleBatchTrash = async (selectedIds: string[]) => {
    try {
      if (provider === 'gmail') await gmailService.batchTrash(selectedIds);
      else if (provider === 'outlook') await outlookService.batchTrash(selectedIds);
      inbox.refetch();
    } catch { /* list stays unchanged */ }
  };

  const handleBatchRestore = async (selectedIds: string[]) => {
    try {
      if (provider === 'gmail') await gmailService.batchUntrash(selectedIds);
      else if (provider === 'outlook') await outlookService.batchUntrash(selectedIds);
      inbox.refetch();
    } catch { /* list stays unchanged */ }
  };

  //Guard — show a not-connected message before calling the email API.
  if (authStatus) {
    if (provider === 'gmail' && !authStatus.gmail.connected) {
      return (
        <div style={{ padding: 24, height: '100%', backgroundColor: '#f3f4f6' }}>
          <p style={{ color: '#6b7280' }}>Gmail is not connected. Open the Account panel to connect.</p>
        </div>
      );
    }
    if (provider === 'outlook' && !authStatus.outlook.connected) {
      return (
        <div style={{ padding: 24, height: '100%', backgroundColor: '#f3f4f6' }}>
          <p style={{ color: '#6b7280' }}>Outlook is not connected. Open the Account panel to connect.</p>
        </div>
      );
    }
    if (provider === 'unified' && !authStatus.gmail.connected && !authStatus.outlook.connected) {
      return (
        <div style={{ padding: 24, height: '100%', backgroundColor: '#f3f4f6' }}>
          <p style={{ color: '#6b7280' }}>No accounts connected. Open the Account panel to connect Gmail or Outlook.</p>
        </div>
      );
    }
  }

  const sectionLabel = isSearching
    ? `Results for "${query}"`
    : folder
      ? folder
      : provider === 'unified'
        ? 'All Inboxes'
        : 'Inbox';

  return (
    //Flex column that fills the full available height — no page-level scroll
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      backgroundColor: '#f3f4f6',
      overflow: 'hidden',
    }}>

      {/* Top bar — search + compose, fixed height, never scrolls away */}
      <div style={{ padding: '20px 24px 0', flexShrink: 0 }}>
        <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center' }}>
          <form onSubmit={handleSearch} style={{ flex: 1 }}>
            <div style={{ position: 'relative' }}>
              <svg
                width="16" height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#9ca3af"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="text"
                placeholder="Search emails, contacts or labels"
                value={searchInput}
                onChange={e => setSearchInput(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 16px 10px 40px',
                  border: '1px solid #e5e7eb',
                  borderRadius: 10,
                  fontSize: 14,
                  backgroundColor: '#ffffff',
                  color: '#111827',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </form>

          <Link
            to="/compose"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '10px 20px',
              backgroundColor: '#111827',
              color: '#ffffff',
              borderRadius: 10,
              textDecoration: 'none',
              fontSize: 14,
              fontWeight: 600,
              whiteSpace: 'nowrap',
              flexShrink: 0,
            }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
            Compose
          </Link>
        </div>

        {/* Section header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <span style={{ fontSize: 15, fontWeight: 700, color: '#111827' }}>{sectionLabel}</span>
          {!isSearching && (
            <span style={{
              fontSize: 12,
              fontWeight: 600,
              color: '#6b7280',
              backgroundColor: '#e5e7eb',
              borderRadius: 20,
              padding: '1px 8px',
            }}>
              {emails.length}
            </span>
          )}
        </div>

        {error && <p style={{ color: '#dc2626', fontSize: 14, marginBottom: 8 }}>{error}</p>}
      </div>

      {/* Scrollable email list — flex: 1 so it fills the remaining height */}
      <div style={{ flex: 1, minHeight: 0, position: 'relative' }}>
        <div style={{ height: '100%', overflowY: 'auto', padding: '0 24px' }}>
          <EmailList
            emails={emails}
            loading={loading}
            selectable={!isSearching}
            onBatchAction={isTrash ? handleBatchRestore : handleBatchTrash}
            batchActionLabel={isTrash ? 'Restore' : 'Trash'}
          />
        </div>

        {/* Fade overlay at the bottom of the list */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 80,
          background: 'linear-gradient(to bottom, transparent, #f3f4f6)',
          pointerEvents: 'none',
        }} />
      </div>

    </div>
  );
}
