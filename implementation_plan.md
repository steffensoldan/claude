# Umsetzungsplan: Meetily-GLM-Bridge

Übersetzungs-/Zusammenfassungs-Brücke für Meetily-Transkripte mit
austauschbarem LLM-Provider (Anthropic → später Scaleway/GLM 5.2) und
separatem, mehrbenutzerfähigem Web-Interface. Details/Kontext: `PROJECT.md`.
Vollständiges Konzept mit Alternativen-Abwägung:
`/root/.claude/plans/ich-brauche-ein-konzept-agile-sonnet.md`.

---

## 1. Benötigte Benutzerfreigaben / Review

* [x] Build-Ort (Top-Level-Ordner statt `aos/projects/`) — vom Nutzer bestätigt
* [x] Meetily-Spike wird simuliert (plausible Annahme + Fixtures) statt live
      verifiziert — vom Nutzer bestätigt
* [x] Reale Inhalte bereits in Anthropic-Phase erlaubt — vom Nutzer bestätigt
* [x] Vor Produktivbetrieb mit echten Meeting-Inhalten: lokale Verifikation
      des Meetily-Schemas — abgeschlossen 2026-07-04, Schema war falsch,
      korrigiert (siehe `docs/meetily-integration-spike.md`)

---

## 2. Offene Fragen

* [ ] Exakter GLM-5.2-Modell-ID-String bei Scaleway — zur Laufzeit via
      `GET /v1/models` zu verifizieren, sobald ein echter Scaleway-Key vorliegt
      (nicht Teil dieses Umsetzungslaufs, da kein Key verfügbar)

---

## 3. Geplante Änderungen

### Provider-Abstraktion
* **[NEW]** `backend/app/providers/base.py` — `TranslationProvider`-ABC, `TranslationResult`, `ProviderError`
* **[NEW]** `backend/app/providers/anthropic_provider.py`
* **[NEW]** `backend/app/providers/scaleway_provider.py`
* **[NEW]** `backend/app/providers/factory.py`

### Meetily-Source-Abstraktion
* **[NEW]** `backend/app/meetily_source.py` — `MeetilySource`-ABC, `SqliteMeetilySource`, `ExportFolderMeetilySource`
* **[NEW]** `docs/meetily-integration-spike.md`

### Auth/Jobs/DB
* **[NEW]** `backend/app/db.py`
* **[NEW]** `backend/app/auth.py`
* **[NEW]** `backend/app/jobs.py`
* **[NEW]** `backend/app/config.py`

### Web-App
* **[NEW]** `backend/app/main.py`
* **[NEW]** `backend/templates/{login,dashboard}.html`
* **[NEW]** `backend/static/app.js`

### Tests & Doku
* **[NEW]** `backend/tests/{unit,integration,e2e}/*`, `backend/tests/fixtures/*`
* **[NEW]** `backend/pyproject.toml`, `.env.example`, `.gitignore`
* **[NEW]** `walkthrough.md`

---

## 4. Verifizierungsplan

### Automatisierte Tests
* `cd backend && pytest -q` — unit (Provider gegen Mocks, Meetily-Source gegen
  Fixtures, Auth), integration (FastAPI TestClient: Login, Job-Flow,
  Multi-User-Isolation), e2e (Fixture-Transkript → Job → gemockter Provider →
  Download, Inhaltsabgleich)
* `ruff check .`

### Manuelle Verifizierung (außerhalb der automatisierten Schleife)
* Live-Smoke-Test mit echtem Anthropic-Key gegen ein reales Transkript
* Nach Erhalt eines Scaleway-Keys: `GET https://api.scaleway.ai/v1/models`
  gegen echten Key, Modell-ID in `.env` eintragen, Smoke-Test wiederholen
* Vor Ort auf der VM: echte Meetily-Installation, SQLite-Pfad/Schema oder
  Export-Format verifizieren, `MEETILY_SOURCE_*`-Konfiguration anpassen
* Cross-User-Download-Versuch im Browser (zwei Testkonten)
