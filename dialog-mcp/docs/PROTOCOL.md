# Protokoll

Single Source of Truth für den Werkzeugvertrag. Die inhaltlichen Regeln stehen in
`memory/debate-mode.md` im AOS; dieses Dokument beschreibt nur, wie der Server sie durchsetzt.

## Zustände

```
dialog_open
     │
     ▼
  probing ──(alle Sonden liegen)──► probe_review
                                        │
                    converged ──────────┼────────── diverged
                        │               │              │
                        ▼               │              ▼
                      done ◄─── dialog_close ───── debating
                                                  (Zug wechselt
                                                   nach jedem Beitrag)
```

`repeat` führt von `probe_review` zurück nach `probing` mit erhöhter Sondenrunde.
`done` ist terminal — wie im AOS-Dateimodell. Für neuen Klärungsbedarf ein neuer Thread.

## Invarianten

1. **Identität kommt aus dem Token.** Kein Werkzeug nimmt eine Teilnehmer-ID entgegen. Ein Agent
   kann sich nicht als der andere ausgeben.
2. **Nur wer am Zug ist, schreibt.** Der Server hält den Zug; das ersetzt das Mutex aus `status.md`.
3. **Blindheit ist serverseitig.** Während `probing` liefert der Server fremde Sonden nicht aus —
   auch nicht an die Weboberfläche. Genannt wird nur, wessen Sonde fehlt.
4. **Der Rundenzähler steigt beim zweiten Sprecher** einer Runde — die Regel des AOS-Dateimodells.
5. **Konvergenz wird nicht semantisch beurteilt.** Der Server prüft mechanisch und verweigert
   `converged` nur in den zwei Fällen, in denen Einigkeit nachweislich nichts wert ist. Die
   Bewertung selbst spricht ein Debattierender aus, mit Begründung.
6. **Verlängern, Wiederholen und vorzeitiges Schließen sind dem Eigentümer vorbehalten.** Agenten
   empfehlen über das Feld `extension` — Advisory-Modell wie in §4.

## Werkzeuge

| Werkzeug | Wer | Zustand | Wirkung |
|---|---|---|---|
| `dialog_open` | alle | – | legt Thread an, Zustand `probing` |
| `dialog_list` / `dialog_status` | alle | jeder | Übersicht bzw. kompakter Zustand |
| `dialog_read` | alle | jeder | Verlauf; Sonden verdeckt solange `probing` |
| `dialog_probe_submit` | Sondierende | `probing` | eine Sonde je Teilnehmer und Sondenrunde |
| `dialog_probe_results` | alle | ab `probe_review` | alle Sonden + Konvergenz-Vorprüfung |
| `dialog_probe_resolve` | Debattierende, Eigentümer | `probe_review` | `converged` \| `diverged` \| `repeat` |
| `dialog_post` | wer am Zug ist | `debating` | validiert und hängt an, übergibt den Zug |
| `dialog_wait` | alle | jeder | blockiert bis Zug, fällige Sonde oder Zustandswechsel |
| `dialog_close` | Debattierende nach der letzten Runde, Eigentümer jederzeit | ≠ `done` | schließt und exportiert |

## Pflichtfelder von `dialog_post`

| Feld | `strict` | `light` | Regel |
|---|---|---|---|
| `body` | ✓ | ✓ | §5 |
| `evidence[]` — `path` + `locator` | ✓ | – | §1 |
| `objections[]` — `claim`, `reasoning`, `retract_if` | in Runde 1–2 mindestens einer | – | §1 |
| `clearances[]` — Alternative zum Einwand: 2 verschiedene Risikofelder, je mit `retract_if` | ersatzweise | – | §1 |
| `priorities` — ≤ 2 `dimensions` + `sacrifice` | ✓ | – | §3 |
| `matrix` — alle 5 Dimensionen, Compliance mit `gate` | ✓ | – | §3 |
| `residual` — `difference`, `why_unresolvable`, `measurement` | in der letzten Runde | – | §4 |
| `extension` | freiwillig | freiwillig | §4 |

`compliance` darf nicht priorisiert werden: das Gate ist nicht abwägbar.
Risikofelder: `netzwerk`, `daten`, `plattform`, `berechtigungen`, `ressourcen`.

## Wann `converged` abgelehnt wird

- Die normalisierten Artefakte unterscheiden sich → das ist Divergenz.
- Mindestens eine Sonde hat keine Evidenz berührt → geteilter Prior, kein Konsens.
- Alle Sonden haben nur dieselbe einzelne Stelle berührt → kein unabhängiger Befund.

## Export

Beim Abschluss schreibt der Server nach `<export_dir>/<slug>/`:

| Datei | Inhalt |
|---|---|
| `status.md` | Steuerungsdatei im AOS-Format (`status`, `max_rounds`, `current_round`, `started`, `topic`) |
| `from-<id>.md` | Beiträge eines Teilnehmers, Kopfzeile und Signatur wie im AOS-Dialog |
| `probes.md` | Sondenphase; menschliche Sonden sind markiert |
| `outcome.md` | Zusammenfassung des Abschlusses |

Alles UTF-8 **ohne BOM** mit LF. Committet wird von Hand — der Dienst fasst Git nicht an.
