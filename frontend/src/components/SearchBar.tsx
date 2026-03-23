//SearchBar.tsx
//Search input that navigates to the inbox with a query parameter on submit.

import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

//The SearchBar reads the current ?q= param to keep the input in sync with the URL.
//On submit, it navigates to /?q=<query> which InboxPage reads to show search results.
//Clearing the input and submitting navigates back to / (normal inbox).
export default function SearchBar() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [input, setInput] = useState(searchParams.get('q') || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (trimmed) {
      navigate(`/?q=${encodeURIComponent(trimmed)}`);
    } else {
      navigate('/');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8 }}>
      <input
        type="text"
        placeholder="Search emails..."
        value={input}
        onChange={e => setInput(e.target.value)}
        style={{ flex: 1, padding: '8px 12px', border: '1px solid #ccc', borderRadius: 4 }}
      />
      <button
        type="submit"
        style={{
          padding: '8px 16px',
          cursor: 'pointer',
          backgroundColor: '#2185d0',
          color: 'white',
          border: 'none',
          borderRadius: 4,
        }}
      >
        Search
      </button>
    </form>
  );
}
