/* 
This is the server-side chat page for a specific chatid.

*/


import { useChatStore } from '@/store/chatStore';
import SideBar from '@/components/SideBar';
import ChatPageClient from './ChatPageClient';

interface Chat {
  chatId: string;
  chatName: string;
  chatSummary: string;
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