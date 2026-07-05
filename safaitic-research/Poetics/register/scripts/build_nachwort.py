#!/usr/bin/env python3
"""
Baut nur das Nachwort des Register-Bands als eigenes Word-Dokument
(`register/nachwort.docx`) — zum direkten Bearbeiten. Verwendet die Bausteine
und Texte aus build_register.py wieder (Einleitung + Nachwort-Text, Notiz
„Zu den Kapiteltiteln“, Tabellen Corpus-Siglen und Fundorte).

Aufruf (aus Poetics/):
  python3 register/scripts/build_nachwort.py
"""

import os
import zipfile

ns = {"__name__": "build_register"}          # verhindert main()-Lauf
src = os.path.join(os.path.dirname(__file__), "build_register.py")
exec(open(src, encoding="utf-8").read(), ns)

V5, OUT = ns["V5"], "register/nachwort.docx"
head, body, subhead, table, EMPTY = ns["head"], ns["body"], ns["subhead"], ns["table"], ns["EMPTY"]
VORWORT, NOTE, TITLES, CORPUS, FINDORT = ns["VORWORT"], ns["NOTE"], ns["TITLES"], ns["CORPUS"], ns["FINDORT"]

raw = zipfile.ZipFile(V5).read("word/document.xml").decode("utf-8")
decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
root_open = raw[raw.find("<w:document"):raw.find(">", raw.find("<w:document")) + 1]
sect = raw[raw.find("<w:sectPr"):raw.find("</w:body>")]

xml = [head("Nachwort")] + [body(p) for p in VORWORT] + [body(p) for p in NOTE]
xml += [subhead("Zu den Kapiteltiteln")] + [body(p) for p in TITLES]
xml += [subhead("Die Corpus-Siglen"),
        body("Jede Nachdichtung trägt als Kopfzeile zuerst den Fundort, dann die Corpus-Sigle. "
             "Die Siglen bezeichnen die Sammlung oder Edition, in der die Inschrift zuerst erfasst wurde:"),
        table(CORPUS), EMPTY,
        subhead("Die Fundorte"),
        body("Der Fundort ist normalisiert (spezifischster benannter Ort); zwei Zonen ordnen: "
             "die nordostjordanische Ḥarrah und die südsyrische Ṣafā."),
        table(FINDORT), EMPTY]

doc = decl + root_open + "<w:body>" + "".join(xml) + sect + "</w:body></w:document>"
with zipfile.ZipFile(V5) as zin:
    items = [(i, zin.read(i.filename)) for i in zin.infolist()]
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for info, data in items:
        zout.writestr(info, doc.encode("utf-8") if info.filename == "word/document.xml" else data)
print("geschrieben:", OUT)
