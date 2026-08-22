#!/usr/bin/env python3
"""
Muster: Register III „warte" mit allen drei Formvorschlägen zugleich —
(1) Fließtext (jeder Eintrag ein ununterbrochener Block, keine Verszeilen),
(2) infinite Grundform statt narrativem „Er",
(3) Fundort · Sigle als Titel ÜBER dem Text.
Nur zur Ansicht; greift NICHT in den Hauptband ein.

Aufruf (aus safaitic-research/):
  python3 register/scripts/build_muster.py
"""

import os
import zipfile

ns = {"__name__": "build_register"}
exec(open(os.path.join(os.path.dirname(__file__), "build_register.py"), encoding="utf-8").read(), ns)
V5, FINDSPOT = ns["V5"], ns["FINDSPOT"]
run, para, sp, title, tsub, roman, regname = (ns[k] for k in ["run", "para", "sp", "title", "tsub", "roman", "regname"])
PAGEBREAK = ns["PAGEBREAK"]
OUT = "register/muster_register_iii.docx"

def titel(t):  # Fundort · Sigle, klein/braun, ÜBER dem Text
    return para(run(t, '<w:color w:val="7A5C3E"/><w:sz w:val="16"/><w:szCs w:val="16"/>'),
                f'<w:pPr>{sp(before="260", after="40")}</w:pPr>')
def block(t):  # fortlaufender Textblock (Fließtext), Georgia sz22
    return para(run(t, '<w:sz w:val="22"/><w:szCs w:val="22"/>'), f'<w:pPr>{sp(after="60", line="300")}</w:pPr>')
def note(t):
    return para(run(t, '<w:i/><w:color w:val="666666"/><w:sz w:val="18"/><w:szCs w:val="18"/>'), f'<w:pPr>{sp(after="200")}</w:pPr>')

# Register III „warte" — infinite Fließtext-Fassungen (Reihenfolge: Kopfstücke, dann Korpus)
MUSTER = [
 ("ASWS 73", "Von Rbʾl, Sohn des Ḥnn, Sohn des Ẓ˥n, Sohn des Ḫyḏ, Sohn des ˥ḏr. Ziehen zum Wasser, der Dürre gewärtig — dann wieder im Wassermann, im Widder, in der Waage, in der Waage abermals, zwei Jahre in Folge. Und in dieser Zeit trauern vor Schmerz um einen, den man liebte, und um die Kamele, die man weidete, hinausgezogen aus der inneren Wüste. Im Jahr, als Bnt starb."),
 ("RSIS 110", "An diesem Ort sein. Ausschau halten nach den Brüdern. Sie fehlten."),
 ("Is.Mu 255", "Ausschau halten nach der Geliebten. Jaʾlat — gib Sicherheit."),
 ("SIJ 30", "Warten auf den Schnee über dem Hauran."),
 ("LP 1196", "Von Ms¹wd, Sohn des Whbn, Sohn des Hrṯ, Sohn des Ms¹k, Sohn des Qmr, Sohn des ʿwḏ, Sohn des Whbʾl. Ausschau halten nach dem Reiterzug."),
 ("KRS 3051", "Die junge Kamelstute. Hinausziehen ins weite, offene Land. Verzweifeln auf der Lauer nach der Raubschar."),
 ("CSNS 796", "Warten auf den glückenden Raubzug."),
 ("C 2756", "Trauern um die Männer im Späherposten."),
 ("C 2753", "Um die Männer im Späherposten trauern."),
 ("RSIS 322", "Wache halten, auf der Lauer nach dem Löwen."),
 ("WH 175", "In die innere Wüste ziehen. Ausschau halten."),
 ("AbSWS 15", "Von S¹ʿd, Sohn des Ġyrʾl, Sohn des S¹krn, Sohn des Zkr, Sohn des Ẓnʾl. Ausschau halten."),
 ("KWQ 113", "Mit den Ziegen gehen. Ausschau halten."),
 ("ASWS 183", "Auf der Lauer nach dem Löwen."),
 ("CEDS 226", "Ausschau halten nach den Pferden."),
 ("SIJ 323", "Den Kamelen folgen. Ausschau halten."),
 ("SIJ 14", "Ausschau halten nach dem Löwen."),
 ("GSSH 1", "Auf der Lauer liegen am Späherplatz, nach Feinden mit Kamelen."),
 ("C 2194", "Ausschau halten. Yalt — Beute von den Feinden."),
]

raw = zipfile.ZipFile(V5).read("word/document.xml").decode("utf-8")
decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
root_open = raw[raw.find("<w:document"):raw.find(">", raw.find("<w:document")) + 1]
sect = raw[raw.find("<w:sectPr"):raw.find("</w:body>")]

xml = [title("Muster"),
       tsub("Register III · warte — alle drei Formvorschläge", 22, "7A5C3E"),
       note("Fließtext (ein Block je Eintrag) · infinite Grundform statt „Er“ · Fundort·Sigle als Titel oben. Nur zur Ansicht; der Hauptband bleibt unverändert."),
       PAGEBREAK, roman("III"), regname("warte")]
for sg, text in MUSTER:
    ort = FINDSPOT.get(sg, "Fundort unbekannt")
    xml += [titel(f"{ort} · {sg}"), block(text)]

doc = decl + root_open + "<w:body>" + "".join(xml) + sect + "</w:body></w:document>"
with zipfile.ZipFile(V5) as zin:
    items = [(i, zin.read(i.filename)) for i in zin.infolist()]
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
    for info, data in items:
        zout.writestr(info, doc.encode("utf-8") if info.filename == "word/document.xml" else data)
print("geschrieben:", OUT, f"({len(MUSTER)} Einträge)")
