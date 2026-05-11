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

type AiResult = AiSummary | AiCategory | AiEvents | AiReply | AiPriority | AiSpam | null;
type Action = 'summarize' | 'categorize' | 'events' | 'reply' | 'priority' | 'spam';

const FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";

const ACTIONS: { key: Action; label: string; icon: React.ReactNode }[] = [
  {
    key: 'summarize',
    label: 'Summarize',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="21" y1="6" x2="3" y2="6" /><line x1="15" y1="12" x2="3" y2="12" /><line x1="17" y1="18" x2="3" y2="18" />
      </svg>
    ),
  },
  {
    key: 'categorize',
    label: 'Categorize',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z" /><line x1="7" y1="7" x2="7.01" y2="7" />
      </svg>
    ),
  },
  {
    key: 'events',
    label: 'Extract Events',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
      </svg>
    ),
  },
  {
    key: 'reply',
    label: 'Generate Reply',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>
    ),
  },
  {
    key: 'priority',
    label: 'Check Priority',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    key: 'spam',
    label: 'Spam Check',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
    ),
  },
];

const PRIORITY_COLORS: Record<number, string> = {
  5: '#ef4444', 4: '#f97316', 3: '#f59e0b', 2: '#3b82f6', 1: '#6b7280',
};

export default function AiPanel({ provider, messageId }: AiPanelProps) {
  const [activeAction, setActiveAction] = useState<Action | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AiResult>(null);
  const [error, setError] = useState<string | null>(null);

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

  function renderResult() {
    if (loading) {
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#9ca3af', fontSize: 13 }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ animation: 'spin 1s linear infinite' }}>
            <path d="M21 12a9 9 0 11-6.219-8.56" />
          </svg>
          Analysing...
        </div>
      );
    }

    if (error) {
      return (
        <div style={{ fontSize: 13, color: '#ef4444', display: 'flex', alignItems: 'center', gap: 6 }}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {error}
        </div>
      );
    }

    if (!result) return null;

    if (activeAction === 'summarize') {
      const r = result as AiSummary;
      return <p style={{ fontSize: 14, lineHeight: 1.6, color: '#374151', margin: 0 }}>{r.summary}</p>;
    }

    if (activeAction === 'categorize') {
      const r = result as AiCategory;
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 13, color: '#6b7280' }}>Category</span>
          <span style={{
            fontSize: 12, fontWeight: 600,
            padding: '3px 10px', borderRadius: 20,
            backgroundColor: '#eff6ff', color: '#2563eb',
            textTransform: 'capitalize',
          }}>
            {r.category}
          </span>
        </div>
      );
    }

    if (activeAction === 'events') {
      const r = result as AiEvents;
      if (r.events.length === 0) return <p style={{ fontSize: 13, color: '#6b7280', margin: 0 }}>No events found in this email.</p>;
      return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {r.events.map((ev, i) => (
            <div key={i} style={{
              padding: '10px 14px',
              borderRadius: 8,
              backgroundColor: '#f9fafb',
              border: '1px solid #f3f4f6',
            }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: 4 }}>
                {ev.type.replace('_', ' ')}
              </div>
              <div style={{ fontSize: 14, color: '#111827', fontWeight: 500 }}>{ev.description}</div>
              {ev.date && <div style={{ fontSize: 12, color: '#9ca3af', marginTop: 4 }}>{ev.date}</div>}
            </div>
          ))}
        </div>
      );
    }

    if (activeAction === 'reply') {
      const r = result as AiReply;
      return (
        <div style={{
          backgroundColor: '#f9fafb',
          border: '1px solid #f3f4f6',
          borderRadius: 8,
          padding: '14px 16px',
          fontSize: 14,
          lineHeight: 1.7,
          color: '#374151',
          whiteSpace: 'pre-wrap',
        }}>
          {r.draft}
        </div>
      );
    }

    if (activeAction === 'priority') {
      const r = result as AiPriority;
      const color = PRIORITY_COLORS[r.score] ?? '#6b7280';
      const labels: Record<number, string> = { 5: 'Urgent', 4: 'High', 3: 'Normal', 2: 'Low', 1: 'Minimal' };
      return (
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 10,
            backgroundColor: color + '18',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 16, fontWeight: 700, color, flexShrink: 0,
          }}>
            {r.score}
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color }}>{labels[r.score] ?? 'Unknown'} Priority</div>
            <div style={{ fontSize: 13, color: '#6b7280', marginTop: 2 }}>{r.reason}</div>
          </div>
        </div>
      );
    }

    if (activeAction === 'spam') {
      const r = result as AiSpam;
      const isSpam = r.is_spam;
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            backgroundColor: isSpam ? '#fef2f2' : '#f0fdf4',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={isSpam ? '#ef4444' : '#22c55e'} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              {isSpam
                ? <><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></>
                : <polyline points="20 6 9 17 4 12" />
              }
            </svg>
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: isSpam ? '#ef4444' : '#22c55e' }}>
              {isSpam ? 'Likely Spam' : 'Not Spam'}
            </div>
            <div style={{ fontSize: 12, color: '#9ca3af' }}>
              {Math.round(r.confidence * 100)}% confidence
            </div>
          </div>
        </div>
      );
    }

    return null;
  }

  return (
    <div style={{
      padding: '24px 40px',
      borderTop: '1px solid #f3f4f6',
      fontFamily: FONT,
    }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: '#9ca3af', letterSpacing: '0.8px', textTransform: 'uppercase', marginBottom: 14 }}>
        AI Actions
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
        {ACTIONS.map(({ key, label, icon }) => {
          const isActive = activeAction === key;
          return (
            <button
              key={key}
              onClick={() => run(key, () => {
                if (key === 'summarize') return summarizeEmail(provider, messageId);
                if (key === 'categorize') return categorizeEmail(provider, messageId);
                if (key === 'events') return extractEvents(provider, messageId);
                if (key === 'reply') return generateReply(provider, messageId);
                if (key === 'priority') return scorePriority(provider, messageId);
                return checkSpam(provider, messageId);
              })}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                padding: '7px 14px',
                fontSize: 13,
                fontWeight: 500,
                fontFamily: FONT,
                cursor: 'pointer',
                borderRadius: 8,
                border: isActive ? '1px solid #2563eb' : '1px solid #e5e7eb',
                backgroundColor: isActive ? '#eff6ff' : '#f9fafb',
                color: isActive ? '#2563eb' : '#374151',
                transition: 'all 0.15s ease',
              }}
            >
              {icon}
              {label}
            </button>
          );
        })}
      </div>

      {renderResult()}

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
