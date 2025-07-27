# Frontend File, Route, and Type Documentation

## 1. File & Folder Structure

Below is a breakdown of the frontend directory and file layout, with explanations for each node:

```
frontend/
├── public/                  # Static assets (SVGs, images, icons)
│   ├── logo.svg             # App logo
│   ├── next.svg, vercel.svg # Framework and deployment logos
│   └── ...                  # Other SVGs/icons
├── src/
│   ├── app/                 # Next.js app directory (routing, layouts, pages)
│   │   ├── layout.tsx       # Root layout (applies to all pages, sets up fonts, header)
│   │   ├── globals.css      # Global styles (Tailwind, CSS vars)
│   │   ├── page.tsx         # Root landing page (default route)
│   │   ├── favicon.ico      # Favicon
│   │   ├── homepage/        # Homepage after login
│   │   │   └── page.tsx     # Homepage route (shows user chats)
│   │   └── chatpage/        # Chat-related routes
│   │       └── [chatID]/    # Dynamic chat route (per chat session)
│   │           ├── ChatPageClient.tsx # Client-side chat logic/UI
│   │           └── page.tsx           # Server-side chat page
│   └── components/          # Reusable UI components
│       ├── ButtonLink.tsx   # Button for navigation
│       ├── ChatContents.tsx # Chat message list and logic
│       ├── Header.tsx       # App header (logo, user info)
│       ├── LoadingIcon.tsx  # Loading spinner
│       ├── MessageBubble.tsx# Individual chat message bubble
│       ├── PromptInput.tsx  # User prompt input field
│       ├── SideBar.tsx      # Sidebar with chat list
│       └── TypingIndicator.tsx # Animated typing indicator
│   └── store/               # State management (Zustand stores)
│       ├── backendStore.ts  # Backend connection state
│       └── chatStore.ts     # Chat sessions/messages state
├── eslint.config.mjs        # ESLint configuration
├── next.config.ts           # Next.js config
├── package.json             # Project dependencies and scripts
├── postcss.config.mjs       # PostCSS/Tailwind config
├── tsconfig.json            # TypeScript config
└── README.md                # Frontend documentation
```

## 2. Routing Overview

- **Root (`/`)**: Landing page (`src/app/page.tsx`).
- **Homepage (`/homepage`)**: Shows user chats after login (`src/app/homepage/page.tsx`).
- **Chat Page (`/chatpage/[chatID]`)**: Dynamic route for each chat session (`src/app/chatpage/[chatID]/page.tsx`).
  - Uses `ChatPageClient.tsx` for client-side chat logic.
- **Layout (`layout.tsx`)**: Wraps all pages, sets up fonts, header, and global styles.
- **Loading States**: (Add `loading.tsx` in any route folder to show loading UI for that route.)

## 3. Component Documentation

| Component                | Location                                 | Purpose/Usage                                              | Props (Type)                                   | Server/Client |
|--------------------------|------------------------------------------|------------------------------------------------------------|------------------------------------------------|--------------|
| ButtonLink               | src/components/ButtonLink.tsx            | Navigation button, used for redirects                      | button_text: string, link: string              | Client       |
| ChatContents             | src/components/ChatContents.tsx           | Displays chat messages, handles chat logic                 | chatID: string                                 | Client       |
| Header                   | src/components/Header.tsx                | App header, logo, user info, navigation                    | None                                           | Client       |
| LoadingIcon              | src/components/LoadingIcon.tsx           | Animated loading spinner                                   | None                                           | Client       |
| MessageBubble            | src/components/MessageBubble.tsx         | Renders a single chat message                              | message: Message                               | Client       |
| PromptInput              | src/components/PromptInput.tsx           | User input for prompts/messages                            | onSubmit: fn, disabled?: bool, placeholder?: string | Client   |
| SideBar                  | src/components/SideBar.tsx               | Sidebar with chat list, new chat button                    | chats: Chat[]                                   | Client       |
| TypingIndicator          | src/components/TypingIndicator.tsx       | Animated indicator for assistant typing                    | None                                           | Client       |

## 4. Custom Hooks and Utilities

- **Zustand Stores**:
  - `useBackendStore` (`src/store/backendStore.ts`):
    - Manages backend connection state (`backendInit`).
    - API: `{ backendInit: boolean, setBackendInit: (value: boolean) => void }`
  - `useChatStore` (`src/store/chatStore.ts`):
    - Manages chat sessions, messages, and related actions.
    - API: likely includes `chats`, `addChat`, `addMessage`, `updateChat` (see code for details).
- **Utilities**:
  - Random ID generation (e.g., `crypto.randomBytes(16).toString('hex')` in chat logic).

## 5. Type Definitions

**Defined in multiple files (e.g., `ChatPageClient.tsx`, `SideBar.tsx`, `chatStore.ts`)**:

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

- **Props interfaces**: Each component defines its own props interface (e.g., `ButtonLink`, `PromptInput`, `MessageBubble`).
- **Type Sharing**: Types are reused across components and stores for consistency.

## 6. API Integration

- **Backend Store**: `useBackendStore` manages whether the backend is initialized, but direct API calls are not shown in the provided code.
- **Chat Store**: `useChatStore` is used for chat state, but API endpoints for chat data are not explicitly defined in the frontend code provided.
- **Data Flow**: Most data is managed in client-side state; integration with backend APIs should be added in store actions or via React hooks.

## 7. Suggestions for Extension

- **Adding Pages/Routes**:
  - Create a new folder in `src/app/` with a `page.tsx` for each new route.
  - Use dynamic route folders (e.g., `[param]`) for parameterized routes.
- **Adding Components**:
  - Place new components in `src/components/`.
  - Define clear, typed props interfaces for each component.
  - Prefer functional components and client/server directives as needed.
- **Adding Types**:
  - Define shared types in a central file (e.g., `src/types/` or in stores/components as needed).
  - Reuse types across components and stores to ensure consistency.
- **Reusable Patterns**:
  - Use Zustand for state abstraction.
  - Follow file naming conventions (`PascalCase` for components, `camelCase` for hooks).
  - Keep logic modular and components focused on a single responsibility.

---

This documentation is intended to help new and existing developers quickly understand, extend, and maintain the frontend codebase. Update this section as the project evolves.

This documentation is intended to help new and existing developers quickly understand, maintain, and extend the frontend codebase with confidence and consistency.
## Wingman

* This is a LLM based chat web app to behave similar ot a locally run chatGPT
* This system will employ RAG to index any required files
    # Task:
    - Try and implement RAG using simpleRAG to index the users files for a global search
    - After search try and create agents to do more specific tasks
    - This app will be containerized 
