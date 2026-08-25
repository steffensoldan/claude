# dialog-mcp

MCP-Server für regelgebundene Debatten zwischen zwei Agenten — die Server-Fassung des
AOS-Dialogs. Was in `memory/debate-mode.md` als Konvention steht, ist hier Zustandsautomat
und Schema: ein Beitrag ohne Rücknahmebedingung wird nicht ermahnt, sondern abgelehnt.

Dazu kommt, was das Dateimodell nicht leisten kann: eine **blinde Sondenphase** vor dem
ersten Austausch. Beide Seiten lösen unabhängig, geben ein Artefakt ab, und erst danach
entscheidet sich, ob überhaupt debattiert wird.

## Was der Server durchsetzt

- **Identität aus dem Bearer-Token.** Kein Werkzeug nimmt eine Teilnehmer-ID als Argument.
- **Schreibrecht am Zug.** Ersetzt das Mutex aus `status.md`, ohne Dateikonvention.
- **Blindheit serverseitig.** Fremde Sonden werden während der Phase nicht ausgeliefert —
  auch nicht an die Weboberfläche.
- **Debattenmodus als Schema.** Evidenzangabe, Rücknahmebedingung, deklarierte Priorität mit
  benanntem Opfer, Kriterien-Matrix, und in der letzten Runde die Restdifferenz samt Messdesign.
- **Advisory-Modell.** Verlängern, Sonden wiederholen und vorzeitig schließen bleiben dem
  Menschen vorbehalten; Agenten empfehlen.

Der vollständige Werkzeugvertrag steht in [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

## Compliance

Der Dienst erfüllt das Gate aus `debate-mode.md` §3:

| Hard-Blocker | Status |
|---|---|
| Unkontrollierter Datenabfluss | Keine ausgehenden Verbindungen. Daten liegen in SQLite auf dem Host und im Export-Verzeichnis. |
| Proprietäre Lizenz ohne freie Option | Nur `mcp`, `starlette`/`uvicorn` und `jinja2` — alle quelloffen. |
| Online-Zwang zur Laufzeit | Keiner. Der Dienst läuft vollständig im internen Netz. |

Die Weboberfläche lädt **keine externen Assets** — Stile liegen unter `static/`. Ein CDN-Aufruf
wäre nach §3 ein heilbarer Verstoß und wird von vornherein vermieden.

## Betrieb

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
cp config.example.toml config.toml && chmod 600 config.toml
# Token erzeugen:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
.venv/bin/python -m dialog_mcp --config config.toml
```

Der Dienst hört auf einem Port und bedient beides:

- MCP: `http://<host>:<port>/mcp`
- Weboberfläche: `http://<host>:<port>/`

Für den Dauerbetrieb liegt eine systemd-Unit unter [`deploy/dialog-mcp.service`](deploy/dialog-mcp.service)
bei — eigener Benutzer, schreibgeschütztes System, keine neuen Privilegien.

**Erreichbarkeit:** An `127.0.0.1` binden und einen Reverse-Proxy mit TLS davorsetzen, oder an
die interne Schnittstelle binden. Von außerhalb des ZEW-Netzes ist der Dienst nicht erreichbar —
Cloud-Sessions in Anthropics Rechenzentrum können ihn deshalb nicht nutzen; Clients müssen im
Netz laufen.

## Clients anbinden

Claude Code:

```bash
claude mcp add --transport http aos-dialog https://dialog.zew.intern/mcp \
  --header "Authorization: Bearer <token-des-teilnehmers>"
```

Jeder Teilnehmer bekommt sein eigenes Token — daran hängt seine Identität im Dialog.
Andere MCP-Clients werden analog konfiguriert: Streamable HTTP auf `/mcp` plus
`Authorization`-Header.

## Ablauf eines Dialogs

```
dialog_open  →  alle reichen blind dialog_probe_submit ein
             →  dialog_probe_results  →  dialog_probe_resolve
                    converged: fertig, keine Debatte
                    diverged:  dialog_post im Wechsel  →  dialog_close
```

Statt zu pollen: `dialog_wait` blockiert, bis der Aufrufer am Zug ist.

## Weboberfläche

Mitlesen in Echtzeit (Server-Sent Events, kein Polling), eigene Sonde einreichen, und für den
Eigentümer die Steuerung, die §4 dem Menschen vorbehält. Anmeldung mit demselben Token, das
auch die Agenten benutzen; Sitzungen liegen im Arbeitsspeicher, ein Neustart erzwingt neue
Anmeldung. Formulare sind CSRF-geschützt, das Sitzungs-Cookie ist `HttpOnly` und `SameSite=Strict`.

Eine menschliche Sonde ist keine unabhängige *Modell*-Stichprobe. Für die Fehler-Dekorrelation
ist sie wertvoller als eine dritte Instanz desselben Modells, im Messdesign für *k* Sonden zählt
sie aber nicht mit — der Export markiert sie deshalb.

## Export ins AOS

Beim Abschluss schreibt der Server `<export_dir>/<slug>/` im gewohnten AOS-Format
(`status.md`, `from-<id>.md`, `probes.md`, `outcome.md`), UTF-8 ohne BOM. Der Dienst fasst Git
nicht an — committet wird von Hand.

## Tests

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest tests -q
```

Enthält einen End-to-End-Lauf über echtes HTTP: zwei Token, blinde Sonden, Divergenz, zwei
Runden, Abschluss — plus die Gegenprobe, dass konvergente Sonden den Thread ohne Debatte beenden.

## Offen

- **Runner**, der Agenten selbst aufweckt. Bewusst nicht enthalten: der Dienst startet keine
  Prozesse und braucht deshalb keine API-Schlüssel auf dem Host.
- **Anpassung von `dialog/README.md` und `commands/dialog-reply.md`** im AOS, damit die Agenten
  die Werkzeuge statt der Dateien nutzen.
