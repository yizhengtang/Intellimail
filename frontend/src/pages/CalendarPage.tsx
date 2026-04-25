//CalendarPage.tsx
//Unified calendar view — displays extracted events from all providers in a monthly grid.

import { useState, useEffect } from 'react';
import type { CalendarEvent } from '../types/calendar';
import { getEvents, deleteEvent } from '../services/eventsService';

const DAY_HEADERS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

const PROVIDER_COLORS: Record<string, string> = {
  gmail: '#EA4335',
  outlook: '#0078D4',
  teams: '#6264A7',
};

//Returns the number of days in a given month.
function daysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}

//Returns the day-of-week index (0=Mon … 6=Sun) for the 1st of a given month.
//JavaScript's getDay() returns 0=Sun so we rotate it to Mon-based.
function firstWeekdayOfMonth(year: number, month: number): number {
  const day = new Date(year, month - 1, 1).getDay();
  return day === 0 ? 6 : day - 1;
}

export default function CalendarPage() {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth() + 1);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);

  const todayYear = today.getFullYear();
  const todayMonth = today.getMonth() + 1;
  const todayDate = today.getDate();

  useEffect(() => {
    setLoading(true);
    getEvents(year, month)
      .then(setEvents)
      .catch(() => setEvents([]))
      .finally(() => setLoading(false));
  }, [year, month]);

  function prevMonth() {
    if (month === 1) { setYear(y => y - 1); setMonth(12); }
    else setMonth(m => m - 1);
  }

  function nextMonth() {
    if (month === 12) { setYear(y => y + 1); setMonth(1); }
    else setMonth(m => m + 1);
  }

  async function handleDelete(id: number) {
    await deleteEvent(id);
    setEvents(prev => prev.filter(e => e.id !== id));
    setSelectedEvent(null);
  }

  //Returns events that fall on a specific day.
  function eventsForDay(day: number): CalendarEvent[] {
    const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return events.filter(e => e.event_date === dateStr);
  }

  const totalDays = daysInMonth(year, month);
  const offset = firstWeekdayOfMonth(year, month);
  //Total cells = offset blank cells + day cells, rounded up to a full week row.
  const totalCells = Math.ceil((offset + totalDays) / 7) * 7;

  return (
    <div style={{ padding: '24px', backgroundColor: '#f3f4f6', minHeight: '100%' }}>

      {/* Header — month name + navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <h2 style={{ fontSize: 20, fontWeight: 700, color: '#111827', margin: 0 }}>
          {MONTH_NAMES[month - 1]} {year}
        </h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={prevMonth}
            style={{
              width: 32, height: 32, borderRadius: 8, border: '1px solid #e5e7eb',
              backgroundColor: '#ffffff', cursor: 'pointer', display: 'flex',
              alignItems: 'center', justifyContent: 'center', color: '#374151',
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          </button>
          <button
            onClick={nextMonth}
            style={{
              width: 32, height: 32, borderRadius: 8, border: '1px solid #e5e7eb',
              backgroundColor: '#ffffff', cursor: 'pointer', display: 'flex',
              alignItems: 'center', justifyContent: 'center', color: '#374151',
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          </button>
        </div>
      </div>

      {/* Calendar grid */}
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: 12,
        border: '1px solid #e5e7eb',
        overflow: 'hidden',
      }}>

        {/* Day-of-week headers */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', borderBottom: '1px solid #e5e7eb' }}>
          {DAY_HEADERS.map(d => (
            <div key={d} style={{
              padding: '10px 0',
              textAlign: 'center',
              fontSize: 12,
              fontWeight: 600,
              color: '#6b7280',
            }}>
              {d}
            </div>
          ))}
        </div>

        {/* Day cells */}
        {loading ? (
          <p style={{ padding: 24, color: '#9ca3af', fontSize: 14 }}>Loading...</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)' }}>
            {Array.from({ length: totalCells }).map((_, i) => {
              const day = i - offset + 1;
              const isCurrentMonth = day >= 1 && day <= totalDays;
              const isToday = isCurrentMonth && day === todayDate && month === todayMonth && year === todayYear;
              const dayEvents = isCurrentMonth ? eventsForDay(day) : [];

              return (
                <div
                  key={i}
                  style={{
                    minHeight: 90,
                    padding: '6px 8px',
                    borderRight: (i + 1) % 7 === 0 ? 'none' : '1px solid #f3f4f6',
                    borderBottom: '1px solid #f3f4f6',
                    backgroundColor: isToday ? '#eff6ff' : '#ffffff',
                  }}
                >
                  {isCurrentMonth && (
                    <>
                      {/* Day number */}
                      <div style={{
                        fontSize: 13,
                        fontWeight: isToday ? 700 : 400,
                        color: isToday ? '#2563eb' : '#374151',
                        marginBottom: 4,
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        backgroundColor: isToday ? '#dbeafe' : 'transparent',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}>
                        {day}
                      </div>

                      {/* Event chips */}
                      {dayEvents.map(event => (
                        <div
                          key={event.id}
                          onClick={() => setSelectedEvent(event)}
                          style={{
                            fontSize: 11,
                            fontWeight: 500,
                            color: '#ffffff',
                            backgroundColor: PROVIDER_COLORS[event.provider] ?? '#6b7280',
                            borderRadius: 4,
                            padding: '2px 6px',
                            marginBottom: 2,
                            cursor: 'pointer',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                          }}
                          title={event.title}
                        >
                          {event.event_time && (
                            <span style={{ opacity: 0.85, marginRight: 4 }}>{event.event_time}</span>
                          )}
                          {event.title}
                        </div>
                      ))}
                    </>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Event detail modal */}
      {selectedEvent && (
        <div
          onClick={() => setSelectedEvent(null)}
          style={{
            position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50,
          }}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{
              backgroundColor: '#ffffff', borderRadius: 12, padding: 24,
              width: 360, boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            }}
          >
            {/* Provider tag */}
            <div style={{
              display: 'inline-flex', alignItems: 'center', gap: 5,
              fontSize: 11, fontWeight: 600, color: '#ffffff',
              backgroundColor: PROVIDER_COLORS[selectedEvent.provider] ?? '#6b7280',
              borderRadius: 6, padding: '2px 8px', marginBottom: 12,
            }}>
              {selectedEvent.provider.charAt(0).toUpperCase() + selectedEvent.provider.slice(1)}
            </div>

            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#111827', margin: '0 0 8px' }}>
              {selectedEvent.title}
            </h3>

            {selectedEvent.event_date && (
              <p style={{ fontSize: 13, color: '#6b7280', margin: '0 0 4px' }}>
                📅 {selectedEvent.event_date}{selectedEvent.event_time ? ` at ${selectedEvent.event_time}` : ''}
              </p>
            )}

            {selectedEvent.sender_name && (
              <p style={{ fontSize: 13, color: '#6b7280', margin: '0 0 4px' }}>
                👤 {selectedEvent.sender_name}
              </p>
            )}

            {selectedEvent.description && (
              <p style={{ fontSize: 13, color: '#6b7280', margin: '0 0 16px', textTransform: 'capitalize' }}>
                Type: {selectedEvent.description.replace('_', ' ')}
              </p>
            )}

            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
              <button
                onClick={() => setSelectedEvent(null)}
                style={{
                  padding: '6px 14px', borderRadius: 8, border: '1px solid #e5e7eb',
                  backgroundColor: '#ffffff', fontSize: 13, cursor: 'pointer', color: '#374151',
                }}
              >
                Close
              </button>
              <button
                onClick={() => handleDelete(selectedEvent.id)}
                style={{
                  padding: '6px 14px', borderRadius: 8, border: 'none',
                  backgroundColor: '#ef4444', fontSize: 13, cursor: 'pointer', color: '#ffffff',
                  fontWeight: 600,
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
