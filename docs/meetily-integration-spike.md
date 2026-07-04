# Meetily-Integrations-Spike — SIMULIERT, vor Ort zu verifizieren

Diese Session lief in einer Cloud-Sandbox ohne Zugriff auf eine echte
Meetily-Installation (Tauri-Desktop-App, benötigt Windows/macOS/Linux-GUI +
Audio-Hardware für ein reales Testmeeting). Der unten beschriebene Spike
wurde daher **nicht live durchgeführt**, sondern durch eine dokumentierte,
plausible Annahme ersetzt (Nutzer-Entscheidung, siehe Chat-Verlauf).

## Recherchebefund (Web-Recherche, nicht live gegen Meetily verifiziert)

- Meetily (aktuelle Tauri/Rust-Generation) hat **keine dokumentierte laufende
  REST-API** — die frühere FastAPI-Schnittstelle ist laut Projekt-Doku nicht
  mehr die aktive API.
- Persistenz läuft über **SQLite** ("meeting metadata, transcripts, and
  summaries").
- Ob die Community Edition einen Markdown-/JSON-Export anbietet, war nicht
  abschließend recherchierbar.

## Angenommenes Schema (für Implementierung + Tests verwendet)

**SQLite-Variante** (`SqliteMeetilySource`), Tabelle `meetings`:

```sql
CREATE TABLE meetings (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    created_at    TEXT NOT NULL,   -- ISO 8601
    transcript_text TEXT NOT NULL
);
```

**Export-Ordner-Variante** (`ExportFolderMeetilySource`, Default in `.env.example`
— bevorzugt, da entkoppelt von Meetilys internem Schema): ein `*.json` pro
Meeting im konfigurierten Ordner:

```json
{
  "id": "meeting-2026-07-01-weekly-sync",
  "title": "Weekly Sync",
  "created_at": "2026-07-01T10:00:00Z",
  "transcript": "Speaker 1: ...\nSpeaker 2: ..."
}
```

## Zwingender Verifikationsschritt vor Produktivbetrieb (lokal auf der VM)

1. Meetily installieren, ein Testmeeting durchführen.
2. SQLite-Datei lokalisieren (typischer Tauri-Datenpfad unter Windows:
   `%APPDATA%\<app-id>\...` — Wildcard-Suche, nicht hartkodieren) **oder**
   prüfen, ob ein Export-Button existiert.
3. Bei SQLite: `sqlite3 <KOPIE-der-Datei> ".schema"` gegen eine **Kopie**
   ausführen — nie die Live-Datenbank direkt öffnen (Schreibsperre/
   Korruptionsrisiko, besonders im WAL-Modus).
4. Reale Feldnamen/Typen mit der obigen Annahme abgleichen. Bei Abweichung:
   `meetily_source.py` anpassen (nur die betroffene Klasse, Surgical
   Changes — das gemeinsame `MeetilySource`-Interface bleibt unverändert).
5. `.env`: `MEETILY_SOURCE_MODE` und `MEETILY_SOURCE_PATH` auf den realen
   Pfad/Modus setzen.

Bis dahin läuft die Anwendung ausschließlich gegen die Fixture-Daten unter
`backend/tests/fixtures/`.
