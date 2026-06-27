# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**UIGen** — an AI-powered React component generator with live preview. Users describe a component in chat; Claude generates and iterates on it using tool calls; the result is rendered in a sandboxed iframe in real time.

The app lives in `uigen/uigen/`. All commands below should be run from that directory.

## Commands

```bash
# First-time setup (install deps, generate Prisma client, run migrations)
npm run setup

# Development server (Turbopack)
npm run dev

# Build for production
npm run build

# Lint
npm run lint

# Run all tests
npm test

# Run a single test file
npx vitest run src/lib/__tests__/file-system.test.ts

# Reset the database
npm run db:reset
```

## Architecture

### Request / AI flow

1. **`src/app/api/chat/route.ts`** — The only API route. Receives `{ messages, files, projectId }`, prepends a system prompt with prompt caching, calls `streamText` with two tools, and on finish saves messages + file state to the DB (authenticated users only).
2. **`src/lib/provider.ts`** — Returns either `anthropic("claude-haiku-4-5")` (when `ANTHROPIC_API_KEY` is set) or `MockLanguageModel` (a fully local fallback that returns canned components without calling the API).
3. **`src/lib/prompts/generation.tsx`** — System prompt that instructs Claude to always create `/App.jsx` as the entry point and use `@/` for local imports.

### AI tools (server-side + client-side mirror)

Two tools are registered in the API route and also handled client-side in `FileSystemContext.handleToolCall`:

- **`str_replace_editor`** (`src/lib/tools/str-replace.ts`) — `view`, `create`, `str_replace`, `insert`. This is the primary tool for writing files.
- **`file_manager`** (`src/lib/tools/file-manager.ts`) — `rename`, `delete`.

The server executes each tool against a `VirtualFileSystem` instance to persist state; the client mirrors every tool call to update the in-browser `VirtualFileSystem` so the UI stays in sync without a round-trip.

### Virtual file system

`src/lib/file-system.ts` — `VirtualFileSystem` is an in-memory tree (plain `Map`). It is **not persisted to disk**. Serialization (`serialize()` / `deserializeFromNodes()`) converts it to/from a plain `Record<string, FileNode>` for JSON transport and DB storage.

The DB `Project.data` column stores the serialized VFS; `Project.messages` stores the full conversation history as JSON.

### Live preview pipeline

`src/lib/transform/jsx-transformer.ts`:
1. `createImportMap(files)` — Babel-transforms every `.js/.jsx/.ts/.tsx` file in the VFS to plain JS, wraps each in a `Blob` URL, and builds an [import map](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap). React 19 is served from `esm.sh`. Third-party packages are also resolved via `esm.sh`. Missing local imports get placeholder stub modules.
2. `createPreviewHTML(entryPoint, importMap, styles, errors)` — Produces a full HTML document that loads Tailwind from CDN, injects the import map, and dynamically `import()`s the entry point (defaults to `/App.jsx`).

`src/components/preview/PreviewFrame.tsx` renders an `<iframe srcdoc={…}>`. The iframe rerenders on every `refreshTrigger` increment (which fires on every file change).

### React context layer

Both contexts wrap the entire workspace:

- **`FileSystemContext`** (`src/lib/contexts/file-system-context.tsx`) — Owns the `VirtualFileSystem` instance, tracks the selected file, exposes mutation helpers, and routes incoming `onToolCall` events from the AI stream to the right VFS method.
- **`ChatContext`** (`src/lib/contexts/chat-context.tsx`) — Wraps the Vercel AI SDK `useChat` hook; serializes the current VFS and passes it as `body` on every request so the server can reconstruct state.

### Auth

JWT-based, cookie-stored (`auth-token`, 7-day expiry). `src/lib/auth.ts` signs/verifies tokens with `jose`. Passwords hashed with `bcrypt`. Anonymous users can use the app without signing in; their work is tracked via `src/lib/anon-work-tracker.ts` (localStorage) and offered for save on sign-up.

### Database

Prisma + SQLite (`prisma/dev.db`). Two models: `User` and `Project`. `Project.userId` is nullable (anonymous projects are possible but not persisted — the server only saves when `projectId` is set **and** the user is authenticated).

Generated Prisma client lands in `src/generated/prisma/` (not `node_modules`).

### Routing

- `/` — Home. Authenticated users are immediately redirected to their most recent project (or a freshly created one). Anonymous users see the main workspace.
- `/[projectId]` — Project page. Requires auth; redirects to `/` if the project is not found or not owned by the user.
