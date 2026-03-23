//useSearch.ts
//Custom hook that searches emails based on the active provider and a query string.

import { useState, useEffect, useCallback } from 'react';
import type { EmailSummary } from '../types/email';
import { useProvider } from '../context/ProviderContext';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';

//This hook takes a search query and calls the correct search endpoint.
//When the query is empty, it returns an empty array and does not call any API.
//For 'unified' mode, it searches both providers in parallel and merges results.
export function useSearch(query: string) {
  const { provider } = useProvider();
  const [results, setResults] = useState<EmailSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async () => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (provider === 'gmail') {
        const data = await gmailService.searchEmails(query);
        setResults(data.map(e => ({ ...e, provider: 'gmail' as const })));

      } else if (provider === 'outlook') {
        const data = await outlookService.searchEmails(query);
        setResults(data.map(e => ({ ...e, provider: 'outlook' as const })));

      } else {
        const [gmailData, outlookData] = await Promise.all([
          gmailService.searchEmails(query),
          outlookService.searchEmails(query),
        ]);

        const merged = [
          ...gmailData.map(e => ({ ...e, provider: 'gmail' as const })),
          ...outlookData.map(e => ({ ...e, provider: 'outlook' as const })),
        ];

        merged.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
        setResults(merged);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [query, provider]);

  useEffect(() => {
    search();
  }, [search]);

  return { results, loading, error };
}
