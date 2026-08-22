#!/usr/bin/env python3
"""
Baut Version 5 aus Version 4: vereinheitlicht das Stimm-Register auf die
dritte Person (Er-Form), wie die safaitischen Originale (l-Fulān + 3. Person).

Bis v4 standen die verknappten Gedichte im Ich (Aneignung), nur die langen
Steine im Er. v5 hebt diese Sonderbehandlung auf: Alle Stücke sprechen in der
dritten Person. Die Steine waren schon Er und bleiben unberührt.

Umstellung Ich -> Er (nur im Gedicht-Bereich, also zwischen der Kapitel-I-
Überschrift und der „Editorischen Notiz“; Front-/Backmatter-Prosa bleibt):

  - deutsches Präteritum ist in 1./3. Person identisch (ich blieb / er blieb),
    Verbformen ändern sich also kaum;
  - Subjekt:        Ich/ich -> Er/er
  - Präsens 1. Sg.: „Ich bin“ -> „Er ist“
  - Possessiv:      mein… -> sein…
  - reflexiv:       mich -> sich   (er sehnte sich …)
  - Objekt/Dativ:   machte/zerbrach/trieb/über mich -> … ihn;
                    gib/fehlten/bringt/nahm/nimm mir -> … ihm
  - Plural (JSLih 077, zwei Stifter): Wir -> Sie, uns -> sie

Anrufungen an die Gottheit (Imperativ: „Allat — gib Sicherheit“), Fluch-/
Segensformeln und die Frauenstimme C 5142 („Sie …“) bleiben unangetastet.
Außerdem: editorische Notiz (Zwei-Register-/Aneignungs-Absätze) nachgezogen.

Aufruf (aus erweitert/):
  python3 scripts/build_v5.py \
      wer_dies_liest_lebe_lang_erweitert_v4.docx \
      wer_dies_liest_lebe_lang_erweitert_v5.docx
"""

import sys
import re
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DOC = "word/document.xml"

RULES = [
    (r"\bmachte mich\b", "machte ihn"),
    (r"\bzerbrach mich\b", "zerbrach ihn"),
    (r"\btrieb mich\b", "trieb ihn"),
    (r"\bLass mich\b", "Lass ihn"),
    (r"\büber mich\b", "über ihn"),
    (r"\bgib mir\b", "gib ihm"),
    (r"\bfehlten mir\b", "fehlten ihm"),
    (r"\bbringt mir\b", "bringt ihm"),
    (r"\bnahm mir\b", "nahm ihm"),
    (r"\bnimm mir\b", "nimm ihm"),
    (r"\bWir\b", "Sie"),
    (r"\buns\b", "sie"),
    (r"\bmich\b", "sich"),
    (r"\bmir\b", "ihm"),
    (r"\bMeine\b", "Seine"),
    (r"\bmeines\b", "seines"), (r"\bmeinem\b", "seinem"), (r"\bmeinen\b", "seinen"),
    (r"\bmeiner\b", "seiner"), (r"\bmeine\b", "seine"), (r"\bmein\b", "sein"),
    (r"\bIch bin\b", "Er ist"),
    (r"\bIch\b", "Er"), (r"\bich\b", "er"),
]

PROSE = [
    ("in denen die Inschriften ins Ich übertragen",
     "Dieser Band führt zwei Register, beide in der dritten Person der Originale: "
     "Die safaitische Eingangsformel lautet l-Fulān („Von X“), danach erzählt der "
     "Text über seinen Schreiber weiter — „und er trauerte“. Der Autor dokumentiert "
     "sich selbst, er spricht nicht als er selbst. Das erste Register sind die "
     "Gedichte: stark verknappte Nachdichtungen, Genealogien getilgt, Lücken "
     "geschlossen. Das zweite Register sind die Steine: lange Inschriften, die am "
     "Kopf der Abschnitte und am Schluss des Bandes stehen und in treuer Langzeile "
     "wiedergegeben sind. Was die beiden Register unterscheidet, ist der Grad der "
     "Verknappung, nicht die Stimme."),
    ("Die Gedichte holen diese Stimme ins Ich",
     "Die Aneignung, von der das Vorwort spricht, liegt damit nicht in der Stimme, "
     "sondern in der Auswahl und der Verdichtung: Was uns berührt, ist gewählt und "
     "verknappt — nicht ins Ich umgeschrieben. Die Distanz des Dokuments bleibt "
     "gewahrt."),
]


def text(p):
    return "".join((t.text or "") for r in p.findall(f"{W}r") for t in r.findall(f"{W}t"))


def feats(p):
    f = set()
    for r in p.findall(f"{W}r"):
        rpr = r.find(f"{W}rPr")
        if rpr is None:
            continue
        s = rpr.find(f"{W}sz")
        if s is not None:
            f.add("sz" + s.get(f"{W}val"))
        b = rpr.find(f"{W}b")
        if b is not None:
            f.add("b")
    return f


def set_text(e, newtext):
    runs = e.findall(f"{W}r")
    first = runs[0]
    first.findall(f"{W}t")[0].text = newtext
    for t in first.findall(f"{W}t")[1:]:
        first.remove(t)
    for r in runs[1:]:
        e.remove(r)


def er(t):
    for a, b in RULES:
        t = re.sub(a, b, t)
    return t


def transform(raw):
    ro_start = raw.find("<w:document")
    ro_end = raw.find(">", ro_start)
    orig_root = raw[ro_start:ro_end + 1]
    for pfx, uri in re.findall(r'xmlns:([A-Za-z0-9]+)="([^"]+)"', orig_root):
        ET.register_namespace(pfx, uri)
    root = ET.fromstring(raw)
    body = root.find(f"{W}body")
    els = [e for e in list(body) if e.tag == f"{W}p"]

    # Gedicht-Bereich abgrenzen: Kapitel-I-Überschrift … „Editorische Notiz“
    start = end = None
    for i, e in enumerate(els):
        t = text(e).strip(); f = feats(e)
        if start is None and t == "I" and "b" in f and "sz40" in f:
            start = i
        if t == "Editorische Notiz":
            end = i
    if start is None or end is None:
        raise SystemExit("Gedicht-Bereich nicht gefunden")

    changed = 0
    for e in els[start:end]:
        if "sz22" not in feats(e):
            continue
        old = text(e)
        new = er(old)
        if new != old:
            set_text(e, new); changed += 1
    print(f"  Verszeilen umgestellt: {changed}")

    # editorische Notiz nachziehen
    for needle, newtext in PROSE:
        hit = [e for e in els if needle in text(e)]
        if len(hit) != 1:
            raise SystemExit(f"Notiz {needle!r}: {len(hit)} Treffer")
        set_text(hit[0], newtext)

    out = ET.tostring(root, encoding="unicode")
    s = out.find("<w:document"); en = out.find(">", s)
    out = out[:s] + orig_root + out[en + 1:]
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    with zipfile.ZipFile(src) as zin:
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]
    new_doc = transform(
        next(d for i, d in items if i.filename == DOC).decode("utf-8")
    ).encode("utf-8")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            zout.writestr(info, new_doc if info.filename == DOC else data)
    print(f"geschrieben: {dst}")


if __name__ == "__main__":
    main()
