// components/PromptInput.tsx
"use client"
import { useState, useRef, KeyboardEvent } from "react";
import { useChatStore } from '@/store/chatStore';
import { PaperAirplaneIcon } from "@heroicons/react/24/outline";
import { get } from "http";
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
  message: Message[];
  createdAt: Date;
  updatedAt: Date;
}


interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
  placeholder?: string;
  chatID:string;
}

export default function PromptInput({ onSubmit, disabled = false, placeholder = "Type your message...",chatID }: PromptInputProps) {
  const [prompt, setPrompt] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const [textareaHeight, setTextareaHeight] = useState(48); // px, min height

  const chats = useChatStore((state) => state.chats);
  const addChat = useChatStore((state) => state.addChat);
  const addMessage = useChatStore((state) => state.addMessage);
  const getChatById = useChatStore((state) => state.getChatById);
  

  // Constants for min/max height (px)
  const MIN_HEIGHT = 48; // 2 lines
  const MAX_HEIGHT = 200; // ~7-8 lines, adjust as needed

  // Adjust textarea height on input
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const newHeight = Math.max(MIN_HEIGHT, Math.min(scrollHeight, MAX_HEIGHT));
      textareaRef.current.style.height = `${newHeight}px`;
      setTextareaHeight(newHeight);
    }
  };

  // Reset textarea height on clear
  const handleSubmit = () => {
    if (prompt.trim() && !disabled) {

      // Create new message object
      const newMessage: Message = {
        id: crypto.randomBytes(16).toString('hex'),
        content: prompt,
        role: 'user',
        timestamp: new Date(),
        isLoading: false
      };

      // check if chatID exists in the store
      if (getChatById(chatID)) {


        // Add message to the existing chat
        addMessage(chatID, newMessage);

      }
      else{
        // Create new chat if chatID does not exist
        const newChat: Chat = {
          chatId: chatID,
          chatName: `New Chat: ${prompt.substring(0, 6)}`,
          chatSummary: prompt.substring(0, 20),
          message: [newMessage],
          createdAt: new Date(),
          updatedAt: new Date()
        };

        // Add new chat to the store
        addChat(newChat);
        addMessage(newChat.chatId, newMessage);
      }


      onSubmit(prompt.trim());
      setPrompt("");
      if (textareaRef.current) {
        textareaRef.current.style.height = `${MIN_HEIGHT}px`;
      }
      setTextareaHeight(MIN_HEIGHT);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSubmit();
  };

  const handlePlusClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      // You can handle the file(s) here, e.g., upload or preview
      // For now, just log the file(s)
      console.log('Selected file(s):', files);
    }
  };

  // The main container grows with textarea, actions always pinned to bottom
  return (
    <div
      className="flex flex-col flex-3 relative rounded-xl border bg-slate-800 border-blue-400 px-4 pt-3 pb-2 pr-4 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 disabled:bg-gray-100 disabled:cursor-not-allowed min-h-[48px] max-h-[350px]"
      style={{
        minHeight: `${MIN_HEIGHT + 48}px`, // 48px for actions row
        maxHeight: `${MAX_HEIGHT + 60}px`, // allow for actions row
        height: 'auto',
      }}
    >
      <form onSubmit={handleFormSubmit} className="flex flex-col h-full">
        {/* Textarea section */}
        <div className="flex-1 flex flex-col border-b border-gray-600" id="prompt-input-textarea">
          <textarea
            ref={textareaRef}
            value={prompt}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={2}
            style={{
              minHeight: `${MIN_HEIGHT}px`,
              maxHeight: `${MAX_HEIGHT}px`,
              height: `${textareaHeight}px`,
              overflowY: textareaHeight >= MAX_HEIGHT ? 'auto' : 'hidden',
              resize: 'none',
            }}
            className="w-full flex-1 focus:outline-none scroll-smooth dark-scrollbar text-white-100 bg-transparent resize-none"
          />
        </div>
        {/* Actions section pinned to bottom */}
        <div
          className="flex flex-row items-center justify-between pt-2 relative bg-slate-800 z-10"
          id="prompt-input-actions"
          style={{
            position: 'sticky',
            bottom: 0,
            background: 'inherit',
          }}
        >
          {/* Plus icon and file input */}
          <div className="flex items-end">
            <button
              type="button"
              aria-label="Add file or image"
              className="p-2 rounded-lg hover:bg-gray-300 text-blue-500 flex items-center justify-center transition-colors duration-200"
              onClick={handlePlusClick}
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
              tabIndex={-1}
            >
              {/* Plus SVG icon */}
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            </button>
            {/* Tooltip */}
            {showTooltip && (
              <div className="absolute left-12 bottom-1/2 translate-y-1/2 bg-gray-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap shadow-lg z-20">
                add file/image
              </div>
            )}
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={handleFileChange}
              multiple={false}
            />
          </div>
          <button
            type="submit"
            disabled={disabled || !prompt.trim()}
            className="p-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}

