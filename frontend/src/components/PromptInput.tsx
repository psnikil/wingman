// components/PromptInput.tsx
"use client"
import { useState, useRef, KeyboardEvent } from "react";
import { PaperAirplaneIcon } from "@heroicons/react/24/outline";

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function PromptInput({ onSubmit, disabled = false, placeholder = "Type your message..." }: PromptInputProps) {
  const [prompt, setPrompt] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showTooltip, setShowTooltip] = useState(false);

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
    // Auto-resize textarea for growing with content, min 3 lines (72px)
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.max(72, Math.min(scrollHeight, 150))}px`;
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

  return (
    <div className="flex flex-col flex-3 relative resize-none rounded-xl border bg-slate-800 border-blue-400 px-4 py-3 pr-4 
                     focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 
                     disabled:bg-gray-100 disabled:cursor-not-allowed 
                     max-h-[350px] min-h-[48px] overflow-y-hidden">
      <form onSubmit={handleFormSubmit} className="flex flex-col h-full ">
        {/* Textarea section */}
        <div className="flex-1 flex flex-col border-b border-gray-600 " id="prompt-input-textarea">
          <textarea
            ref={textareaRef}
            value={prompt}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={2}
            className="w-full resize-none flex-1 focus:outline-none scroll-smooth dark-scrollbar text-white-100 bg-transparent"
          />
        </div>
        {/* Actions section pinned to bottom */}
        <div className="flex flex-row items-center justify-between pt-2 relative bg-slate-800 z-10" id="prompt-input-actions">
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
            className="p-2 rounded-lg bg-blue-500 text-white 
                       hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed 
                       transition-colors duration-200 flex items-center justify-center"
          >
            <PaperAirplaneIcon className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}

