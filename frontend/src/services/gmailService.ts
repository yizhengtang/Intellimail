import api from './api';
import type { EmailSummary, EmailDetail, ComposeEmailPayload, ReplyPayload, Folder, DraftSummary, DraftDetail } from '../types/email';

//Gmail API Service
//Each function maps to one endpoint in backend/app/routers/gmail.py
//All endpoints are prefixed with /gmail

//Emails

//GET /gmail/emails
//This function list emails from a folder
export const getEmails = (folder: string = 'INBOX', maxResults: number = 10) =>
  api.get<never, EmailSummary[]>('/gmail/emails', {
    params: {
      folder,
      max_results: maxResults
    }
  });

//GET /gmail/emails/:id
//This function retrieves the full email details
export const getEmailDetail = (messageId: string) =>
  api.get<never, EmailDetail>(`/gmail/emails/${messageId}`);

//GET /gmail/emails/:id/conversations
//This function retrieves the conversation thread for a specific email
export const getConversations = (messageId: string) =>
  api.get<never, EmailDetail[]>(`/gmail/emails/${messageId}/conversations`);

//Search

//GET /gmail/search
//This function searches individual emails by query
export const searchEmails = (query: string, maxResults: number = 5) =>
  api.get<never, EmailSummary[]>('/gmail/search', {
    params: {
      query,
      max_results: maxResults
    }
  });

//GET /gmail/search/conversations
//This function searches by conversation threads
export const searchConversations = (query: string, maxResults: number = 5) =>
  api.get<never, EmailSummary[]>('/gmail/search/conversations', {
    params: {
      query,
      max_results: maxResults
    }
  });

//Send & Reply

//POST /gmail/send
//This function sends a new email
export const sendEmail = (payload: ComposeEmailPayload) =>
  api.post('/gmail/send', null, {
    params: {
      to: payload.to,
      subject: payload.subject,
      body: payload.body,
      body_type: payload.body_type || 'plain'
    }
  });

//POST /gmail/emails/:id/reply
//This function replies to the sender only
export const replyEmail = (messageId: string, payload: ReplyPayload) =>
  api.post(`/gmail/emails/${messageId}/reply`, null, {
    params: {
      body: payload.body,
      body_type: payload.body_type || 'plain'
    }
  });

//POST /gmail/emails/:id/reply-all
//This function replies to all recipients
export const replyAllEmail = (messageId: string, payload: ReplyPayload) =>
  api.post(`/gmail/emails/${messageId}/reply-all`, null, {
    params: {
      body: payload.body,
      body_type: payload.body_type || 'plain'
    }
  });

//Attachments

//GET /gmail/emails/:id/attachments/download
//This function downloads attachments from one email
export const downloadAttachments = (messageId: string) =>
  api.get(`/gmail/emails/${messageId}/attachments/download`);

//GET /gmail/emails/:id/attachments/download-all
//This function downloads all attachments from the conversation thread
export const downloadAllAttachments = (messageId: string) =>
  api.get(`/gmail/emails/${messageId}/attachments/download-all`);

//Trash

//POST /gmail/emails/:id/trash
//This function moves an email to trash
export const trashEmail = (messageId: string) =>
  api.post(`/gmail/emails/${messageId}/trash`);

//POST /gmail/emails/:id/untrash
//This function restores an email from trash
export const untrashEmail = (messageId: string) =>
  api.post(`/gmail/emails/${messageId}/untrash`);

//POST /gmail/emails/trash/batch
//This function trashes multiple emails at once
export const batchTrash = (messageIds: string[]) =>
  api.post('/gmail/emails/trash/batch', {
    message_ids: messageIds
  });

//POST /gmail/emails/untrash/batch
//This function restores multiple emails from trash
export const batchUntrash = (messageIds: string[]) =>
  api.post('/gmail/emails/untrash/batch', {
    message_ids: messageIds
  });

//DELETE /gmail/emails/:id
//This function permanently deletes an email
export const deleteEmail = (messageId: string) =>
  api.delete(`/gmail/emails/${messageId}`);

//POST /gmail/trash/empty
//This function empties the trash folder
export const emptyTrash = () =>
  api.post('/gmail/trash/empty');

//Labels

//GET /gmail/labels
//This function lists all labels
export const getLabels = () =>
  api.get<never, Folder[]>('/gmail/labels');

//GET /gmail/labels/:id
//This function gets the details of a specific label
export const getLabelDetail = (labelId: string) =>
  api.get<never, Folder>(`/gmail/labels/${labelId}`);

//POST /gmail/labels
//This function creates a new label
export const createLabel = (name: string) =>
  api.post('/gmail/labels', null, {
    params: { name }
  });

//PATCH /gmail/labels/:id
//This function updates an existing label
export const updateLabel = (
  labelId: string,
  updates: {
    name?: string;
    label_list_visibility?: string;
    message_list_visibility?: string;
  }
) =>
  api.patch(`/gmail/labels/${labelId}`, updates);

//DELETE /gmail/labels/:id
//This function deletes a label
export const deleteLabel = (labelId: string) =>
  api.delete(`/gmail/labels/${labelId}`);

//POST /gmail/emails/:id/labels
//This function adds or removes labels from an email
export const modifyEmailLabels = (
  messageId: string,
  addLabels?: string[],
  removeLabels?: string[]
) =>
  api.post(`/gmail/emails/${messageId}/labels`, {
    add_labels: addLabels,
    remove_labels: removeLabels
  });

//Drafts

//GET /gmail/drafts
//This function lists all drafts
export const getDrafts = (maxResults: number = 10) =>
  api.get<never, DraftSummary[]>('/gmail/drafts', {
    params: {
      max_results: maxResults
    }
  });

//GET /gmail/drafts/:id
//This function gets the details of a specific draft
export const getDraftDetail = (draftId: string) =>
  api.get<never, DraftDetail>(`/gmail/drafts/${draftId}`);

//POST /gmail/drafts
//This function creates a new draft
export const createDraft = (payload: ComposeEmailPayload) =>
  api.post('/gmail/drafts', null, {
    params: {
      to: payload.to,
      subject: payload.subject,
      body: payload.body,
      body_type: payload.body_type || 'plain'
    }
  });

//POST /gmail/drafts/:id/send
//This function sends an existing draft
export const sendDraft = (draftId: string) =>
  api.post(`/gmail/drafts/${draftId}/send`);

//DELETE /gmail/drafts/:id
//This function deletes a draft
export const deleteDraft = (draftId: string) =>
  api.delete(`/gmail/drafts/${draftId}`);
