//ai.ts
//TypeScript interfaces for all /ai/* API responses and the chat message shape.

//ChatMessage is one turn in the conversation history sent to /ai/chat.
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface AiStatus {
  gmail: number;
  outlook: number;
  teams: number;
  total: number;
}

export interface AiIngestResult {
  indexed: number;
  skipped: number;
}

export interface AiEvent {
  type: string;
  date: string;
  description: string;
}

export interface AiSummary { summary: string; }
export interface AiCategory { category: string; }
export interface AiEvents { events: AiEvent[]; }
export interface AiReply { draft: string; }
export interface AiPriority { score: number; reason: string; }
export interface AiSpam { is_spam: boolean; confidence: number; }
export interface AiChatResponse { response: string; }
