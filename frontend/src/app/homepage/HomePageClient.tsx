"use client"
import PromptInput from '@/components/PromptInput';
import SideBar from '@/components/SideBar';
import crypto from 'crypto';
import { useChatStore } from '@/store/chatStore';
import { useLLMstore } from '@/store/backendStore';
import { useState, useRef, useEffect } from 'react';

  let newChat: Chat = {
    chatId: '',
    chatName: '',
    chatSummary: '',
    messages: [],
    createdAt: new Date(),
    updatedAt: new Date(),
  };


export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
}

export interface Chat {
  chatId: string;
  chatName: string;
  chatSummary: string;
  messages?: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Payload {
  userPrompt?: string;
  model?:string;
}

const HEADER_HEIGHT = 150;

export default function HomePageClient() {
  // creating empty messages and chats to pass to the HomePageClient component
  const chats = useChatStore((state) => state.chats);
  const addChat = useChatStore((state) => state.addChat);
  const addMessage = useChatStore((state) => state.addMessage);

  const { available_llms, setLLMstore, chosen_llm, setChosenLLM } = useLLMstore();
  const [Backendchats, setChats] = useState<Chat[]>([]);

  let newChat: Chat = {
    chatId: '',
    chatName: '',
    chatSummary: '',
    messages: [],
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  let newMessage: Message[] = [];

  const fetchAvailableLLMs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/list_ollama_models`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setLLMstore(data || []);
      if (!chosen_llm && data && data.length > 0) {
        setChosenLLM(data[0]);
      }
      console.log('Fetched chat data:', data);
    } catch (error) {
      console.error('Error fetching chat data:', error);
    }
  };

  const updateChosenLLM = (llm: string) => {
    try {
      if (!available_llms.includes(llm)) {
        console.error('error in updating chosen llm');
      }
      setChosenLLM(llm);
      console.log('the updated LLM from Zustand is', llm);
    } catch (error) {
      console.error('error in updating chosen llm');
    }
  };

  useEffect(() => {
    // Fetch chat data when component mounts
    const fetchChatData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_all_chats`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        setChats(data || []);
        console.log('Fetched chat data:', data);
      } catch (error) {
        console.error('Error fetching chat data:', error);
      }
    };

    fetchChatData();
    fetchAvailableLLMs();
  }, []);

  //below function should re-route to chatpage and/or send prompt to backend
  const handlePrompt = async (prompt: string) => {
    console.log('User prompt:', prompt);

    let payload: Payload = {
      userPrompt: prompt,
      model: chosen_llm,
    };
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/Createchat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Failed to fetch');
      const chatID = await res.json();
      console.log('The new chat is with is :', chatID);
      window.location.href = `/chatpage/${chatID}`;
    } catch (err: any) {
      console.error('Error sending message to new chat:', err.message);
    }
  };

  // Dropdown styling: top right of main section
  return (
    <div className="flex flex-1 border rounded-sm border-zinc-600 min-h-svh" style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
      <SideBar chats={Backendchats} />
      <main className="flex-1 flex flex-col bg-neutral-900 p-6 relative">
        {/* LLM Dropdown */}
        <div className="absolute right-6 top-6 z-20">
          <select
            className="bg-zinc-800 text-white border border-zinc-600 rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow"
            value={chosen_llm}
            onChange={e => updateChosenLLM(e.target.value)}
            disabled={available_llms.length === 0}
          >
            {available_llms.length === 0 ? (
              <option value="">Loading models...</option>
            ) : (
              available_llms.map(llm => (
                <option key={llm} value={llm}>{llm}</option>
              ))
            )}
          </select>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-shadow-gray-400 text-2xl font-light">
            Welcome to Wingman! Select a chat or start a new conversation.
            <PromptInput onSubmit={handlePrompt} disabled={false} placeholder="Start the conversation..." chatID={newChat.chatId} />
          </div>
        </div>
      </main>
    </div>
  );
}
