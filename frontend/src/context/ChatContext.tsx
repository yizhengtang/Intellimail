//ChatContext.tsx
//Stores the AI chat history globally so it survives navigation between pages.
//Backed by localStorage so the conversation also survives a page refresh.

import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import type { ChatMessage } from '../types/ai';

interface ChatContextType {
  history: ChatMessage[];
  setHistory: (history: ChatMessage[]) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatContextProvider({ children }: { children: ReactNode }) {
  //Initialise from localStorage so history survives a page refresh.
  const [history, setHistoryState] = useState<ChatMessage[]>(() => {
    try {
      const saved = localStorage.getItem('chat_history');
      return saved ? (JSON.parse(saved) as ChatMessage[]) : [];
    } catch {
      return [];
    }
  });

  //Write to both state and localStorage on every update.
  function setHistory(next: ChatMessage[]) {
    setHistoryState(next);
    try {
      localStorage.setItem('chat_history', JSON.stringify(next));
    } catch {
      //localStorage unavailable — state-only is still fine for the current session.
    }
  }

  return (
    <ChatContext.Provider value={{ history, setHistory }}>
      {children}
    </ChatContext.Provider>
  );
}

//useChat reads the current chat context.
//Throws if used outside ChatContextProvider — catches wiring bugs early.
export function useChat() {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within a ChatContextProvider');
  return context;
}
