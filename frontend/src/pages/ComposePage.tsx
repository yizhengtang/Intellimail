//ComposePage.tsx
//Page for composing and sending a new email.

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProvider } from '../context/ProviderContext';
import ComposeForm from '../components/ComposeForm';
import type { Provider } from '../types/email';
import * as gmailService from '../services/gmailService';
import * as outlookService from '../services/outlookService';

//This page wraps ComposeForm and handles the actual send API call.
//It reads the active provider from context to set the default sender.
//After a successful send, it navigates back to the inbox.
export default function ComposePage() {
  const { provider } = useProvider();
  const navigate = useNavigate();
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async (data: { to: string; subject: string; body: string; provider: Provider }) => {
    setSending(true);
    setError(null);

    try {
      const payload = { to: data.to, subject: data.subject, body: data.body };

      if (data.provider === 'gmail') {
        await gmailService.sendEmail(payload);
      } else {
        await outlookService.sendEmail(payload);
      }

      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send email');
    } finally {
      setSending(false);
    }
  };

  return (
    <div>
      {error && <p style={{ color: 'red', padding: '0 24px' }}>{error}</p>}
      <ComposeForm defaultProvider={provider} sending={sending} onSend={handleSend} />
    </div>
  );
}
