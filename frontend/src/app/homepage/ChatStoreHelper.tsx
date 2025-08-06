
'use client';

import PromptInput from '@/components/PromptInput';
import SideBar from '@/components/SideBar';
import crypto from 'crypto';
import { useChatStore } from '@/store/chatStore';
import React, { useState } from "react";

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



// export default function HomePageClient({newChat}: {newChat: Chat}) {

//     const chats = useChatStore((state) => state.chats);
//     const addChat = useChatStore((state) => state.addChat);
//     const addMessage = useChatStore((state) => state.addMessage);

//     console.log('the new chat is ', newChat);

//     //below function should re-route to chatpage and/or send prompt to backend
//     const handlePrompt = (newChat:Chat) => {
//         // Your logic to handle/submit the prompt, e.g., send to backend/chat API
//         // console.log("User prompt:", prompt);
        
//         // let newMessage: Message = {
//         //     id: crypto.randomBytes(16).toString('hex'),
//         //     content: prompt,
//         //     role: 'user',
//         //     timestamp: new Date(),
//         //     isLoading: false
//         // };
        
//         // //Temporary logic to create a new chat
//         // let newChat: Chat = {
//         //     chatId: crypto.randomBytes(16).toString('hex'),
//         //     chatName: `New Chat: ${prompt.substring(0, 6)}`,
//         //     chatSummary: prompt.substring(0, 20),
//         //     messages: [],
//         // };

//         addChat(newChat); // Add new chat to the list
//         if (newChat.messages) {
//           addMessage(newChat.chatId, newChat.messages[0]); // Add messages to the chat
//         }

//         // //sending the chat to the backend
//         // const payload: Payload = { chatId: newChat.chatId, prompt };
//         // const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/chat`, {
//         //   method: 'POST',
//         //   headers: {
//         //     'Content-Type': 'application/json',
//         //   },
//         //   body: JSON.stringify(payload),
//         // });
//         // if (!res.ok) throw new Error('Failed to fetch');
//         // const result = await res.json();

//         console.log('the chats are ', chats);

//         // //Redirect to chat page
//         // window.location.href = `/chatpage/${newChat.chatId}`;

//     };

//     //using magic number , need to make it dynamic
//     const HEADER_HEIGHT = 150;


//     return (
//     <div className='flex flex-1 border rounded-sm border-zinc-600 min-h-svh' style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
//       {/* Sidebar component*/}
//       <SideBar chats={chats} /> 
//       {/* Content Area */}
//       <main className="flex-1 flex items-center justify-center bg-neutral-900 p-6 ">
//         <div className="text-shadow-gray-400 text-2xl font-light">
//           Welcome to Wingman! Select a chat or start a new conversation.
//           <PromptInput onSubmit={handlePrompt} disabled={false} placeholder = "Start the conversation..."/>
//         </div>
//       </main>
//     </div>
//     );
// }{}

export default function getChats(){
  const chats = useChatStore((state) => state.chats);
  return chats;
}