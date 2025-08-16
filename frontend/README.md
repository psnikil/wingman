---
# Wingman Frontend (Next.js + TailwindCSS + TypeScript)

This is the frontend for the **Wingman LLM Chat App**—a modern, local ChatGPT-like experience with a custom UI, built using [Next.js](https://nextjs.org/), [TailwindCSS](https://tailwindcss.com/), and TypeScript.

---

## Getting Started

1. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```
2. **Run the development server**
   ```bash
   npm run dev
   # or yarn dev, pnpm dev, bun dev
   ```
   Open [http://localhost:3000](http://localhost:3000) to view the app.

3. **Edit pages/components**
   - Main entry: `src/app/page.tsx`
   - All changes auto-update in dev mode.

---

## Project Structure

```
frontend/
├── public/                  # Static assets (SVGs, images, icons)
├── src/
│   ├── app/                 # Next.js app directory (routing, layouts, pages)
│   │   ├── layout.tsx       # Root layout (fonts, header, global styles)
│   │   ├── globals.css      # Tailwind/global CSS
│   │   ├── page.tsx         # Landing page ("/")
│   │   ├── homepage/        # Homepage after login
│   │   └── chatpage/        # Chat routes (dynamic: [chatID])
│   ├── components/          # Reusable UI components
│   └── store/               # Zustand state stores
├── package.json             # Project dependencies/scripts
├── tailwind.config.js       # Tailwind config
├── next.config.ts           # Next.js config
├── tsconfig.json            # TypeScript config
└── README.md                # This file
```

### Key Folders & Files

- `public/` — Static assets (logos, SVGs, etc.)
- `src/app/` — Routing, layouts, pages
- `src/components/` — UI components (ButtonLink, ChatContents, Header, etc.)
- `src/store/` — Zustand stores for chat/backend state

---

## Routing Overview

- `/` — Landing page (`src/app/page.tsx`)
- `/homepage` — Homepage after login (`src/app/homepage/page.tsx`)
- `/chatpage/[chatID]` — Dynamic chat session route (`src/app/chatpage/[chatID]/page.tsx`)
  - Uses `ChatPageClient.tsx` for client-side chat logic
- Layout (`layout.tsx`) wraps all pages (fonts, header, global styles)
- Add `loading.tsx` in any route folder for loading UI

---

## Components & State

| Component         | Location                        | Purpose/Usage                                 | Props (Type)                                   |
|-------------------|---------------------------------|-----------------------------------------------|------------------------------------------------|
| ButtonLink        | src/components/ButtonLink.tsx   | Navigation button for redirects               | button_text: string, link: string              |
| ChatContents      | src/components/ChatContents.tsx | Displays chat messages, handles chat logic    | chatID: string                                 |
| Header            | src/components/Header.tsx       | App header (logo, user info, nav)             | —                                              |
| LoadingIcon       | src/components/LoadingIcon.tsx  | Animated loading spinner                      | —                                              |
| MessageBubble     | src/components/MessageBubble.tsx| Renders a single chat message                 | message: Message                               |
| PromptInput       | src/components/PromptInput.tsx  | User input for prompts/messages               | onSubmit: fn, disabled?: bool, placeholder?: string |
| SideBar           | src/components/SideBar.tsx      | Sidebar with chat list, new chat button       | chats: Chat[]                                  |
| TypingIndicator   | src/components/TypingIndicator.tsx| Animated indicator for assistant typing   | —                                              |

### State Management (Zustand)

- `useBackendStore` (`src/store/backendStore.ts`):
  - Manages backend connection state (`backendInit`)
- `useChatStore` (`src/store/chatStore.ts`):
  - Manages chat sessions, messages, and actions

---

## Type Definitions

Shared across components and stores (see `chatStore.ts`, `ChatPageClient.tsx`, etc.):

```ts
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
```

Each component defines its own props interface. Types are reused for consistency.

---

## API Integration

- Most data is managed in client-side state (Zustand)
- Backend API integration (FastAPI) should be added in store actions or React hooks
- See backend documentation for available endpoints

---

## Extending the Frontend

- **Add Pages/Routes**: Create a folder in `src/app/` with `page.tsx` for each new route
- **Add Components**: Place in `src/components/`, define typed props
- **Add Types**: Use a shared types file or colocate with stores/components
- **Patterns**: Use Zustand for state, keep components focused and modular

---

## About Wingman

- LLM-based chat web app (local ChatGPT alternative)
- Custom UI, fast and modern UX
- Will support RAG (Retrieval Augmented Generation) for file search
- Future: agent workflows, containerization, and more

---

For questions, see the backend README or contact the dev team. Update this doc as the project evolves.

