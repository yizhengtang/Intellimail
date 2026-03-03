// Provider type — represents which email service is active
export type Provider = 'gmail' | 'outlook' | 'unified';

//EmailSummary will return a list of emails from the /emails endpoint.
//Both Gmail and Outlook return this same shape from the API
export interface EmailSummary {
  id: string;
  subject: string;
  from: string;
  snippet: string;
  date: string;
  is_read: boolean;
  has_attachments: boolean;
  thread_id?: string;   // Gmail only
  from_name?: string;   // Outlook only
  provider?: Provider;  // Added client-side for unified view
}

// EmailDetail will return the full details of an email from the /emails/:id endpoint.
// Gmail and Outlook have slightly different fields here
export interface EmailDetail {
  id: string;
  subject: string;
  from: string;
  to: string;
  snippet?: string;
  body: string;
  date: string;
  has_attachments: boolean;
  //Gmail-specific
  thread_id?: string;
  starred?: boolean;
  label?: string;
  //Outlook-specific
  from_name?: string;
  cc?: string;
  body_type?: string;
  is_read?: boolean;
  importance?: string;
  flagged?: boolean;
  conversation_id?: string;
}

//ComposeEmailPayload is the request body for the compose email endpoint,.
export interface ComposeEmailPayload {
  to: string;
  subject: string;
  body: string;
  // Gmail: 'plain'/'html', Outlook: 'Text'/'HTML'
  body_type?: string; 
}

// ReplyPayload is the request body for the reply email endpoint.
export interface ReplyPayload {
  body: string;
  body_type?: string;
}

//Folder is the shape of a folder or labek.
export interface Folder {
  id: string;
  name: string;
  // Gmail labels may include these
  type?: string;
  message_count?: number;
  // Outlook folders may include these
  parent_folder_id?: string;
  child_folder_count?: number;
  unread_count?: number;
  total_count?: number;
}

//DraftSummary is the shape of a draft email.
export interface DraftSummary {
  id: string;
  subject?: string;
  to?: string;
  snippet?: string;
  date?: string;
}

//DraftDetail is the shape of a draft email when viewing the full details.
export interface DraftDetail {
  id: string;
  subject: string;
  to: string;
  body: string;
  body_type?: string;
  cc?: string;
  bcc?: string;
}
