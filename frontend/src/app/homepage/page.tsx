/* 
This is the homepage of the user post the login/set up. This page shows the user their chats.
clicking on the chats should redirect the user to the chats page with the chat id and any other parameters. 
*/

'use client';

import PromptInput from '@/components/PromptInput';
import crypto from 'crypto';
import Link from "next/link";
import React, { useState } from "react";

interface Chat {
  chatId: string;
  chatName: string;
  chatSummary: string;
}

/* Below are the test data for the UI*/ 
const chats: Chat[] = [
  {
    chatId: "1a2b3c",
    chatName: "Trip Planning",
    chatSummary: "Discussed ideas for a summer trip to Spain."
  },
  {
    chatId: "4d5e6f",
    chatName: "Code Review",
    chatSummary: "Reviewed the latest updates to the homepage."
  }
]

const CloseSidebarIcon = ({ className }: { className?: string }) => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    className={className}
  >
    <rect x="5" y="5" width="14" height="14" rx="3" strokeWidth="2"/>
    <line x1="9" y1="7" x2="9" y2="17" strokeWidth="2"/>
    <circle cx="9" cy="12" r="1.2" fill="currentColor" />
  </svg>
);


//Deprecated:this function generates a random 16byte hex value
function NumberGenerator(){
  const randomByteString = crypto.randomBytes(16).toString('hex');
  return '/chatpage/'+ randomByteString;
}


export default function Homepage() {

  const [sidebarOpen, setSidebarOpen] = useState(true);

  //below function should re-route to chatpage and/or send prompt to backend
  const handlePrompt = (prompt: string) => {
    // Your logic to handle/submit the prompt, e.g., send to backend/chat API
    console.log("User prompt:", prompt);
    //Temporary logic to create a new chat
    let newChat: Chat = {
      chatId: crypto.randomBytes(16).toString('hex'),
      chatName: `New Chat: ${prompt.substring(0, 20)}`,
      chatSummary: prompt
    };
    chats.push(newChat); // Add new chat to the list

    //Redirect to chat page
    window.location.href = `/chatpage/${newChat.chatId}`;

    
  };

  //using magic number , need to make it dynamic
  const HEADER_HEIGHT = 150;

  return (
    <div className='flex flex-1 border rounded-sm border-zinc-600 min-h-svh' style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
      {/* Sidebar*/ }
      {sidebarOpen ? (
        <aside className="relative w-80 min-w-[18rem] max-w-xsp-4 overflow-y-auto flex flex-col border-r border-zinc-600 rounded-sm">
          {/* Close Icon */}
          <button
            aria-label="Close sidebar"
            className="absolute top-4 right-3 text-gray-500 hover:text-gray-700 text-xl"
            onClick={() => setSidebarOpen(false)}
          >
            <CloseSidebarIcon className="w-6 h-6" />
          </button>
          <h2 className="border-b p-4 border-zinc-600 text-xl font-semibold mb-4">
            Chats
          </h2>
          <ul className='flex-1'>
            {chats.map((chat) => (
              <li key={chat.chatId} className="mb-2 border border-zinc-600 rounded-xl">
                <Link href={`/chatpage/${chat.chatId}`} className="block p-3 rounded hover:bg-gray-700 transition">
                  
                    <div className="font-medium">{chat.chatName}</div>
                    <div className="text-sm text-gray-500 truncate">{chat.chatSummary}</div>
                  
                </Link>
              </li>
            ))}
          </ul>
        </aside>
      ):(
         // Collapsed sidebar ("handle" area)
        <div className="w-12 border-r rounded-sm border-zinc-600 flex flex-col items-center p-4">
          <button
            aria-label="Open sidebar"
            className="flex-1 text-gray-500 hover:text-gray-700"
            onClick={() => setSidebarOpen(true)}
          >
            {/* Flip the icon horizontally for open */}
            <span className="block rotate-180">
              <CloseSidebarIcon className="w-6 h-6" />
            </span>
          </button>
        </div>
      )}
      {/* Content Area */}
      <main className="flex-1 flex items-center justify-center bg-neutral-900 p-6 ">
        <div className="text-shadow-gray-400 text-2xl font-light">
          Welcome to Wingman! Select a chat or start a new conversation.
          <PromptInput onSubmit={handlePrompt} />
        </div>
      </main>
    </div>
  );
}