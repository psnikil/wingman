# File & Folder Structure

Below is a breakdown of the frontend directory and file layout, with explanations for each node:

```
frontend/
├── public/                  # Static assets (SVGs, images, icons)
│   ├── logo.svg             # App logo
│   ├── next.svg, vercel.svg # Framework and deployment logos
│   └── ...                  # Other SVGs/icons
├── src/
│   ├── app/                 # Next.js app directory (routing, layouts, pages)
│   │   ├── layout.tsx       # Root layout (applies to all pages)
│   │   ├── globals.css      # Global styles (Tailwind, CSS vars)
│   │   ├── page.tsx         # Root landing page
│   │   ├── favicon.ico      # Favicon
│   │   ├── homepage/        # Homepage after login
│   │   │   └── page.tsx     # Homepage route
│   │   └── chatpage/        # Chat-related routes
│   │       └── [chatID]/    # Dynamic chat route (per chat session)
│   │           ├── ChatPageClient.tsx # Client-side chat logic/UI
│   │           └── page.tsx           # Server-side chat page
│   ├── components/          # Reusable UI components
│   │   ├── ButtonLink.tsx   # Button for navigation
│   │   ├── ChatContents.tsx # Chat message list and logic
│   │   ├── Header.tsx       # App header (logo, user info)
│   │   ├── LoadingIcon.tsx  # Animated loading spinner
│   │   ├── MessageBubble.tsx# Individual chat message bubble
│   │   ├── PromptInput.tsx  # User prompt input field
│   │   ├── SideBar.tsx      # Sidebar with chat list
│   │   └── TypingIndicator.tsx # Animated typing indicator
│   ├── pages/               # (Legacy/unused Next.js pages directory)
│   └── store/               # State management (Zustand stores)
│       ├── backendStore.ts  # Backend connection state
│       └── chatStore.ts     # Chat and message state
├── package.json             # Project dependencies and scripts
├── tailwind.config.mjs      # TailwindCSS configuration
├── tsconfig.json            # TypeScript configuration
├── next.config.ts           # Next.js configuration
└── ...                      # Other config and setup files
```

---

# Routing Overview

## Pages & Routes

- `/` (Root): Landing page, can be customized for onboarding or login.
- `/homepage`: User's main dashboard after login, shows chat list.
- `/chatpage/[chatID]`: Dynamic route for individual chat sessions. Renders chat UI for a specific chat.

## Routing Mechanisms

- **Dynamic Routing:** Folders like `[chatID]` enable per-chat pages.
- **Layouts:** `layout.tsx` provides a global layout (header, fonts, styles) for all routes.
- **Loading States & Templates:** (Not present in current code, but can be added as `loading.tsx` or `template.tsx` in any route folder for custom loading or error boundaries.)

---

# Component Documentation

Below is a summary of each component, its location, purpose, usage, and props:

## ButtonLink (`src/components/ButtonLink.tsx`)
- **Purpose:** Navigation button that redirects on click.
- **Usage:** Used wherever a styled navigation button is needed.
- **Props:**
  - `button_text: string` — Button label
  - `link: string` — Route to navigate to
- **Type:** Client component

## ChatContents (`src/components/ChatContents.tsx`)
- **Purpose:** Displays chat messages and handles chat logic for a given chat session.
- **Usage:** Used in chat page to render message list and handle prompt submission.
- **Props:**
  - `chatID: string` — ID of the chat session
- **Type:** Client component

## Header (`src/components/Header.tsx`)
- **Purpose:** App header with logo and user info; handles navigation on logo click.
- **Usage:** Rendered in the root layout, visible on all pages.
- **Props:** None
- **Type:** Client component

## LoadingIcon (`src/components/LoadingIcon.tsx`)
- **Purpose:** Animated spinner for loading states.
- **Usage:** Shown during async operations or loading screens.
- **Props:** None
- **Type:** Client component

## MessageBubble (`src/components/MessageBubble.tsx`)
- **Purpose:** Renders a single chat message (user or assistant), with avatars and typing indicator.
- **Usage:** Used within chat message lists.
- **Props:**
  - `message: Message` — Message object (see types below)
- **Type:** Client component

## PromptInput (`src/components/PromptInput.tsx`)
- **Purpose:** Input field for user prompts, supports file upload and dynamic resizing.
- **Usage:** Used at the bottom of chat pages for user input.
- **Props:**
  - `onSubmit: (prompt: string) => void` — Callback for prompt submission
  - `disabled?: boolean` — Disable input
  - `placeholder?: string` — Input placeholder
- **Type:** Client component

## SideBar (`src/components/SideBar.tsx`)
- **Purpose:** Sidebar listing all chats, with button to create new chat.
- **Usage:** Shown on main/chat pages for navigation.
- **Props:**
  - `chats: Chat[]` — List of chat sessions
- **Type:** Client component

## TypingIndicator (`src/components/TypingIndicator.tsx`)
- **Purpose:** Animated indicator for assistant typing.
- **Usage:** Shown in chat when assistant is generating a response.
- **Props:** None
- **Type:** Client component

---

# Custom Hooks and Utilities

- **Zustand Stores:**
  - `useBackendStore` (`src/store/backendStore.ts`):
    - Manages backend connection state (`backendInit` boolean).
    - Methods: `setBackendInit(value: boolean)`
  - `useChatStore` (`src/store/chatStore.ts`):
    - Manages chat sessions and messages.
    - Methods: `addChat`, `addMessage`, `updateChat`, etc.
- **React Hooks:**
  - Standard hooks (`useState`, `useEffect`, `useRef`) are used throughout for state and lifecycle management.
- **Utilities:**
  - Random ID generation using `crypto.randomBytes` for chat/message IDs.

---

# Type Definitions

## Message
```typescript
interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isLoading?: boolean;
}
```
**Defined in:** Multiple files (chat components, stores)

## Chat
```typescript
interface Chat {
  chatId: string;
  chatName: string;
  chatSummary: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}
```
**Defined in:** Multiple files (chat components, stores)

## BackendStore (Zustand)
```typescript
type BackendStore = {
  backendInit: boolean;
  setBackendInit: (value: boolean) => void;
}
```
**Defined in:** `src/store/backendStore.ts`

---

# API Integration

- **Backend Integration:**
  - The frontend interacts with a backend for chat and RAG features (details abstracted in stores and handlers).
  - API endpoints are not hardcoded in the frontend; data is managed via state stores and passed to components.
  - Data flow: User input → store update → (potential backend call) → UI update.
- **Input/Output Types:**
  - Inputs: User prompts (string), chat/message objects (see types above)
  - Outputs: Updated chat/message state, assistant responses

---

# Suggestions for Extension

- **Adding Pages:**
  - Create a new folder in `src/app/` with a `page.tsx` file for each new route.
  - For dynamic routes, use `[param]` folder naming.
- **Adding Components:**
  - Place new components in `src/components/`.
  - Follow existing naming and prop typing conventions.
- **Adding Types:**
  - Define new types/interfaces near their usage or in a shared types file for reuse.
  - Reuse and extend existing types where possible.
- **Reusable Patterns:**
  - Use Zustand for state abstraction.
  - Prefer functional, typed React components.
  - Use Tailwind utility classes for styling.
  - Keep logic and UI concerns separated (container vs. presentational components).

---

This documentation is intended to help new and existing developers quickly understand, maintain, and extend the frontend codebase with confidence and consistency.
## Wingman

* This is a LLM based chat web app to behave similar ot a locally run chatGPT
* This system will employ RAG to index any required files
    # Task:
    - Try and implement RAG using simpleRAG to index the users files for a global search
    - After search try and create agents to do more specific tasks
    - This app will be containerized 
