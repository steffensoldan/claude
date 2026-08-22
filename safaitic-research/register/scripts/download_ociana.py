#!/usr/bin/env python3
"""
Lädt für die 134 Inschriften des Register-Bands die OCIANA-Seiten herunter,
damit die assoziierten Felszeichnungen (Kamel, Pferd, Löwe …) ausgewertet
werden können.

WICHTIG: Muss in einer Umgebung MIT Netzzugang laufen — z. B. Claude Cowork auf
dem Desktop oder eine Claude-Code-Web-Session mit offener Netzwerk-Policy. Die
aktuelle Agent-Session blockiert ociana.osu.edu / krc.orient.ox.ac.uk auf
Proxy-Ebene (403), darum die Auslagerung.

Zwei Stufen (damit die Auswertungs-Intelligenz bei Claude bleibt):
  1) Dieses Skript lädt NUR die HTML-Seiten herunter (Netz nötig).
  2) Den Ordner `register/ociana_pages/` zippen und wieder hochladen; Claude
     parst ihn lokal und baut die Tabelle „Inschriften mit grafischem Element“.

Nur Python-Standardbibliothek — keine Installation nötig.

Aufruf (aus safaitic-research/):
  python3 register/scripts/download_ociana.py
Ergebnis:
  register/ociana_pages/<Sigle>.html   (je Inschrift eine Seite)
  register/ociana_pages/_status.csv    (Sigle, HTTP-Status, Bytes, URL)
"""

import csv
import os
import time
import urllib.request
import urllib.error

CSV_IN = "register/ociana_rockart_check.csv"   # Siglen + OCIANA-Direktlinks
OUT_DIR = "register/ociana_pages"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120 Safari/537.36")
DELAY = 1.0          # höfliche Pause zwischen Abrufen (Sekunden)
RETRIES = 3


def safe(name):
    return name.replace(" ", "_").replace("/", "-").replace(".", "_")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()


def main():
    if not os.path.exists(CSV_IN):
        raise SystemExit(f"Eingabeliste fehlt: {CSV_IN} (aus safaitic-research/ starten).")
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = list(csv.DictReader(open(CSV_IN, encoding="utf-8")))
    status = []
    for i, row in enumerate(rows, 1):
        sg = row["Sigle"].strip()
        url = row["OCIANA-URL"].strip()
        if not url:
            status.append((sg, "no-url", 0, ""))
            print(f"[{i}/{len(rows)}] {sg}: keine URL")
            continue
        last = None
        for attempt in range(1, RETRIES + 1):
            try:
                code, data = fetch(url)
                with open(os.path.join(OUT_DIR, safe(sg) + ".html"), "wb") as f:
                    f.write(data)
                status.append((sg, code, len(data), url))
                print(f"[{i}/{len(rows)}] {sg}: {code} ({len(data)} B)")
                last = None
                break
            except urllib.error.HTTPError as e:
                last = e.code
                if e.code in (403, 404, 410):     # nicht wiederholen
                    break
                time.sleep(2 * attempt)
            except Exception as e:                 # Timeout/DNS/… → Retry
                last = f"ERR {type(e).__name__}"
                time.sleep(2 * attempt)
        if last is not None:
            status.append((sg, last, 0, url))
            print(f"[{i}/{len(rows)}] {sg}: {last}")
        time.sleep(DELAY)

    with open(os.path.join(OUT_DIR, "_status.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Sigle", "Status", "Bytes", "URL"])
        w.writerows(status)

    ok = sum(1 for s in status if str(s[1]) == "200")
    print(f"\nFertig: {ok}/{len(rows)} Seiten geladen.")
    if ok == 0:
        print("Keine Seite geladen — vermutlich immer noch ohne Netzzugang, "
              "oder die alten Oxford-Links sind tot. Dann bitte die Siglen im "
              "OSU-Portal (ociana.osu.edu) suchen und dessen URLs in die CSV-"
              "Spalte 'OCIANA-URL' eintragen, dann erneut starten.")
    else:
        print(f"Ordner '{OUT_DIR}' zippen und hochladen — Claude wertet ihn aus.")


if __name__ == "__main__":
    main()
