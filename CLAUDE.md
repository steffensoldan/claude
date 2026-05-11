# Projektkontext: uigen Deployment

## Aktueller Stand
Branch: `claude/extract-zip-file-5CVsX` (gepusht auf origin)

Die uigen-App (Next.js 15, Prisma, Anthropic AI SDK) wurde extrahiert und für Vercel vorbereitet.

## Erledigte Schritte
- `uigen/uigen/` — App-Code liegt im Repo
- `uigen/uigen/prisma/schema.prisma` — auf PostgreSQL umgestellt (`env("DATABASE_URL")`)
- `uigen/uigen/vercel.json` — erstellt (120s Timeout für `/api/chat`)
- `.github/workflows/deploy.yml` — GitHub Actions Workflow für automatisches Vercel-Deployment

## Nächste Aufgabe: Vercel einrichten
Playwright MCP ist jetzt konfiguriert (`claude mcp add playwright` ✓, `~/.claude.json`).

**Ziel:** Mit Playwright MCP auf vercel.com navigieren und das Projekt einrichten:
1. vercel.com öffnen → Login
2. New Project → Import `steffensoldan/claude` aus GitHub
3. Root Directory auf `uigen/uigen` setzen
4. Environment Variables setzen:
   - `ANTHROPIC_API_KEY` (User muss den Wert nennen)
   - `JWT_SECRET` (32 zufällige Zeichen)
   - `DATABASE_URL` (Neon PostgreSQL URL — User muss Account erstellen auf neon.tech)
5. Deploy starten

## Vercel-Konto des Users
Noch nicht bekannt — beim Start der neuen Session erfragen.

## Wichtige Dateipfade
- App: `/home/user/claude/uigen/uigen/`
- Workflow: `/home/user/claude/.github/workflows/deploy.yml`
- Prisma Schema: `/home/user/claude/uigen/uigen/prisma/schema.prisma`
