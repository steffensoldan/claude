#!/usr/bin/env python3
"""
Lädt die OCIANA-Bilddateien (Fotos/Zeichnungen) der 7 Steine mit grafischem
Element herunter — Grundlage, um sie in den Band einzubetten.

WICHTIG: Braucht Netzzugang (Claude Cowork o. ä.); die reguläre Agent-Session
blockiert krc.orient.ox.ac.uk (403).

Eingabe : register/rockart_images_manifest.csv  (Sigle, Motiv, Bild-Nr, Datei, URL)
Ausgabe : register/rockart_images/<Sigle>__<imid>.jpg   (mehrere je Stein)

Danach:  Ordner register/rockart_images/ zippen und hochladen. Der Band-Build
(build_register.py) bettet je Stein automatisch das erste dort gefundene Bild
neben die Inschrift ein (v4). Zum gezielten Auswählen kann man das gewünschte
Bild zusätzlich als <Sigle>.jpg ablegen (hat Vorrang).

Nur Standardbibliothek. Aufruf (aus safaitic-research/):
  python3 register/scripts/download_rockart_images.py
"""

import csv
import os
import time
import urllib.request
import urllib.error

CSV_IN = "register/rockart_images_manifest.csv"
OUT_DIR = "register/rockart_images"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
DELAY = 1.0


def safe(name):
    return name.replace(" ", "_").replace("/", "-").replace(".", "_")


def main():
    if not os.path.exists(CSV_IN):
        raise SystemExit(f"Manifest fehlt: {CSV_IN} (aus safaitic-research/ starten).")
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8")))
    ok = 0
    for i, r in enumerate(rows, 1):
        sg, url = r["Sigle"], r["URL"]
        imid = r["Dateiname"].replace(".jpg", "")
        dest = os.path.join(OUT_DIR, f"{safe(sg)}__{imid}.jpg")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(dest, "wb") as f:
                f.write(data)
            ok += 1
            print(f"[{i}/{len(rows)}] {sg} {imid}: {len(data)} B")
        except Exception as e:
            print(f"[{i}/{len(rows)}] {sg} {imid}: FEHLER {e}")
        time.sleep(DELAY)
    print(f"\nFertig: {ok}/{len(rows)} Bilder in '{OUT_DIR}'.")
    print("Ordner zippen und hochladen; dann baue ich den Band mit Abbildungen (v4).")


if __name__ == "__main__":
    main()
