#!/usr/bin/env python3
"""
Baut Version 3 aus Version 2: jedes Kapitel auf 15 Stücke aufgefüllt.

Die neuen Nachdichtungen werden je Kapitel in der Reihenfolge ihrer Eignung
(OCIANA-LiteraryScore absteigend) ans Kapitelende angehängt — so kann man von
hinten her kürzen. Quelle der Auswahl: VORSCHLAG_15ER_AUSGABE.md bzw. die
Longlist (band1/data); für „Sehnsucht“ ergänzt aus der größeren Narrativ-Tabelle.
Stil wie die bestehenden Gedichte: Ich-Form, Genealogie getilgt, Lücken
geglättet, Gottesnamen eingedeutscht, darunter eine „Sigle …“-Zeile.

Aufruf (aus erweitert/):
  python3 scripts/build_v3.py \
      wer_dies_liest_lebe_lang_erweitert_v2.docx \
      wer_dies_liest_lebe_lang_erweitert_v3.docx
"""

import sys
import re
import copy
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DOC = "word/document.xml"

# Anker = letzte bestehende Gedicht-Sigle des Kapitels (neue Stücke kommen danach;
# bei XII vor den Schlussstein, daher KRS 2916 als Anker).
ANCHOR = {
    "I": "Sigle C 4772", "II": "Sigle BS 209", "III": "Sigle Is.Mu 255",
    "IV": "Sigle AbaNS 679", "V": "Sigle LP 297", "VI": "Sigle KRS 775",
    "VII": "Sigle WH 1198", "VIII": "Sigle WH 1501.2", "IX": "Sigle KJB 138",
    "X": "Sigle LP 1267", "XI": "Sigle RWQ 187", "XII": "Sigle KRS 2916",
}

# (Sigle, [Verszeilen])  — je Kapitel in Eignungsreihenfolge
ADD = {
"I": [
 ("NSR 34.1", ["Die späten Regen hindurch", "weidete ich und lagerte", "und trauerte um ʾsd."]),
 ("C 1156", ["Ich trauerte um ʿbd", "und um ʾnʿm, um ʿbṯn,", "um Mlk, um ʿd, um Ḥb,", "und blieb die späten Regen", "an diesem Wasser,", "im Monat S¹bṭ."]),
 ("AbSWS 21", ["Ich trauerte um Rbḥ", "und lagerte am beständigen Wasser", "und trauerte um die Gefährten."]),
 ("C 2240", ["Hier lagerte ich,", "unterwegs in die innere Wüste,", "zerschlagen vor Trauer um Ṣrmt."]),
 ("SIAM 29", ["Ich baute", "und blieb die späten Regen", "und zog mit den Kamelen", "in die innere Wüste."]),
 ("LP 406", ["Ich kam ans Wasser,", "und mein Vater tränkte die Kamele,", "eines nach dem andern, im ǧaww —", "der Winter brachte keinen Regen,", "im Jahr, als Wdn aus dem Römerland floh."]),
 ("C 3345", ["Die Trockenzeit", "an diesen zwei Hängen,", "in Not,", "auf der Wanderung."]),
 ("WAMS 6 2", ["In Not", "blieb ich die späten Regen."]),
],
"II": [
 ("KRS 1881", ["Ich weidete das Tal,", "mit dem Stamm unterwegs,", "und kam ans Wasser", "beim Untergang des Skorpions."]),
 ("AMSI 27", ["Ich trauerte um Mʿn", "und verlor den Verstand."]),
 ("AWS 213", ["Aus der inneren Wüste", "kehrte ich zurück zum Wasser", "und kam an die Tränke."]),
 ("WH 651", ["Ich war arm", "und zog auf einen Raubzug", "und kam zu Pferd", "aus der Wüste zurück."]),
 ("AWS 221", ["Ich kam ans Wasser bei al-Namāra,", "als der Skorpion aufging."]),
 ("WH 1016", ["Ich zog ans Wasser,", "als der Skorpion aufging."]),
 ("KRS 1770", ["Ich kam ans Wasser", "und wanderte weiter in der Waage.", "Baalschamin —", "nimm die Bedrängnis, nimm das Nichtwissen."]),
 ("AWS 2", ["Ich zog nach Nmrt,", "die späten Regen dort zu bleiben,", "im Jahr, als ich die Krippe baute", "und den Brunnen grub."]),
],
"III": [
 ("AWS 340", ["Ich kehrte zur Tränke zurück", "im Jahr, als die Sippen Ḫl und Nqd stritten,", "und hielt Ausschau nach dem Bruder."]),
 ("Lemaire 1", ["Ich trauerte um die Mutter", "und um Ḥrs¹, zu früh dahin,", "und hielt Ausschau nach dem Bruder", "und weidete."]),
 ("SIJ 699", ["Ich hielt Ausschau nach Ḥnn.", "Rudā — Erbarmen.", "Wer dies auskratzt: erblinde."]),
 ("JSLih 071", ["Ich war Befehlshaber in al-Ḥigr", "und hielt ein Jahr lang stand", "gegen den Übergriff des S¹fy,", "dann führte ich die Karawanen", "durch diese Wüsten."]),
 ("AWS 341", ["Aus der inneren Wüste", "kam ich zurück zum Wasser,", "im Jahr, als die Sippen stritten,", "und hielt Wache", "im Krieg der Nabatäer."]),
 ("Damascus Museum 17752", ["Ich trauerte um den Vater", "und um ʿwḏ, den Oheim,", "und um S²ʿ,", "und hielt Ausschau.", "Wer dies zerstört —", "dem schlage Duschara die Hand ab."]),
 ("ZN 9", ["Ich trauerte vor Schmerz", "um den Bruder, den sie gefangen hielten,", "im Jahr, als die Sippe ʿwḏ", "die Römer vertrieb,", "und hielt Ausschau nach Yrb."]),
 ("KRS 1124", ["Ich trauerte um ʾnʿm,", "um Nṣrʾl, um Qdm, um ʾbgr,", "und hielt Wache gegen den Feind.", "Allat — gib Sicherheit.", "Wer dies auskratzt: erblinde."]),
],
"IV": [
 ("SIJ 263", ["Ich wusch die Schafe", "und weidete die Kamele", "und hielt Ausschau.", "Allat — Erbarmen."]),
 ("TaNS 1", ["Ich weidete die Kamelherde,", "mit dem Stamm unterwegs,", "und floh vor den Nabatäern", "im Jahr, als Ḥmt erschlagen wurde."]),
 ("ASWS 319", ["Ich weidete die Schafe", "und trauerte vor Schmerz."]),
 ("HaNSB 145", ["Die junge Kamelstute.", "Ich weidete die Kamele", "mit den großen Höckern."]),
 ("WH 3049", ["Ich war hier", "und blieb die Trockenzeit in der Ḥarrah", "und trieb die Pferde fort", "aus dem Hauran,", "im Jahr der Flut."]),
 ("Is.L 82", ["Die junge Kamelstute.", "Ich weidete auf ṯudāʾ,", "unterwegs mit dem Stamm."]),
 ("HaNSC 16", ["Ich weidete die Kamelherde,", "mit dem Stamm unterwegs."]),
 ("KRS 2769", ["Ich weidete", "und ließ die Herde allein ziehen", "in einen Wind."]),
 ("C 2936", ["Ich weidete die Schafe", "und hielt nach den Regenwolken Ausschau."]),
],
"V": [
 ("C 5224", ["Ich zeichnete die Ziegen", "mit schwarzem Strich", "und war auf Raubzug."]),
 ("KRS 1804", ["Schwach und mager", "weidete ich die Wasserläufe", "auf dem Raubzug."]),
 ("C 3680", ["Ich raubte", "im Jahr des Krieges von Nabatäa."]),
 ("KRS 3249", ["Die Maultierstute.", "Verstört um die Gefährten", "war ich auf Raubzug in der Ḥarrah.", "Wer dies auskratzt: erblinde."]),
 ("HYGQ 95", ["Ich zog auf Raubzug", "gegen die Nabatäer."]),
 ("BRenv.B 1", ["Ich half den Ziegen werfen", "im Jahr, als die ʾl Hḏr gefangen wurden,", "im Jahr, als die Liḥyaniten", "über die ʾs¹kn herfielen."]),
 ("BRenv.A 5", ["Ich half den Ziegen werfen", "im Jahr, als die ʾl Hḏr gefangen wurden", "und die Liḥyaniten", "die ʾs¹kn überfielen."]),
 ("C 2538", ["Verstört —", "ich hatte die Gefährten verloren", "in einem Überfall."]),
 ("SIJ 172", ["Ich trauerte um Ḥrb", "und zog in den Kampf."]),
],
"VI": [
 ("WH 986", ["Ich trauerte vor Schmerz", "um einen, den ich liebte."]),
 ("KRS 1813", ["Vor Schmerz", "trauerte ich um einen Geliebten."]),
 ("C 2775", ["Ich trauerte vor Schmerz", "um Nr, um Ṣfwn, um Ks¹ṭ,", "und war verstört um die Gefährten.", "Wer dies auskratzt: erblinde."]),
 ("LP 411", ["Ich trauerte um ʾqwm", "und um ʾnʿm", "und trauerte vor Schmerz."]),
 ("RSIS 210", ["Ich fand die Spuren des ʾs¹r", "und trauerte vor Schmerz", "um Whbʾl, um Ys¹lm, um Mtn."]),
 ("KRS 424", ["Ich trauerte", "und trauerte vor Schmerz."]),
 ("C 2712", ["Ich trauerte vor Schmerz um den Vater", "und um den Oheim,", "im Jahr, als ʾmtr starb."]),
 ("C 1989", ["Ich fand die Spur des Ṣʿd,", "des Reiters,", "den sie begruben,", "und trauerte vor Schmerz."]),
 ("Is.Mu 253", ["Ich fand die Spuren des Vaters", "und weinte", "und dachte an den Bruder ʿwl", "und trauerte vor Schmerz,", "elend und voller Kummer."]),
],
"VII": [
 ("C 4273", ["Ich trauerte um den Vater", "und um den Bruder, zu früh dahin,", "und um Ḫlṣ und um ʾtm."]),
 ("Is.Mu 25", ["Ich weidete dies Tal", "auf einem Raubzug,", "im Jahr, als Mʿn erschlagen wurde."]),
 ("ZSI 1", ["Zerschlagen vor Trauer", "um die Mutter, die starb,", "baute ich den Steinhaufen über ihr."]),
 ("INAS 32", ["Ich trauerte um Nṣr,", "den sie erschlugen.", "Duschara — Rache an Nṭyʾ."]),
 ("TIJ 522", ["Ich trauerte um Ḫld, die Schwester.", "Sie starb ungern,", "sie sträubte sich gegen den Tod."]),
 ("CEDS 117", ["Meine Ziegen starben", "in diesem Pferch."]),
 ("LP 236", ["Ich trauerte um Ġṯ,", "den sie erschlugen —", "Lh, gib mir Glück auf der Reise —", "und um ʾs¹d und um ʾrṣf."]),
 ("WH 387", ["Ich kehrte zurück zum Wasser", "im Jahr, als der König starb."]),
],
"VIII": [
 ("AbaNS 361", ["Ich weinte vor Kummer", "um einen, den ich liebte."]),
 ("WH 2472", ["Vor Kummer weinte ich", "um den Geliebten."]),
 ("KhBG 344", ["Um den Geliebten", "weinte ich vor Kummer."]),
 ("C 2770", ["Verstört um den Oheim", "weinte ich um Tm,", "um Mlkt, um Nr.", "Schaihaqaum —", "Sicherheit dem, der dies unberührt lässt."]),
 ("CEDS 411", ["Ich weinte vor Kummer."]),
 ("HaNSB 83", ["Vor Kummer", "weinte ich."]),
 ("WH 3506", ["Ich weinte,", "vor Kummer."]),
 ("WH 1756", ["Und ich weinte vor Kummer."]),
],
"IX": [
 ("JSLih 077", ["Wir errichteten das Grabmal", "für Mr, Sohn des Ḥwt,", "und trugen die Kosten,", "Ernte um Ernte der späten Regen —", "seit Rṣs¹ uns in Not gestürzt hat,", "im Jahr zwanzig, als der König …"]),
 ("HaNSC 3", ["Ich war in Not", "dies Jahr."]),
 ("WH 1255", ["Ich bin in Not.", "Rudā."]),
 ("SIJ 925 926", ["In Not", "und niedergeschlagen."]),
 ("WH 81", ["Ich war in Not", "und bedürftig der Gunst."]),
 ("Jacobson D.3.A.7 b", ["Lh —", "ohne Bedrängnis", "für den Sohn des ʿry."]),
 ("SIJ 590", ["Ich war in Not.", "Allat — gib Fülle."]),
 ("Jacobson B.3.C.4", ["Allat, gedenke des ʾbs¹lm", "und wende alle Not."]),
 ("KRS 1964", ["Ich überwinterte in Bedrängnis,", "knapp an Vorrat,", "und brachte die Schafe", "der Sippe Ḥlṣ in Sicherheit."]),
],
"X": [
 ("JaS 43.2", ["Ich blieb die späten Regen", "und sehnte mich nach ʾḫw.", "Allat — gib Sicherheit."]),
 ("Is.H 520", ["Ich trieb die Pferde", "und hielt Ausschau nach den Kamelen in ʿqft.", "Baalschamin und Gad-ʿAud —", "Rettung und Sicherheit;", "und dem, der dies auskratzt:", "Schmerz, in Liebe."]),
 ("LP 562.1", ["Ich fand die Inschrift des Vaters", "und sehnte mich nach ihm.", "Die Schafe sind sein."]),
 ("CSNS 190", ["Ich hielt vorzüglich Wache —", "und war verliebt."]),
 ("C 2832", ["Ich kaufte die Kamelstute", "vom Bruder ʿḏ, für hundert,", "und sehnte mich nach dem Vater", "und den beiden Brüdern."]),
 ("SIJ 818", ["Hier lagerte ich", "und sehnte mich."]),
 ("C 88", ["Vertrauter des Mk,", "sehnte ich mich nach Bʿls¹my", "und den Kindern des Oheims.", "Allat und Duschara —", "Sicherheit und Wiedersehen mit der Familie."]),
 ("LP 438", ["Die Sturzflut trieb mich fort bei Brs.", "Ich fand die Spuren der Gefährten", "und sehnte mich nach ihnen."]),
 ("NSR 53.2", ["Ich überwinterte bei mnʿt", "und sehnte mich nach dem Bruder.", "Gunst und Sicherheit."]),
 ("SIJ 352", ["Ich entkam den Römern", "und sehnte mich nach den Brüdern,", "fern in der inneren Wüste."]),
 ("KRS 124", ["Ich kehrte zurück zum Wasser", "und sehnte mich nach einem Freund.", "Allat — Blindheit dem, der dies auskratzt."]),
 ("Is.Mu 897", ["Ich fand die Inschrift", "des Oheims ʾnʿm", "und sehnte mich nach ihm."]),
],
"XI": [
 ("CSNS 538", ["Ich war dabei,", "als die Regenflut kam."]),
 ("HYGQ 24", ["Der Löwe."]),
 ("HaNSB 235", ["Am Tümpel,", "den die Sturzflut zurückließ."]),
 ("KRS 1583", ["Dies ist die Zeichnung", "eines Löwen."]),
 ("C 1621", ["Dies ist die Zeichnung", "des Löwen."]),
 ("KRS 1341", ["Die Zeichnung des Löwen."]),
 ("KJB 74", ["Die Zeichnung", "eines Steinbocks und eines Hundes."]),
 ("WH 1229", ["Und der Löwe", "ist bei ihm."]),
 ("SIJ 30", ["Ich wartete", "auf den Schnee", "über dem Hauran."]),
],
"XII": [
 ("BRenv.J 12", ["Ich weidete die Ziegen", "in diesem Tal,", "während einer Dürre."]),
 ("Is.Mu 70", ["Ich weidete dies Tal", "im Jahr des Kampfes der ʾl Mgd."]),
 ("C 4233", ["Ich weidete", "im Jahr des ṣmkk."]),
 ("RQ.D 1", ["Ich trauerte um Ḥzqn", "im Jahr der Sippe Ḍf."]),
 ("C 269", ["Ich weidete im Tal", "auf frischem Gras, im Wassermann,", "im Jahr des Gs²m und Ḥnʾl."]),
 ("KRS 2394", ["Ich weidete", "im Jahr der Tötung in Klbt."]),
 ("WH 1867.1", ["Ich weidete die MSTY", "in einem Jahr,", "dessen Name fehlt."]),
],
}


def text(p):
    return "".join((t.text or "") for r in p.findall(f"{W}r") for t in r.findall(f"{W}t"))


def set_text(e, newtext):
    runs = e.findall(f"{W}r")
    first = runs[0]
    first.findall(f"{W}t")[0].text = newtext
    for t in first.findall(f"{W}t")[1:]:
        first.remove(t)
    for r in runs[1:]:
        e.remove(r)


def transform(raw):
    ro_start = raw.find("<w:document")
    ro_end = raw.find(">", ro_start)
    orig_root = raw[ro_start:ro_end + 1]
    for pfx, uri in re.findall(r'xmlns:([A-Za-z0-9]+)="([^"]+)"', orig_root):
        ET.register_namespace(pfx, uri)
    root = ET.fromstring(raw)
    body = root.find(f"{W}body")

    # Vorlagen aus dem Dokument klonen
    poem_tpl = sig_tpl = None
    for e in list(body):
        if e.tag != f"{W}p":
            continue
        t = text(e).strip()
        if poem_tpl is None and t == "Ich blieb das Tal hindurch,":
            poem_tpl = e
        if sig_tpl is None and t.startswith("Sigle "):
            sig_tpl = e
    if poem_tpl is None or sig_tpl is None:
        raise SystemExit("Vorlagen nicht gefunden")

    def make(tpl, s):
        n = copy.deepcopy(tpl)
        n.findall(f"{W}r")[0].findall(f"{W}t")[0].text = s
        return n

    total = 0
    for rom, poems in ADD.items():
        anchor = ANCHOR[rom]
        hit = [e for e in list(body) if e.tag == f"{W}p" and text(e).strip().startswith(anchor)]
        if len(hit) != 1:
            raise SystemExit(f"Anker {anchor!r}: {len(hit)} Treffer")
        pos = list(body).index(hit[0]) + 1
        for sigle, lines in poems:
            for ln in lines:
                body.insert(pos, make(poem_tpl, ln)); pos += 1
            body.insert(pos, make(sig_tpl, "Sigle " + sigle)); pos += 1
            total += 1

    # Vorwort: Stückzahl aktualisieren
    vh = [e for e in list(body) if e.tag == f"{W}p" and "wenige Dutzend" in text(e)]
    if len(vh) == 1:
        set_text(vh[0], text(vh[0]).replace("wenige Dutzend", "gegen zweihundert"))

    print(f"  eingefügt: {total} neue Stücke")
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
        next(data for info, data in items if info.filename == DOC).decode("utf-8")
    ).encode("utf-8")
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            zout.writestr(info, new_doc if info.filename == DOC else data)
    print(f"geschrieben: {dst}")


if __name__ == "__main__":
    main()
