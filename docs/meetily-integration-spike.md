# Meetily-Integrations-Spike — Status: VERIFIZIERT gegen echte Meetily-Installation

**2026-07-04, VM:** Meetily v0.4.0 wurde auf der Ziel-VM installiert und das
reale SQLite-Schema gegen eine Kopie der Live-Datenbank verifiziert (siehe
"Verifiziertes Schema" unten). Die ursprüngliche, in der Cloud-Sandbox
getroffene Annahme (siehe "Historie" ganz unten) war in einem entscheidenden
Punkt falsch und wurde korrigiert.

## Installation (2026-07-04)

- Neueste Release von `github.com/Zackriya-Solutions/meetily/releases` geholt:
  **v0.4.0**.
- `meetily_0.4.0_x64_en-US.msi` (Pro-Maschine-Installer) scheiterte mit
  Error 1925 („Log on as administrator") — die Sitzung lief ohne
  Admin-Rechte.
- `meetily_0.4.0_x64-setup.exe /S /CURRENTUSER` (NSIS-Installer,
  Pro-Nutzer-Modus) **funktionierte ohne Admin-Rechte**: installiert nach
  `%LOCALAPPDATA%\meetily\`.
- Beide Installer-Downloads per SHA256 gegen den von der GitHub-API
  gemeldeten Digest verifiziert.

## Realer Datenpfad (verifiziert)

Nach einmaligem Start von `meetily.exe` legt die App an:
- **SQLite-DB (WAL-Modus):** `%APPDATA%\com.meetily.ai\meeting_minutes.sqlite`
  (App-ID `com.meetily.ai`, nicht `meetily`)
- Kein automatischer JSON-/Markdown-Export gefunden — die
  export_folder-Variante bleibt vorerst unbelegt (siehe unten).

Schema wurde gegen eine **Kopie** der DB geprüft (App vorher sauber beendet,
damit WAL eingecheckt ist) — nie die Live-Datei direkt geöffnet.

## Verifiziertes Schema

Bestätigt sowohl durch Introspektion der realen (leeren, da noch kein
Testmeeting aufgezeichnet wurde) DB als auch durch Abgleich mit den
offiziellen Migrationsdateien im Meetily-Repo
(`frontend/src-tauri/migrations/*.sql`):

```sql
-- meetings: NUR Metadaten, KEIN Transkript-Feld (Annahme unten war falsch)
CREATE TABLE meetings (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    folder_path TEXT              -- seit Migration 20251006, pro-Meeting-Ordner
);

-- transcripts: EIN ROW PRO AUDIOSEGMENT, nicht pro Meeting
CREATE TABLE transcripts (
    id              TEXT PRIMARY KEY,
    meeting_id      TEXT NOT NULL,   -- Fremdschlüssel, NICHT unique
    transcript      TEXT NOT NULL,   -- Text dieses einen Segments
    timestamp       TEXT NOT NULL,
    summary         TEXT,
    action_items    TEXT,
    key_points      TEXT,
    audio_start_time REAL,           -- Sekunden ab Aufnahmebeginn (seit Migr. 20251006)
    audio_end_time   REAL,
    duration         REAL,
    speaker          TEXT            -- 'mic' oder 'system' (seit Migr. 20251110)
);
```

**Wichtigste Abweichung von der ursprünglichen Annahme:** Es gibt kein
`transcript_text`-Feld auf `meetings`. Der vollständige Meeting-Text muss aus
allen `transcripts`-Zeilen mit passender `meeting_id`, sortiert nach
`audio_start_time`/`timestamp`, zusammengesetzt werden (ein Zeile pro
Sprachsegment, `speaker` unterscheidet Mikrofon vs. Systemaudio, nicht
benannte Sprecher). `transcript_chunks` (mit einem `transcript_text`-Feld,
das zufällig namensgleich zur ursprünglichen Annahme ist) ist eine interne
Arbeitstabelle für die Chunk-Verarbeitung während der Transkription, nicht
die finale Quelle.

**Code-Fix:** `backend/app/meetily_source.py::SqliteMeetilySource` wurde
entsprechend umgeschrieben (JOIN über `meeting_id`, Aggregation der
Segment-Zeilen). `ExportFolderMeetilySource` ist unverändert, da Meetily
keinen nativen Export in diesem Format anbietet — falls die App künftig
eine Export-Funktion bekommt, muss deren tatsächliches Format erneut geprüft
werden.

**Weiterhin offen (kein reales Testmeeting durchgeführt):** Die obige
Segment-Struktur ist durch Schema + Migrationshistorie sehr sicher belegt,
aber nicht durch echte Beispieldaten (DB war zum Zeitpunkt der Prüfung leer,
kein Mikrofon/Testaufnahme in diesem Auftrag). Vor dem ersten echten
Produktiv-Job: ein reales Testmeeting in Meetily aufnehmen und
`get_transcript()` gegen die dabei entstehenden Zeilen prüfen.

## `.env`-Konfiguration (aktualisiert)

```
MEETILY_SOURCE_MODE=sqlite
MEETILY_SOURCE_PATH=C:\Users\sts\AppData\Roaming\com.meetily.ai\meeting_minutes.sqlite
```

---

## Historie: ursprüngliche Annahme (Cloud-Sandbox, vor VM-Verifikation)

Die Implementierung entstand ursprünglich in einer Cloud-Sandbox ohne Zugriff
auf eine echte Meetily-Installation. Der Spike wurde dort durch eine
dokumentierte, aber **wie oben gezeigt teilweise falsche** Annahme ersetzt:

```sql
-- ANNAHME, WIDERLEGT — meetings hat KEIN transcript_text-Feld
CREATE TABLE meetings (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    transcript_text TEXT NOT NULL
);
```

Die Export-Ordner-Variante (`ExportFolderMeetilySource`, weiterhin Fallback
ohne bekanntes natives Gegenstück in Meetily) blieb unverändert:

```json
{
  "id": "meeting-2026-07-01-weekly-sync",
  "title": "Weekly Sync",
  "created_at": "2026-07-01T10:00:00Z",
  "transcript": "Speaker 1: ...\nSpeaker 2: ..."
}
```
