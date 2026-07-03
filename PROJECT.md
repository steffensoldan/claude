# Project: Wisskomm-Viz

**Interaktive Befund-Aufbereitung als Hausdienst für alle Forschenden des ZEW**

---

## 1. Übersicht & Ziel
Wisskomm-Viz ist ein interner Dienst, mit dem Forschungsberichte des ZEW (z. B. PDF Discussion Papers) automatisch in interaktive, DSGVO-konforme und markenkonforme Standalone-HTML-Seiten umgewandelt werden können. 

*   **Eingabe:** PDF-Dokument + Optionale Anforderungen via Web-Oberfläche.
*   **Verarbeitung:** Lokale Text-Extraktion, Strukturierung & Kernaussagen-Generierung via Claude API, und statische HTML-Rendering via Jinja2 Templates.
*   **Ausgabe:** Komplett eigenständige HTML-Dateien zur Veröffentlichung (ohne CDNs, Tracker oder Google Fonts).

---

## 2. Tech-Stack
*   **Backend:** Python 3.11, FastAPI, Uvicorn
*   **PDF-Parsing:** pypdf (4.2.0)
*   **KI-Modell:** Anthropic API (`claude-opus-4-8`)
*   **Template Engine:** Jinja2
*   **Datenbank/Speicher:** Dateibasierte Sessions (.json)
*   **Deployment:** Paramiko (SSH/SFTP-Automatisierung)

---

## 3. Verzeichnisstruktur
```text
wisskomm-viz/
├── implementation_plan.md  # Detaillierte Fachspezifikation und Datenverträge
├── PROJECT.md              # Diese Einstiegsdokumentation (Tech-Stack & Setup)
├── walkthrough.md          # Änderungshistorie und Verifikationsdokumentation
├── app.py                  # FastAPI Anwendung (Upload, Refine, Dashboard)
├── prompt.py               # API-Schnittstelle und System-Prompts für Claude
├── build.py                # HTML Compiler aus extrahierten JSON-Daten
├── deploy.py               # SSH-basiertes Deployment-Skript für die Linux-VM
├── requirements.txt        # Python Abhängigkeiten
├── templates/              # HTML Vorlagen für Dashboard, Editor-UI und Ausgabe
│   ├── dashboard.html      # Einstiegsseite mit Upload
│   ├── ui.html             # Editor-Ansicht (Split-Screen Vorschau & Feedback-Chat)
│   └── standalone.html     # Das Ziel-Layout für den finalen Befund
├── sessions/               # Temporäre Speicherung der Bearbeitungssitzungen (JSON)
└── output/                 # Speicherort der generierten Publikationsordner
```

---

## 4. Setup & Startbefehle (Lokal)
1.  Isoliertes Environment einrichten:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
2.  Umgebungsvariable für API-Schlüssel setzen (z. B. in einer `.env`):
    ```env
    ANTHROPIC_API_KEY=sk-ant-api03-...
    ```
3.  Server lokal starten:
    ```bash
    uvicorn app:app --host 127.0.0.1 --port 8090 --env-file .env
    ```

---

## 5. Betrieb auf der ZEW-VM (Produktion)
Da auf der VM kein Root-Zugriff für Portfreigaben besteht, läuft das Projekt im **Subdirectory-Routing** über eine bereits geöffnete Django-Instanz:

1.  **FastAPI/Uvicorn** läuft intern auf Port `8090` und lauscht auf `localhost`.
2.  **Django** (`stellar-galaxy`) läuft auf Port `8080` und leitet alle Anfragen unter `/wisskomm` über einen Proxy-View (`wisskomm_proxy`) an Port `8090` weiter.
3.  **Gunicorn-Konfiguration:** Gunicorn ist mit `--timeout 120` gestartet, um Abbrüche während der längeren Opus-Modellaufrufe zu verhindern.
4.  **Autostart:** Ein Cronjob (`@reboot`) startet Uvicorn bei Systemneustarts automatisch.

### Deployment ausführen
Um lokale Code-Änderungen auf die VM zu übertragen:
```bash
python deploy.py
```
*(Das Skript verbindet sich via SSH mit der VM `192.168.70.65`, überträgt die Dateien, führt Pip-Installs im venv aus, beendet die alten Prozesse und startet Uvicorn mit der `.env`-Konfiguration neu).*
