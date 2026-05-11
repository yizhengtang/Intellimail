//SyncPage.tsx
//Inbox sync page — shows current indexed email counts and lets the user sync Gmail and Outlook into ChromaDB.

import { useState, useEffect, useCallback } from 'react';
import { ingestEmails, getAiStatus } from '../services/aiService';
import type { AiStatus, AiIngestResult } from '../types/ai';

//SyncPage calls /ai/status on mount to show how many emails are already indexed per provider.
//Sync Gmail and Sync Outlook each call /ai/ingest/{provider} with max_results=10.
//Sync All calls both sequentially and shows combined results.
//Emails already in ChromaDB are skipped by the backend — only new emails are embedded.
export default function SyncPage() {
  const [status, setStatus] = useState<AiStatus | null>(null);
  const [statusLoading, setStatusLoading] = useState(true);

  const [gmailResult, setGmailResult] = useState<AiIngestResult | null>(null);
  const [outlookResult, setOutlookResult] = useState<AiIngestResult | null>(null);

  //syncing tracks which operation is running so individual buttons show loading state.
  const [syncing, setSyncing] = useState<'gmail' | 'outlook' | 'all' | null>(null);
  const [error, setError] = useState<string | null>(null);

  //Loads current indexed counts from ChromaDB on mount.
  const fetchStatus = useCallback(async () => {
    setStatusLoading(true);
    try {
      const data = await getAiStatus();
      setStatus(data);
    } catch {
      setStatus(null);
    } finally {
      setStatusLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  //Refreshes the status count after any sync so the numbers update without a page reload.
  const syncGmail = async () => {
    setSyncing('gmail');
    setGmailResult(null);
    setError(null);
    try {
      const result = await ingestEmails('gmail', 10);
      setGmailResult(result);
      await fetchStatus();
    } catch {
      setError('Gmail sync failed. Make sure you are authenticated.');
    } finally {
      setSyncing(null);
    }
  };

  const syncOutlook = async () => {
    setSyncing('outlook');
    setOutlookResult(null);
    setError(null);
    try {
      const result = await ingestEmails('outlook', 10);
      setOutlookResult(result);
      await fetchStatus();
    } catch {
      setError('Outlook sync failed. Make sure you are authenticated.');
    } finally {
      setSyncing(null);
    }
  };

  //Sync All runs Gmail first, then Outlook — sequential so errors are isolated per provider.
  const syncAll = async () => {
    setSyncing('all');
    setGmailResult(null);
    setOutlookResult(null);
    setError(null);
    try {
      const gResult = await ingestEmails('gmail', 10);
      setGmailResult(gResult);
    } catch {
      setError('Gmail sync failed. Outlook sync will still run.');
    }
    try {
      const oResult = await ingestEmails('outlook', 10);
      setOutlookResult(oResult);
    } catch {
      setError(prev => prev
        ? prev + ' Outlook sync also failed.'
        : 'Outlook sync failed. Make sure you are authenticated.');
    }
    await fetchStatus();
    setSyncing(null);
  };

  const isSyncing = syncing !== null;

  return (
    <div style={{ padding: 24, maxWidth: 600 }}>
      <h2 style={{ marginBottom: 4 }}>Sync Inbox</h2>
      <p style={{ color: '#555', marginBottom: 24, fontSize: 14 }}>
        Syncing indexes the latest 10 emails from each provider into the AI knowledge base.
        Emails already indexed are skipped — only new emails are embedded.
      </p>

      {/* Current status */}
      <div style={{ border: '1px solid #e0e0e0', borderRadius: 4, padding: 16, marginBottom: 24 }}>
        <h4 style={{ margin: '0 0 12px' }}>Current Index</h4>
        {statusLoading ? (
          <p style={{ color: '#888', fontSize: 14 }}>Loading...</p>
        ) : status ? (
          <div style={{ display: 'flex', gap: 32, fontSize: 14 }}>
            <div><strong>{status.gmail}</strong> Gmail emails indexed</div>
            <div><strong>{status.outlook}</strong> Outlook emails indexed</div>
            <div><strong>{status.total}</strong> total</div>
          </div>
        ) : (
          <p style={{ color: '#888', fontSize: 14 }}>Could not load status.</p>
        )}
      </div>

      {/* Sync buttons */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
        <button
          onClick={syncGmail}
          disabled={isSyncing}
          style={{
            padding: '10px 20px',
            cursor: isSyncing ? 'not-allowed' : 'pointer',
            border: '1px solid #ccc',
            borderRadius: 4,
            backgroundColor: syncing === 'gmail' ? '#f0f0f0' : 'transparent',
            fontSize: 14,
            opacity: isSyncing && syncing !== 'gmail' ? 0.5 : 1,
          }}
        >
          {syncing === 'gmail' ? 'Syncing Gmail...' : 'Sync Gmail'}
        </button>

        <button
          onClick={syncOutlook}
          disabled={isSyncing}
          style={{
            padding: '10px 20px',
            cursor: isSyncing ? 'not-allowed' : 'pointer',
            border: '1px solid #ccc',
            borderRadius: 4,
            backgroundColor: syncing === 'outlook' ? '#f0f0f0' : 'transparent',
            fontSize: 14,
            opacity: isSyncing && syncing !== 'outlook' ? 0.5 : 1,
          }}
        >
          {syncing === 'outlook' ? 'Syncing Outlook...' : 'Sync Outlook'}
        </button>

        <button
          onClick={syncAll}
          disabled={isSyncing}
          style={{
            padding: '10px 20px',
            cursor: isSyncing ? 'not-allowed' : 'pointer',
            border: 'none',
            borderRadius: 4,
            backgroundColor: syncing === 'all' ? '#1a6fb5' : '#2185d0',
            color: 'white',
            fontSize: 14,
            opacity: isSyncing && syncing !== 'all' ? 0.5 : 1,
          }}
        >
          {syncing === 'all' ? 'Syncing All...' : 'Sync All'}
        </button>
      </div>

      {/* Results */}
      {(gmailResult || outlookResult) && (
        <div style={{ border: '1px solid #e0e0e0', borderRadius: 4, padding: 16, marginBottom: 16 }}>
          <h4 style={{ margin: '0 0 12px' }}>Sync Results</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 14 }}>
            {gmailResult && (
              <div>
                Gmail — <strong>{gmailResult.indexed} new</strong> emails indexed,{' '}
                <span style={{ color: '#888' }}>{gmailResult.skipped} skipped</span>
              </div>
            )}
            {outlookResult && (
              <div>
                Outlook — <strong>{outlookResult.indexed} new</strong> emails indexed,{' '}
                <span style={{ color: '#888' }}>{outlookResult.skipped} skipped</span>
              </div>
            )}
          </div>
        </div>
      )}

      {error && <p style={{ color: '#cc0000', fontSize: 13 }}>{error}</p>}
    </div>
  );
}
