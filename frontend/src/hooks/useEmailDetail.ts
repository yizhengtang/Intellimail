//useEmailDetail.ts
//Custom hook that fetches the full detail of a single email by provider and message ID.

import { useState, useEffect, useCallback } from 'react';
import type { EmailDetail } from '../types/email';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';

//This hook takes the provider and messageId directly as parameters.
export function useEmailDetail(provider: string, messageId: string) {
  const [email, setEmail] = useState<EmailDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDetail = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (provider === 'gmail') {
        const data = await gmailService.getEmailDetail(messageId);
        setEmail(data);
      } else if (provider === 'outlook') {
        const data = await outlookService.getEmailDetail(messageId);
        setEmail(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch email detail');
    } finally {
      setLoading(false);
    }
  }, [provider, messageId]);

  useEffect(() => {
    fetchDetail();
  }, [fetchDetail]);

  return { email, loading, error, refetch: fetchDetail };
}
