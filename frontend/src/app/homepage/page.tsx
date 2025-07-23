/* 
This is the homepage of the user post the login/set up. This page shows the user their chats.
clicking on the chats should redirect the user to the chats page with the chat id and any other parameters. 
*/

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
  createdAt?: Date;
  updatedAt?: Date;
}



//Deprecated:this function generates a random 16byte hex value
function NumberGenerator(){
  const randomByteString = crypto.randomBytes(16).toString('hex');
  return '/chatpage/'+ randomByteString;
}

//Create new chat from prompt
function createNewChat(prompt: string) {

    const addChat = useChatStore((state) => state.addChat);
    const addMessage = useChatStore((state) => state.addMessage);

    console.log("User prompt:", prompt);
    
    let newMessage:Message = {
      id: crypto.randomBytes(16).toString('hex'),
      content: prompt,
      role: 'user',
      timestamp: new Date(),
      isLoading: false
    };
    //Temporary logic to create a new chat
    let newChat:Chat = {
      chatId: crypto.randomBytes(16).toString('hex'),
      chatName: `New Chat: ${prompt.substring(0, 6)}`,
      chatSummary: prompt.substring(0, 20),
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    addChat(newChat) // Add new chat to the list
    addMessage(newChat.chatId,newMessage);



}


export default function Homepage() {

   const chats = useChatStore((state) => state.chats);
   const addChat = useChatStore((state) => state.addChat);
   const addMessage = useChatStore((state) => state.addMessage);

  //below function should re-route to chatpage and/or send prompt to backend
  const handlePrompt = (prompt: string) => {
    // Your logic to handle/submit the prompt, e.g., send to backend/chat API
    console.log("User prompt:", prompt);
    
    let newMessage:Message = {
      id: crypto.randomBytes(16).toString('hex'),
      content: prompt,
      role: 'user',
      timestamp: new Date(),
      isLoading: false
    };
    //Temporary logic to create a new chat
    let newChat:Chat = {
      chatId: crypto.randomBytes(16).toString('hex'),
      chatName: `New Chat: ${prompt.substring(0, 6)}`,
      chatSummary: prompt.substring(0, 20),
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    addChat(newChat) // Add new chat to the list
    addMessage(newChat.chatId,newMessage);

    console.log('the chats are ',chats);

    //Redirect to chat page
    window.location.href = `/chatpage/${newChat.chatId}`;

    
  };

  //using magic number , need to make it dynamic
  const HEADER_HEIGHT = 150;

  return (
    <div className='flex flex-1 border rounded-sm border-zinc-600 min-h-svh' style={{ minHeight: `calc(100vh - ${HEADER_HEIGHT}px)` }}>
      {/* Sidebar component*/}
      <SideBar chats={chats} /> 
      {/* Content Area */}
      <main className="flex-1 flex items-center justify-center bg-neutral-900 p-6 ">
        <div className="text-shadow-gray-400 text-2xl font-light">
          Welcome to Wingman! Select a chat or start a new conversation.
          <PromptInput onSubmit={handlePrompt} disabled={false} placeholder = "Start the conversation..."/>
        </div>
      </main>
    </div>
  );
}