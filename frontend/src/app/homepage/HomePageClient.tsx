"use client"
import PromptInput from '@/components/PromptInput';
import SideBar from '@/components/SideBar';
import crypto from 'crypto';
import { useChatStore } from '@/store/chatStore';
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

  const[Backendchats, setChats] = useState<Chat[]>([]);
  


  let newChat: Chat = {
    chatId: '',
    chatName: '',
    chatSummary: '',
    messages: [],
    createdAt: new Date(),
    updatedAt: new Date(),
  };


  let newMessage: Message[] = [];


  useEffect(() => {
      // Fetch chat data when component mounts
      const fetchChatData = async () => {
          try {
              const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_all_chats`);
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              const data = await response.json();
              // Assuming data contains the chat object
              setChats(data || []);
              console.log("Fetched chat data:", data);
          }
          catch (error) {
              console.error('Error fetching chat data:', error);
          }
      }
      fetchChatData();
  },[]);
  

  //below function should re-route to chatpage and/or send prompt to backend
  const handlePrompt = async (prompt: string) => {
    console.log("User prompt:", prompt);
    
    let payload: Payload = {
      userPrompt: prompt
    }
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
      console.log("The new chat is with is :", chatID);
      window.location.href = `/chatpage/${chatID}`;

    } catch (err: any) {
      console.error('Error sending message to new chat:', err.message);
    }
  };
  console.log('the chats are outside', newChat);
  return (
    <div className='flex flex-1 border rounded-sm border-zinc-600 min-h-svh' style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
      <SideBar chats={Backendchats}/>
      <main className="flex-1 flex items-center justify-center bg-neutral-900 p-6 ">
        <div className="text-shadow-gray-400 text-2xl font-light">
          Welcome to Wingman! Select a chat or start a new conversation.
          <PromptInput onSubmit={handlePrompt} disabled={false} placeholder="Start the conversation..." chatID={newChat.chatId} />
        </div>
      </main>
    </div>
  );
}
