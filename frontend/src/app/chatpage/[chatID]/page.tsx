/* 
This is the server-side chat page for a specific chatid.

*/


import { useChatStore } from '@/store/chatStore';
import SideBar from '@/components/SideBar';
import ChatPageClient from './ChatPageClient';

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

interface ChatPageProps {
    params: {
        chatID: string;
    }
}



export default async function ChatPage({ params }: ChatPageProps) {

  
  const { chatID } = await params;

  return (
    <ChatPageClient chatID={chatID}/>
  );
}