// components/PromptInput.tsx
"use client"
import { useState } from "react";
import { PaperAirplaneIcon } from "@heroicons/react/24/outline"; // Heroicons: install with `npm install @heroicons/react`

export default function PromptInput({ onSubmit }: { onSubmit: (prompt: string) => void }) {
  const [prompt, setPrompt] = useState("");

  const handleInput = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    onSubmit(prompt);
    setPrompt("");
  };

  return (
    <form 
      onSubmit={handleInput} 
      className="flex items-center w-full max-w-xl mx-auto mt-8"
    >
      <div className="flex flex-1 items-center bg-slate-800 rounded-full px-4 py-2 shadow focus-within:ring-2 ring-blue-300">
        <input
          type="text"
          className="flex-1 bg-transparent outline-none text-gray-400 placeholder-gray-400 py-2"
          placeholder="Enter your prompt..."
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
        />
        <button
          type="submit"
          className="ml-2 rounded-full p-2 bg-blue-500 text-white hover:bg-blue-600 transition"
          aria-label="Send prompt"
        >
          <PaperAirplaneIcon className="h-5 w-5" />
        </button>
      </div>
    </form>
  );
}
