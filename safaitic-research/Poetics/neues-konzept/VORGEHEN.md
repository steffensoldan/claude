# Vorgehen — Neues Konzept
*Stand: Juni 2026*

---

## 1. Korpusbasis

**Quelle:** OCIANA (Oxford Corpus of the Inscriptions of Ancient North Arabia),
University of Oxford / Khalili Research Centre.
**Datei:** `ociana_corpus.xml` (43 MB, proprietäres Flat-XML, nicht EpiDoc/TEI).
**Verteilung:** Als GitHub-Release `v01-data` diesem Repository angehängt.

---

## 2. Filterlogik — von 37.955 auf die Teilmengen

```
37.955  Gesamtinschriften im Korpus
      ↓ Script = "Safaitic"
31.768  Safaitische Inschriften

      ↓ Kern (Übersetzung nach Genealogie-Stripping) = leer
18.535  Reine Signaturen         z.B. "By ʾnʿm"  oder  "By S¹ny son of Ms¹k son of …"
                                 → Kapitel I (Präsentativ), bisher nicht erschlossen

      ↓ Kern 1–29 Zeichen, kein Gebet, kein Ereignis
 6.594  Minimale Aktionstexte    z.B. "By ʿbd son of Tm — and he camped"
                                 → Kapitel I, bisher nicht erschlossen

      ↓ Kern ≥ 30 Zeichen, kein Anrufungs-Regex
 3.285  Narrative ohne Anrufung  → safaitic_narrative.xlsx  (NEU: +798 vs. Band 1)
                                 → Kapitel II, III, IV, VI, VII

      ↓ Vokativpartikel h + Gottesname im Transliterationstext
 2.018  Anrufungs-Inschriften    → safaitic_invocations.xlsx
                                 → alle Kapitel, v.a. III und V
```

**Wichtig:** Anrufungen und Narrative schließen sich gegenseitig aus.
Eine Inschrift fällt in genau eine der beiden Kategorien.

---

## 3. Neu gegenüber Band 1 / Erweiterte Ausgabe

| | Band 1 | Erweitert | Neues Konzept |
|---|---|---|---|
| Basis | Top 69 Texte (Score) | Pool 130 (Kern ≥ 25 W) | Vollkorpus 31.768 |
| Signaturen (≈18.500) | nein | nein | **ja** |
| Minimal-Aktionen (≈6.600) | nein | nein | **ja** |
| Narrative-Datei | 2.487 Texte | 2.487 Texte | **3.285 Texte** |
| Strukturprinzip | Jahresbogen | Jahresbogen + Steine (Er-Form) | 7 Sprechregister |

---

## 4. Ausgabedateien (alle in `data/`)

| Datei | Inhalt | Zeilen |
|---|---|---|
| `safaitic_invocations.xlsx` | 2.018 Anrufungen, nach Kategorien | 2.018 |
| `safaitic_narrative.xlsx` | 3.285 narrative Texte ohne Anrufung, nach Score | 3.285 |
| `safaitic_full_corpus.xlsx` | Alle 31.768 Safaitischen, Typ-Spalte | 31.768 |
| `safaitic_top100_interesting.txt` | Top 100 nach Scoring (Hist./Astro./Emotion/Szene) | — |
| `safaitic_top50_stories.txt` | Top 50 nach Kerntextlänge | — |

Das Skript `scripts/generate_outputs.py` reproduziert alle fünf Dateien
aus `ociana_corpus.xml` (Laufzeit ca. 60–90 s).

---

## 5. Struktur des Poetics-Ordners

```
Poetics/
├── band1/           Erstausgabe "Wer dies liest, lebe lang"
│                    69 Nachdichtungen, Jahresbogen, Ich-Form
│                    Skripte: score.py, build_xlsx.py, book.js
│
├── erweitert/       Erweiterte Ausgabe
│                    Manuskript + Übergabe-Dokumentation
│                    9 neue Steine (Er-Form), 2 Echos, Schlussstein
│
└── neues-konzept/   Dieses Verzeichnis
    ├── VORGEHEN.md       Dieses Dokument
    ├── KONZEPT.md        Konzeptionelle Beschreibung / Vorwort-Entwurf
    ├── PROOF_OF_CONCEPT.md   21 Gedichte als Strukturprobe
    ├── data/             Ausgabedateien (Vollkorpus-Lauf)
    └── scripts/          generate_outputs.py
```

---

## 6. Offene Punkte

- [ ] Kapitel I braucht direkte Auswahl aus `safaitic_full_corpus.xlsx`
      (Typ = "Signature" oder "Minimal") — Kriterien noch festlegen
- [ ] Dedup-Logik für Signaturen prüfen (viele Namensähnlichkeiten)
- [ ] Glossar der Siglen für neue Inschriften ergänzen
      (SSWS, AAHY, KRS 1991 u.a. noch unbelegt)
- [ ] Verhältnis zu Band 1 / Erweitert klären:
      separater Band oder Erweiterung des Erweitert-Manuskripts?
