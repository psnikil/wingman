'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import PromptInput from '@/components/PromptInput';
import { useLLMstore } from '@/store/backendStore';
import crypto from 'crypto';

interface Message {
  messageId: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
}

interface ChatContentProps {
  chatID: string;
  onPromptSent?: () => void;
}


export default function ChatContent({ chatID, onPromptSent }: ChatContentProps) {
  //these are for the local messages for this component
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { available_llms, setLLMstore, chosen_llm, setChosenLLM } = useLLMstore();

  const fetchAvailableLLMs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/list_ollama_models`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setLLMstore(data || []);
      if (!chosen_llm && data && data.length > 0) {
        setChosenLLM(data[0]);
      }
      console.log('Fetched chat data:', data);
    } catch (error) {
      console.error('Error fetching chat data:', error);
    }
  };

  const updateChosenLLM = (llm: string) => {
    try {
      if (!available_llms.includes(llm)) {
        console.error('error in updating chosen llm');
      }
      setChosenLLM(llm);
      console.log('the updated LLM from Zustand is', llm);
    } catch (error) {
      console.error('error in updating chosen llm');
    }
  };

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    fetchAvailableLLMs();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load messages for current chat
  useEffect(() => {
    // Load messages from your store or API based on chatID

    //fetching the chat data from the backend
    const fetchChatData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_chat_messages/${chatID}`);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log("Fetched chat data:", data);
        setMessages(data.messages || []);
      } catch (error) {
        console.error('Error fetching chat data:', error);
      }
    }
    fetchChatData();
  }, [chatID]);



  const handlePrompt = async (prompt: string) => {

    const update_payload = {
      chatId:chatID,
      prompt:prompt
    }
    // Update the chat meta data on the first prompt
    if(messages.length === 0){
      console.log('updating the chat meta data')
      try {
        const update = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/updatechat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(update_payload),
        });
        if (!update.ok) throw new Error('Failed to fetch');
        const res = await update.json();
        console.log("The result of the update is :", res);

      } catch (err: any) {
        console.error('Error sending message:', err.message);
      }
    }

    // Create and add the user's message immediately
    const userMessage: Message = {
      messageId: crypto.randomBytes(16).toString('hex'),
      content: prompt,
      role: 'user',
      timestamp: new Date(),
      isLoading: true
    };
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    const payload = {
      chatId: chatID,
      prompt: prompt,
      model: chosen_llm
    };

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Failed to fetch');
      const LLMresponse = await res.json();
      console.log("Response from backend:", LLMresponse);

      // Replace the last user message's isLoading with false and add the assistant's response
      setMessages(prev => {
        // Remove isLoading from the last user message
        const updated = prev.map((msg, idx) =>
          idx === prev.length - 1 ? { ...msg, isLoading: false } : msg
        );
        return [...updated, LLMresponse.message];
      });
    } catch (err: any) {
      console.error('Error sending message:', err.message);
      // Optionally, update the last message to show error
      setMessages(prev => {
        const updated = prev.map((msg, idx) =>
          idx === prev.length - 1 ? { ...msg, isLoading: false, content: msg.content + ' (Failed to get response)' } : msg
        );
        return updated;
      });
    } finally {
      setIsTyping(false);
      // Call onPromptSent callback if provided
      if (typeof onPromptSent === 'function') {
        onPromptSent();
      }
    }
  };
  
  console.log('Messages in ChatContent:', messages, messages.length);

  return (
    <div className="flex flex-col relative">
      {/* Chat Header */}
      <div className="border-b border-gray-500 p-4 top-0 z-10 relative">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">AI</span>
          </div>
          <div>
            <h2 className="font-semibold">AI Assistant</h2>
            <p className="text-sm text-gray-500">Online</p> {/*Change to variable */}
          </div>
        </div>
        {/* LLM Dropdown */}
        <div className="absolute right-4 top-4 z-20">
          <select
            className="bg-zinc-800 text-white border border-zinc-600 rounded px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow"
            value={chosen_llm}
            onChange={e => updateChosenLLM(e.target.value)}
            disabled={available_llms.length === 0}
          >
            {available_llms.length === 0 ? (
              <option value="">Loading models...</option>
            ) : (
              available_llms.map(llm => (
                <option key={llm} value={llm}>{llm}</option>
              ))
            )}
          </select>
        </div>
      </div>

      {/* Messages Container */}
      <div className="h-full max-h-[700px] overflow-y-auto px-4 py-6 space-y-4 scroll-smooth dark-scrollbar">
        {messages.length === 0 ? (
          <WelcomeMessage />
        ) : (
          messages.map((message) => (
            <MessageBubble 
              key={message.messageId} 
              message={message} 
            />
          ))
        )}
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      <div className='flex flex-row'>
        <PromptInput onSubmit={handlePrompt} disabled={false} placeholder = "Type message..." chatID={chatID}/>
      </div>
    </div>
  );
}

// Welcome message component for empty chat
function WelcomeMessage() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center py-12">
      <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
        <span className="text-white text-2xl">✨</span>
      </div>
      <h3 className="text-xl font-semibold mb-2">
        Start a conversation
      </h3>
      <p className="text-gray-500 max-w-md">
        Ask me anything! I'm here to help with questions, creative tasks, analysis, and more.
      </p>
    </div>
  );
}
