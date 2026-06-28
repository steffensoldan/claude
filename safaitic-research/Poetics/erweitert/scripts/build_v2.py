#!/usr/bin/env python3
"""
Baut die zweite Fassung des erweiterten Manuskripts aus der ersten.

v2 nimmt den redaktionellen Apparat zurück (siehe UEBERGABE_ERWEITERTE_AUSGABE.md,
Abschnitt 0). Der Inhalt der Nachdichtungen und Steine bleibt unangetastet;
verändert wird nur, was um die Texte herum steht:

  1. Namens-Zwischenüberschriften am Kopf der Steine (fett, sz24) entfernt.
  2. Poetische Kapitel-Untertitel (Farbe 666666) entfernt.
  3. Quellenangabe einheitlich als „Sigle xy“ unter jedem Stück:
     "Quellsigle …" -> "Sigle …"; die "STEIN · …"/"SCHLUSSSTEIN · …"-Kicker
     entfallen, dafür je eine "Sigle …"-Zeile unter den ganzen Steinen.
  4. Echo aufgelöst: an den beiden Echo-Stellen nur noch der ganze Stein,
     die verknappten Fassungen (ASWS 73, C 4803) gestrichen.
  5. Wiederkehrende Schlussformeln (Refrain-Seiten zwischen den Kapiteln)
     entfernt.
  Plus: mitgezogene Prosa-Korrekturen in Vorwort, editorischer Notiz, Glossar.

Arbeitsweise: direktes Transform der document.xml in der docx. Alle nicht
berührten Absätze bleiben byte-genau erhalten. Der originale Root-Tag wird
wörtlich wiederhergestellt, damit keine xmlns-Deklarationen verloren gehen
(bekanntes ElementTree-Verhalten).

Aufruf (aus erweitert/):
  python3 scripts/build_v2.py \
      wer_dies_liest_lebe_lang_erweitert.docx \
      wer_dies_liest_lebe_lang_erweitert_v2.docx
"""

import sys
import re
import copy
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DOC = "word/document.xml"


def text(p):
    return "".join((t.text or "") for r in p.findall(f"{W}r") for t in r.findall(f"{W}t"))


def feats(p):
    f = set()
    for r in p.findall(f"{W}r"):
        rpr = r.find(f"{W}rPr")
        if rpr is None:
            continue
        if rpr.find(f"{W}b") is not None:
            f.add("b")
        c = rpr.find(f"{W}color")
        if c is not None:
            f.add("c" + c.get(f"{W}val"))
        s = rpr.find(f"{W}sz")
        if s is not None:
            f.add("sz" + s.get(f"{W}val"))
        sp = rpr.find(f"{W}spacing")
        if sp is not None and sp.get(f"{W}val"):
            f.add("spc" + sp.get(f"{W}val"))
    return f


def is_p(e):
    return e.tag == f"{W}p"


def set_text(e, newtext):
    """Setzt den Text eines Absatzes, Format des ersten Runs bleibt erhalten."""
    runs = e.findall(f"{W}r")
    first = runs[0]
    first.findall(f"{W}t")[0].text = newtext
    for t in first.findall(f"{W}t")[1:]:
        first.remove(t)
    for r in runs[1:]:
        e.remove(r)


# Steine: Ankerzeile (letzte Zeile des Steins) -> Sigle, die darunter ergänzt wird
STONES = [
    ("und man werfe ihn aus dem Grab.", "Sigle RSIS 351"),
    ("zuletzt bei al-Namārah.", "Sigle KRS 900"),
    ("und hielt Ausschau nach den Pferden.", "Sigle CEDS 230"),
    ("und um Ṭr aus dem Stamm S¹mw.", "Sigle LP 653"),
    ("zum Stamm ˥wḏ.", "Sigle LP 540"),
    ("und um Ṣrf.", "Sigle RQ.A 5"),
    ("Leid dem, der sie zerstört.", "Sigle HSNS 5"),
    ("im Jahr, als Bnt starb.", "Sigle ASWS 73"),
    ("Wer diese Schrift liest: lebe lang.", "Sigle C 4803"),
]

# Prosa-Korrekturen: (Suchnadel im v1-Absatz, neuer Volltext)
PROSE = [
    (
        "Dazwischen kehrt, wie ein Rad",
        "Geordnet ist der Band nach dem Jahr der Steppe: Dürre und Lager, Wege und Wasser, "
        "Spähen, Weide, Raub, Krankheit, Tod, Klage, Angst, Sehnsucht, die Zeichen am Himmel "
        "— und zuletzt das Jahr selbst, an dem alles gemessen wurde. Immer wieder schließen "
        "die Steine mit derselben Geste: ein Fluch gegen das Auslöschen, ein Segen für den, "
        "der liest. Wir sind der, den sie meinten.",
    ),
    (
        "Das zweite Register sind die Steine: sieben lange",
        "Dieser Band führt zwei Register. Das erste sind die Gedichte: stark verknappte "
        "Nachdichtungen, in denen die Inschriften ins Ich übertragen, Genealogien getilgt "
        "und Lücken geschlossen wurden — Aneignung als Methode, wie im Vorwort beschrieben. "
        "Das zweite Register sind die Steine: lange Inschriften, die am Kopf der Abschnitte "
        "und am Schluss des Bandes stehen und in treuer Langzeile wiedergegeben sind.",
    ),
    (
        "bleibt der bloße Name des Schreibers als Kopf des Steins",
        "Die Steine sprechen in der dritten Person. Das ist keine Übersetzerentscheidung, "
        "sondern die Form der Originale: Die safaitische Eingangsformel lautet l-Fulān "
        "(„Von X“), danach erzählt der Text über seinen Schreiber weiter — „und er trauerte“. "
        "Der Autor dokumentiert sich selbst, er spricht nicht als er selbst. Die Gedichte "
        "holen diese Stimme ins Ich; die Steine lassen ihr die Distanz des Dokuments.",
    ),
    (
        "Zwei Steine erscheinen doppelt, als Echo",
        "Der Band schließt mit dem ganzen Stein C 4803 — jenem Stein, aus dem sein Titel "
        "geschnitten ist: „Wer dies liest, lebe lang.“",
    ),
    (
        "trägt die Quellsigle der zugrunde liegenden",
        "Grundlage sind die englischen Editionen des OCIANA-Korpus (Online Corpus of the "
        "Inscriptions of Ancient North Arabia). Jede Nachdichtung trägt die Sigle der "
        "zugrunde liegenden Inschrift; darüber ist der Originaleintrag mit Transliteration, "
        "Übersetzung und Fundort auffindbar.",
    ),
]


def transform(raw):
    # Originalen Root-Tag (mit allen xmlns + mc:Ignorable) sichern und Prefixe registrieren
    ro_start = raw.find("<w:document")
    ro_end = raw.find(">", ro_start)
    orig_root = raw[ro_start:ro_end + 1]
    for pfx, uri in re.findall(r'xmlns:([A-Za-z0-9]+)="([^"]+)"', orig_root):
        ET.register_namespace(pfx, uri)

    root = ET.fromstring(raw)
    body = root.find(f"{W}body")
    children = list(body)

    seen = set()
    del_elems = []

    def mark(e):
        if id(e) not in seen:
            seen.add(id(e))
            del_elems.append(e)

    # (1)(2)(3-Kicker): klassifikationsbasierte Löschungen
    for e in children:
        if not is_p(e):
            continue
        f = feats(e)
        if any(x == "c666666" for x in f):          # Kapitel-Untertitel + Echo-Notiz
            mark(e)
        elif "b" in f and "sz24" in f:               # Namens-Zwischenüberschriften
            mark(e)
        elif "spc40" in f:                           # STEIN/ECHO/SCHLUSSSTEIN-Kicker
            mark(e)

    # (4)(5): ganze Strophen-Einheiten löschen (Rückwärtssuche bis zur vorigen Sigle/Überschrift)
    def mark_unit(end_e):
        idx = children.index(end_e)
        mark(end_e)
        j = idx - 1
        while j >= 0:
            pj = children[j]
            if not is_p(pj):
                break
            t = text(pj).strip()
            f = feats(pj)
            if t.startswith("Quellsigle") or t.startswith("Sigle"):
                break
            if "b" in f and ("sz30" in f or "sz40" in f):
                break
            if "c666666" in f or "spc40" in f:
                break
            mark(pj)
            j -= 1

    for e in children:
        if not is_p(e):
            continue
        t = text(e).strip()
        if t == "Quellsigle ASWS 73":               # verknapptes Echo-Gedicht
            mark_unit(e)
        elif t == "Quellsigle C 4803":              # verknapptes Schlussstein-Gedicht (Kap. X)
            mark_unit(e)
        elif t.startswith("wiederkehrende Schlussformel"):  # Refrain-Seiten
            mark_unit(e)

    for e in del_elems:
        body.remove(e)

    # (3): "Quellsigle …" -> "Sigle …"
    for e in list(body):
        if is_p(e) and text(e).startswith("Quellsigle"):
            t = text(e)
            e.findall(f"{W}r")[0].findall(f"{W}t")[0].text = "Sigle" + t[len("Quellsigle"):]

    # (3): "Sigle …"-Zeile unter jeden ganzen Stein
    tpl = next(e for e in list(body) if is_p(e) and text(e).startswith("Sigle "))

    def make_sigle(label):
        n = copy.deepcopy(tpl)
        n.findall(f"{W}r")[0].findall(f"{W}t")[0].text = label
        return n

    for anchor, label in STONES:
        hits = [e for e in list(body) if is_p(e) and text(e).strip() == anchor]
        if len(hits) != 1:
            raise SystemExit(f"Anker {anchor!r}: {len(hits)} Treffer (erwartet 1)")
        body.insert(list(body).index(hits[0]) + 1, make_sigle(label))

    # Prosa-Korrekturen
    for needle, newtext in PROSE:
        hits = [e for e in list(body) if is_p(e) and needle in text(e)]
        if len(hits) != 1:
            raise SystemExit(f"Prosa {needle!r}: {len(hits)} Treffer (erwartet 1)")
        set_text(hits[0], newtext)
    head = [e for e in list(body) if is_p(e) and text(e).strip() == "Glossar der Quellsiglen"]
    if len(head) != 1:
        raise SystemExit("Glossar-Überschrift nicht eindeutig gefunden")
    set_text(head[0], "Glossar der Siglen")

    # Serialisieren, originalen Root-Tag wörtlich wiederherstellen
    out = ET.tostring(root, encoding="unicode")
    s = out.find("<w:document")
    en = out.find(">", s)
    out = out[:s] + orig_root + out[en + 1:]
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + out


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    with zipfile.ZipFile(src) as zin:
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]
    new_doc = transform(
        next(data for info, data in items if info.filename == DOC).decode("utf-8")
    ).encode("utf-8")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            zout.writestr(info, new_doc if info.filename == DOC else data)
    print(f"geschrieben: {dst}")


if __name__ == "__main__":
    main()
