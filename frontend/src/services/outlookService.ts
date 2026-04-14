import api from './api';
import type { EmailSummary, EmailDetail, ComposeEmailPayload, ReplyPayload, Folder, DraftSummary, DraftDetail, AttachmentInfo } from '../types/email';

//Outlook API Service
//Each function maps to one endpoint in backend/app/routers/outlook.py
//All endpoints are prefixed with /outlook

//Emails

//GET /outlook/emails
//This function lists emails from a folder
export const getEmails = (folder: string = 'inbox', maxResults: number = 10) =>
  api.get<never, EmailSummary[]>('/outlook/emails', {
    params: {
      folder,
      max_results: maxResults
    }
  });

//GET /outlook/emails/:id
//This function retrieves the full email details
export const getEmailDetail = (messageId: string) =>
  api.get<never, EmailDetail>(`/outlook/emails/${messageId}`);

//GET /outlook/emails/:id/conversations
//This function retrieves the conversation thread for a specific email
export const getConversations = (messageId: string) =>
  api.get<never, EmailDetail[]>(`/outlook/emails/${messageId}/conversations`);

//Search

//GET /outlook/search
//This function searches individual emails by query
export const searchEmails = (query: string, maxResults: number = 5) =>
  api.get<never, EmailSummary[]>('/outlook/search', {
    params: {
      query,
      max_results: maxResults
    }
  });

//GET /outlook/search/conversations
//This function searches by conversation threads
export const searchConversations = (query: string, maxResults: number = 5) =>
  api.get<never, EmailSummary[]>('/outlook/search/conversations', {
    params: {
      query,
      max_results: maxResults
    }
  });

//Send & Reply

//POST /outlook/send
//This function sends a new email
export const sendEmail = (payload: ComposeEmailPayload) =>
  api.post('/outlook/send', null, {
    params: {
      to: payload.to,
      subject: payload.subject,
      body: payload.body,
      body_type: payload.body_type || 'Text'
    }
  });

//POST /outlook/emails/:id/reply
//This function replies to the sender only
export const replyEmail = (messageId: string, payload: ReplyPayload) =>
  api.post(`/outlook/emails/${messageId}/reply`, null, {
    params: {
      body: payload.body,
      body_type: payload.body_type || 'Text'
    }
  });

//POST /outlook/emails/:id/reply-all
//This function replies to all recipients
export const replyAllEmail = (messageId: string, payload: ReplyPayload) =>
  api.post(`/outlook/emails/${messageId}/reply-all`, null, {
    params: {
      body: payload.body,
      body_type: payload.body_type || 'Text'
    }
  });

//Attachments

//GET /outlook/emails/:id/attachments
//Returns the metadata list (id, filename, content_type, size) for all attachments in an email
export const getAttachments = (messageId: string) =>
  api.get<never, AttachmentInfo[]>(`/outlook/emails/${messageId}/attachments`);

//Constructs the direct URL for a single attachment.
//Used in <img src> for images and <a href> for document downloads — the browser requests it directly.
export const getAttachmentUrl = (messageId: string, attachmentId: string) =>
  `http://localhost:8000/outlook/emails/${messageId}/attachments/${attachmentId}`;

//GET /outlook/emails/:id/attachments/download
//This function downloads attachments from one email
export const downloadAttachments = (messageId: string) =>
  api.get(`/outlook/emails/${messageId}/attachments/download`);

//GET /outlook/emails/:id/attachments/download-all
//This function downloads all attachments from the conversation thread
export const downloadAllAttachments = (messageId: string) =>
  api.get(`/outlook/emails/${messageId}/attachments/download-all`);

//Mark Read/Unread (Outlook only)

//PATCH /outlook/emails/:id/read
//This function marks an email as read
export const markAsRead = (messageId: string) =>
  api.patch(`/outlook/emails/${messageId}/read`);

//PATCH /outlook/emails/:id/unread
//This function marks an email as unread
export const markAsUnread = (messageId: string) =>
  api.patch(`/outlook/emails/${messageId}/unread`);

//Move (Outlook only)

//POST /outlook/emails/:id/move
//This function moves an email to a different folder
export const moveToFolder = (messageId: string, destinationId: string) =>
  api.post(`/outlook/emails/${messageId}/move`, {
    destination_id: destinationId
  });

//Trash

//POST /outlook/emails/:id/trash
//This function moves an email to trash
export const trashEmail = (messageId: string) =>
  api.post(`/outlook/emails/${messageId}/trash`);

//POST /outlook/emails/:id/untrash
//This function restores an email from trash
export const untrashEmail = (messageId: string) =>
  api.post(`/outlook/emails/${messageId}/untrash`);

//POST /outlook/emails/trash/batch
//This function trashes multiple emails at once
export const batchTrash = (messageIds: string[]) =>
  api.post('/outlook/emails/trash/batch', {
    message_ids: messageIds
  });

//POST /outlook/emails/untrash/batch
//This function restores multiple emails from trash
export const batchUntrash = (messageIds: string[]) =>
  api.post('/outlook/emails/untrash/batch', {
    message_ids: messageIds
  });

//DELETE /outlook/emails/:id
//This function permanently deletes an email
export const deleteEmail = (messageId: string) =>
  api.delete(`/outlook/emails/${messageId}`);

//POST /outlook/trash/empty
//This function empties the trash folder
export const emptyTrash = () =>
  api.post('/outlook/trash/empty');

//GET /outlook/trash
//This function gets all trashed emails (Outlook only)
export const getTrash = (maxResults: number = 10) =>
  api.get<never, EmailSummary[]>('/outlook/trash', {
    params: {
      max_results: maxResults
    }
  });

//Folders

//GET /outlook/folders
//This function lists all folders
export const getFolders = (includeHidden: boolean = false) =>
  api.get<never, Folder[]>('/outlook/folders', {
    params: {
      include_hidden: includeHidden
    }
  });

//GET /outlook/folders/:id
//This function gets the details of a specific folder
export const getFolderDetail = (folderId: string) =>
  api.get<never, Folder>(`/outlook/folders/${folderId}`);

//POST /outlook/folders
//This function creates a new folder
export const createFolder = (displayName: string) =>
  api.post('/outlook/folders', null, {
    params: {
      display_name: displayName
    }
  });

//POST /outlook/folders/:id/child
//This function creates a child folder inside a parent folder (Outlook only)
export const createChildFolder = (parentFolderId: string, displayName: string) =>
  api.post(`/outlook/folders/${parentFolderId}/child`, null, {
    params: {
      display_name: displayName
    }
  });

//PATCH /outlook/folders/:id
//This function updates an existing folder
export const updateFolder = (folderId: string, displayName: string) =>
  api.patch(`/outlook/folders/${folderId}`, null, {
    params: {
      display_name: displayName
    }
  });

//DELETE /outlook/folders/:id
//This function deletes a folder
export const deleteFolder = (folderId: string) =>
  api.delete(`/outlook/folders/${folderId}`);

//Drafts

//GET /outlook/drafts
//This function lists all drafts
export const getDrafts = (maxResults: number = 10) =>
  api.get<never, DraftSummary[]>('/outlook/drafts', {
    params: {
      max_results: maxResults
    }
  });

//GET /outlook/drafts/:id
//This function gets the details of a specific draft
export const getDraftDetail = (draftId: string) =>
  api.get<never, DraftDetail>(`/outlook/drafts/${draftId}`);

//POST /outlook/drafts
//This function creates a new draft
export const createDraft = (payload: ComposeEmailPayload) =>
  api.post('/outlook/drafts', null, {
    params: {
      to: payload.to,
      subject: payload.subject,
      body: payload.body,
      body_type: payload.body_type || 'Text'
    }
  });

//PATCH /outlook/drafts/:id
//This function updates an existing draft (Outlook only)
export const updateDraft = (
  draftId: string,
  updates: {
    subject?: string;
    body?: string;
    body_type?: string;
    to?: string;
    cc?: string;
    bcc?: string;
  }
) =>
  api.patch(`/outlook/drafts/${draftId}`, updates);

//POST /outlook/drafts/:id/send
//This function sends an existing draft
export const sendDraft = (draftId: string) =>
  api.post(`/outlook/drafts/${draftId}/send`);

//DELETE /outlook/drafts/:id
//This function deletes a draft
export const deleteDraft = (draftId: string) =>
  api.delete(`/outlook/drafts/${draftId}`);
