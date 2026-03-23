//useFolders.ts
//Custom hook that fetches the folder/label list based on the active provider.

import { useState, useEffect, useCallback } from 'react';
import type { Folder } from '../types/email';
import { useProvider } from '../context/ProviderContext';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';

//Gmail system labels worth showing in the sidebar.
//All other system labels (CATEGORY_*, YELLOW_STAR, UNREAD, IMPORTANT, SPAM, CHAT, etc.)
//are internal labels that Gmail's own UI hides from the folder list.
const GMAIL_VISIBLE_SYSTEM_LABELS = ['INBOX', 'SENT', 'TRASH', 'DRAFT', 'STARRED'];

//Filters Gmail labels to only include user-created labels and the useful system ones.
//Gmail labels have a "type" field: "system" for built-in, "user" for custom labels.
const filterGmailLabels = (labels: Folder[]): Folder[] =>
  labels.filter(label =>
    label.type === 'user' || GMAIL_VISIBLE_SYSTEM_LABELS.includes(label.name)
  );

//This hook reads the active provider from context and calls the correct service.
//Gmail uses "labels" as its folder system, Outlook uses "folders".
//For 'unified' mode, it fetches from both and merges them.
//Each folder is tagged with its provider so the sidebar knows which provider it belongs to.
export function useFolders() {
  const { provider } = useProvider();
  const [folders, setFolders] = useState<(Folder & { provider?: string })[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFolders = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (provider === 'gmail') {
        const data = await gmailService.getLabels();
        setFolders(filterGmailLabels(data).map(f => ({ ...f, provider: 'gmail' })));

      } else if (provider === 'outlook') {
        const data = await outlookService.getFolders();
        setFolders(data.map(f => ({ ...f, provider: 'outlook' })));

      } else {
        const [gmailData, outlookData] = await Promise.all([
          gmailService.getLabels(),
          outlookService.getFolders(),
        ]);

        const merged = [
          ...filterGmailLabels(gmailData).map(f => ({ ...f, provider: 'gmail' })),
          ...outlookData.map(f => ({ ...f, provider: 'outlook' })),
        ];

        setFolders(merged);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch folders');
    } finally {
      setLoading(false);
    }
  }, [provider]);

  useEffect(() => {
    fetchFolders();
  }, [fetchFolders]);

  return { folders, loading, error, refetch: fetchFolders };
}
