"use client"

import Link from "next/link";
import React, { useState } from "react"
import { useChatStore } from '@/store/chatStore';
import crypto from 'crypto';

/* 
This is the file for the side bar component.
The side bar contains the list of chats and a button to create a new chat.
 */
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

interface SideBarProps {
  chats?: Chat[];
}


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

const CreateNewChatIcon = ({ className }: { className?: string }) => (
    <svg
       xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1}
        stroke="currentColor"
        className={className}
    >
    <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M16.862 3.487a2.122 2.122 0 113 3L9 17.35 5 18.5l1.15-4L16.862 3.487z"
    />
    <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M19 13v5a2 2 0 01-2 2H6a2 2 0 01-2-2V7a2 2 0 012-2h5"
    />
    </svg>
    );

export default function SideBar({chats = []}: SideBarProps) {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const addChat = useChatStore((state) => state.addChat);
    const chatStore = useChatStore((state) => state.chats);

    console.log("Chats in SideBar 1:", chats);
    if (chats.length === 0 ) {
        console.log("No chats provided to SideBar");
        chats = chatStore; // Fallback to store if no chats prop is provided
    }
  

    const createNewChat = () => {
    // Logic to create a new chat
        const newChat: Chat = {
            chatId: crypto.randomBytes(16).toString('hex'),
            chatName: `New Chat ${new Date().toLocaleTimeString()}`,
            chatSummary: 'This is a new chat',
            messages: [],
            createdAt: new Date(),
            updatedAt: new Date()
        };
        addChat(newChat);

        //Redirect to chat page
        window.location.href = `/chatpage/${newChat.chatId}`;

    }


    console.log("Chats in SideBar:", chats);
    return(
        <div className=' border-r border-zinc-600 rounded-sm'>
            {sidebarOpen ? (
                <aside className="relative w-80 min-w-[18rem] max-w-xsp-4 overflow-y-auto flex flex-col">
                {/* Close Icon */}
                <button
                    aria-label="Close sidebar"
                    className="absolute top-4 right-3 text-gray-500 hover:text-gray-700 text-xl"
                    onClick={() => setSidebarOpen(false)}
                >
                    <CloseSidebarIcon className="w-6 h-6" />
                </button>
                <span className="border-b border-zinc-600 p-4">
                    <h2 className=" text-xl font-semibold mb-4">
                        Dashboard
                    </h2>

                    <button
                        className="w-full text-white p-3 rounded hover:bg-gray-700 transition"
                        onClick={() => createNewChat()}>
                        New chat
                        <CreateNewChatIcon className="flex-1 inline-block w-5 h-5 ml-2" /> 
                    </button>
          
                </span>
                <span className="flex-1 overflow-y-auto p-1">
                <h2 className=" text-l font-semibold mb-4 p-2 border-b border-zinc-700">
                    Recent Chats
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
                    
                </span>
                </aside>
            ):(
                // Collapsed sidebar ("handle" area)
                <div className="w-12 flex flex-col items-center p-4">
                <button
                    aria-label="Open sidebar"
                    className="flex text-gray-500 hover:text-gray-700"
                    onClick={() => setSidebarOpen(true)}
                >
                    {/* Flip the icon horizontally for open */}
                    <span className="block rotate-180">
                    <CloseSidebarIcon className="w-6 h-6" />
                    </span>
                </button>
                </div>
            )}
        </div>
    );

}
