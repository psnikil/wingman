'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import PromptInput from '@/components/PromptInput';
import crypto from 'crypto';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
}

interface ChatContentProps {
  chatID: string;
}

export default function ChatContent({ chatID }: ChatContentProps) {
  //these are for the local messages for this component
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);



  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load messages for current chat
  useEffect(() => {
    // Load messages from your store or API based on chatID

    //fetching the chat data from the backend
    const fetchChatData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_chat/${chatID}`);
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
    // Optionally update chat meta after first message (not used here)

    // Create and add the user's message immediately
    const userMessage: Message = {
      id: crypto.randomBytes(16).toString('hex'),
      content: prompt,
      role: 'user',
      timestamp: new Date(),
      isLoading: true
    };
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    const payload = {
      chatId: chatID,
      prompt: prompt
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
    }
  };
  
  console.log('Messages in ChatContent:', messages);

  return (
    <div className="flex flex-col h-full ">
      {/* Chat Header */}
      <div className="border-b border-gray-500 p-4 top-0 z-10">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">AI</span>
          </div>
          <div>
            <h2 className="font-semibold">AI Assistant</h2>
            <p className="text-sm text-gray-500">Online</p> {/*Change to variable */}
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div className="h-full max-h-[600px] overflow-y-auto px-4 py-6 space-y-4 scroll-smooth dark-scrollbar">
        {messages.length === 0 ? (
          <WelcomeMessage />
        ) : (
          messages.map((message) => (
            <MessageBubble 
              key={message.id} 
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
