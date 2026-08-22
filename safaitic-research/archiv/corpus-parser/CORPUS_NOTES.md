# OCIANA Corpus Notes

Practical notes on the corpus format, quirks, and decisions made during
development. Useful context for anyone working with this data.

---

## Corpus overview

- **Full name**: Oxford Corpus of the Inscriptions of Ancient North Arabia
- **Source**: University of Oxford, Khalili Research Centre
- **URL**: http://krc.orient.ox.ac.uk/ociana/
- **Bulk XML**: Available via the GitHub Release `v01-data` in this repository
- **Size**: 43 MB uncompressed, ~37,955 inscriptions

---

## XML format — NOT EpiDoc TEI

The OCIANA bulk XML is a **flat proprietary format**, not EpiDoc TEI. Each
inscription is a flat `<inscription>` element with typed child elements:

```xml
<inscription>
  <siglum>C 97, 96</siglum>
  <script>Safaitic</script>
  <transliteration>l ʿbd bn ...</transliteration>
  <translation>By ʿBd son of ...</translation>
  <site>Ḥarrat al-Ḥamad</site>
  <country>Saudi Arabia</country>
  <url>http://krc.orient.ox.ac.uk/ociana/corpus/pages/OCIANA_0001234.html</url>
  ...
</inscription>
```

The `sample_data/` folder contains 20 EpiDoc TEI files (different format, used
only for initial development and `--sample` mode).

---

## Vocative particle — critical distinction

**In the OCIANA corpus**, the divine vocative is `h` as a **standalone word**:

```
h lt        = "O Allāt"       ← correct form in this corpus
h rḍw       = "O Rudā"
h bʿls¹mn  = "O Baʿalshameen"
```

**Not** the EpiDoc form `w-h-Allāt` (hyphenated prefix). Using the wrong pattern
would find zero results.

---

## Script varieties in the corpus

| Script | Count (approx.) |
|--------|-----------------|
| Safaitic | 31,768 |
| Hismaic | ~3,500 |
| Nabataean | ~1,500 |
| Other / unidentified | ~1,200 |

Only `script = "Safaitic"` is processed.

---

## Corpus ordering

Inscriptions are **not** ordered geographically or chronologically. They follow
the academic publication history of the sub-corpora. The siglum prefix identifies
the sub-corpus:

| Prefix | Sub-corpus / Site area |
|--------|------------------------|
| `C` | Corpus (Winnett & Reed, main collection) |
| `KRS` | Khirbet al-Samrā |
| `LP` | Lava plain (Ḥarrat al-Rajil) |
| `ASWS` | Ahl al-Shaʿb watering site |
| `Is.H` / `Is.M` / `Is.Mu` | Isutu (various sites) |
| `SG` | Sakākā area |
| `ZeWA` | Zeʾlūl / Wadi Araba |
| `AWS` | Azraq watering site |
| `HCH` | Ḥarrat al-Shamah |
| `HaNSB` | Ḥarrat al-Nawāsif |
| `RWQ` | Rawwāfa |
| `NBR` | Nabataean region |
| `MA` | Mādabā area |

---

## Known data issues

### Damaged / bracket notation
Many transliterations contain editorial markup:
- `{...}` = uncertain reading
- `[...]` = lacuna (missing text)
- `(...)` = editorial addition
- `----` = illegible passage

Request-word extraction handles these by stripping such characters before lookup.

### Duplicate inscriptions
Some inscriptions appear twice with slightly different sigla (copies made by
different expeditions). Deduplicated in the curated `.txt` exports by matching
the first 120 characters of the stripped narrative.

### "Other" category (~283 entries)
Inscriptions that fall through all category patterns. Causes:
- Heavily damaged request word
- Unusual or hapax vocabulary
- Request word that is itself a deity name (paired invocations where the
  second deity name looks like a request)

### Shams (sun goddess)
The Shams deity appears frequently in EpiDoc sample data and scholarly literature
but has **zero occurrences** as a vocative in the OCIANA bulk corpus. The
detection pattern was removed after confirming this.

---

## Transliteration conventions

OCIANA uses a specific transliteration system for Safaitic:
- `s¹` / `s²` = two different sibilant phonemes (sin₁ / sin₂)
- `ḥ` `ṭ` `ẓ` `ḏ` `ġ` = emphatic/pharyngeal consonants
- `ʾ` = aleph (glottal stop)
- `ʿ` = ayin (pharyngeal fricative)
- `š` = shin

These characters are preserved exactly as-is throughout the pipeline.
