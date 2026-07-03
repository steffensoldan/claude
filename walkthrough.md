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
