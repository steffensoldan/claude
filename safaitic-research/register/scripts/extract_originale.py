#!/usr/bin/env python3
"""
Zieht fuer die 138 Stuecke des Bandes die safaitischen Originale aus dem
OCIANA-Vollkorpus und schreibt sie neben die deutsche Fassung.

Quelle: ociana_corpus.xml (37.871 Inschriften) aus dem GitHub-Release
`v01-data` dieses Repositoriums.
  https://github.com/steffensoldan/claude/releases/download/v01-data/ociana_corpus.xml
  sha256 5a90c113356fac5943f34036464680f4a8651a69cb34102fed6bc54af0a3077c
Die Datei ist mit 45 MB zu gross fuer das Repository und wird nicht mit-
committet; dieses Skript laedt sie bei Bedarf und prueft die Pruefsumme.

Aufruf (aus safaitic-research/):
  python3 register/scripts/extract_originale.py
Ausgabe:
  register/originale_138.tsv   (Register, Sigle, Fundort, Transliteration,
                                OCIANA-Uebersetzung, deutsche Fassung)
"""

import csv, hashlib, html, importlib.util, os, re, urllib.request

URL = ("https://github.com/steffensoldan/claude/releases/download/"
       "v01-data/ociana_corpus.xml")
SHA = "5a90c113356fac5943f34036464680f4a8651a69cb34102fed6bc54af0a3077c"
CACHE = os.environ.get("OCIANA_XML", "/tmp/ociana_corpus.xml")
BUILD = "register/scripts/build_register.py"
OUT = "register/originale_138.tsv"
ORDER = ["stehen", "ritzen", "harren", "fehlen",
         "bitten", "klagen", "fluchen", "bezeugen"]


def korpus_holen():
    if os.path.exists(CACHE):
        got = hashlib.sha256(open(CACHE, "rb").read()).hexdigest()
        if got == SHA:
            return CACHE
        print(f"Cache hat falsche Pruefsumme ({got[:12]}…), lade neu.")
    print(f"lade {URL} …")
    urllib.request.urlretrieve(URL, CACHE)
    got = hashlib.sha256(open(CACHE, "rb").read()).hexdigest()
    if got != SHA:
        raise SystemExit(f"Pruefsumme weicht ab: {got}")
    return CACHE


def korpus_lesen(pfad):
    raw = open(pfad, encoding="utf-8").read()
    def feld(rec, tag):
        m = re.search(rf"<{tag}>(.*?)</{tag}>", rec, re.S)
        return html.unescape(m.group(1)).strip() if m else ""
    out = {}
    for rec in re.findall(r"<inscription>(.*?)</inscription>", raw, re.S):
        sg = feld(rec, "siglum")
        if sg:
            out[sg] = (feld(rec, "transliteration"), feld(rec, "translation"))
    return out


def band_lesen():
    spec = importlib.util.spec_from_file_location("b", BUILD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    band = {}
    for _rom, name, entries in mod.REGISTERS:
        for hdr, lines in entries:
            ort, sig = hdr.split(" · ")
            band[sig] = (name, ort, list(lines))
    return band


def main():
    korpus = korpus_lesen(korpus_holen())
    band = band_lesen()
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    nk = {}
    for k, v in korpus.items():
        nk.setdefault(norm(k), v)

    zeilen, fehlt = [], []
    for sig, (reg, ort, de) in band.items():
        hit = nk.get(norm(sig))
        if hit:
            zeilen.append([reg, sig, ort, hit[0], hit[1].replace("\n", " "), " / ".join(de)])
        else:
            fehlt.append(sig)
    zeilen.sort(key=lambda r: (ORDER.index(r[0]), r[1]))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["Register", "Sigle", "Fundort", "Transliteration",
                    "OCIANA-Uebersetzung", "Deutsche Fassung"])
        w.writerows(zeilen)
    print(f"geschrieben: {OUT}  ({len(zeilen)}/{len(band)} Stuecke)")
    if fehlt:
        print("ohne Original:", ", ".join(fehlt))


if __name__ == "__main__":
    main()
