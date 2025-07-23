// components/PromptInput.tsx
"use client"
import { useState, useRef, KeyboardEvent } from "react";
import { PaperAirplaneIcon } from "@heroicons/react/24/outline";

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function PromptInput({ 
  onSubmit, 
  disabled = false, 
  placeholder = "Type your message..." 
}: PromptInputProps) {
  const [prompt, setPrompt] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (prompt.trim() && !disabled) {
      onSubmit(prompt.trim());
      setPrompt("");
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSubmit();
  };

  return (
    <div className="flex flex-1 items-end space-x-3 p-4 border-gray-200">
      <form onSubmit={handleFormSubmit} className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={prompt}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className="w-full resize-none rounded-xl border bg-slate-800 border-blue-400 px-4 py-3 pr-12 
                     focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 
                     disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-400
                     max-h-[150px] min-h-[48px] overflow-y-hidden"
        />
        
        <button
          type="submit"
          disabled={disabled || !prompt.trim()}
          className="absolute right-8 bottom-5 p-2 rounded-lg bg-blue-500 text-white 
                     hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed 
                     transition-colors duration-200 flex items-center justify-center"
        >
          <PaperAirplaneIcon className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}

