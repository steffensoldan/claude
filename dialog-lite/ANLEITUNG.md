# Anleitung: Agent-Dialog einrichten und benutzen

Kurzfassung für die Praxis. Technische Details stehen in der README.

Bei dialog-lite gibt es keinen Dienst zu starten. Jeder Agent startet den Server
selbst, sobald er ein Werkzeug benutzt. Einrichten ist einmalig, danach reicht es,
beiden Agenten dasselbe Thema zu geben.


## Teil 1 — Einmalig einrichten

### 1. Code holen und installieren

    git clone -b claude/session-communication-iwyzwe https://github.com/steffensoldan/claude C:\AOS\dialog
    cd C:\AOS\dialog\dialog-lite
    python -m venv .venv
    .venv\Scripts\pip install -e .

Unter Linux oder macOS statt `.venv\Scripts\` entsprechend `.venv/bin/`.

### 2. Ordner für die Dialoge anlegen

Dort landen die HTML-Dateien, eine je Thema:

    mkdir C:\AOS\dialoge

### 3. Bei Claude Code registrieren

`-s user` sorgt dafür, dass der Dialog in allen Projekten verfügbar ist:

    claude mcp add aos-dialog -s user -- C:\AOS\dialog\dialog-lite\.venv\Scripts\python.exe -m dialog_lite --as claude --dir C:\AOS\dialoge

### 4. Beim zweiten Harness registrieren

Fast alle Harnesses nutzen dieselbe JSON-Form. Wo die Datei liegt, steht in deren
Dokumentation:

    {
      "mcpServers": {
        "aos-dialog": {
          "command": "C:\\AOS\\dialog\\dialog-lite\\.venv\\Scripts\\python.exe",
          "args": ["-m", "dialog_lite", "--as", "lokales-modell", "--dir", "C:\\AOS\\dialoge"]
        }
      }
    }

Zwei Dinge müssen stimmen:

- `--as` ist bei beiden **unterschiedlich**. Das ist die Identität im Dialog, frei
  wählbar — nichts ist auf bestimmte Agenten verdrahtet.
- `--dir` ist bei beiden **identisch**. Sonst reden sie an verschiedenen Ordnern
  vorbei und sehen einander nie.

### 5. Prüfen

In Claude Code eingeben:

    /mcp

`aos-dialog` muss dort mit sieben Werkzeugen auftauchen. Beim zweiten Harness
entsprechend in dessen Werkzeugliste nachsehen.


## Teil 2 — Bei einer konkreten Frage

Nichts zu starten. Beide Agenten bekommen dasselbe Thema mit demselben Kürzel
(slug). Ein Agent eröffnet, der andere steigt ein.

### An den ersten Agenten

> Nutze `aos-dialog`. Öffne einen Dialog mit slug `export-allowlist`, Thema
> "Allowlist oder Denylist im Secret-Check von export-aos.ps1?", Partner
> `lokales-modell`, 3 Runden. Sieh dir `scripts/export-aos.ps1` selbst an und
> reiche deine Sonde ein — ein Artefakt, keine Prosa: Datei und Zeile. Danach
> warte; lies nichts vom anderen.

### An den zweiten Agenten

> Nutze `aos-dialog`. Der Dialog `export-allowlist` läuft. Sieh dir
> `scripts/export-aos.ps1` selbst an und reiche deine Sonde ein, bevor du
> irgendetwas vom anderen liest. Danach `dialog_probe_resolve`: stimmen die
> Artefakte überein, `converged`, sonst `diverged`. Bei `diverged` debattiert ihr
> im Wechsel bis `dialog_close`.

Der Partnername im ersten Prompt muss exakt das `--as` des zweiten Agenten sein.

### Mitlesen

Die Datei `C:\AOS\dialoge\export-allowlist.html` doppelklicken. Sie lädt sich alle
fünf Sekunden nach, solange der Dialog läuft, und hört damit auf, sobald er
geschlossen ist. Danach steht das Ergebnis in derselben Datei — verschickbar,
archivierbar, ohne Werkzeug lesbar.


## Teil 3 — Wenn etwas klemmt

**"… ist am Zug, nicht …"**
Kein Defekt, sondern die Regel. Der Zug wechselt streng nach jedem Beitrag. Der
Agent soll `dialog_read` aufrufen und warten, bis er dran ist.

**"Der Einwand … hat keine Rücknahmebedingung"**
Auch Absicht. Gib dem Agenten den Satz mit: *Jeder Einwand endet mit "Ich ziehe
das zurück, wenn ___".* Wer die Bedingung nicht angeben kann, hat ein Stilmittel
geliefert, keinen Einwand.

**"Die Sondenphase läuft noch"**
Der andere hat seine Sonde noch nicht abgegeben. Das ist der Sinn der Phase:
niemand sieht die Erstlösung des anderen, bevor beide geliefert haben.

**"Gleichzeitige Änderung an …"**
Beide haben zugleich geschrieben. Der Server bricht ab, statt zu überschreiben.
Der Agent soll neu lesen und den Aufruf wiederholen.

**Werkzeuge tauchen nicht auf**
Pfad zur `python.exe` prüfen — er muss auf die `.venv` im Projekt zeigen, nicht auf
eine System-Python-Installation. Danach das Harness neu starten.


## Anhang — die große Variante (dialog-mcp)

Nur nötig, wenn du nachgewiesene Identität, erzwungene Blindheit oder Zugriff von
mehreren Rechnern brauchst. Dort gibt es einen echten Dienst:

    cd C:\AOS\dialog\dialog-mcp
    python -m venv .venv
    .venv\Scripts\pip install -e .
    copy config.example.toml config.toml

In `config.toml` je Teilnehmer ein Token eintragen. Token erzeugen mit:

    python -c "import secrets; print(secrets.token_urlsafe(32))"

Starten:

    .venv\Scripts\python -m dialog_mcp --config config.toml

Für den Dauerbetrieb liegt unter `deploy/dialog-mcp.service` eine systemd-Unit bei.

Die Agenten anbinden:

    claude mcp add --transport http aos-dialog http://<host>:8770/mcp --header "Authorization: Bearer <token>"

Jeder Teilnehmer bekommt sein eigenes Token — daran hängt seine Identität.
Mitgelesen wird im Browser unter `http://<host>:8770/`.
Der Ablauf bei einer konkreten Frage ist derselbe wie in Teil 2.
