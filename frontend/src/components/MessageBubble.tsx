'use client';



import TypingIndicator from './TypingIndicator';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
}

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} items-end`}>
      {/* Avatar for assistant */}
      {!isUser && (
        <div className="flex-shrink-0 mr-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
            AI
          </div>
        </div>
      )}

      {/* Message bubble */}
      <div className={`max-w-[70%] px-4 py-3 rounded-2xl border text-sm whitespace-pre-line break-words
        ${isUser
          ? 'bg-blue-500 text-white border-blue-400 rounded-br-none'
          : 'bg-gray-100 text-gray-900 border-gray-200 rounded-bl-none'}
      `}>
        {/* If assistant is loading, show typing indicator */}
        {message.isLoading && message.role === 'assistant' ? (
          <TypingIndicator />
        ) : (
          <span>{message.content}</span>
        )}
      </div>

      {/* Avatar for user */}
      {isUser && (
        <div className="flex-shrink-0 ml-2">
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
            U
          </div>
        </div>
      )}
    </div>
  );
}
