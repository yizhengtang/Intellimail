//TeamsAiPanel.tsx
//AI action panel for a Teams chat thread — 4 agent buttons and an inline result area.
//When "Suggest Reply" runs, the draft is passed up to TeamsChatPage via onReplyDraft
//so it pre-fills the send textarea for the user to edit before sending.

import { useState } from 'react';
import {
  summarizeChat,
  generateChatReply,
  extractChatEvents,
  scoreChatPriority,
} from '../services/aiService';
import type { AiSummary, AiReply, AiEvents, AiPriority } from '../types/ai';

interface TeamsAiPanelProps {
  chatId: string;
  onReplyDraft: (draft: string) => void;
}

type Action = 'summarize' | 'reply' | 'events' | 'priority';
type AiResult = AiSummary | AiReply | AiEvents | AiPriority | null;

//Shared button style — same pattern as AiPanel.tsx.
const btnStyle: React.CSSProperties = {
  padding: '6px 12px',
  cursor: 'pointer',
  border: '1px solid #ccc',
  borderRadius: 4,
  backgroundColor: 'transparent',
  fontSize: 13,
};

//TeamsAiPanel renders 4 AI action buttons for a single Teams chat thread.
//Each button calls the relevant service function, shows a loading state, then displays the result.
export default function TeamsAiPanel({ chatId, onReplyDraft }: TeamsAiPanelProps) {
  const [activeAction, setActiveAction] = useState<Action | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AiResult>(null);
  const [error, setError] = useState<string | null>(null);

  //Shared runner — clears previous result, calls the service function, stores the result.
  //If the action is "reply", the draft is also passed up to the parent page to pre-fill the send box.
  async function run(action: Action, call: () => Promise<AiResult>) {
    setActiveAction(action);
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const data = await call();
      setResult(data);
      if (action === 'reply' && data) {
        onReplyDraft((data as AiReply).draft);
      }
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

    if (activeAction === 'reply') {
      const r = result as AiReply;
      return (
        <div>
          <p style={{ fontSize: 12, color: '#888', marginBottom: 4 }}>Draft pre-filled in the send box below.</p>
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: 13 }}>{r.draft}</pre>
        </div>
      );
    }

    if (activeAction === 'events') {
      const r = result as AiEvents;
      if (r.events.length === 0) return <p style={{ fontSize: 13 }}>No events found.</p>;
      return (
        <ul style={{ paddingLeft: 16, fontSize: 13, margin: '8px 0' }}>
          {r.events.map((ev, i) => (
            <li key={i}>
              <strong>{ev.type}</strong>{ev.date ? ` — ${ev.date}` : ''}: {ev.description}
            </li>
          ))}
        </ul>
      );
    }

    if (activeAction === 'priority') {
      const r = result as AiPriority;
      return (
        <p style={{ fontSize: 13 }}>
          Priority: <strong>{r.score}/5</strong> — {r.reason}
        </p>
      );
    }

    return null;
  }

  return (
    <div style={{ borderBottom: '1px solid #e0e0e0', padding: '16px 24px' }}>
      <p style={{ fontWeight: 600, marginBottom: 10, fontSize: 13 }}>AI Actions</p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 12 }}>
        <button style={btnStyle} onClick={() => run('summarize', () => summarizeChat(chatId))}>
          Summarize
        </button>
        <button style={btnStyle} onClick={() => run('reply', () => generateChatReply(chatId))}>
          Suggest Reply
        </button>
        <button style={btnStyle} onClick={() => run('events', () => extractChatEvents(chatId))}>
          Find Events
        </button>
        <button style={btnStyle} onClick={() => run('priority', () => scoreChatPriority(chatId))}>
          Check Priority
        </button>
      </div>

      {renderResult()}
    </div>
  );
}
