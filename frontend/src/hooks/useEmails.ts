//useEmails.ts
//Custom hook that fetches the email list based on the active provider.

import { useState, useEffect, useCallback } from 'react';
import type { EmailSummary } from '../types/email';
import { useProvider } from '../context/ProviderContext';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';

//This hook reads the active provider from context and calls the correct service.
//For 'unified' mode, it fetches from both Gmail and Outlook in parallel,
//tags each email with its provider, merges, and sorts by date descending.
export function useEmails(folder?: string, maxResults: number = 10) {
  const { provider } = useProvider();
  const [emails, setEmails] = useState<EmailSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEmails = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (provider === 'gmail') {
        const data = await gmailService.getEmails(folder || 'INBOX', maxResults);
        setEmails(data.map(e => ({ ...e, provider: 'gmail' as const })));

      } else if (provider === 'outlook') {
        const data = await outlookService.getEmails(folder || 'inbox', maxResults);
        setEmails(data.map(e => ({ ...e, provider: 'outlook' as const })));

      } else {
        //fetch from both providers in parallel
        const [gmailData, outlookData] = await Promise.all([
          gmailService.getEmails(folder || 'INBOX', maxResults),
          outlookService.getEmails(folder || 'inbox', maxResults),
        ]);

        const merged = [
          ...gmailData.map(e => ({ ...e, provider: 'gmail' as const })),
          ...outlookData.map(e => ({ ...e, provider: 'outlook' as const })),
        ];

        //Sort by date descending so newest emails appear first
        merged.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
        setEmails(merged);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch emails');
    } finally {
      setLoading(false);
    }
  }, [provider, folder, maxResults]);

  //Re-fetch whenever the provider, folder, or maxResults changes
  useEffect(() => {
    fetchEmails();
  }, [fetchEmails]);

  return { emails, loading, error, refetch: fetchEmails };
}
