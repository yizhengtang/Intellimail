//useDrafts.ts
//Custom hook that fetches the draft list and provides draft operations (send, delete).

import { useState, useEffect, useCallback } from 'react';
import type { DraftSummary } from '../types/email';
import { useProvider } from '../context/ProviderContext';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';

//This hook reads the active provider from context and fetches drafts from the correct service.
//For 'unified' mode, it fetches from both Gmail and Outlook in parallel,
//tags each draft with its provider, merges, and sorts by date descending.
//It also exposes sendDraft and deleteDraft which call the correct service
//based on the draft's provider, then refetch the list.
export function useDrafts(maxResults: number = 10) {
  const { provider } = useProvider();
  const [drafts, setDrafts] = useState<DraftSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDrafts = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (provider === 'gmail') {
        const data = await gmailService.getDrafts(maxResults);
        setDrafts(data.map(d => ({ ...d, provider: 'gmail' as const })));

      } else if (provider === 'outlook') {
        const data = await outlookService.getDrafts(maxResults);
        setDrafts(data.map(d => ({ ...d, provider: 'outlook' as const })));

      } else {
        const [gmailData, outlookData] = await Promise.all([
          gmailService.getDrafts(maxResults),
          outlookService.getDrafts(maxResults),
        ]);

        const merged = [
          ...gmailData.map(d => ({ ...d, provider: 'gmail' as const })),
          ...outlookData.map(d => ({ ...d, provider: 'outlook' as const })),
        ];

        merged.sort((a, b) => new Date(b.date || '').getTime() - new Date(a.date || '').getTime());
        setDrafts(merged);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch drafts');
    } finally {
      setLoading(false);
    }
  }, [provider, maxResults]);

  useEffect(() => {
    fetchDrafts();
  }, [fetchDrafts]);

  //Send a draft via the correct provider, then refresh the list
  const sendDraft = async (draftId: string, draftProvider: string) => {
    if (draftProvider === 'gmail') {
      await gmailService.sendDraft(draftId);
    } else {
      await outlookService.sendDraft(draftId);
    }
    fetchDrafts();
  };

  //Delete a draft via the correct provider, then refresh the list
  const deleteDraft = async (draftId: string, draftProvider: string) => {
    if (draftProvider === 'gmail') {
      await gmailService.deleteDraft(draftId);
    } else {
      await outlookService.deleteDraft(draftId);
    }
    fetchDrafts();
  };

  return { drafts, loading, error, refetch: fetchDrafts, sendDraft, deleteDraft };
}
