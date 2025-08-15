/* This is the client-side page for chatpage */

'use client';

import { useChatStore } from '@/store/chatStore';
import SideBar from '@/components/SideBar';
import PromptInput from '@/components/PromptInput';
import ChatContents from '@/components/ChatContents';
import crypto from 'crypto';
import { useState, useRef, useEffect } from 'react';

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
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

interface Props {
    chatID: string;
}

export default function ChatPageClient({ chatID }: Props){

    
    const[Backendchats, setChats] = useState<Chat[]>([]);
    const chats = useChatStore((state) => state.chats);
    const addMessage = useChatStore((state) => state.addMessage);


    //using magic number , need to make it dynamic
    const HEADER_HEIGHT = 150;

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
                console.error('Error fetching all chat data:', error);
            }
        }
        fetchChatData();
    },[]);
    
    const handlePrompt = (prompt: string) => {
        // Your logic to handle/submit the prompt, e.g., send to backend/chat API

    
    let newMessage: Message = {
        id: crypto.randomBytes(16).toString('hex'),
        content: prompt,
        role: 'user',
        timestamp: new Date(),
        isLoading: false
    };
    
    addMessage(chatID, newMessage);
        console.log("User prompt:", prompt);
    };

    return(
        <div className='flex flex-1 border rounded-sm border-zinc-600 ' style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
            <SideBar chats={Backendchats}/> 
            {/* Main content area */}
            <main className="flex-1 flex flex-col bg-neutral-900 p-6 ">
                <div className="flex-1 flex flex-col min-h-0">
                    <ChatContents chatID={chatID} />
                </div>
                {/* <PromptInput onSubmit={handlePrompt} /> */}
            </main>
            {/* Additional chat functionalities can be added here */}
        </div>
    )
  
}