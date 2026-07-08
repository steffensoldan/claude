# Safaitic Invocation Extractor

A data pipeline for extracting, classifying, and exporting divine invocation
inscriptions from the OCIANA corpus (Oxford Corpus of the Inscriptions of Arabia
Nabataean and Nearby).

## What this project does

Safaitic is an ancient North Arabian script (c. 1st century BCE – 4th century CE),
used by nomadic peoples of the Syro-Arabian steppe. The OCIANA corpus contains
~38,000 inscriptions. This project:

1. Parses the full corpus XML (~43 MB, 37,955 inscriptions)
2. Identifies all inscriptions containing a **divine invocation** — the vocative
   particle `h` followed by a deity name (e.g. `h lt` = "O Allāt")
3. Classifies each by deity, request type, and thematic category
4. Exports styled Excel files and curated plain-text lists

## Output files

| File | Contents |
|------|----------|
| `safaitic_invocations.xlsx` | 2,018 divine invocation inscriptions, 8 sheets |
| `safaitic_narrative.xlsx` | 2,487 non-invocation narrative inscriptions, 14 sheets |
| `safaitic_top100_interesting.txt` | Top 100 most narratively rich invocations (scored) |
| `safaitic_top50_stories.txt` | Top 50 longest invocations (raw length) |
| `safaitic_sample_20.xlsx` | 20-row sample for quick inspection |

## Getting started

### Requirements

```bash
pip install lxml pandas openpyxl
```

### Corpus file

The OCIANA corpus XML is **not included in the repository** (43 MB). Download it from
the GitHub Release attached to this repository (`v01-data`) and place it at:

```
safaitic-research/ociana_corpus.xml
```

### Run

```bash
# Full corpus
python3 parse_safaitic.py --xml ociana_corpus.xml

# Bundled sample data only (no corpus needed)
python3 parse_safaitic.py --sample
```

## The 8 attested deities

| Deity | Transliteration forms |
|-------|-----------------------|
| Allāt | `lt`, `ʾlt`, `ylt`, `yʾlt` |
| Rudā | `rḍw`, `rḍy`, `rḍ` |
| Baʿalshameen | `bʿls¹mn`, `bʿls¹m` |
| Dushara | `ds²r`, `ḏs²r` |
| Yaṯaʿ | `yṯʿ`, `ʾṯʿ` |
| Šaʿhaqam | `s²ʿhqm`, `s²ʿqm` |
| Gaddaref | `gdḍf` |
| Gadʿawdh | `gdʿwḏ` |

## Thematic categories

| Category | Description | Count |
|----------|-------------|-------|
| Security & Protection | `s¹lm` (security), `ḥmyt` (protection), `flṭ` (deliverance) | ~900 |
| Vengeance & Cursing | `nqm` / `ṯʾr` (vengeance), `ʿwr` (blindness on enemy) | ~500 |
| Prosperity & Gain | `ġnmt` (plunder), `s¹ʿd` (fortune), `rwḥ` (relief) | ~200 |
| Relief & Wellbeing | `rwḥ` (ease), `mḥlt` (respite) | ~100 |
| Mixed | Multiple request types in one inscription | ~50 |
| Other | Damaged, ambiguous, or unclassified | ~283 |

## Project structure

```
safaitic-research/
├── parse_safaitic.py           Main pipeline script
├── README.md                   This file
├── WALKTHROUGH.md              Step-by-step data pipeline explanation
├── CORPUS_NOTES.md             Notes on the OCIANA XML format and quirks
├── sample_data/                20 EpiDoc TEI XML test files
│   ├── KRS0001.xml … KRS0004.xml
│   ├── WH0001.xml  … WH0004.xml
│   └── … (16 more)
├── safaitic_invocations.xlsx   (generated)
├── safaitic_narrative.xlsx     (generated)
├── safaitic_top100_interesting.txt
└── safaitic_top50_stories.txt
```
