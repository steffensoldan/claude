# Walkthrough (Stand: 02.07.2026)

Dieses Dokument dokumentiert die Behebung von Verbindungsproblemen, API-Fehlern und Rendering-Blockaden der Anwendung **Wisskomm-Viz** auf der ZEW-VM sowie die erfolgreiche Umstellung auf das stärkste KI-Modell.

---

## 1. Zusammenfassung der vorgenommenen Änderungen

### 1.1 Stabilitäts- & Deployment-Verbesserungen (`app.py` & `deploy.py`)
*   **Dotenv-Integration:** `app.py` lädt die API-Keys nun robust über `python-dotenv` aus der `.env`-Datei, auch wenn der Dienst im Hintergrund ohne vererbte Shell-Variablen läuft.
*   **Uvicorn-Startparameter:** Das Deployment-Skript `deploy.py` startet Uvicorn nun explizit mit der Option `--env-file .env`.

### 1.2 Behebung der API-Verbindungsprobleme und Modell-Upgrade (`prompt.py`)
*   **Modell-Upgrade auf Opus 4.8:** Die Anwendung wurde auf das stärkste verfügbare Modell **`claude-opus-4-8`** umgestellt.
*   **Veraltete Parameter entfernt:** Der Parameter `temperature` wurde aus dem API-Aufruf entfernt, da dieser bei der Nutzung des Opus 4.8-Modells veraltet ist und zu einem API-Fehler (Status 400) führte.
*   **Token-Limit erhöht (Truncation Fix):** Das maximale Output-Limit (`max_tokens`) wurde von 4000 auf **8000** erhöht. Dies verhindert, dass der JSON-Output aufgrund der vorausgehenden Denk-Tokens des Modells („Thinking“) mitten im Schreibvorgang abgeschnitten wird.

### 1.3 Gunicorn-Timeout-Anpassung auf der VM (`stellar-galaxy`)
*   **Behebung der Gunicorn-Worker-Abbrüche:** Da die Verarbeitung komplexer PDFs mit Claude Opus 4.8 mehr als 30 Sekunden in Anspruch nehmen kann, brach Gunicorn (die Django-Instanz auf Port 8080) die Verbindung ab. Der Gunicorn-Timeout auf der VM wurde per SSH-Skript von 30 Sekunden auf **120 Sekunden** erhöht.

### 1.4 Clickjacking / IFrame-Sicherheitsblockade gelöst (`coop_app/views.py`)
*   **xframe_options_exempt:** Der Django-Endpunkt `wisskomm_proxy`, welcher Anfragen an den FastAPI-Dienst auf Port 8090 weiterleitet, wurde mit dem Decorator `@xframe_options_exempt` versehen. Dadurch wird der Header `X-Frame-Options: DENY` für diesen Endpunkt unterdrückt, sodass Firefox und Chrome das IFrame im Editor-Dashboard anstandslos laden.

---

## 2. Testergebnisse & Verifikation

Die Fehlerbehebung wurde über lokale Diagnoseskripte direkt auf der remote VM durchgeführt und erfolgreich validiert:

1.  **Gültigkeit des API-Schlüssels:** Verifiziert durch direkte API-Abfragen via Python und cURL vom Linux-Server.
2.  **Modell-Kompatibilität:** Diagnosetests bestanden für `claude-opus-4-8` und `claude-haiku-4-5`.
3.  **End-to-End-Upload:** Ein simulierter PDF-Multipart-Upload an den Port-8080-Proxy lief erfolgreich durch und lieferte den Status **`200 OK`** samt der vollständig generierten HTML-Befundseite.
4.  **IFrame-Kompatibilität:** Der Ausschluss des `X-Frame-Options`-Headers wurde im HTTP-Antwortkopf verifiziert.

---

# Walkthrough (Stand: 03.07.2026) — Sicherheits- & Betriebs-Härtung

Zweite Änderungsrunde durch Claude Code: Beseitigung eines Secret-Lecks, Härtung des Netzwerk-Bindings und Ersteinrichtung der Versionskontrolle.

## 1. Änderungen (lokales Repo)
*   **`deploy.py`:** Hartkodiertes SSH-Passwort, Server-IP, User und Pfade entfernt. Konfiguration jetzt ausschließlich über Umgebungsvariablen (`WISSKOMM_VM_*`) bzw. lokale `.env`; Abbruch mit Klartext-Hinweis bei fehlenden Variablen. Start- und Crontab-Kommando auf `--host 127.0.0.1` umgestellt.
*   **`.gitignore` / `.env.example`:** Neu angelegt (`.env`, `venv/`, `sessions/`, `output/`, `uvicorn.log` ausgeschlossen; Vorlage für alle benötigten Variablen).
*   **`requirements.txt`:** `anthropic` auf `==0.115.1` gepinnt (Stand VM), fehlendes `python-dotenv==1.2.2` ergänzt.
*   **`SPEC-Wisskomm-Viz.md` → `implementation_plan.md`:** Umbenannt gemäß AOS-Dateikonvention; Referenzen in `PROJECT.md` und `task.md` nachgezogen.
*   **`build.py`:** Tippfehler „Standlone" → „Standalone" in der Log-Ausgabe.
*   **`wisskomm-viz.service`:** `--host 127.0.0.1 --env-file .env`; als derzeit inaktiv dokumentiert (System-Unit erfordert root; Autostart läuft über Crontab).

## 2. Änderungen auf der VM (als `sts`, ohne root)
*   `.env`-Berechtigung von `644` auf `600` gesetzt.
*   `@reboot`-Crontab auf das kanonische Startkommando (localhost, `--env-file`) angeglichen.
*   Testartefakte (`test`, `test-*`) aus `output/` entfernt; echte Publikationen (`dp*`) erhalten.
*   Uvicorn per Prozess-Simulation neu gestartet (kein echter Reboot mangels root und wegen mitlaufender Django-Instanz).

## 3. Versionskontrolle
*   Repository initialisiert, erster Commit (`init:`), Push als Branch `claude/wisskomm-viz` nach `steffensoldan/claude`.

## 4. Testergebnisse & Verifikation
1.  **Localhost-Bindung:** `ss` bestätigt `127.0.0.1:8090`; direkter externer Zugriff auf `:8090` liefert kein Ergebnis mehr (erwartet).
2.  **Selbsttest VM-intern:** `GET http://127.0.0.1:8090/wisskomm` → **HTTP 200**.
3.  **End-to-End über Proxy:** `GET http://192.168.70.65:8080/wisskomm` → **HTTP 200** (Nutzerpfad unverändert funktionsfähig).
4.  **Secret-Gegenprobe:** Kein Passwort mehr in `deploy.py`; keine `.env`/Key-Dateien im Git-Staging.

## 5. Offen
*   SSH-Key-Auth statt Passwort in `deploy.py` (separat vereinbart).
*   Echter Reboot-Test des `@reboot`-Autostarts steht aus (root erforderlich).

---

# Walkthrough (Stand: 03.07.2026) — Quarto-Pilot (Ausbaustufe 3)

Isolierter Pilot des im `implementation_plan.md` (Teil J) entworfenen Quarto-Hausdienstes:
aus einer Quelle mehrere Formate mit zentraler ZEW-CD. Kein Eingriff in den laufenden
FastAPI-Dienst.

## 1. Neue Dateien (Repo)
*   `_quarto.yml` — 4 Formate (html, typst/PDF, revealjs, pptx); `brand: _brand.yml`; `embed-resources`.
*   `_brand.yml` — zentrale ZEW-CD; Farben aus den offiziellen RGB-Werten normalisiert;
    System-Schrift als DSGVO-sauberer Platzhalter (ZEW-Hausschrift folgt als WOFF2).
*   `theme/zew.scss` — HTML-Feinschliff (Hero, Signal-Meter, KPI-Karten).
*   `templates/reference-zew.pptx` — PPTX-CD-Vorlage (Theme-Farbschema + Schriften via python-pptx).
*   `publications/zew-dp-26-021/index.qmd` + `data/*.csv` + `data/README.md` — Referenz-DP;
    Grafiken mit matplotlib in CD-Farben (formatübergreifend statisch).

## 2. Bewusste Pilot-Entscheidungen
*   **Charts als matplotlib-Standbilder** (statt Observable/interaktiv), damit alle vier Formate
    aus derselben Quelle funktionieren (Interaktivität ginge nur in HTML/RevealJS).
*   **Kein Marken-Rot:** Die ZEW-CD führt kein Rot; die Signatur „signal/diluted" nutzt Blau
    (voll) vs. Grau (verdünnt). Finale Festlegung offen.

## 3. Build-Umgebung auf der VM (user-lokal, ohne root)
*   Quarto 1.9.38 nach `~/opt/quarto-1.9.38` (Tarball, kein root).
*   Isolierter venv `~/wisskomm-quarto-pilot/.venv` (via `virtualenv`) mit
    `ipykernel nbclient nbformat matplotlib pandas pyyaml`.
*   Render mit `QUARTO_PYTHON` auf den venv gesetzt. Pilot liegt getrennt vom Dienst unter
    `~/wisskomm-quarto-pilot/` — der FastAPI-Dienst bleibt unberührt.

## 4. Testergebnisse & Verifikation
1.  **Render:** alle vier Formate erzeugt — `index.html` (self-contained), `index.pdf` (Typst),
    `slides.html` (RevealJS), `index.pptx`.
2.  **DSGVO (statisch):** keine `fonts.googleapis`/`gstatic`; keine externen `src`/`href`/`url()`;
    Assets als `data:`-URIs eingebettet. Finaler Netzwerk-Monitor zur Laufzeit steht als
    letzte Bestätigung noch aus.
3.  **PPTX-Realität:** Folien-XML enthält nativen `<a:t>`-Text (editierbar); 3 Chart-Bilder
    unter `ppt/media/` — bestätigt: Text editierbar, Grafiken als Standbilder.

## 5. Offen
*   ZEW-Hausschrift (WOFF2) einbinden; offizielles CD-Handbuch gegenprüfen.
*   „signal vs. diluted" ohne Marken-Rot final festlegen.

---

# Walkthrough (Stand: 03.07.2026) — Quarto-Serving (getrennte Eingänge)

Die Quarto-Ausgaben sind jetzt für Nutzer unter eigener URL erreichbar, parallel zum
KI-Pfad. Kein Django-Eingriff nötig — der bestehende Proxy `re_path(^wisskomm/(?P<path>.*)$)`
reicht beliebige Unterpfade an den FastAPI-Dienst weiter.

## 1. Änderungen (Repo)
*   `app.py`: zusätzliches StaticFiles-Mount `/wisskomm/pub` → `published/` (Pfad über
    `WISSKOMM_PUBLISH_DIR` überschreibbar, `html=True`). KI-Pfad `/wisskomm/view` unverändert.
*   `publish_quarto.py` (neu): env-getriebenes Skript, das auf der VM `quarto render` ausführt
    und `_site/publications/*` in den bedienten `published/`-Ordner kopiert.
*   `.env.example`: `WISSKOMM_QUARTO_DIR`, `WISSKOMM_QUARTO_BIN`, `WISSKOMM_PUBLISH_DIR`.
*   `.gitignore`: `published/`.

## 2. Deployment (VM, nach ausdrücklicher Freigabe)
*   `app.py` hochgeladen, Quarto-Ausgabe nach `~/wisskomm-viz/published/` kopiert, Uvicorn
    kanonisch (localhost, `--env-file`) neu gestartet.

## 3. Testergebnisse & Verifikation
1.  Intern (127.0.0.1:8090): `/wisskomm` → 200 (KI-Pfad unverändert),
    `/wisskomm/pub/zew-dp-26-021/` → 200.
2.  Extern über Django-Proxy (192.168.70.65:8080): `/wisskomm` → 200;
    `/wisskomm/pub/zew-dp-26-021/` → 200 (4,85 MB, Titel korrekt ausgeliefert).

## 4. Zugangsmodell (Ergebnis)
*   **KI-Schnellentwurf:** `…/wisskomm` (Upload) → `…/wisskomm/view/<slug>/`.
*   **Quarto-Hausdienst:** `…/wisskomm/pub/<slug>/`.

## 5. Offen
*   Auto-Rebuild-Trigger (aktuell Publishing als eigener Schritt via `publish_quarto.py`).

## 6. Nachtrag: Dashboard-Verlinkung (03.07.2026)
*   `app.py` (Dashboard-Route) sammelt veröffentlichte Quarto-Pubs unter `PUBLISH_DIR`
    (Ordner mit `index.html`), liest den Titel aus dem HTML und erkennt vorhandene Formate.
*   `templates/dashboard.html`: neue Sektion „Quarto-Hausdienst" mit Links Web/PDF/Folien/PPTX.
*   Deployed und über den Proxy verifiziert: `/wisskomm` → 200, Sektion + `/wisskomm/pub/…`-Links vorhanden.

---

# Sync-Checkpoint (03.07.2026, vor Ausbau „zwei Zugänge / KI→Quarto")

Vor Beginn der nächsten Erweiterung wurde die Dreifach-Synchronität verifiziert:

*   **Lokal ↔ GitHub:** Working Tree sauber, Branch `claude/wisskomm-viz` gepusht
    (Stand Commit `5db45e4`), 0 Commits Differenz zu `origin`.
*   **Lokal ↔ VM (MD5-Abgleich, alle identisch):**
    *   deployte App (`~/wisskomm-viz`): `app.py`, `prompt.py`, `build.py`,
        `requirements.txt`, `wisskomm-viz.service`, `templates/{dashboard,ui,standalone}.html`.
    *   Quarto-Projekt (`~/wisskomm-quarto-pilot`): `_quarto.yml`, `_brand.yml`,
        `theme/zew.scss`, `templates/reference-zew.pptx`, `publications/zew-dp-26-021/*`.
*   **Nur lokal/GitHub (bewusst nicht auf der VM):** `deploy.py`, `publish_quarto.py`,
    `.env.example`, `.gitignore`, Doku — reine Steuer-/Repo-Dateien, kein Laufzeitbedarf.

Ausgangsbasis für den Ausbau ist damit sauber und reproduzierbar.

---

# Walkthrough (Stand: 03.07.2026) — Zwei wählbare Zugänge (KI→Quarto-Prototyp)

Nutzer wählen beim Upload den Ausgabe-Zugang: **Fixes HTML** (unverändert) oder **Quarto**
(Mehrformat mit ZEW-CD). Der Quarto-Zugang nutzt das bestehende KI-JSON — Claude schreibt
**kein** freies Quarto; ein Konverter erzeugt CSVs + eine getemplatete `.qmd`.

## 1. Änderungen (Repo)
*   `templates/dashboard.html`: Radio-Auswahl `output_mode` (html/quarto) im Upload-Formular.
*   `app.py` (`upload_pdf`): `output_mode` entgegennehmen, in Session speichern; bei `quarto`
    → `build_quarto.build_quarto_publication(...)` via `run_in_threadpool` → Redirect
    `/wisskomm/pub/<slug>/`. Fixed-HTML-Pfad unverändert.
*   `build_quarto.py` (neu): KI-JSON → `data/*.csv` (Datenvertrag) + `.qmd` aus Vorlage →
    `quarto render` (Subprozess, Quarto-venv als Engine) → Ausgaben nach `published/<slug>/`.
*   `templates/publication.qmd.j2` (neu): feste `.qmd`-Struktur mit matplotlib-Charts (lesen die
    CSVs) und ZEW-CD. Eigene Jinja-Delimiter `[[ ]]`/`[% %]`, damit Python-`{ }` nicht kollidiert.
*   `deploy.py`: `build_quarto.py` + `publication.qmd.j2` in die Upload-Liste aufgenommen.

## 2. Verifikation
1.  **Offline (lokal, ohne Quarto):** echte Session-JSON → alle `[[ ]]`-Platzhalter aufgelöst,
    CSVs korrekt, keine Delimiter-Kollision; `py_compile` aller Dateien OK.
2.  **VM (nach Freigabe):** Deploy + Uvicorn-Neustart; Dashboard trägt die Auswahl.
    Render-Test (`build_quarto` gegen `dp26011`-Daten) → `/wisskomm/pub/dp26011-quarto/` 200
    (extern über Proxy, 4,9 MB; PDF 200). Testartefakt danach entfernt.
3.  **Regression:** `/wisskomm/view/dp26011/index.html` → 200 (Fixed-HTML unverändert).

## 3. Bewusste Prototyp-Grenzen
*   An die aktuelle (BCA-)Datenstruktur gebunden — wie das Fixed-HTML.
*   KI-Textfelder mit HTML-Tags: sauber im HTML-Output, in PDF/PPTX ggf. ignoriert.
*   Kein Refine/Chat für Quarto-Pubs (generate-once); Live-Render blockiert kurz (Sekunden).

## 4. Fix (03.07.2026): Quarto-Uploads erzeugten toten /view/-Link
*   **Symptom:** Quarto-Uploads (z. B. `dp26018`) tauchten auch in „Bestehende Publikationen"
    (Fixed-HTML) auf, dort mit `/wisskomm/view/<slug>/…` → 404 (kein Fixed-HTML-Output).
*   **Fix (`app.py`):** Dashboard-Route überspringt Sessions mit `output_mode == "quarto"`
    in der Fixed-HTML-Liste; sie erscheinen nur in der Quarto-Sektion mit `/pub/`-Links
    (Web/PDF/Folien/PPTX). Verifiziert: `view/dp26018` = 0 Links, `pub/dp26018` = 4 Links.
*   **Legibility (`publication.qmd.j2`):** größere Schrift (14) + höhere Auflösung (dpi 160)
    + größere Beschriftungen/Figuren; `dp26018` neu gerendert.

## 5. Fix (03.07.2026): keine Format-Navigation aus der gerenderten Ansicht
*   **Symptom:** Der Django-Proxy folgt dem 303-Redirect nach dem Upload serverseitig
    (`urllib`), daher wird die Web-Version unter der `/upload`-URL angezeigt. Die gerenderte
    Seite hatte keine Links zu den anderen Formaten → „not found" bzw. Sackgasse; nur manuelle
    `/pub/<slug>/…`-URLs funktionierten.
*   **Fix (`build_quarto.py`):** `_inject_format_bar()` fügt oben in `index.html` eine Leiste
    mit **absoluten** Links (Web/PDF/Folien/PPTX + Dashboard) ein. Absolute `/wisskomm/pub/`-Pfade
    funktionieren unabhängig davon, unter welcher URL die Seite gerade angezeigt wird.
*   Verifiziert (extern über Proxy): Leiste vorhanden, alle Zielformate 200; `dp26008`/`dp26018`
    neu gerendert.

## 6. Fix (03.07.2026): Upload großer PDFs → leere Antwort (NS_ERROR_NET_EMPTY_RESPONSE)
*   **Ursache (aus gunicorn.log):** Der Django-Proxy (`stellar-galaxy/coop_app/views.py:27`,
    `body = request.body`) liest den kompletten Upload in den Speicher; das unterliegt
    Djangos `DATA_UPLOAD_MAX_MEMORY_SIZE` (Default **2,5 MB**). PDFs darüber → `RequestDataTooBig`
    → leere Antwort, **bevor** die Anfrage Wisskomm erreicht. Kein Wisskomm-Bug.
*   **Fix (PROJEKTÜBERGREIFEND, in `stellar-galaxy` = Antigravity):** in `coop_app/settings.py`
    `DATA_UPLOAD_MAX_MEMORY_SIZE` und `FILE_UPLOAD_MAX_MEMORY_SIZE` = **10 MB**; Gunicorn neu
    gestartet. Verifiziert: 3-MB-Upload passiert den Proxy (HTTP 400 „PDF-Extraktion",
    kein RequestDataTooBig).
*   **ACHTUNG Drift:** Änderung direkt auf der VM gemacht; die lokale Kopie unter
    `projects/Projekte-Antigravity/stellar-galaxy` ist dadurch veraltet → mit Antigravity
    synchronisieren. Wisskomm selbst wurde für diesen Fix NICHT geändert.
*   **Bekannte Rest-Grenze:** Sehr große Paper könnten das 120-s-Timeout (Claude + Render)
    treffen (bewusst nicht angefasst).

---

# Walkthrough (Stand: 06.07.2026) — ZEW-CD-Integration (Integrationstiefe 1)

Änderungsrunde durch Antigravity: Integration der Hausschriften und CD-Farbwerte aus dem `zewEcon`-Vorlagenpaket in den Quarto-Generierungspfad von Wisskomm-Viz sowie Härtung des Deployments.

## 1. Änderungen
*   **Schrifteinbindung:** ZEW-Hausschriften `LinLibertine` (Serif) und `Calibri` (Sans-Serif) unter `theme/fonts/` abgelegt.
*   **_brand.yml:** Die Fonts im Quarto-Branding-Schema registriert und die Farbpalette auf die offiziellen Hex-Codes (`#c8d202`, `#35484f`, `#abdadc`, `#9c9e9f`) angepasst.
*   **theme/zew.scss:** Update aller Farbspezifikationen. `@font-face`-Deklarationen für die lokalen TTF-Schriften hinzugefügt, sodass Linux Libertine (Fließtext) und Calibri (Überschriften) in Web- und RevealJS-Ausgaben nativ gerendert werden.
*   **templates/publication.qmd.j2:** Matplotlib-Farbwörterbuch und Szenarienzuordnungen aktualisiert. Die Matplotlib-`rcParams` wurden so konfiguriert, dass Diagramme standardmäßig mit der Schriftart `Calibri` gerendert werden.
*   **deploy.py:** Hinzufügen der neuen Schriftdateien (`theme/fonts/*.ttf`), `_brand.yml`, `_quarto.yml` und `theme/zew.scss` zur SFTP-Uploadliste. Falls kein Passwort in der `.env` hinterlegt ist, versucht das Skript einen schlüsselspezifischen SSH-Login (unter Verwendung von `~/.ssh/id_ed25519`).

## 2. Testergebnisse & Verifikation
1.  **Lokale Kompilierung:** `py_compile` von `deploy.py` und `build_quarto.py` erfolgreich durchgeführt.
2.  **Git-Synchronisation:** Alle Änderungen im Branch `claude/wisskomm-viz` auf GitHub gepusht.

---

# Walkthrough (Stand: 06.07.2026) — Umschaltbarer LLM-Provider (Claude vs. Scaleway GLM-5.2)

Änderungsrunde durch Antigravity: Implementierung einer dynamischen Umschaltlogik in Wisskomm-Viz, um flexibel zwischen dem standardmäßigen Anthropic Claude und der Scaleway GLM-5.2 API wechseln zu können.

## 1. Änderungen
*   **templates/publication.qmd.j2 / prompt.py:** 
    - Implementierung einer Provider-Weiche über die Umgebungsvariablen `WISSKOMM_LLM_PROVIDER` (Werte: `anthropic` oder `scaleway`) und `WISSKOMM_LLM_MODEL`.
    - Nutzt **Lazy Imports** für `openai` und `anthropic` in `prompt.py`, sodass kein Importfehler auftritt, wenn eine der Bibliotheken nicht installiert ist.
    - System-Prompt-Handling für die OpenAI-kompatible Scaleway-Schnittstelle als erste System-Message implementiert.
*   **requirements.txt:** `openai==1.59.0` hinzugefügt.
*   **.env.example:** Neue Umgebungsvariablen (`WISSKOMM_LLM_PROVIDER`, `WISSKOMM_LLM_MODEL`, `SCW_SECRET_KEY`) dokumentiert.

## 2. Verwendung (Switching)
- **Claude:** `WISSKOMM_LLM_PROVIDER=anthropic` + `ANTHROPIC_API_KEY` setzen.
- **Scaleway GLM:** `WISSKOMM_LLM_PROVIDER=scaleway` + `SCW_SECRET_KEY` setzen.

---

# Walkthrough (Stand: 06.07.2026) — ZEW-CD-Feinschliff & System-Härtung

Dritte Änderungsrunde durch Antigravity: Behebung von API- und Render-Abbrüchen bei der Integration der ZEW-Hausschriften, Dynamisierung der Grafikgenerierung für beliebige Studien und Anhebung der Dateigrößen-Limits.

## 1. Änderungen
*   **Schriften-Lokalisierung:** Die ZEW-Hausschriften `LinLibertine` und `Calibri` wurden in ein `fonts/`-Verzeichnis direkt auf der Quarto-Projekt-Wurzelebene verschoben, um die Kompatibilität mit dem internen Dependency-Kopierer von Quarto herzustellen. Die Pfade in `_brand.yml` und `deploy.py` wurden entsprechend angepasst.
*   **theme/zew.scss:** Bereinigung manueller, redundanter `@font-face`-Deklarationen, um Compiler-Warnungen bei der PDF- und RevealJS-Erstellung zu vermeiden.
*   **templates/publication.qmd.j2:** Vollständige Dynamisierung der Matplotlib-Diagrammzellen. Die Grafikerstellung ermittelt die abzubildenden Kenngrößen nun dynamisch anhand der extrahierten numerischen Datenspalten, anstatt cba-spezifische Variablen wie `leakage_pct` hart zu codieren. Dies verhindert KeyErrors bei beliebigen Studien.
*   **prompt.py:**
    - Lenientes JSON-Parsing (`strict=False`) zur Tolerierung von Sonder-/Steuerzeichen.
    - Kontext-Kürzung für lange Dokumenttexte (auf die ersten 40.000 und die letzten 10.000 Zeichen), um das 32k-Limit von GLM-5.2 sicher einzuhalten.
    - Erhöhung von `max_tokens` auf `16384` und Deaktivierung des fehlerhaften JSON-Modus des Providers, um Schleifen oder vorzeitiges Abschneiden der Generierung zu verhindern.
*   **coop_app/settings.py (Proxy-Projekt `stellar-galaxy`):** Anhebung der Django-Upload-Grenzen (`DATA_UPLOAD_MAX_MEMORY_SIZE` und `FILE_UPLOAD_MAX_MEMORY_SIZE`) von 10 MB auf **50 MB**, gefolgt von einem geordneten Gunicorn-Reload auf der VM.

## 2. Testergebnisse & Verifikation
1.  **Dateiupload:** Übergroße PDF-Dokumente passieren den Django-Proxy auf Port 8080 nun problemlos und ohne Verbindungsabbrüche.
2.  **LLM-Weiche:** Die API-Abfragen an den Scaleway-Provider laufen fehlerfrei durch und liefern vollständig parsebares JSON.
3.  **Visualisierung & Rendering:** Die Generierung aller vier Zielformate läuft ohne KeyError oder Pfad-Fehler durch und wendet das ZEW-Branding korrekt an.
