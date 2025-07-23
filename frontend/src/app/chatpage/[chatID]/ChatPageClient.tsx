/* This is the client-side page for chatpage */

'use client';

import { useChatStore } from '@/store/chatStore';
import SideBar from '@/components/SideBar';
import PromptInput from '@/components/PromptInput';
import ChatContents from '@/components/ChatContents';
import crypto from 'crypto';

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

// TODO:Find a way to pass 'chats' as a parameter to this function
//function to update the chat using inputted prompt
// function updateChat(chatID: string, prompt: string) {
//     // const addMessage = useChatStore((state) => state.addMessage);
    
//     let newMessage: Message = {
//         id: crypto.randomBytes(16).toString('hex'),
//         content: prompt,
//         role: 'user',
//         timestamp: new Date(),
//         isLoading: false
//     };
    
//     addMessage(chatID, newMessage);
// }


export default function ChatPageClient({ chatID }: Props){

    const chats = useChatStore((state) => state.chats);
    const addMessage = useChatStore((state) => state.addMessage);


    //using magic number , need to make it dynamic
    const HEADER_HEIGHT = 150;

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
            <SideBar chats={chats} /> 
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