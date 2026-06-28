---
name: zew-praesentation
description: Erstellt oder bearbeitet eine ZEW-Präsentation im offiziellen Corporate Design. Nutzt den offiziellen pptx-Skill als Engine (Template-Editing), wendet die ZEW-CI an und rendert Windows-nativ über PowerPoint. Aufruf: /zew-praesentation <Thema oder Aufgabe>
---

Erstelle oder bearbeite eine ZEW-PowerPoint-Präsentation. Aufgabe: $ARGUMENTS

## Engine: offizieller pptx-Skill (kein handgeschriebenes XML aus dem Nichts)

Verwende den **`pptx`-Skill** (`anthropic-skills:pptx`) als Maschine. Der bewährte
Template-Editing-Workflow ist Pflicht — **nicht** Folien-XML von Hand neu erfinden:

1. `thumbnail.py` + `extract-text` auf das Quell-Deck → Layouts und Platzhalter sichten
2. `unpack.py` → Folien-XML bearbeiten (Edit-Tool, ein `<a:p>` je Listenpunkt)
3. `clean.py` → `pack.py … --original <quelle>`

**Quelle wählen (Priorität):**
1. **Existiert ein in PowerPoint gestaltetes Quell-Deck** (z. B. `input/*.pptx`, das Aufbau
   und Inhalt vorgibt)? → **Dieses als Template nehmen** und Inhalte verfeinern. Native
   PowerPoint-Optik bleibt erhalten — das ist der wichtigste Qualitätshebel.
2. Sonst die ZEW-Basisvorlage: `<AOS_ROOT>\templates\Vorlage PPT.pptx`

Folien aus Layouts neu zu generieren ist nur die letzte Option (kein Quell-Deck, keine Vorlage).

## ZEW-CI — verbindliche Regeln

- Schrift ausschließlich **Calibri** (Titel Bold)
- **Flach**: kein Schatten, keine 3D-, keine Verlaufseffekte
- **Logos & Wordmark nie verschieben, skalieren oder löschen**
- Folienformat **33,87 × 19,05 cm** (16:9)
- Fließtext Grau 80 %, Mindestgröße 18 pt; Titel Intrans auf Weiß oder Weiß auf Farbe
- Bei Layout-/Inhaltsunsicherheit: **fragen, nicht raten** (max. eine Rückfrage)

### Farbpalette (ab 2023)

| Name | HEX | RGB |
|---|---|---|
| Eisblau (Hauptakzent) | `aadade` | 170 / 218 / 222 |
| News Grün | `c8d400` | 200 / 212 / 0 |
| News Grün abgedunkelt | `a2bc0c` | 162 / 188 / 12 |
| ZEW Intrans | `39484f` | 57 / 72 / 79 |
| Grau 80 % | `575756` | 87 / 87 / 86 |
| Eisblau abgedunkelt I | `7bbec4` | 123 / 190 / 196 |
| Eisblau abgedunkelt II | `80b3c4` | 128 / 179 / 196 |

Tabellen: Kopfzeile Intrans (weiße Schrift), Bandzeilen helles Eisblau (`f0f6f7`),
Gruppen-/Tagestrenner Eisblau. Charts: primär Eisblau + News Grün, Grau als Neutralton.
Legacy-Farben (ZEW Blau `003f7f`, Hellblau `0090d4`, Grün `78be20`) nur auf explizite Anfrage.

## Design-Hinweise (mit der ZEW-CI vereinbar)

Die Anti-AI-Slop-Regeln des pptx-Skills gelten und decken sich mit der CI:
**keine Akzentlinien unter Titeln, keine dekorativen Vollbreit-Balken/Ribbons** —
einzige Ausnahme ist die CI-eigene Logo-/Wordmark-Kopfmarke der Vorlage.
Layouts dürfen variieren (Tabelle, Zwei-Spalten, Callout, Kennzahl), aber stets CI-konform,
flach und in der Palette. Kein Text-Overflow; lieber kürzen/splitten als überlaufen lassen.

## Render & visuelle QA (Windows — LibreOffice fehlt)

Der `soffice`+`pdftoppm`-Pfad des pptx-Skills läuft hier **nicht**. Stattdessen
PowerPoint-COM:

```powershell
powershell -File <AOS_ROOT>\scripts\pptx-to-png.ps1 -Pptx "<deck>.pptx"
# erzeugt <deck-Ordner>\render\Folie1.PNG …
```

Danach die PNGs visuell prüfen (frischer Blick — Subagent empfohlen) auf: Überlappung,
Overflow/abgeschnittener Text, kollidierende Fußnoten/Seitenzahlen, ungleiche Abstände,
Kontrast, Platzhalterreste. **Höchstens ein Fix-und-Prüf-Zyklus**, dann stoppen — kein
Pixel-Schubsen.

Content-QA zusätzlich: `extract-text <deck>.pptx` auf fehlende Inhalte, Tippfehler,
falsche Reihenfolge und Platzhalterreste (`grep -iE "x{3,}|lorem|TODO|\[insert"`).

## Input-Konvention (Projektordner)

- `input/` enthält i. d. R. **ein Struktur-/Quell-PPTX** (gibt Aufbau + Inhalt vor) und
  **`.txt`-Dateien** für Tabellen-/Detailinhalte.
- Output: `<Projektordner>\<Name>_ZEW.pptx`.

## Umgang mit Smart Quotes / Umlauten

Beim Einfügen neuer Texte XML-Entities nutzen (`&#x201C;`/`&#x201D;`/`&#x2019;`), Umlaute
korrekt setzen. unpack/pack des pptx-Skills kodieren Smart Quotes automatisch.
