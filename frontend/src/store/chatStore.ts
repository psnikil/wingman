/* this is a store for global access to the chats variable */
import { create } from "zustand";

export type Chat = {
  chatId: string;
  chatName: string;
  chatSummary: string;
};

type ChatState = {
  chats: Chat[];
  addChat: (chat: Chat) => void;
  updateChat: (id: string, data: Partial<Chat>) => void;
  setChats: (chats: Chat[]) => void;
};

/* Below are the test data for the UI*/ 
let chats: Chat[] = [
  {
    chatId: "1a2b3c",
    chatName: "Trip Planning",
    chatSummary: "Discussed ideas for a summer trip to Spain."
  },
  {
    chatId: "4d5e6f",
    chatName: "Code Review",
    chatSummary: "Reviewed the latest updates to the homepage."
  }
]

export const useChatStore = create<ChatState>((set) => ({
  chats: chats,
  addChat: (chat) =>
    set((state) => ({
      chats: [...state.chats, chat],
    })),
  updateChat: (id, data) =>
    set((state) => ({
      chats: state.chats.map((c) => (c.chatId === id ? { ...c, ...data } : c)),
    })),
  setChats: (chats) => set(() => ({ chats })),
}));
