# Projektkontext: uigen Deployment

## Aktueller Stand
Branch: `claude/extract-zip-file-5CVsX` (gepusht auf origin)

## App-Überblick
uigen ist ein KI-gestützter UI-Generator. Der Nutzer gibt einen Prompt ein, Claude generiert React-Komponenten via Streaming direkt im Browser.

**Tech Stack:**
- Next.js 15 (App Router, Turbopack)
- Vercel AI SDK (`ai@4.3.16`, `@ai-sdk/anthropic@1.2.12`) — **kein Edge Runtime, reines Node.js**
- Prisma 6 mit PostgreSQL (war SQLite, wurde umgestellt)
- Auth via JWT + HttpOnly-Cookie (`jose`), kein NextAuth
- Model: `claude-haiku-4-5` (via `@ai-sdk/anthropic`)

---

## Vercel Deployment — alle relevanten Details

### Root Directory
```
uigen/uigen
```
Vercel muss auf dieses Unterverzeichnis zeigen (nicht das Repo-Root).

### Runtime: Node.js (NICHT Edge)
Die Chat-Route (`/api/chat`) läuft zwingend auf **Node.js Runtime** — kein `export const runtime = 'edge'` setzen. Gründe:
- `bcrypt` ist ein natives Node.js-Modul
- Prisma Client funktioniert nicht auf Edge Runtime
- `server-only` setzt Node.js voraus

### maxDuration: 120 Sekunden
Gesetzt an zwei Stellen:
- `src/app/api/chat/route.ts`: `export const maxDuration = 120;`
- `vercel.json`: `"maxDuration": 120` für `src/app/api/chat/route.ts`

**Wichtig:** 120s erfordert Vercel **Pro-Plan**. Hobby-Plan ist auf 60s begrenzt.
Alternativ: `maxDuration` auf 60 senken für Hobby-Plan.

### vercel.json
```json
{
  "functions": {
    "src/app/api/chat/route.ts": {
      "maxDuration": 120
    }
  }
}
```

### Build-Konfiguration in Vercel
| Setting | Wert |
|---|---|
| Framework Preset | Next.js (auto-detected) |
| Root Directory | `uigen/uigen` |
| Build Command | `npm run build` |
| Install Command | `npm install && npx prisma generate` |
| Output Directory | `.next` (Standard) |

**Kritisch:** `npx prisma generate` muss vor dem Build laufen, sonst fehlt der Prisma Client. In Vercel unter "Install Command" eintragen oder als `postinstall`-Script in `package.json` hinzufügen.

### Environment Variables (alle drei zwingend erforderlich)

| Variable | Beschreibung | Wert |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API Key für Claude | `sk-ant-...` — ohne diesen Key läuft ein Mock-Provider |
| `JWT_SECRET` | Signiert Auth-Cookies (HS256) | Min. 32 zufällige Zeichen, z.B. aus `openssl rand -base64 32` |
| `DATABASE_URL` | PostgreSQL Connection String | Neon-Format: `postgresql://user:pass@host/db?sslmode=require` |

Ohne `ANTHROPIC_API_KEY` fällt die App auf einen Mock-Provider zurück (canned responses, kein echtes Claude).

### Datenbank: Neon PostgreSQL (kostenlos)
1. neon.tech → New Project → Connection string kopieren
2. Als `DATABASE_URL` in Vercel eintragen
3. Nach erstem Deployment: Prisma Migrations ausführen:
   ```bash
   DATABASE_URL="..." npx prisma migrate deploy
   ```
   (einmalig, lokal oder via Neon Console)

### Streaming
Die Chat-Route streamt via `streamText().toDataStreamResponse()` (Vercel AI SDK Data Stream Protocol). Vercel unterstützt das nativ — kein spezielles Setup nötig.

---

## Erledigte Schritte
- `uigen/uigen/` — App-Code liegt im Repo ✓
- `uigen/uigen/prisma/schema.prisma` — auf PostgreSQL umgestellt ✓
- `uigen/uigen/vercel.json` — erstellt (120s Timeout) ✓
- `.github/workflows/deploy.yml` — GitHub Actions Workflow ✓

## Nächste Aufgabe: Vercel-Projekt einrichten
Playwright MCP ist konfiguriert (`~/.claude.json`, `claude mcp add playwright`).

**Ablauf via Playwright:**
1. vercel.com → Login
2. New Project → Import `steffensoldan/claude` aus GitHub
3. Root Directory: `uigen/uigen`
4. Install Command: `npm install && npx prisma generate`
5. Environment Variables setzen (siehe Tabelle oben)
6. Deploy starten

**Vercel-Konto des Users:** Noch nicht bekannt — beim Start der neuen Session erfragen.

---

## Wichtige Dateipfade
| Pfad | Beschreibung |
|---|---|
| `uigen/uigen/src/app/api/chat/route.ts` | Chat-Streaming-Endpunkt, maxDuration=120 |
| `uigen/uigen/src/lib/provider.ts` | Model-Auswahl, Mock-Fallback ohne API Key |
| `uigen/uigen/src/lib/auth.ts` | JWT-Auth, liest `JWT_SECRET` |
| `uigen/uigen/prisma/schema.prisma` | PostgreSQL-Schema (User, Project) |
| `uigen/uigen/vercel.json` | Vercel Function-Config |
| `.github/workflows/deploy.yml` | CI/CD via GitHub Actions |
