//teams.ts
//TypeScript interfaces for Microsoft Teams data returned by the /teams/* API endpoints.
//These are Teams-native types — they do not share the EmailSummary or EmailDetail shape.

//TeamsChat is the shape of one chat from GET /teams/chats.
export interface TeamsChat {
  id: string;
  topic: string;            // group chat name, or "Chat with {name}" for 1:1 chats
  chat_type: string;        // "oneOnOne" | "group"
  last_sender: string;      // display name of the last message sender
  last_message: string;     // plain text preview of the last message
  last_message_time: string; // ISO datetime string
  member_count: number;
}

//TeamsMessage is the shape of one message from GET /teams/chats/{id}/messages.
export interface TeamsMessage {
  id: string;
  sender_name: string;
  content: string;
  content_type: string;     // "text" | "html"
  created_at: string;       // ISO datetime string
  has_attachments: boolean;
}
