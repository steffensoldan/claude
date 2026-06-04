#!/usr/bin/env python3
"""
OCIANA Safaitic Invocation Extractor
=====================================
Downloads (or uses local) the OCIANA bulk EpiDoc TEI XML corpus, extracts all
inscriptions containing invocations via the vocative particle 'h-' and known
deities (Allāt, Rudā, Shams), clusters results into four categories, and
exports a styled .xlsx file.

Usage:
    # Use bundled sample data (no download needed):
    python3 parse_safaitic.py --sample

    # Use a local directory of EpiDoc XML files:
    python3 parse_safaitic.py --xml-dir /path/to/xml/files

    # Use a local ZIP archive (as downloaded from ORA):
    python3 parse_safaitic.py --zip /path/to/OCIANA_bulk.zip

    # Attempt download from ORA (works on an unrestricted network):
    python3 parse_safaitic.py --download
"""

import os
import io
import re
import sys
import time
import zipfile
import argparse
import requests
from pathlib import Path
from lxml import etree
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.views import SheetView

# ── EpiDoc TEI namespace ────────────────────────────────────────────────────
TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NS}

# ── ORA download URL ────────────────────────────────────────────────────────
ORA_URL = (
    "https://ora.ox.ac.uk/objects/uuid:08a60ae8-e61d-486e-9ef1-836ca71d904c"
    "/download_file?safe_filename=OCIANA_bulk.zip&type_of_work=Dataset"
)

# ── Deity detection patterns ────────────────────────────────────────────────
# Matches the vocative h- prefix directly attached to deity names in the
# Safaitic transliteration used by OCIANA.
DEITY_PATTERNS = {
    "Allāt": re.compile(
        r"\bh-All[aā]t\b|\bh-ʾlt\b|\bh-ʾllt\b|\bh-ʾlāt\b",
        re.IGNORECASE | re.UNICODE,
    ),
    "Rudā": re.compile(
        r"\bh-Rud[aā]\b|\bh-rḍw\b|\bh-rdw\b",
        re.IGNORECASE | re.UNICODE,
    ),
    "Shams": re.compile(
        r"\bh-Š[mn]s\b|\bh-S¹ms\b|\bh-Šms\b|\bh-šms\b",
        re.IGNORECASE | re.UNICODE,
    ),
}

# Also catch any h- invocation not tied to a known deity (generic detection)
GENERIC_H_INVOC = re.compile(r"\bh-[A-ZÀ-öø-ÿʾʿḥṣṭẓḍḏṯṣḳġšṯ]", re.UNICODE)

# ── Category classification keywords ───────────────────────────────────────
# Keys are checked against both the Safaitic transliteration AND the English
# translation text.

CATEGORY_RULES = {
    "Protection & Security": {
        # `slm` omitted from transliteration: it doubles as a very common personal
        # name (l-Slm bn …) and the translation pattern reliably catches "peace".
        # `w-slm` (with conjunction) is safe and included.
        "transliteration": re.compile(
            r"\bḥm[yt][-h]?\b|\bḥmyt\b|\bw-slm\b|\bʿwn[-h]?\b|\bns²r[-h]?\b"
            r"|\bns¹r[-h]?\b|\bḥfẓ\b|\bḥfẓ-h\b",
            re.IGNORECASE | re.UNICODE,
        ),
        "translation": re.compile(
            r"\b(protect|protection|guard|safety|safe|peace|help|shelter|"
            r"defend|defense|salvation|save)\b",
            re.IGNORECASE,
        ),
    },
    "Vengeance & Curse": {
        "transliteration": re.compile(
            r"\bnqm[-h]?\b|\blʿn\b|\bṯʾr[-h]?\b|\bṯʾr\b",
            re.IGNORECASE | re.UNICODE,
        ),
        "translation": re.compile(
            r"\b(vengeance|avenge|curse|retribution|punish|enemy|enemies|"
            r"wrath|erase|obliterate|harm|evil)\b",
            re.IGNORECASE,
        ),
    },
    "Pastoral & Logistic Success": {
        # `ġnm` without the definite article `h-` is also a common personal name
        # (bn ġnm = "son of Ġnm"), so require `h-ġnm` for the flock/sheep sense.
        "transliteration": re.compile(
            r"\bmrʿ\b|\bgyt\b|\bks²b\b|\bwbl\b|\brʿy\b|\bibl\b|\bh-ġnm\b"
            r"|\btns¹ʿd\b|\btns²ʿd\b",
            re.IGNORECASE | re.UNICODE,
        ),
        "translation": re.compile(
            r"\b(pasture|grazing|rain|camel|camels|flock|flocks|sheep|cattle|"
            r"herd|herded|pastured|good fortune|gain|success|harvest)\b",
            re.IGNORECASE,
        ),
    },
}


# ── XML helpers ─────────────────────────────────────────────────────────────

def _text_of(element) -> str:
    """Recursively join all text content of an XML element."""
    return " ".join(t.strip() for t in element.itertext() if t.strip())


def parse_inscription(xml_path: str | Path) -> dict | None:
    """Parse one EpiDoc TEI file; return a record dict or None if no invocation."""
    try:
        tree = etree.parse(str(xml_path))
    except etree.XMLSyntaxError:
        return None

    root = tree.getroot()

    # ── inscription ID ──────────────────────────────────────────────────────
    idno = root.find(".//tei:idno[@type='filename']", NS)
    insc_id = idno.text.strip() if idno is not None and idno.text else Path(xml_path).stem

    # ── location ────────────────────────────────────────────────────────────
    settlement = root.find(".//tei:settlement", NS)
    location = (settlement.text or "").strip() if settlement is not None else ""

    # ── edition text ────────────────────────────────────────────────────────
    edition_div = root.find(
        ".//tei:div[@type='edition']", NS
    )
    edition_text = _text_of(edition_div) if edition_div is not None else ""

    # ── translation text ────────────────────────────────────────────────────
    transl_div = root.find(".//tei:div[@type='translation']", NS)
    translation = _text_of(transl_div) if transl_div is not None else ""

    # ── detect invocation ───────────────────────────────────────────────────
    deities_found = [
        name
        for name, pat in DEITY_PATTERNS.items()
        if pat.search(edition_text)
    ]

    # Fallback: generic h- invocation (h- followed by uppercase/special char)
    has_generic = bool(GENERIC_H_INVOC.search(edition_text))

    if not deities_found and not has_generic:
        return None  # not an invocation inscription

    # ── classify ────────────────────────────────────────────────────────────
    matched_categories = []
    for cat, rules in CATEGORY_RULES.items():
        if rules["transliteration"].search(edition_text) or \
           rules["translation"].search(translation):
            matched_categories.append(cat)

    if len(matched_categories) == 0:
        category = "Uncategorised Invocation"
    elif len(matched_categories) == 1:
        category = matched_categories[0]
    else:
        category = "Mixed Formulas"

    return {
        "Inscription ID": insc_id,
        "Location": location,
        "Deities Invoked": ", ".join(deities_found) if deities_found else "Unknown",
        "Category": category,
        "Safaitic Text (Transliteration)": edition_text,
        "English Translation": translation,
        "Source File": Path(xml_path).name,
    }


# ── Corpus loading ───────────────────────────────────────────────────────────

def load_from_directory(xml_dir: Path) -> list[dict]:
    files = list(xml_dir.glob("**/*.xml"))
    print(f"  Found {len(files)} XML files in {xml_dir}")
    records = []
    for f in files:
        rec = parse_inscription(f)
        if rec:
            records.append(rec)
    return records


def load_from_zip(zip_path: Path) -> list[dict]:
    records = []
    with zipfile.ZipFile(zip_path) as zf:
        xml_members = [m for m in zf.namelist() if m.endswith(".xml")]
        print(f"  Found {len(xml_members)} XML files in ZIP")
        for member in xml_members:
            data = zf.read(member)
            try:
                tree = etree.parse(io.BytesIO(data))
            except etree.XMLSyntaxError:
                continue
            # write to temp and reuse parse_inscription logic inline
            root = tree.getroot()
            tmp_path = Path("/tmp/_ociana_tmp.xml")
            tmp_path.write_bytes(data)
            rec = parse_inscription(tmp_path)
            if rec:
                rec["Source File"] = member
                records.append(rec)
    return records


def download_ora(url: str, out_path: Path) -> Path | None:
    """Attempt to download the ORA ZIP. Returns local path on success."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; academic-research-script/1.0; "
            "safaitic-corpus-extractor)"
        )
    }
    print(f"  Attempting download from ORA …")
    for attempt in range(1, 5):
        try:
            r = requests.get(url, headers=headers, timeout=120, stream=True)
            if r.status_code == 200:
                out_path.write_bytes(r.content)
                print(f"  Downloaded {len(r.content):,} bytes → {out_path}")
                return out_path
            else:
                print(f"  HTTP {r.status_code} on attempt {attempt}")
        except requests.RequestException as exc:
            print(f"  Network error on attempt {attempt}: {exc}")
        if attempt < 4:
            wait = 2 ** attempt
            print(f"  Retrying in {wait}s …")
            time.sleep(wait)
    return None


# ── Excel export ─────────────────────────────────────────────────────────────

_CAT_COLOURS = {
    "Protection & Security":         "1F497D",  # dark blue
    "Vengeance & Curse":             "C0392B",  # deep red
    "Pastoral & Logistic Success":   "27AE60",  # green
    "Mixed Formulas":                "8E44AD",  # purple
    "Uncategorised Invocation":      "7F8C8D",  # grey
}

_CAT_FILL = {k: PatternFill("solid", fgColor=v) for k, v in _CAT_COLOURS.items()}

_HEADER_FONT   = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
_BODY_FONT     = Font(name="Calibri", size=10)
_WRAP_ALIGN    = Alignment(wrap_text=True, vertical="top")
_CENTER_ALIGN  = Alignment(horizontal="center", vertical="center")
_THIN_BORDER   = Border(
    left=Side(style="thin"),  right=Side(style="thin"),
    top=Side(style="thin"),   bottom=Side(style="thin"),
)

_COLUMNS = [
    "Inscription ID",
    "Location",
    "Deities Invoked",
    "Category",
    "Safaitic Text (Transliteration)",
    "English Translation",
    "Source File",
]

_COL_WIDTHS = {
    "Inscription ID":                  18,
    "Location":                        28,
    "Deities Invoked":                 22,
    "Category":                        30,
    "Safaitic Text (Transliteration)": 55,
    "English Translation":             55,
    "Source File":                     22,
}


def _apply_header_row(ws, fill_colour: str):
    hdr_fill = PatternFill("solid", fgColor=fill_colour)
    for col_idx, col_name in enumerate(_COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.font      = _HEADER_FONT
        cell.fill      = hdr_fill
        cell.alignment = _CENTER_ALIGN
        cell.border    = _THIN_BORDER


def _write_data_rows(ws, rows: list[dict], alt_fill: str):
    alt = PatternFill("solid", fgColor=alt_fill)
    plain = PatternFill("solid", fgColor="FFFFFF")
    for r_idx, rec in enumerate(rows, start=2):
        row_fill = alt if r_idx % 2 == 0 else plain
        for c_idx, col_name in enumerate(_COLUMNS, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=rec.get(col_name, ""))
            cell.font      = _BODY_FONT
            cell.alignment = _WRAP_ALIGN
            cell.border    = _THIN_BORDER
            cell.fill      = row_fill


def _freeze_and_size(ws):
    ws.freeze_panes = "A2"
    for col_idx, col_name in enumerate(_COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = _COL_WIDTHS[col_name]
    # row heights: header taller, data rows auto
    ws.row_dimensions[1].height = 22
    for r in range(2, ws.max_row + 1):
        ws.row_dimensions[r].height = 60


def export_excel(records: list[dict], output_path: Path):
    if not records:
        print("  No matching inscriptions found — nothing to export.")
        return

    df = pd.DataFrame(records, columns=_COLUMNS)

    categories = [
        "Protection & Security",
        "Vengeance & Curse",
        "Pastoral & Logistic Success",
        "Mixed Formulas",
        "Uncategorised Invocation",
    ]

    # Write via pandas first (creates the file), then re-open with openpyxl
    with pd.ExcelWriter(str(output_path), engine="openpyxl") as writer:
        # ── Summary sheet ────────────────────────────────────────────────────
        summary_rows = []
        for cat in categories:
            subset = df[df["Category"] == cat]
            if not subset.empty:
                top_deities = (
                    subset["Deities Invoked"]
                    .str.split(", ")
                    .explode()
                    .value_counts()
                    .head(3)
                    .index.tolist()
                )
                summary_rows.append({
                    "Category":            cat,
                    "Count":               len(subset),
                    "% of Total":          f"{100 * len(subset) / len(df):.1f}%",
                    "Top Deities":         ", ".join(top_deities),
                })
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        # ── All Invocations sheet ────────────────────────────────────────────
        df.to_excel(writer, sheet_name="All Invocations", index=False)

        # ── Per-category sheets ──────────────────────────────────────────────
        for cat in categories:
            subset = df[df["Category"] == cat]
            if not subset.empty:
                safe_name = cat[:31]  # Excel sheet name limit
                subset.to_excel(writer, sheet_name=safe_name, index=False)

    # ── Re-open to apply formatting ─────────────────────────────────────────
    wb = load_workbook(str(output_path))

    # Format Summary sheet
    ws_summary = wb["Summary"]
    sum_fill  = PatternFill("solid", fgColor="2C3E50")
    sum_alt   = PatternFill("solid", fgColor="ECF0F1")
    sum_plain = PatternFill("solid", fgColor="FFFFFF")
    for cell in ws_summary[1]:
        cell.font      = _HEADER_FONT
        cell.fill      = sum_fill
        cell.alignment = _CENTER_ALIGN
        cell.border    = _THIN_BORDER
    ws_summary.freeze_panes = "A2"
    for r_idx in range(2, ws_summary.max_row + 1):
        cat_val = ws_summary.cell(row=r_idx, column=1).value
        cat_colour = _CAT_COLOURS.get(cat_val, "FFFFFF")
        cat_chip   = PatternFill("solid", fgColor=cat_colour)
        row_fill   = sum_alt if r_idx % 2 == 0 else sum_plain
        for c_idx in range(1, ws_summary.max_column + 1):
            cell = ws_summary.cell(row=r_idx, column=c_idx)
            cell.font      = Font(
                name="Calibri", size=11,
                bold=(c_idx == 1),
                color="FFFFFF" if c_idx == 1 else "2C3E50",
            )
            cell.fill      = cat_chip if c_idx == 1 else row_fill
            cell.alignment = _CENTER_ALIGN
            cell.border    = _THIN_BORDER
    for col in ws_summary.columns:
        ws_summary.column_dimensions[col[0].column_letter].width = 32

    # Format All Invocations sheet
    ws_all = wb["All Invocations"]
    _apply_header_row(ws_all, "2C3E50")
    _write_data_rows(ws_all, records, "EBF5FB")
    _freeze_and_size(ws_all)

    # Format per-category sheets
    for cat in categories:
        safe_name = cat[:31]
        if safe_name not in wb.sheetnames:
            continue
        ws = wb[safe_name]
        colour = _CAT_COLOURS.get(cat, "2C3E50")
        alt_colour = _lighten_hex(colour)
        subset_records = [r for r in records if r["Category"] == cat]
        _apply_header_row(ws, colour)
        _write_data_rows(ws, subset_records, alt_colour)
        _freeze_and_size(ws)

    # Move Summary to first position
    wb.move_sheet("Summary", offset=-len(wb.sheetnames) + 1)

    wb.save(str(output_path))
    print(f"\n  Exported {len(records)} inscriptions → {output_path}")


def _lighten_hex(hex_colour: str, factor: float = 0.85) -> str:
    """Return a lightened version of a hex RGB colour for alternating rows."""
    r = int(hex_colour[0:2], 16)
    g = int(hex_colour[2:4], 16)
    b = int(hex_colour[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"{r:02X}{g:02X}{b:02X}"


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract Safaitic invocation inscriptions from OCIANA EpiDoc XML"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--sample", action="store_true",
        help="Use the bundled sample EpiDoc XML files (no download needed)"
    )
    source.add_argument(
        "--xml-dir", metavar="DIR",
        help="Directory containing EpiDoc XML files"
    )
    source.add_argument(
        "--zip", metavar="FILE",
        help="Local ZIP archive of OCIANA bulk XML (as downloaded from ORA)"
    )
    source.add_argument(
        "--download", action="store_true",
        help="Attempt to download the bulk corpus from Oxford ORA (requires network access)"
    )
    parser.add_argument(
        "--output", metavar="FILE", default="safaitic_invocations.xlsx",
        help="Output .xlsx filename (default: safaitic_invocations.xlsx)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  OCIANA Safaitic Invocation Extractor")
    print("=" * 60)

    records: list[dict] = []

    if args.sample:
        sample_dir = Path(__file__).parent / "sample_data"
        if not sample_dir.exists():
            print(f"  ERROR: sample_data/ not found at {sample_dir}")
            sys.exit(1)
        print(f"\n[1/3] Loading sample data from {sample_dir}")
        records = load_from_directory(sample_dir)

    elif args.xml_dir:
        xml_dir = Path(args.xml_dir)
        if not xml_dir.exists():
            print(f"  ERROR: Directory not found: {xml_dir}")
            sys.exit(1)
        print(f"\n[1/3] Loading XML files from {xml_dir}")
        records = load_from_directory(xml_dir)

    elif args.zip:
        zip_path = Path(args.zip)
        if not zip_path.exists():
            print(f"  ERROR: ZIP file not found: {zip_path}")
            sys.exit(1)
        print(f"\n[1/3] Loading from ZIP: {zip_path}")
        records = load_from_zip(zip_path)

    elif args.download:
        print(f"\n[1/3] Downloading corpus from ORA …")
        zip_out = Path("OCIANA_bulk.zip")
        result = download_ora(ORA_URL, zip_out)
        if result is None:
            print(
                "\n  Download failed. The ORA host may block automated requests\n"
                "  or require authentication in your network environment.\n"
                "\n  Manual download steps:\n"
                "    1. Open in a browser:\n"
                "       https://ora.ox.ac.uk/objects/uuid:08a60ae8-e61d-486e-9ef1-836ca71d904c\n"
                "    2. Click the 'Download' or 'Get the data' link to save the ZIP.\n"
                "    3. Re-run: python3 parse_safaitic.py --zip OCIANA_bulk.zip\n"
            )
            sys.exit(1)
        print(f"\n[1/3] Loading from downloaded ZIP: {zip_out}")
        records = load_from_zip(zip_out)

    print(f"\n[2/3] Parsing complete.")
    print(f"       Total inscriptions scanned: see file count above")
    print(f"       Invocation inscriptions found: {len(records)}")

    if records:
        cat_counts = {}
        for r in records:
            cat_counts[r["Category"]] = cat_counts.get(r["Category"], 0) + 1
        print("\n  Category breakdown:")
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
            print(f"    {cat:<38} {count:>4}")

    print(f"\n[3/3] Exporting to {args.output} …")
    output_path = Path(args.output)
    export_excel(records, output_path)

    print("\nDone.")


if __name__ == "__main__":
    main()
