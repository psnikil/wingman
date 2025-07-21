/* this is a store for global access to the chats variable */
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

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
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

interface ChatState {
  chats: Chat[];
  currentChatId: string | null;
  
  // Chat operations
  addChat: (chat: Omit<Chat, 'messages' | 'createdAt' | 'updatedAt'>) => void;
  updateChat: (id: string, data: Partial<Chat>) => void;
  deleteChat: (id: string) => void;
  setChats: (chats: Chat[]) => void;
  setCurrentChat: (chatId: string) => void;
  
  // Message operations
  addMessage: (chatId: string, message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateMessage: (chatId: string, messageId: string, updates: Partial<Message>) => void;
  getMessages: (chatId: string) => Message[];
  clearMessages: (chatId: string) => void;
  
  // Utility functions
  getCurrentChat: () => Chat | null;
  getChatById: (chatId: string) => Chat | null;
}

// Enhanced test data with messages
const initialChats: Chat[] = [
  {
    chatId: "1a2b3c",
    chatName: "Trip Planning",
    chatSummary: "Discussed ideas for a summer trip to Spain.",
    messages: [
      {
        id: "msg1",
        content: "I'm planning a trip to Spain this summer. Any recommendations?",
        role: "user",
        timestamp: new Date("2025-07-15T10:00:00Z")
      },
      {
        id: "msg2", 
        content: "Spain is wonderful! I'd recommend visiting Barcelona for its architecture, Madrid for museums, and Seville for authentic Andalusian culture. What type of experiences are you most interested in?",
        role: "assistant",
        timestamp: new Date("2025-07-15T10:01:00Z")
      }
    ],
    createdAt: new Date("2025-07-15T09:59:00Z"),
    updatedAt: new Date("2025-07-15T10:01:00Z")
  },
  {
    chatId: "4d5e6f",
    chatName: "Code Review",
    chatSummary: "Reviewed the latest updates to the homepage.",
    messages: [
      {
        id: "msg3",
        content: "Can you review this React component for performance issues?",
        role: "user",
        timestamp: new Date("2025-07-16T14:30:00Z")
      }
    ],
    createdAt: new Date("2025-07-16T14:29:00Z"),
    updatedAt: new Date("2025-07-16T14:30:00Z")
  }
];

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      chats: initialChats,
      currentChatId: null,

      // Chat operations
      addChat: (chatData) =>
        set((state) => {
          const newChat: Chat = {
            ...chatData,
            messages: [],
            createdAt: new Date(),
            updatedAt: new Date()
          };
          return {
            chats: [...state.chats, newChat],
            currentChatId: newChat.chatId
          };
        }),

      updateChat: (id, data) =>
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.chatId === id 
              ? { ...chat, ...data, updatedAt: new Date() }
              : chat
          ),
        })),

      deleteChat: (id) =>
        set((state) => ({
          chats: state.chats.filter((chat) => chat.chatId !== id),
          currentChatId: state.currentChatId === id ? null : state.currentChatId
        })),

      setChats: (chats) => set(() => ({ chats })),

      setCurrentChat: (chatId) => set(() => ({ currentChatId: chatId })),

      // Message operations
      addMessage: (chatId, messageData) =>
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.chatId === chatId
              ? {
                  ...chat,
                  messages: [
                    ...chat.messages,
                    {
                      ...messageData,
                      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                      timestamp: new Date()
                    }
                  ],
                  updatedAt: new Date()
                }
              : chat
          ),
        })),

      updateMessage: (chatId, messageId, updates) =>
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.chatId === chatId
              ? {
                  ...chat,
                  messages: chat.messages.map((msg) =>
                    msg.id === messageId ? { ...msg, ...updates } : msg
                  ),
                  updatedAt: new Date()
                }
              : chat
          ),
        })),

      getMessages: (chatId) => {
        const chat = get().chats.find((c) => c.chatId === chatId);
        return chat?.messages || [];
      },

      clearMessages: (chatId) =>
        set((state) => ({
          chats: state.chats.map((chat) =>
            chat.chatId === chatId
              ? { ...chat, messages: [], updatedAt: new Date() }
              : chat
          ),
        })),

      // Utility functions
      getCurrentChat: () => {
        const { chats, currentChatId } = get();
        return chats.find((chat) => chat.chatId === currentChatId) || null;
      },

      getChatById: (chatId) => {
        const { chats } = get();
        return chats.find((chat) => chat.chatId === chatId) || null;
      },
    }),
    {
      name: "chat-store",
      storage: createJSONStorage(() => sessionStorage), //for dev use session may change for deployment
      partialize: (state) => ({ chats: state.chats, currentChatId: state.currentChatId }),
    }
  )
);

