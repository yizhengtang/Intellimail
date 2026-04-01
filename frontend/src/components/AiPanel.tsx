//AiPanel.tsx
//AI action panel — renders 6 agent buttons for the open email and displays each result inline.

import { useState } from 'react';
import {
  summarizeEmail,
  categorizeEmail,
  extractEvents,
  generateReply,
  scorePriority,
  checkSpam,
} from '../services/aiService';
import type { AiSummary, AiCategory, AiEvents, AiReply, AiPriority, AiSpam } from '../types/ai';

interface AiPanelProps {
  provider: string;
  messageId: string;
}

//Union of every possible result shape — only one action is active at a time.
type AiResult = AiSummary | AiCategory | AiEvents | AiReply | AiPriority | AiSpam | null;

type Action = 'summarize' | 'categorize' | 'events' | 'reply' | 'priority' | 'spam';

//Shared button style — extracted as a constant to avoid repetition.
const btnStyle: React.CSSProperties = {
  padding: '6px 12px',
  cursor: 'pointer',
  border: '1px solid #ccc',
  borderRadius: 4,
  backgroundColor: 'transparent',
  fontSize: 13,
};

//AiPanel renders 6 AI action buttons for a single email.
//Each button calls the relevant service function, shows a loading state, then displays the result.
export default function AiPanel({ provider, messageId }: AiPanelProps) {
  const [activeAction, setActiveAction] = useState<Action | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AiResult>(null);
  const [error, setError] = useState<string | null>(null);

  //Shared runner — clears previous result, calls the service function, stores the result.
  async function run(action: Action, call: () => Promise<AiResult>) {
    setActiveAction(action);
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const data = await call();
      setResult(data);
    } catch {
      setError('Request failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  //Renders the result section based on which action was last run.
  function renderResult() {
    if (loading) return <p style={{ color: '#888', fontSize: 13 }}>Loading...</p>;
    if (error) return <p style={{ color: '#cc0000', fontSize: 13 }}>{error}</p>;
    if (!result) return null;

    if (activeAction === 'summarize') {
      const r = result as AiSummary;
      return <p style={{ fontSize: 13 }}>{r.summary}</p>;
    }

    if (activeAction === 'categorize') {
      const r = result as AiCategory;
      return <p style={{ fontSize: 13 }}>Category: <strong>{r.category}</strong></p>;
    }

    if (activeAction === 'events') {
      const r = result as AiEvents;
      if (r.events.length === 0) return <p style={{ fontSize: 13 }}>No events found.</p>;
      return (
        <ul style={{ paddingLeft: 16, fontSize: 13, margin: '8px 0' }}>
          {r.events.map((ev, i) => (
            <li key={i}>
              <strong>{ev.type}</strong> — {ev.date}: {ev.description}
            </li>
          ))}
        </ul>
      );
    }

    if (activeAction === 'reply') {
      const r = result as AiReply;
      return <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: 13 }}>{r.draft}</pre>;
    }

    if (activeAction === 'priority') {
      const r = result as AiPriority;
      return (
        <p style={{ fontSize: 13 }}>
          Priority score: <strong>{r.score}/10</strong> — {r.reason}
        </p>
      );
    }

    if (activeAction === 'spam') {
      const r = result as AiSpam;
      return (
        <p style={{ fontSize: 13 }}>
          {r.is_spam ? '⚠ Likely spam' : '✓ Not spam'} (confidence: {Math.round(r.confidence * 100)}%)
        </p>
      );
    }

    return null;
  }

  return (
    <div style={{ padding: '16px 24px', borderTop: '1px solid #e0e0e0' }}>
      <p style={{ fontWeight: 600, marginBottom: 10, fontSize: 13 }}>AI Actions</p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 12 }}>
        <button style={btnStyle} onClick={() => run('summarize', () => summarizeEmail(provider, messageId))}>
          Summarize
        </button>
        <button style={btnStyle} onClick={() => run('categorize', () => categorizeEmail(provider, messageId))}>
          Categorize
        </button>
        <button style={btnStyle} onClick={() => run('events', () => extractEvents(provider, messageId))}>
          Extract Events
        </button>
        <button style={btnStyle} onClick={() => run('reply', () => generateReply(provider, messageId))}>
          Generate Reply
        </button>
        <button style={btnStyle} onClick={() => run('priority', () => scorePriority(provider, messageId))}>
          Check Priority
        </button>
        <button style={btnStyle} onClick={() => run('spam', () => checkSpam(provider, messageId))}>
          Spam Check
        </button>
      </div>

      {renderResult()}
    </div>
  );
}
