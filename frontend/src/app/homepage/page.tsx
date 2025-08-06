/* 
This is the homepage of the user post the login/set up. This page shows the user their chats.
clicking on the chats should redirect the user to the chats page with the chat id and any other parameters. 
*/

import PromptInput from '@/components/PromptInput';
import SideBar from '@/components/SideBar';
import crypto from 'crypto';
import { useChatStore } from '@/store/chatStore';
// import React, { useState } from "react";
import getChats from './ChatStoreHelper';

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
  data:any
}


// //Deprecated:this function generates a random 16byte hex value
// function NumberGenerator(){
//   const randomByteString = crypto.randomBytes(16).toString('hex');
//   return '/chatpage/'+ randomByteString;
// }

// //Create new chat from prompt
// function createNewChat(prompt: string) {

//     const addChat = useChatStore((state) => state.addChat);
//     const addMessage = useChatStore((state) => state.addMessage);

//     console.log("User prompt:", prompt);
    
//     let newMessage:Message = {
//       id: crypto.randomBytes(16).toString('hex'),
//       content: prompt,
//       role: 'user',
//       timestamp: new Date(),
//       isLoading: false
//     };
//     //Temporary logic to create a new chat
//     let newChat:Chat = {
//       chatId: crypto.randomBytes(16).toString('hex'),
//       chatName: `New Chat: ${prompt.substring(0, 6)}`,
//       chatSummary: prompt.substring(0, 20),
//       messages: [],
//       createdAt: new Date(),
//       updatedAt: new Date()
//     };
//     addChat(newChat) // Add new chat to the list
//     addMessage(newChat.chatId,newMessage);



// }


export default async function Homepage() {

  //  const chats = useChatStore((state) => state.chats);
  //  const addChat = useChatStore((state) => state.addChat);
  //  const addMessage = useChatStore((state) => state.addMessage);

  // creating empty messages and chats to pass to the HomePageClient component
  let newChat: Chat = {
    chatId: '',
    chatName: '',
    chatSummary: '',
    messages: [],
    createdAt: new Date(),
    updatedAt:  new Date(),
  };

  let newMessage: Message[] = [];


  //below function should re-route to chatpage and/or send prompt to backend
  const handlePrompt = async (prompt: string) => {
    // Your logic to handle/submit the prompt, e.g., send to backend/chat API
    console.log("User prompt:", prompt);
    
    newMessage = [{
      id: crypto.randomBytes(16).toString('hex'),
      content: prompt,
      role: 'user',
      timestamp: new Date(),
      isLoading: false
    }];
    //Temporary logic to create a new chat
    newChat = {
      chatId: crypto.randomBytes(16).toString('hex'),
      chatName: `New Chat: ${prompt.substring(0, 6)}`,
      chatSummary: prompt.substring(0, 20),
      messages: newMessage,
      createdAt: new Date(),
      updatedAt: new Date()
    };
    //sending the chat to the backend
    let payload:Payload = {
      data: newChat
    } 

    try{
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

    console.log('the chats are ',newChat);

    //Redirect to chat page
    window.location.href = `/chatpage/${newChat.chatId}`;

    
  };

    //using magic number , need to make it dynamic
  const HEADER_HEIGHT = 150;


  console.log('the new chat is server page', newChat);
  return (
    // <div className="homePageServer">
      // <HomePageClient newChat={newChat} />
    // </div>
    <div className='flex flex-1 border rounded-sm border-zinc-600 min-h-svh' style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
      {/* Sidebar component only give chats when requested from backend here*/}
      <SideBar/> 
      {/* Content Area */}
      <main className="flex-1 flex items-center justify-center bg-neutral-900 p-6 ">
        <div className="text-shadow-gray-400 text-2xl font-light">
          Welcome to Wingman! Select a chat or start a new conversation.
          <PromptInput onSubmit={handlePrompt} disabled={false} placeholder = "Start the conversation..." chatID={newChat.chatId}/>
        </div>
      </main>
    </div>
  );
}