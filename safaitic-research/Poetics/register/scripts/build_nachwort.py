#!/usr/bin/env python3
"""
Baut nur das Nachwort des Register-Bands als eigenes Word-Dokument
(`register/nachwort.docx`) — zum direkten Bearbeiten. Verwendet die Bausteine
und Texte aus build_register.py wieder (die drei Nachwort-Abschnitte: Das
OCIANA-Korpus, Die editorischen Siglen, Die Fundorte).

Aufruf (aus Poetics/):
  python3 register/scripts/build_nachwort.py
"""

import os
import zipfile

ns = {"__name__": "build_register"}          # verhindert main()-Lauf
src = os.path.join(os.path.dirname(__file__), "build_register.py")
exec(open(src, encoding="utf-8").read(), ns)

V5, OUT = ns["V5"], "register/nachwort.docx"
head, body, subhead, defitem, EMPTY = ns["head"], ns["body"], ns["subhead"], ns["defitem"], ns["EMPTY"]
NW_OCIANA, NW_SIGLEN_INTRO, NW_SIGLEN = ns["NW_OCIANA"], ns["NW_SIGLEN_INTRO"], ns["NW_SIGLEN"]
NW_FUNDORT_INTRO, NW_FUNDORTE = ns["NW_FUNDORT_INTRO"], ns["NW_FUNDORTE"]

raw = zipfile.ZipFile(V5).read("word/document.xml").decode("utf-8")
decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
root_open = raw[raw.find("<w:document"):raw.find(">", raw.find("<w:document")) + 1]
sect = raw[raw.find("<w:sectPr"):raw.find("</w:body>")]

xml = [head("Nachwort"), subhead("Das OCIANA-Korpus")] + [body(p) for p in NW_OCIANA]
xml += [subhead("Die editorischen Siglen (Ergänzung)"), body(NW_SIGLEN_INTRO)]
xml += [defitem(t, d) for t, d in NW_SIGLEN] + [EMPTY]
xml += [subhead("Die Fundorte"), body(NW_FUNDORT_INTRO)]
xml += [defitem(t, d) for t, d in NW_FUNDORTE] + [EMPTY]

doc = decl + root_open + "<w:body>" + "".join(xml) + sect + "</w:body></w:document>"
with zipfile.ZipFile(V5) as zin:
    items = [(i, zin.read(i.filename)) for i in zin.infolist()]
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for info, data in items:
        zout.writestr(info, doc.encode("utf-8") if info.filename == "word/document.xml" else data)
print("geschrieben:", OUT)
