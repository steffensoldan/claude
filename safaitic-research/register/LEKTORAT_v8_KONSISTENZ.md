# Lektorat v8 — Begriffskonsistenz gegen die safaitischen Originale

Stand: 2026-08-27 · Fassung: `wer_dies_liest_register_v8.docx` (138 Stücke)

**Frage.** Werden Wörter, die im safaitischen Original gleich sind, im Deutschen auch gleich wiedergegeben?

**Datenlage — vollständig.** Alle **138 von 138** Stücken sind mit Transliteration und OCIANA-Übersetzung belegt. Quelle: `ociana_corpus.xml` (37.871 Inschriften) aus dem GitHub-Release `v01-data` dieses Repositoriums, SHA-256 `5a90c113…` verifiziert. Die Datei ist mit 45 MB zu groß fürs Repository; `scripts/extract_originale.py` lädt sie bei Bedarf, prüft die Prüfsumme und schreibt **`originale_138.tsv`** — Original, englische Edition und deutsche Fassung nebeneinander, eine Zeile je Stück.

> Vorher lagen die Originale verstreut: 135 HTML-Seiten in `ociana_pages.zip` (deckten nur 126 Stücke ab, die später ergänzten fehlten) und Transliterationsspalten in `../archiv/corpus-parser/safaitic_invocations.xlsx` und `…_narrative.xlsx` (fünf weitere). Beides ist jetzt durch die eine TSV-Datei abgelöst.

---

## A · Deutliche Abweichungen

### 1. Das Wach- und Warte-Feld (Register III)

Drei verschiedene Originalverben und vier deutsche Wendungen kreuzen sich frei — in beide Richtungen.

| Original | deutsche Wiedergaben |
|---|---|
| **`ḫrṣ`** (13 Stücke) | „hielt Ausschau" 8× · „hielt Wache" 3× (HCH 102, RSIS 322, RWQ 120) · „auf der Lauer" 2× (ASWS 183, RSIS 322) |
| **`tẓr`** (5) | „wartete" 2× (SIJ 30, WAMS 19.2) · „hielt Ausschau" (KWQ 113) · „hielt Wache" (SIJ 10) · „Späherplatz / auf der Lauer" (GSSH 1) |
| **`nẓr`** (2) | „hielt Ausschau" (CEDS 226) · „wartete" (HCH 195) |
| **`mẓr`** (3) | „Späherposten" 2× (C 2753, C 2756) · „Späherplatz" (GSSH 1) |

Umgekehrt steht **„hielt Ausschau" für `ḫrṣ`, `tẓr` und `nẓr`**, „hielt Wache" für `ḫrṣ` und `tẓr`. RSIS 322 führt sogar beide Wendungen für dasselbe Wort im selben Stück.

*Kein Fehler:* HCH 125 lässt `ḫrṣ` unübersetzt — dort übersetzt OCIANA selbst nicht, das Deutsche folgt korrekt.

### 2. Das Objekt der Fluchformel

Von 19 Stücken mit `ʿwr` tragen **8 ein explizites `h- s¹fr` / `h- ḫṭṭ`** im Original. Fünf benennen es im Deutschen, **drei lassen es fallen**:

| | Original | deutsch |
|---|---|---|
| C 4803 · KRS 941 · RSIS 132 · RSIS 351 · WH 368 | `h- s¹fr` / `h- ḫṭṭ` | „die/diese Schrift" ✓ |
| **C 2775 · C 4439 · LP 308** | `h- ḫṭṭ` / `h- s¹fr` | nur „dies" ✗ |

Am schärfsten an einem Paar: **LP 308** und **RSIS 132** sind wörtlich gleich gebaut — `w wgm ʿl- … w h lt ʿwr ḏ yʿwr h- s¹fr` — und heißen einmal „Blindheit dem, der **dies** blind macht", einmal „Blindheit dem, der **die Schrift** blind macht".

Wo das Original **kein** Objekt hat, sagt das Deutsche „dies" (7×) — außer wo OCIANA ein „[the writing]" ergänzt: C 5299 und KRS 2919 folgen dem („die Schrift"), **Is.Mu 242 folgt ihm nicht** („dies").

### 3. Weitere gleichgebaute Stellen

| Original | deutsche Wiedergaben | Stellen |
|---|---|---|
| **`ḥl(l) h- dr`** (3) | „war" · „blieb" · „lagerte an diesem Ort" | HSNS 5 / RSIS 110 / RSIS 351 |
| **`flṭ m- bʾs¹`** (2) | „Errettung vom Bösen" · „errette aus der Not" | C 1629 / MKJS 80 |
| **`f bʾs¹ m ẓll`** (3) | „wer überlebt, verzweifelt" 2× · „und die Trauer legte sich über ihn" | C 2551, KRS 941 / KRS 17 |

## B · Mittlere und geringe Abweichungen

| Original | deutsche Wiedergaben | Stellen | Anmerkung |
|---|---|---|---|
| **`s¹by`** (3) | „den sie fortführten" · „der gefangen war" · „den gefangenen" | KRS 17 / RQ.A 5 / RQ.D 6 | „fortführten" erfindet ein Subjekt |
| **`qtl`** (Partizip) | „erschlagen" 5× · „getötet" 2× · „ermordet" 1× | LP 653, BWM 3 / RQ.D 6, ZN 1 / LP 243 | gleiche Konstruktion |
| **`ḫṭṭ`** | „Schrift" 2× · „Ritzung" 1× | RSIS 351, WH 368 / C 2551 | |
| **`ḏkr`** | „dachte an" 2× · „gedachte" · „erkannte" | C 4803, KRS 17 / RSIS 351 / C 2551 | Rollen verschieden, vertretbar |
| **`ṯʾr`** | „Blutrache" 3× · „Rache" 1× | Is.Mu 242, LP 243, LP 461 / C 2551 | dort mit Ergänzung „an dem, der…" |
| **`wrd`** | „kam ans Wasser" · „zog zum Wasser" | KRS 1586 / ASWS 73 | |

## C · Konsistent — die tragenden Formeln halten

| Original | deutsch | |
|---|---|---|
| `ḥwb` | „weinte vor Kummer" | **12/12** |
| `wgm` | „trauerte" | 26/27 |
| `ʿwr` (Verb) | „blind machen / blenden" | 18/19 (RSIS 351 „auslöscht" — dokumentierte Ausnahme, dort ist die Strafe Krätze, kein Blind-Wortspiel) |
| `s¹lm` | „Sicherheit" | 13/14 (LP 1291 verbal: „heil davon") |
| `flṭ` | „Errettung / errette" | 6/6 |
| `bky` | „weinte" | 4/4 |
| `rʿy` | „weidete" | 4/4 |
| `ḥḍr` | „am beständigen Wasser (lagern)" | 3/3 |
| `ʾs²rq` | „zog tief in die Wüste" | 3/3 |
| `myt` | „starb" | 3/3 |
| `s²nʾ` | „Feind" | 5/5 |
| `mny` | „Schicksal" | 2/2 |

`s¹fr` wird sauber nach Wortart geschieden: als Nomen „Schrift" (6×), als Verb „schrieb" (SIJ 291).

## D · Umgekehrte Richtung — ein deutsches Wort für mehrere Originale

- **„Beute"** für `ġnmt` und `nqmt` — laut `LEKTORAT_v6.md` gewollt, folgt der OCIANA-Glosse.
- **„Schrift"** für `s¹fr`, `ktb` und `ḫṭṭ`.
- **„hielt Ausschau"** für `ḫrṣ`, `tẓr` und `nẓr` (siehe A.1).
- **„weinte"** für `bky` und `ḥwb` — sauber gelöst: `ḥwb` trägt durchgehend den Zusatz „vor Kummer".

## E · Nebenbefunde

- **Is.Mu 88** — `w wr{d} {b-} {h-} mrbʿt w s¹ʾr ----` („und er kam zur Tränke in einem Gebiet mit reichlich Weide und blieb …", so OCIANA) ist im Deutschen nicht wiedergegeben. Das widerspricht dem Befund in `LEKTORAT_v6.md`, es verbleibe kein inhaltlicher Ausschnitt.
- **LP 653** — `ḥḍr h- dr`: OCIANA hat „he camped by permanent water **at this place**"; das Deutsche gibt nur „Er lagerte am beständigen Wasser".

## Vorschlag für v9

Eine feste Zuordnung im Wach-/Warte-Feld, damit Register III trägt:

| Original | fest auf |
|---|---|
| `ḫrṣ` | Ausschau halten |
| `tẓr` | warten |
| `nẓr` | wachen |
| `mẓr` | Späherposten |

Dazu: das Fluchobjekt dem Original folgen lassen (C 2775, C 4439, LP 308 → „die Schrift"; Is.Mu 242 → „die Schrift", da OCIANA es ergänzt), `ḥl(l) h- dr` auf eine Wendung festlegen, `flṭ m- bʾs¹` angleichen, `f bʾs¹ m ẓll` als Litanei durchziehen, `qtl` auf „erschlagen" vereinheitlichen.
