# dialog-lite

Dialog zwischen zwei Agenten — **eine HTML-Datei je Thema, sonst nichts.** Kein Dienst,
kein Port, kein Token, keine Datenbank. Jeder Client startet den Server selbst über stdio.

Die Datei ist zugleich dreierlei: **Speicher** (der Zustand liegt als JSON im Kopf),
**Liveticker** (sie lädt sich alle fünf Sekunden nach, solange der Dialog läuft) und
**Abschlussdokument** (beim Schließen fällt das Nachladen weg). Doppelklick genügt —
sie funktioniert über `file://`, ohne Server und auf einem Stick.

> Die große Schwester ist [`../dialog-mcp/`](../dialog-mcp/): HTTP-Dienst, Bearer-Token,
> SQLite, voller Debattenmodus, Weboberfläche. Wer nachgewiesene Identität, erzwungene
> Blindheit oder Mehrbenutzerbetrieb braucht, nimmt die.

## Was durchgesetzt wird

Drei Regeln, mehr nicht:

1. **Nur wer am Zug ist, schreibt.** Der Zug wechselt nach jedem Beitrag; der Rundenzähler
   steigt beim zweiten Sprecher einer Runde — wie im AOS-Dateimodell.
2. **Kein leerer Beitrag.**
3. **Jeder Einwand braucht seine Rücknahmebedingung.** Ohne `retract_if` wird der Beitrag
   abgelehnt: *„Wer das nicht angeben kann, hat ein Stilmittel geliefert, keinen Einwand."*

Dazu die **blinde Sondenphase**: Vor Runde 1 reichen beide verdeckt ein Artefakt ein —
Datei und Zeile, ein Testfall, eine konkrete Entscheidung. Stimmen sie überein, ist die
Debatte unnötig und der Dialog endet sofort. Die Sonden liegen währenddessen in
`<slug>.probe-<id>.json` und wandern erst beim Auflösen in die HTML-Datei; der Ticker
bleibt so auch für den mitlesenden Menschen blind.

Kriterien-Matrix, Priorisierung und Restdifferenz-Pflicht gibt es hier nicht.

## Einrichten

```bash
python3 -m venv .venv && .venv/bin/pip install -e .
```

Bei jedem teilnehmenden Harness den Server als stdio-MCP-Server eintragen, mit der eigenen
Kennung. Für Claude Code:

```bash
claude mcp add aos-dialog -- /pfad/zu/.venv/bin/python -m dialog_lite \
  --as claude --dir /pfad/zu/dialogen
```

Das andere Harness bekommt denselben Befehl mit anderem `--as` und **demselben `--dir`**.
Die Kennungen sind frei wählbar — nichts ist auf bestimmte Agenten verdrahtet.

## Ablauf

```
dialog_open  →  beide reichen dialog_probe ein  →  dialog_probe_resolve
                     converged: fertig, keine Debatte
                     diverged:  dialog_post im Wechsel  →  dialog_close
```

| Werkzeug | Wirkung |
|---|---|
| `dialog_open(slug, topic, partner, max_rounds=3)` | Legt `<slug>.html` an, startet die Sondenphase |
| `dialog_list()` | Dialoge im Ordner mit Zustand und wer am Zug ist |
| `dialog_read(slug)` | Voller Verlauf; fremde Sonden verdeckt, solange die Phase läuft |
| `dialog_probe(slug, artifact)` | Blinde Erstlösung |
| `dialog_probe_resolve(slug, outcome, rationale)` | `converged` \| `diverged`, Begründung Pflicht |
| `dialog_post(slug, body, objections)` | Beitrag; `objections` = `[{claim, retract_if}]` |
| `dialog_close(slug, summary)` | Ergebnis eintragen, Ticker abschalten |

## Drei Einschränkungen, offen benannt

- **Identität ist eine Behauptung, kein Nachweis.** Wer den Server mit `--as beta` startet,
  ist Beta. Das ist zumutbar, solange du beide Clients selbst konfigurierst.
- **Blindheit ist Konvention, keine Garantie.** Die Sonden liegen auf derselben Platte, auf
  die beide Agenten Dateizugriff haben. Der Server liefert sie nicht aus und der Ticker
  enthält sie nicht — aber ein Agent, der gezielt `<slug>.probe-<partner>.json` öffnet,
  umgeht das. In `dialog-mcp` ist es ausgeschlossen, weil die Daten hinter einer
  Schnittstelle liegen.
- **Zwei Teilnehmer, ein Ordner, ein Mensch.** Kein Mehrbenutzerbetrieb, keine Rollen.

Gleichzeitiges Schreiben ist abgesichert, nicht ignoriert: geschrieben wird atomar über
`os.replace`, und ein `revision`-Zähler bricht den Aufruf mit klarer Meldung ab, wenn
zwischen Lesen und Schreiben jemand dazwischenkam.

## Tests

```bash
.venv/bin/pip install -e ".[dev]" && .venv/bin/python -m pytest tests -q
```

Darunter ein End-to-End-Lauf mit **zwei echten Prozessen** über stdio auf demselben Ordner —
blinde Sonden, Divergenz, Runden, Abschluss — und die Gegenprobe, dass übereinstimmende
Sonden die Debatte überspringen.
