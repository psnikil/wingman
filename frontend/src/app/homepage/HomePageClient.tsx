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
  data: any;
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
    newMessage = [{
      id: crypto.randomBytes(16).toString('hex'),
      content: prompt,
      role: 'user',
      timestamp: new Date(),
      isLoading: false
    }];

    newChat = {
      chatId: crypto.randomBytes(16).toString('hex'),
      chatName: `New Chat: ${prompt.substring(0, 6)}`,
      chatSummary: prompt.substring(0, 20),
      messages: newMessage,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    let payload: Payload = {
      data: newChat
    }
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/Createchat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload.data),
      });
      if (!res.ok) throw new Error('Failed to fetch');
      const result = await res.json();
      console.log("Response from backend:", result);
    } catch (err: any) {
      console.error('Error sending message:', err.message);
    }
    console.log('the chats are ', newChat);
    addChat(newChat);
    addMessage(newChat.chatId, newMessage[0]);

    window.location.href = `/chatpage/${newChat.chatId}`;
  };
  console.log('the chats are outside', newChat);
  return (
    <div className='flex flex-1 border rounded-sm border-zinc-600 min-h-svh' style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
      <SideBar />
      <main className="flex-1 flex items-center justify-center bg-neutral-900 p-6 ">
        <div className="text-shadow-gray-400 text-2xl font-light">
          Welcome to Wingman! Select a chat or start a new conversation.
          <PromptInput onSubmit={handlePrompt} disabled={false} placeholder="Start the conversation..." chatID={newChat.chatId} />
        </div>
      </main>
    </div>
  );
}
