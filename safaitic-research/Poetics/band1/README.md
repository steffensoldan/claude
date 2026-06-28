# Safaitic — Gedichtband

*Wer dies liest, lebe lang* — eine literarische, nachgedichtete Auswahl aus den
erzählenden safaitischen Inschriften der nordarabischen Steppe (1. Jh. v. – 4. Jh. n. Chr.).

## Ziel

Aus einem großen Inschriftenkorpus einen **Gedichtband** formen, der die Lebens- und
Ausdruckswelt der nomadischen Verfasser spürbar macht: verknappt, klanghaft, verankert —
aber ausdrücklich *nicht* wissenschaftlich-vollständig.

Leitgedanke: Die Auswahl ist kuratiert und folgt unserem Ohr. Sie sagt damit mehr über die
Lesenden aus als über die Entstehungszeit. Diese Übersetzungsdistanz (beschädigter Stein →
philologische Lesung → englische OCIANA-Übersetzung → deutsche Nachdichtung) ist nicht Mangel,
sondern Gegenstand des Bandes.

Vorbild der Anlage ist weniger eine Edition als die kuratierende Verdichtung im Sinne der
*Carmina Burana*: thematische Ordnung plus ein verbindendes Rahmenkonzept (hier der
Jahreszyklus der Steppe) mit einem wiederkehrenden Refrain als Klammer.

## Inhalt des Ordners

```
safaitic-research/
├── README.md                          Dieses Dokument (Ziel, Überblick)
├── safaitic_gedichtband.docx          Manuskript: 69 Nachdichtungen, 12 Abschnitte, 4 Refrains
├── docs/
│   ├── vorgehen.md                    Methodik: Phasen, Bewertungsraster, Architektur, Grenzen
│   └── struktur.md                    Aufbau des Bandes + Zuordnung Thema → Jahresbogen
├── data/
│   └── safaitic_gedichtband_auswahl.xlsx   Shortlist (150) + gerankte Longlist (2.451)
└── scripts/
    ├── score.py                       Dedup + literarisch gewichtetes Scoring
    ├── build_xlsx.py                  Auswahltabelle aus dem Scoring-Ergebnis
    └── book.js                        Erzeugung des docx-Manuskripts (docx-js)
```

## Datengrundlage

- Quelle: **OCIANA** (Online Corpus of the Inscriptions of Ancient North Arabia), englische Editionen.
- Eingang: `safaitic_narrative_2.xlsx` — 2.487 erzählende (nicht bloß anrufende) Inschriften, 14 Blätter.
  Diese Eingangsdatei ist hier **nicht** abgelegt; sie wird für die Reproduktion im Arbeitsverzeichnis erwartet.
- Jede Nachdichtung trägt die OCIANA-Quellsigle; darüber ist der Originaleintrag auffindbar.

## Reproduktion

Vom Repo-Wurzelverzeichnis aus, mit `safaitic_narrative_2.xlsx` im Arbeitsverzeichnis:

```bash
# 1) Scoring: Dedup + literarisch gewichtetes Scoring -> scored.pkl
python3 scripts/score.py

# 2) Auswahltabelle -> data/safaitic_gedichtband_auswahl.xlsx
python3 scripts/build_xlsx.py

# 3) Manuskript -> safaitic_gedichtband.docx
npm install -g docx
node scripts/book.js
```

Zwischenartefakt `scored.pkl` muss nicht versioniert werden.
Abhängigkeiten: Python (pandas, numpy, openpyxl), Node.js (docx).

## Stand

Erstfassung, Juni 2026. 69 Gedichte; auf ~80 erweiterbar (Material in `data/` vorhanden).

## Hinweis zu Rechten

Die englischen Übersetzungen stammen aus OCIANA und unterliegen dessen Bedingungen. Die
deutschen Nachdichtungen sind eigenständige, interpretierende Bearbeitungen.
