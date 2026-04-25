//eventsService.ts
//Axios functions for the /events API endpoints.

import api from './api';
import type { CalendarEvent } from '../types/calendar';

//GET /events?year=&month=
//Fetches all events for a given year and month.
export const getEvents = (year: number, month: number) =>
  api.get<never, CalendarEvent[]>('/events', { params: { year, month } });

//DELETE /events/:id
//Deletes a specific event by ID.
export const deleteEvent = (id: number) =>
  api.delete<never, { deleted: boolean }>(`/events/${id}`);
