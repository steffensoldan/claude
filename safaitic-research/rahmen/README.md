# `rahmen/` — Der Band mit erzählender Klammer

**Versuchsordner.** Hier entsteht eine Fassung des Bandes, die dem Register-Band einen
erzählenden Rahmen vor- und nachstellt. Der Ordner ist bewusst **eigenständig**: Er enthält
alles, was zum Bauen nötig ist, und greift auf nichts außerhalb zu. `register/` und `archiv/`
bleiben unangetastet — wird die Fassung verworfen, genügt es, diesen Ordner zu löschen.

| Datei | Rolle |
|---|---|
| `wer_dies_liest_register_v6.docx` | **Grundlage.** Die handbearbeitete v6 des Autors, unverändert. Wird nur gelesen: als Textquelle und als Docx-Skelett (Georgia-Styles, `sectPr`). |
| `scripts/build_rahmen.py` | Eigenständiges Bauskript. Keine Importe aus `register/`. |
| `wer_dies_liest_die_sache_v7.docx` | **Ausgabe.** Entsteht beim Lauf; überschreibt die Grundlage nicht. |
| `RAHMEN.md` | Konzept „Die Sache", getroffene Entscheidungen, Aufbau. |

## Bauen

```bash
# aus safaitic-research/
python3 rahmen/scripts/build_rahmen.py
# -> rahmen/wer_dies_liest_die_sache_v7.docx
```

Idempotent: Zwei Läufe erzeugen dieselbe Datei. Eingabe und Ausgabe sind verschiedene Dateien,
die Grundlage bleibt bit-identisch zur hochgeladenen Handfassung.

## Was sich gegenüber der Grundlage ändert

Nur Vorwort und Nachwort. **Die 138 Stücke, die acht Registerüberschriften und alle Kopfzeilen
„Fundort · Sigle" sind zeichengleich übernommen** — geprüft beim Bauen.

- Das Vorwort (acht Gedankenstrich-Absätze) ist durch den **Rahmen-Eingang** ersetzt, ebenfalls
  acht Absätze. Sein Informationsgehalt steckt jetzt in den Absätzen 4, 5 und 8.
- Nach Register VIII folgt der **Rahmen-Schluss**; seine letzte Zeile ist der Titel des Bandes,
  gesetzt wie auf dem Titelblatt.
- Der Apparat (OCIANA-Absätze, Erstausgaben, Fundorte, Sonderzeichen) steht **im Wortlaut der
  Handfassung** als nüchterner Anhang dahinter. Kein Wort daran ist geändert — auch die Nennung
  der maschinellen Analyse bleibt dort stehen, wo der Autor sie hingesetzt hat.

## Offener Punkt

Im dritten OCIANA-Absatz steht „… kommen aus OCIANA.L. Analyse, Übertragen und Sortieren …".
Das `L.` sieht nach einem verrutschten Zeichen aus. Es ist **unverändert übernommen** und wartet
auf eine Entscheidung des Autors.
