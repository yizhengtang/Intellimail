//teamsService.ts
//Teams API service — each function maps to one endpoint in backend/app/routers/teams.py.
//All endpoints are prefixed with /teams.

import api from './api';
import type { TeamsChat, TeamsMessage } from '../types/teams';

//Chats

//GET /teams/chats
//Returns a list of chats the user is part of.
export const listChats = (maxResults: number = 10) =>
  api.get<never, TeamsChat[]>('/teams/chats', { params: { max_results: maxResults } });

//GET /teams/chats/{chatId}/messages
//Returns all messages in a chat, ordered newest-first.
export const getChatMessages = (chatId: string, maxResults: number = 50) =>
  api.get<never, TeamsMessage[]>(`/teams/chats/${chatId}/messages`, { params: { max_results: maxResults } });

//POST /teams/chats/{chatId}/messages
//Sends a plain-text message to an existing chat.
export const sendChatMessage = (chatId: string, body: string) =>
  api.post(`/teams/chats/${chatId}/messages`, { body });

//Teams

//GET /teams/teams
//Returns a list of Teams the user has joined.
export const listJoinedTeams = () =>
  api.get<never, { id: string; name: string }[]>('/teams/teams');

//Ingest

//POST /teams/ingest/{chatId}
//Embeds a chat's messages into ChromaDB for AI use.
export const ingestChat = (chatId: string, maxResults: number = 50) =>
  api.post(`/teams/ingest/${chatId}`, null, { params: { max_results: maxResults } });
