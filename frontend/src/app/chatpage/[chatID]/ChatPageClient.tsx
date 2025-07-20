/* This is the client-side page for chatpage */

'use client';

import { useChatStore } from '@/store/chatStore';
import SideBar from '@/components/SideBar';
import PromptInput from '@/components/PromptInput';

interface Chat {
  chatId: string;
  chatName: string;
  chatSummary: string;
}

interface Props {
    chatID: string;
}


export default function ChatPageClient({ chatID }: Props){

    const chats = useChatStore((state) => state.chats);

    //using magic number , need to make it dynamic
    const HEADER_HEIGHT = 150;

    const handlePrompt = (prompt: string) => {
        // Your logic to handle/submit the prompt, e.g., send to backend/chat API
        console.log("User prompt:", prompt);
    };

    return(
        <div className='flex flex-1 border rounded-sm border-zinc-600 ' style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
            <SideBar chats={chats} /> 
            {/* Main content area */}
            <main className="flex-1 flex items-center justify-center bg-neutral-900 p-6 ">
                <div className="text-shadow-gray-400 text-2xl font-light">
                    The chat id for this chat is {chatID}.
                    <PromptInput onSubmit={handlePrompt} />
                </div>
            </main>
            {/* Additional chat functionalities can be added here */}
        </div>
        
    )
  
}