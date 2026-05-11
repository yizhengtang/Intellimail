//calendar.ts
//TypeScript interface for a calendar event returned by the /events API.

export interface CalendarEvent {
  id: number;
  title: string;
  event_date: string;        // YYYY-MM-DD
  event_time?: string;       // HH:MM — nullable
  description?: string;      // event type: meeting | deadline | action_item | reminder
  provider: 'gmail' | 'outlook' | 'teams';
  source_email_id: string;
  sender_name?: string;
}
