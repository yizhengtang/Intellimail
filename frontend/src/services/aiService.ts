//aiService.ts
//All AI API call functions — each maps to one endpoint in backend/app/routers/ai.py.
//All endpoints are prefixed with /ai.

import api from './api';
import type {
  AiStatus,
  AiIngestResult,
  AiSummary,
  AiCategory,
  AiEvents,
  AiReply,
  AiPriority,
  AiSpam,
  AiChatResponse,
  ChatMessage,
} from '../types/ai';

//Sync

//POST /ai/ingest/:provider
//Pulls emails from the provider and indexes them into ChromaDB.
export const ingestEmails = (provider: string, maxResults: number = 20) =>
  api.post<never, AiIngestResult>(`/ai/ingest/${provider}`, null, {
    params: { max_results: maxResults },
  });

//GET /ai/status
//Returns the count of indexed emails per provider.
export const getAiStatus = () =>
  api.get<never, AiStatus>('/ai/status');

//Email agents

//POST /ai/emails/:provider/:id/summarize
export const summarizeEmail = (provider: string, messageId: string) =>
  api.post<never, AiSummary>(`/ai/emails/${provider}/${messageId}/summarize`);

//POST /ai/emails/:provider/:id/categorize
export const categorizeEmail = (provider: string, messageId: string) =>
  api.post<never, AiCategory>(`/ai/emails/${provider}/${messageId}/categorize`);

//POST /ai/emails/:provider/:id/events
export const extractEvents = (provider: string, messageId: string) =>
  api.post<never, AiEvents>(`/ai/emails/${provider}/${messageId}/events`);

//POST /ai/emails/:provider/:id/reply
export const generateReply = (provider: string, messageId: string) =>
  api.post<never, AiReply>(`/ai/emails/${provider}/${messageId}/reply`);

//POST /ai/emails/:provider/:id/priority
export const scorePriority = (provider: string, messageId: string) =>
  api.post<never, AiPriority>(`/ai/emails/${provider}/${messageId}/priority`);

//POST /ai/emails/:provider/:id/spam
export const checkSpam = (provider: string, messageId: string) =>
  api.post<never, AiSpam>(`/ai/emails/${provider}/${messageId}/spam`);

//Teams chat agents

//POST /ai/chats/:chatId/summarize
export const summarizeChat = (chatId: string) =>
  api.post<never, AiSummary>(`/ai/chats/${chatId}/summarize`);

//POST /ai/chats/:chatId/reply
export const generateChatReply = (chatId: string) =>
  api.post<never, AiReply>(`/ai/chats/${chatId}/reply`);

//POST /ai/chats/:chatId/events
export const extractChatEvents = (chatId: string) =>
  api.post<never, AiEvents>(`/ai/chats/${chatId}/events`);

//POST /ai/chats/:chatId/priority
export const scoreChatPriority = (chatId: string) =>
  api.post<never, AiPriority>(`/ai/chats/${chatId}/priority`);

//Chat

//POST /ai/chat
//Sends a user message and conversation history to the chat agent.
export const sendChatMessage = (message: string, history: ChatMessage[]) =>
  api.post<never, AiChatResponse>('/ai/chat', { message, history });
