//ComposeForm.tsx
//Reusable email compose form — To, Subject, Body fields with a provider selector.

import { useState } from 'react';
import type { Provider } from '../types/email';

interface ComposeFormProps {
  defaultProvider: Provider;
  sending: boolean;
  onSend: (data: { to: string; subject: string; body: string; provider: Provider }) => void;
}

//This component manages its own form state (to, subject, body, provider).
export default function ComposeForm({ defaultProvider, sending, onSend }: ComposeFormProps) {
  const [to, setTo] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [provider, setProvider] = useState<Provider>(
    defaultProvider === 'unified' ? 'gmail' : defaultProvider
  );

  return (
    <form onSubmit={e => { e.preventDefault(); onSend({ to, subject, body, provider }); }} style={{ padding: 24 }}>
      <h2>Compose Email</h2>

      <div style={{ marginBottom: 12 }}>
        <label>Send from: </label>
        <select
          value={provider}
          onChange={e => setProvider(e.target.value as Provider)}
          style={{ padding: '6px 8px' }}
        >
          <option value="gmail">Gmail</option>
          <option value="outlook">Outlook</option>
        </select>
      </div>

      <div style={{ marginBottom: 12 }}>
        <input
          type="email"
          placeholder="To"
          value={to}
          onChange={e => setTo(e.target.value)}
          required
          style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <input
          type="text"
          placeholder="Subject"
          value={subject}
          onChange={e => setSubject(e.target.value)}
          required
          style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box' }}
        />
      </div>

      <div style={{ marginBottom: 12 }}>
        <textarea
          placeholder="Write your email..."
          value={body}
          onChange={e => setBody(e.target.value)}
          required
          rows={12}
          style={{ width: '100%', padding: '8px 12px', boxSizing: 'border-box', resize: 'vertical' }}
        />
      </div>

      <button
        type="submit"
        disabled={sending}
        style={{
          padding: '10px 24px',
          cursor: sending ? 'not-allowed' : 'pointer',
          backgroundColor: '#2185d0',
          color: 'white',
          border: 'none',
          borderRadius: 4,
        }}
      >
        {sending ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
}
