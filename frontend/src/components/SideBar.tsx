"use client"

import Link from "next/link";
import React, { useState } from "react"

/* 
This is the file for the side bar component.
The side bar contains the list of chats and a button to create a new chat.
 */
interface Chat {
  chatId: string;
  chatName: string;
  chatSummary: string;
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

export default function SideBar({chats}: {chats: Chat[]}) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

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
