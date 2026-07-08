# Pipeline Walkthrough

This document traces every step from raw XML to final output.

---

## Step 1 — Corpus loading and XML repair

The OCIANA XML file is technically malformed in three ways that must be fixed
before parsing:

```python
# 1. Strip the xs:schema block (uses xs: prefix without a namespace declaration)
content = re.sub(b"<xs:schema>.*?</xs:schema>", b"", content, flags=re.DOTALL)

# 2. Remove control characters (the file contains 0x0B / vertical tab)
content = re.sub(b"[\x00-\x08\x0b\x0c\x0e-\x1f]", b"", content)

# 3. Wrap bare <inscription> elements in a root element
content = b"<corpus>" + content.strip() + b"</corpus>"
```

The file is then parsed with `lxml` in recovery mode:

```python
root = etree.fromstring(content)  # lxml handles remaining quirks
```

---

## Step 2 — Filtering for Safaitic

Each `<inscription>` element has a `<script>` child. Only `"Safaitic"` entries
are processed (31,768 out of 37,955 total). The remaining ~6,000 are Hismaic,
Nabataean, or other scripts.

---

## Step 3 — Detecting divine invocations

In the OCIANA flat XML, the vocative particle is a **standalone word** `h`
immediately followed by a deity name (no hyphen):

```
h lt        → "O Allāt"       ✓
w-h-Allāt   → EpiDoc format   ✗  (not used in this corpus)
```

Detection uses per-deity compiled regexes:

```python
DEITIES = {
    "Allāt":        re.compile(r"\bh\s+(lt|ʾlt|ylt|yʾlt)\b"),
    "Rudā":         re.compile(r"\bh\s+(rḍw|rḍy|rḍ)\b"),
    "Baʿalshameen": re.compile(r"\bh\s+(bʿls¹mn|bʿls¹m)\b"),
    ...
}
```

Only inscriptions matching at least one deity pattern are kept → **2,018 records**.

---

## Step 4 — Extracting the request word

After the deity name, the next semantically meaningful token is the request.
The logic must skip:
- Grammatical particles (`w`, `f`, `l`, `mn`, …)
- Other deity names (for paired invocations like `h lt w ds²r s¹lm`)

```python
_PARTICLES = {"w", "f", "l", "mn", "lt", "rḍw", "ds²r", ...}

def _first_request_word(context):
    for tok in re.split(r"[\s{}\[\]<>.,;]+", context):
        tok = tok.strip(".,;-{}[]()")
        if tok and tok.lower() not in _PARTICLES and len(tok) > 1:
            return tok
    return ""
```

The request word is then looked up in `REQUEST_LABELS` (specific meaning) and
`REQUEST_CATEGORIES` (thematic group).

---

## Step 5 — Extracting the English invocation

From the English translation, the "O Deity…" clause is extracted by splitting on
the first occurrence of `\bO\b`:

```python
_INVOC_SPLIT = re.compile(r"(?:(?:[,.]\s*)?(?:So\s+)?)(\bO\b.+)", re.DOTALL)
```

If no "O" clause is found, the fallback looks for "may …" phrasing.

---

## Step 6 — Excel export

`export_excel()` writes a multi-sheet `.xlsx` using `pandas` + `openpyxl`:

| Sheet | Contents |
|-------|----------|
| Summary | Per-category counts, top deities, top request types |
| All Invocations | All 2,018 rows |
| Security & Protection | Filtered subset |
| Vengeance & Cursing | Filtered subset |
| Prosperity & Gain | Filtered subset |
| Relief & Wellbeing | Filtered subset |
| Mixed | Filtered subset |
| Other | Filtered subset |

Styling: frozen header row, colour-coded headers per category, alternating row
fills, auto column widths, wrapped text.

---

## Step 7 — Curated text exports

Two additional scripts (run inline) produce the curated `.txt` files.

**Top 50 by length** (`safaitic_top50_stories.txt`):
- Strips the genealogical preamble ("By X son of Y son of Z, …") from each
  English translation using a regex
- Sorts by remaining character count
- Top 50 written with siglum, URL, full translation, and stripped narrative

**Top 100 most interesting** (`safaitic_top100_interesting.txt`):
- Same preamble stripping
- Scores each inscription using weighted keyword matching:
  - Historical events (king, Roman, Nabataean, war): +4–6 points each
  - Astronomical dating (Libra, Sagittarius, moon): +4 points
  - Multiple deity invocations: +3 per deity
  - Narrative length: +1 per 20 characters
- Deduplicates near-identical texts
- Top 100 written with siglum, URL, narrative, and English invocation clause

---

## Key numbers

| Metric | Value |
|--------|-------|
| Total inscriptions in corpus | 37,955 |
| Safaitic inscriptions | 31,768 |
| With divine invocations | 2,018 |
| Non-invocation narratives | 2,487 |
| Unique deity forms attested | 8 deities, ~20 spelling variants |
| Shams (sun goddess) | 0 occurrences — not attested in this corpus |
