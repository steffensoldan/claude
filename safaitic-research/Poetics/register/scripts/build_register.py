#!/usr/bin/env python3
"""
Baut den Register-Band (Konzept A, Fassung v5 — bildfrei): safaitische Inschriften
nach den acht Sprechakt-Registern, gestaltet wie die erweiterte Ausgabe v5 (Georgia).

Formfassung v3:
  → Verszeilen (Absatzformat) je Eintrag — der Fließtext-Block aus v2 ist aus
    ästhetischen Gründen zurückgenommen.
  → Fundort · Sigle als Kopfzeile ÜBER dem Text (aus v2 beibehalten).
  → Verbregel: die finite Er-Form bleibt, wo das Original ein Verb vorsieht;
    wo keines vorliegt (Genealogien, Anrufungen, Signaturen), bleibt der Eintrag
    nominal — es wird KEIN Infinitiv eingesetzt.
  → Register II „schreibe“ als „Von X“ (l-Fulān, nominal, ohne „war hier“).
  → Kapitelordnung strukturell, nicht als Lebenszyklus: „schweige“ ist von der
    letzten Position (VIII) auf die Mitte (V) gerückt, damit der Band nicht auf
    das Verstummen zuläuft.
  → Bildfrei (Fassung v5): die sieben Steine mit assoziierter Felszeichnung
    (OCIANA „Associated Drawings“) sind entfernt und durch bildlose Inschriften
    gleicher Registerfunktion ersetzt — safaitische Inschriften sind ganz
    überwiegend reiner Text; die Bildbeigabe ist die Ausnahme und wäre im
    Gedichtband nicht repräsentativ. Ersetzt (raus → rein):
      HYGQ 24, KRS 1341 → Is.Mu 484, WFSG 2.1   (II schreibe)
      KRS 3051          → WH 290                 (III warte)
      HCH 85, C 286, C 1658 → RSIS 132, KRS 2919, C 1087  (VII fluche)
      C 2670            → LP 254                 (VIII bezeuge)
    Alle sieben Ersatz-Siglen sind per OCIANA-„Associated Drawings“-Read als
    bildfrei bestätigt.

Kapitelüberschrift = Verb in der Ich-Form (stehe/schreibe/warte/bitte/schweige/
klage/fluche/bezeuge).

Aufbau je Register:
  → Kopfstücke aus der erweiterten Ausgabe v5 (faithful übernommen) und knappe
    Stimmen aus dem Vollkorpus (Auswahl: REGISTER_BAND_AUSWAHL.md; Kapitel II als
    „Von X“-Signaturenreihe) werden zu einer Liste vereint und dann geordnet.
  → Ordnung (order_chapter): nach Fundort gruppiert (Reihenfolge des ersten
    Auftretens), innerhalb eines Fundorts nach der Nummerierung (z. B. RWQ 187 vor
    RWQ 342); Inschriften mit unbekanntem Fundort ans Kapitelende.
  → Kapitel I „stehe“ hat drei Fundort-Ketten: Km 612 (JaS), Hani (HCH) und
    Qāʿ Fahadah (AAEK/ASFF) — Letztere eine verknüpfte Ahnenreihe (derselbe Mann
    in zwei Lesarten, zwei Brüder derselben Linie).

Front-/Backmatter: ein Vorwort (Frontmatter) und ein Nachwort (Backmatter, drei
Abschnitte: OCIANA-Korpus, editorische Siglen, Fundorte). Das Nachwort steht auch
separat als nachwort.docx (scripts/build_nachwort.py).

Lücken (----) bleiben in Register V („schweige“) offen.

Aufruf (aus Poetics/):
  python3 register/scripts/build_register.py
"""

import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

V5 = "erweitert/wer_dies_liest_lebe_lang_erweitert_v5.docx"
OUT = "register/wer_dies_liest_register_v5.docx"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
GEO = '<w:rFonts w:ascii="Georgia" w:cs="Georgia" w:eastAsia="Georgia" w:hAnsi="Georgia"/>'

def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def run(t, rpr=""): return f'<w:r><w:rPr>{GEO}{rpr}</w:rPr><w:t xml:space="preserve">{esc(t)}</w:t></w:r>'
def para(runs, ppr=""): return f'<w:p>{ppr}{runs}</w:p>'
def sp(**kw): return '<w:spacing ' + ' '.join(f'w:{k}="{v}"' for k,v in kw.items()) + '/>'

def title(t):    return para(run(t, '<w:b/><w:sz w:val="52"/><w:szCs w:val="52"/>'), '<w:pPr><w:jc w:val="center"/></w:pPr>')
def tsub(t,sz,col=None):
    c = f'<w:color w:val="{col}"/>' if col else ''
    return para(run(t, f'{c}<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'), '<w:pPr><w:jc w:val="center"/></w:pPr>')
def head(t):     return para(run(t, '<w:b/><w:sz w:val="30"/><w:szCs w:val="30"/>'))
def body(t):     return para(run(t, '<w:sz w:val="22"/><w:szCs w:val="22"/>'), f'<w:pPr>{sp(after="200", line="320")}</w:pPr>')
def roman(t):    return para(run(t, '<w:b/><w:color w:val="7A5C3E"/><w:sz w:val="40"/><w:szCs w:val="40"/>'), f'<w:pPr>{sp(before="240", after="0")}</w:pPr>')
def regname(t):  return para(run(t, '<w:b/><w:sz w:val="30"/><w:szCs w:val="30"/>'), f'<w:pPr>{sp(after="40")}</w:pPr>')
def subtitle(t): return para(run(t, '<w:color w:val="666666"/><w:sz w:val="20"/><w:szCs w:val="20"/>'), f'<w:pPr>{sp(after="200")}</w:pPr>')
def line(t):     return para(run(t, '<w:sz w:val="22"/><w:szCs w:val="22"/>'), f'<w:pPr>{sp(after="40")}</w:pPr>')
def sigle(t, ort="Fundort unbekannt"):
    label = ort + " · " + t
    return para(run(label, '<w:color w:val="7A5C3E"/><w:sz w:val="16"/><w:szCs w:val="16"/>'), f'<w:pPr>{sp(after="280", before="60")}</w:pPr>')
def titel_ueber(t):  # Fundort · Sigle als Kopfzeile ÜBER dem Text (klein, braun)
    return para(run(t, '<w:color w:val="7A5C3E"/><w:sz w:val="16"/><w:szCs w:val="16"/>'),
                f'<w:pPr>{sp(before="260", after="40")}</w:pPr>')
PAGEBREAK = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

def _alpha(s):
    """Sortierschlüssel: Diakritika/Modifikatoren entfernen, klein, ohne führende Artikel-Striche."""
    k = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    for ch in "ʿʾˀˁ˥‹›«»„“”\"'":
        k = k.replace(ch, "")
    return k.lower().lstrip(" -")

_BORD =('<w:top w:val="single" w:color="DDDDDD" w:sz="4"/><w:left w:val="single" w:color="DDDDDD" w:sz="4"/>'
         '<w:bottom w:val="single" w:color="DDDDDD" w:sz="4"/><w:right w:val="single" w:color="DDDDDD" w:sz="4"/>')
_TBLB = _BORD + '<w:insideH w:val="single" w:color="DDDDDD" w:sz="4"/><w:insideV w:val="single" w:color="DDDDDD" w:sz="4"/>'
EMPTY = '<w:p/>'
def subhead(t): return para(run(t, '<w:b/><w:sz w:val="24"/><w:szCs w:val="24"/>'), f'<w:pPr>{sp(before="200", after="80")}</w:pPr>')
def _cell(inner, w):
    return (f'<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="{w}"/><w:tcBorders>{_BORD}</w:tcBorders>'
            '<w:tcMar><w:top w:type="dxa" w:w="60"/><w:left w:type="dxa" w:w="100"/>'
            '<w:bottom w:type="dxa" w:w="60"/><w:right w:type="dxa" w:w="100"/></w:tcMar></w:tcPr>'+inner+'</w:tc>')
def table(rows, w1=2400, w2=6600):
    trs=[]
    for a,b in rows:
        ca=_cell(para(run(a,'<w:b/><w:sz w:val="18"/><w:szCs w:val="18"/>')), w1)
        cb=_cell(para(run(b,'<w:sz w:val="18"/><w:szCs w:val="18"/>')), w2)
        trs.append('<w:tr>'+ca+cb+'</w:tr>')
    return (f'<w:tbl><w:tblPr><w:tblW w:type="dxa" w:w="{w1+w2}"/><w:tblBorders>{_TBLB}</w:tblBorders></w:tblPr>'
            f'<w:tblGrid><w:gridCol w:w="{w1}"/><w:gridCol w:w="{w2}"/></w:tblGrid>'+''.join(trs)+'</w:tbl>')


# Register: (Ziffer, Name · Sprechaktklasse, Konzept-Unterüberschrift,
#            [v5-Kopfstücke: Sigle], [(Sigle, [Verszeilen]) Korpus-Stimmen])
REGISTERS = [
("I","stehe",
 "",
 [],[
 ("JaS 4",["Von Msk, Sohn des S²dt,","Sohn des Mḥlm, Sohn des S²dt,","Sohn des Mḥlm,","vom Stamm Tm."]),
 ("JaS 5",["Von Tm, Sohn des Mḥlm,","Sohn des S²dt, Sohn des Mḥlm,","vom Stamm Tm."]),
 ("JaS 15",["Von Ḥmr, Sohn des Bnġdw,","Sohn des S¹fʾ, Sohn des Ḥnf."]),
 ("JaS 22",["Von Hnʾ, Sohn des S²nʾ,","Sohn des Gmr, Sohn des Ḍʾ."]),
 ("JaS 13",["Von Gs²m, Sohn des S¹mr,","vom Stamm Bs¹ʾ.","Und er trauerte um Nḥṭ."]),
 ("JaS 21",["Von Tʾl, Sohn des ʿz.","Und er trauerte um den Vater."]),
 ("HCH 99",["Von ʿrb, Sohn des Hrs¹.","Und er trauerte um Hnʾ."]),
 ("HCH 22",["Von Tm, Sohn des Ḫlṣ,","Sohn des Tm, Sohn des S²ʿ.","Und er trauerte um Hnʾ."]),
 ("HCH 38",["Von S¹ʿd, Sohn des Ẓn, Sohn des Ṯlm.","Und er trauerte um Hnʾ."]),
 # Dritter Ort: Qāʿ Fahadah — eine verknüpfte Ahnenreihe (tiefe Kette, derselbe
 # Mann in zwei Lesarten, zwei Brüder derselben Linie)
 ("AAEK 102",["Von Dʾyt,","Sohn des Mʿdʾl, Sohn des ʾḏnt,","Sohn des Hs¹m, Sohn des Gḥs²t,","Sohn des S¹dy, Sohn des Wṭy,","Sohn des Byq, Sohn des Ngrt,","Sohn des Qnfḏ."]),
 ("AAEK 120",["Von ʾzr, Sohn des Ftn,","Sohn des Gṯ, Sohn des S²ʿr,","Sohn des Rḥmʾl,","Sohn des Mrʾt, Sohn des Gryt."]),
 ("ASFF 244",["Von ʾzr, Sohn des Ftn,","Sohn des Mṯn, Sohn des S²ʿhm,","Sohn des Rḥhl,","Sohn des Mrʾt, Sohn des Gryt."]),
 ("ASFF 390",["Von Hnʾt, Sohn des S¹lmt,","Sohn des Lḏn, Sohn des S¹krn,","Sohn des Ndbn, Sohn des Ṣrm."]),
 ("ASFF 392",["Von Kmn, Sohn des S¹lmt,","Sohn des Lḏn, Sohn des S¹krn,","Sohn des Ndbn, Sohn des Ṣrm."]),
]),
("II","schreibe",
 "",
 ["RWQ 342","RWQ 187"],[
 ("Is.Mu 484",["Von Nr, Sohn des Qdm —","und er schrieb seinen Namen","zum ersten Mal."]),
 ("SIJ 291",["Von S²rk —","und er schrieb für den Oheim,","und er schrieb für den wahren Freund."]),
 ("JaS 16",["Von Bnḥt."]),
 ("HCH 117",["Von ʾnʿm."]),
 ("HCH 156",["Von S¹ḫr."]),
 ("HCH 160",["Von Gḥs²."]),
 ("HCH 158.1",["Von Gḥs²."]),
 ("HCH 75",["Von ʿdy."]),
 ("HCH 158.2",["Von S¹ʿd."]),
 ("HCH 31.1",["Von ʿṭs¹."]),
 ("Rees 150",["Von S¹lf."]),
 ("Rees 151",["Von ʾḫwn."]),
 ("Rees 155",["Von S²d."]),
 ("Rees 161 4",["Von Hnb."]),
 ("Rees 176",["Von S¹drt."]),
]),
("III","warte",
 "Sehnsucht, die bleibt — Warten auf Regen, auf Familie, auf Rückkehr; im Stein für einen Späteren konserviert.",
 ["ASWS 73","RSIS 110","Is.Mu 255","SIJ 30"],[
 ("LP 1196",["Von Ms¹wd, Sohn des Whbn,","Sohn des Hrṯ, Sohn des Ms¹k,","Sohn des Qmr, Sohn des ʿwḏ,","Sohn des Whbʾl —","und er hielt Ausschau","nach dem Reiterzug."]),
 ("RWQ 120",["Er hielt Wache","für seine Gefährten,","während sie am beständigen Wasser lagerten,","und trauerte um Yḥy."]),
 ("CSNS 796",["Er wartete","auf den glückenden Raubzug."]),
 ("C 2756",["Er trauerte","um die Männer","im Späherposten."]),
 ("C 2753",["Um die Männer im Späherposten","trauerte er."]),
 ("RSIS 322",["Er hielt Wache,","auf der Lauer nach dem Löwen."]),
 ("WH 175",["Er zog in die innere Wüste","und hielt Ausschau."]),
 ("AbSWS 15",["Von S¹ʿd, Sohn des Ġyrʾl,","Sohn des S¹krn, Sohn des Zkr,","Sohn des Ẓnʾl —","und er hielt Ausschau."]),
 ("KWQ 113",["Er ging mit den Ziegen","und hielt Ausschau."]),
 ("ASWS 183",["Er war auf der Lauer","nach dem Löwen."]),
 ("CEDS 226",["Er hielt Ausschau","nach den Pferden."]),
 ("SIJ 323",["Er folgte den Kamelen","und hielt Ausschau."]),
 ("SIJ 14",["Er hielt Ausschau","nach dem Löwen."]),
 ("GSSH 1",["Er lag auf der Lauer","am Späherplatz,","nach Feinden mit Kamelen."]),
 ("C 2194",["Er hielt Ausschau.","Yalt — Beute von den Feinden."]),
]),
("IV","bitte",
 "Das Gebet, das im Stein steht — an die Gottheit gerichtet, doch der Stein ist das Medium; es verhallt nicht, es bleibt adressiert.",
 ["BS 209","MKJS 80","LP 1267","Is.Mu 88"],[
 ("AbSWS 42",["Er blieb die Trockenzeit.","Allat — gib Sicherheit."]),
 ("WAMS 19.2",["Er wartete auf das Schicksal.","Rudā — errette ihn."]),
 ("C 64",["Allat —","gib Sicherheit."]),
 ("C 134",["Rudā —","schenk Befreiung."]),
 ("C 218",["Yaṯaʿ —","nimm ihm dies Unheil."]),
 ("C 1412",["Allat —","dass er sicher sei,","Allat —"]),
 ("C 805",["Allat —","schenk Errettung."]),
 ("C 885",["Rudā —","dass er sicher sei."]),
 ("C 898",["Er weidete die Esel.","Allat — dass er sicher sei."]),
 ("C 907",["Er war auf der Reise.","Allat — dass er sicher sei."]),
 ("C 1086",["Allat —","dass er sicher sei."]),
 ("C 1496",["Rudā —","hilf dem ʾlh,","Sohn des Bdn."]),
 ("C 1629",["Yalt —","Entkommen vom Bösen","in diesem Jahr."]),
 ("C 1660",["Allat —","dass er sicher sei."]),
]),
("V","schweige",
 "Lücken, die sprechen — nicht jede Lücke ist Zufall; was fehlt, wird durch sein Fehlen bezeichnet.",
 ["RQ.A 5","WH 1867.1","WH 1501.2"],[
 ("JaS 23",["----, Sohn des br,","Sohn des ----,","ʿbkz ----,","vom Stamm ʿmn."]),
 ("HCH 102",["Er hielt Wache","um den Bruder,","der den Kamelen folgte.","Allat und ----","S²ʿh ----"]),
 ("HCH 125",["Von ʾs²ym, Sohn des Drʾl,","Sohn des ʾs²ym, Sohn des Drʾl,","Sohn des Ks¹t, Sohn des ʿbd …","Sohn des S²rk —","ḫrs¹ ----ḫl----"]),
 ("HCH 151",["----lkt,","vom Stamm Fḍg.","Und er trauerte um ----","baute ----"]),
 ("HCH 157",["----, Sohn des ʾs¹lh,","Sohn des Ytm,","[----] ʾs¹ʾ"]),
 ("HCH 164",["Von Ġṯ, Sohn des ʾḫ.","Und er trauerte um den Bruder","----"]),
 ("HCH 183",["Von S¹ny, Sohn des Ḥwr,","Sohn des N----lt,","vom Stamm Fṣ----"]),
 ("HCH 184",["Von ʿbs¹, Sohn des S²ẓr,","und q----ys¹r —","----"]),
 ("HCH 195",["Von Wrs¹, Sohn des ʾglḥ,","Sohn des Ys¹lm, Sohn des ʾglḥ,","Sohn des ʾs¹l ----.","Und er wartete auf die Regen ----"]),
 ("C 1146",["Von Nḏr, Sohn des ʾs¹,","Sohn des Bḥṯ,","und wg----"]),
 ("SIJ 10",["Von Frʾ, Sohn des Frq.","Und er hielt Wache ---- Feinde.","Rudā — Errettung."]),
 ("C 12",["Rudā — Beute ---- von Feinden ----,","und dem, der ohne Milch darbt.","Allat und Schaihaqaum ----"]),
 ("C 1312",["Von Ḥḍg, Sohn des S¹wr ----.","Und er hielt Wache ----"]),
 ("C 1368",["Von Ḫlṣ ----,","Sohn des Qdm,","Sohn des ʾnʿm, Sohn des Rʿ,","vom Stamm ----"]),
]),
("VI","klage",
 "Die Trauer als Denkmal — die Klage, dem Moment entzogen; die Namensliste ist die Form des Schmerzes.",
 ["LP 540","KRS 17","AbaNS 361","C 4273"],[
 ("CSNS 781",["Er weinte vor Kummer."]),
 ("WH 1517",["Er weinte vor Kummer."]),
 ("AbaNS 453",["Er weinte vor Kummer."]),
 ("WH 3829",["Er weinte vor Kummer."]),
 ("WH 3029",["Er weinte vor Kummer","um Fly."]),
 ("WH 2825",["Er weinte vor Kummer."]),
 ("HaNSB 319",["Er weinte vor Kummer."]),
 ("HaNS 708",["Er weinte vor Kummer."]),
 ("HaNSB 346",["Er weinte vor Kummer","um seinen Sohn Wlym."]),
 ("HNSD 13",["Er weinte vor Kummer."]),
 ("SIJ 1001",["Sie weinten vor Kummer."]),
 ("SIJ 811",["Er weinte vor Kummer","um ----Gh."]),
 ("SSWS 28",["Er weinte vor Kummer."]),
 ("C 5367",["Er weinte vor Kummer."]),
]),
("VII","fluche",
 "Der Fluch, der nie endet — der performativste Akt: ein gesprochener Fluch verhallt, ein gemeißelter gilt ewig.",
 ["C 4803","RSIS 351","LP 243","C 2775"],[
 ("WH 368",["Diese Schrift.","Allat —","dem, der sie austilgt:","Blindheit und Lähmung,","Stummheit, Krätze und Räude."]),
 ("LP 461",["Er trauerte um Mlk,","um Ḫrg, um Gm, um ʾys¹, um Ẓn.","Allat und Duschara —","Blutrache!","Und blende, wer dies austilgt."]),
 ("KRS 813",["Er trauerte um Ṣʿd.","Allat — blende, wer dies auskratzt,","und werfe ihn aus dem Grab."]),
 ("KRS 941",["Er fand die Spuren des Ṣʿd","und trauerte vor Schmerz —","Verzweiflung denen, die bleiben.","Das Schicksal schlug ihn nieder."]),
 ("Is.Mu 242",["Er trauerte um Mlk,","um Ḫrg, um Gḥmn, um ʾys¹, um Ẓn.","Allat und Duschara —","Blutrache."]),
 ("RSIS 132",["Er trauerte um Ṣʿd.","Allat —","Blindheit dem, der die Schrift auskratzt."]),
 ("KRS 2919",["Rudā —","blende, wer die Schrift auskratzt."]),
 ("C 1087",["Allat —","Beute dem, der dies vorliest,","Lähmung und schändliche Blindheit","dem, der die Worte verletzt."]),
 ("C 1845",["Allat —","blende, wer dies auskratzt."]),
 ("C 2551",["Er erkannte eine weitere der Ritzungen —","Verzweiflung denen, die bleiben.","Allat —","Rache an dem, der die Tat beging."]),
 ("C 3138",["Rudā —","blende, wer dies auskratzt."]),
 ("C 4439",["Er kam zurück zum Wasser","im Jahr, als die Römer S²mt erschlugen.","Allat —","Blindheit dem, der dies auskratzt."]),
 ("C 5299",["Rudā —","blende, wer die Schrift auskratzt."]),
 ("LP 308",["Er trauerte um Mqm,","um ʿqrb, um S¹ḫr,","um Tmʾl, um Mqm, um Ḥml.","Allat —","Blindheit dem, der dies auskratzt."]),
]),
("VIII","bezeuge",
 "Zeugnis für Unbekannte — die Datierung als Akt: er war dabei, es war dieses Jahr; geschrieben für Fremde, die später kommen.",
 ["HSNS 5","LP 653","ISB 57"],[
 ("LP 254",["Er lagerte am beständigen Wasser","im Jahr, als der Stamm Qmr","dem Stamm Ḥmy Schaden tat,","und trauerte um Ġṯ,","zu früh gestorben, vom Schicksal gebeugt."]),
 ("HSNS 1",["Er zog in die innere Wüste","im Jahr, als Agrippa starb."]),
 ("RQ.D 3",["Er trauerte um den Oheim,","den sie erschlugen,","im Jahr des ʾrm."]),
 ("LP 1291",["Er blieb die späten Regen in diesem Tal,","im Jahr, als der Sturzbach","mit seinen Kamelen vorüberzog."]),
 ("C 2190",["Er zog in die innere Wüste,","im Jahr, als der Oheim starb,","und trauerte um Ks¹ṭ."]),
 ("RQ.D 6",["Er trauerte vor Schmerz","um den getöteten S²rk","und den gefangenen ʿyḏ,","im Jahr der Rm."]),
 ("Is.L 202",["Er weidete auf dem Frühjahrsgras","im Jahr von Taymāʾ."]),
 ("ASFF 267",["Er kam zurück von S¹mwt","im Jahr des Kampfes des Mʿṣ."]),
 ("KRS 1586",["Der Unterstand gehört ʿzgd.","Er kam ans Wasser","im Jahr des ṣh."]),
 ("C 4681",["Er baute den kleinen Unterstand","im Jahr, als die Sturzfluten","in diese Raḥaba kamen.","Allat — Sicherheit;","Blindheit dem, der dies auskratzt."]),
 ("ZN 1",["Er trauerte um den Bruder,","der getötet wurde,","im Jahr des Qbr."]),
 ("RWQ 304",["Er nahm diesen Ort in Besitz","im Jahr des ʾrzʾ."]),
 ("BWM 3",["Er war hier","im Jahr, als Ḥrb und ʾlmn erschlagen wurden,","und zog nach ʾnks¹r."]),
 ("RSIS 324",["Er weidete die Schafe","im Jahr des Krieges gegen die Juden."]),
 ("C 4902",["Er war hier","im Jahr des großen Regens","und jagte auf flachem Land."]),
]),
]

# --- Vorwort (Frontmatter) -------------------------------------------------
VORWORT = [
 "Der Band basiert auf der Sammlung nomadischer Inschriften des ersten bis vierten Jahrhunderts nach Christus. Beduinen ritzten sie in safaitischer Schrift in den Basalt der Wüste im Süden Syriens und in Nordjordanien.",
 "Der Stein konservierte die Markierungen der Hirten und Händler, ihre Inschriften überdauerten die Jahrtausende in extremer Hitze und Kälte. Ihr Reiz beruht wenig auf Handlung oder Drama, sondern auf dem Akt des Schreibens allein oder mit Tieren reisender Männer.",
 "Die von Erosion gezeichnete Flächen des Basalts machen einzelne Zeichen manchmal unleserlich oder zerstört sie – es bleiben sichtbare Lücken dieser Schädigung. Mancherorts ist eine Aufzählung der Ahnen selbst die Markierung, fehlende Namen artikulieren sich über ihre Leerstelle.",
 "Zu etwa 1.500 der 31.800 Inschriften gehören Zeichnungen die zum Teil direkt in die Schrift integriert sind – eine Art antiker Comic. Zeichnungen bleiben diesem Band außen vor, dies markiert ihn als auf verdichtete Schrift fokussierten Band.",
 "Die Anordnung der Kapitel durchläuft verschiedene Akte und Haltungen: vom Stehen am Stein über Wünsche und Flüche hin zu Entzug und Zeugnis. Safaitisch, eine nordarabische Konsonantenschrift ohne Vokale, lässt Modus und Person mehrdeutig, diese sprachliche Unbestimmtheit nur aus Kontexten zu erschließen.",
]

# --- Nachwort (Backmatter) -------------------------------------------------
NW_OCIANA = [
 "Sämtliche Textgrundlagen, Siglen und Ortsbestimmungen dieses Bandes beziehen sich auf das Online Corpus of the Inscriptions of Ancient North Arabia (OCIANA), das an der Universität Oxford entwickelte digitale Referenzkorpus für die epigraphischen Zeugnisse des antiken Nordarabiens. OCIANA erfasst, ediert und systematisiert zehntausende Inschriften – darunter das gesamte bekannte safaitische Korpus – und stellt die wissenschaftliche Nomenklatur, Lesarten sowie Geodaten bereit. Das System dient in diesem Band als philologische Datenbasis und Ausgangspunkt für die poetische Verdichtung und Reduktion.",
]
NW_SIGLEN_INTRO = ("Die im Band verwendeten dreistelligen Buchstabencodes (z. B. KRS, HCH, WH) verweisen auf die "
 "wissenschaftlichen Standard-Editionen und historischen Entdecker-Korpora, in denen die Inschriften erstmals "
 "dokumentiert wurden. Sie dienen im Online Corpus of the Inscriptions of Ancient North Arabia (OCIANA) als "
 "eindeutige Identifikatoren:")
NW_SIGLEN = [
 ("HCH", "Inscriptions in the Harra Collection – Das von G. L. Harding 1953 in der jordanischen Basaltwüste dokumentierte Korpus."),
 ("KRS", "King Ramadan Survey – Funde aus den systematischen archäologischen Surveys in Nordostjordanien."),
 ("LP", "Littmann, Safaitic Inscriptions – Die frühen, grundlegenden Editionen der Enno-Littmann-Expeditionen vom Beginn des 20. Jahrhunderts."),
 ("WH", "Winnett & Harding, Inscriptions from Fifty Safaitic Cairns – Die umfassende Dokumentation von fünfzig Steinhügeln, die als strukturelles Rückgrat der modernen safaitischen Epigraphik gilt."),
]
NW_FUNDORT_INTRO = ("Die Toponyme wurden auf den spezifischsten benannten Ort normalisiert und ordnen sich zwei "
 "geografischen Zonen zu: der nordostjordanischen Ḥarrah und der südsyrischen Ṣafā.")
NW_FUNDORTE = [
 ("Hani", "Steinhügel (Cairn) des Ḥāniʾ, nordostjordanische Ḥarrah; 1953 von G. L. Harding ausgegraben (Sammlung HCH)."),
 ("Km 612", "Kilometerstein 612 (ca. 32 km westlich von Badana) an der alten Pipeline-Piste. Ein Survey-Fundpunkt in Nordostjordanien."),
 ("Wādī Salma / Wādī Sārah", "Trockentäler in der Provinz Al-Mafraq, Nordostjordanien."),
 ("Ḥarrat al-Raǧil", "Basaltwüste im Grenzgebiet von Nordostjordanien und dem nördlichen Saudi-Arabien."),
 ("Jathum / Jawa / Wādī Miqāṭ / Qāʿ al-Maḥfūr / Qāʿ Fahadah / Zimlet Nāṣir", "Fundpunkte und archäologische Surveys innerhalb der nordostjordanischen Basaltwüste (Regionen Safawi und Ruwayshid)."),
 ("Zalaf", "Region um Zalaf am Wādī al-Shām, südsyrische Ṣafā."),
 ("al-ʿĪsāwī / Riǧm Qaʿqūl", "Fundplätze im Gouvernement Rif Dimašq, innerhalb der südsyrischen Basaltlandschaft."),
]

FINDSPOT = {
    'AAEK 102': 'Qāʿ Fahadah',
    'AAEK 120': 'Qāʿ Fahadah',
    'ASFF 244': 'Qāʿ Fahadah',
    'ASFF 267': 'Al-Mafraq',
    'ASFF 390': 'Qāʿ Fahadah',
    'ASFF 392': 'Qāʿ Fahadah',
    'ASWS 183': 'Wādī Sārah',
    'ASWS 73': 'Wādī Sārah',
    'AWS 379': 'Fundort unbekannt',
    'AbSWS 15': 'Wādī Salma',
    'AbSWS 42': 'Wādī Salma',
    'AbaNS 361': 'Site 12',
    'AbaNS 453': 'Site 13',
    'BS 209': 'Al-Mafraq',
    'BWM 3': 'Wādī Miqāṭ',
    'C 1086': 'Rif Dimašq',
    'C 1146': 'Riǧm Qaʿqūl',
    'C 12': 'Ǧabal Says',
    'C 1312': 'Riǧm Qaʿqūl',
    'C 134': 'Ǧabal Says',
    'C 1368': 'Riǧm Qaʿqūl',
    'C 1412': 'Riǧm Qaʿqūl',
    'C 1496': 'Zalaf',
    'C 1087': 'Rif Dimašq',
    'C 1629': 'Zalaf',
    'C 1660': 'Zalaf',
    'C 1845': 'Zalaf',
    'C 218': 'Rif Dimašq',
    'C 2190': 'Zalaf',
    'C 2194': 'Zalaf',
    'C 2551': 'Zalaf',
    'C 2753': 'Zalaf',
    'C 2756': 'Zalaf',
    'C 2775': 'Zalaf',
    'C 3138': 'Zalaf',
    'C 4273': 'Al-Suwaydā',
    'C 4439': 'Al-Suwaydā',
    'C 4681': 'Rif Dimašq',
    'C 4803': 'Zalaf',
    'C 4902': 'Rif Dimašq',
    'C 5299': 'Ḥarrat al-Raǧil',
    'C 5367': 'Ḥarrat al-Raǧil',
    'C 64': 'Ǧabal Says',
    'C 805': 'Rif Dimašq',
    'C 885': 'Khirbat al-Umbāšī',
    'C 898': 'Khirbat al-Hubayrīyah',
    'C 907': 'Khirbat al-Hubayrīyah',
    'CEDS 226': 'EDS 80-5',
    'CSNS 781': 'Qāʿ al-Maḥfūr',
    'CSNS 796': 'Qāʿ al-Maḥfūr',
    'GSSH 1': 'Al-Mafraq',
    'HCH 102': 'Hani',
    'HCH 117': 'Hani',
    'HCH 125': 'Hani',
    'HCH 151': 'Hani',
    'HCH 156': 'Hani',
    'HCH 157': 'Hani',
    'HCH 158.1': 'Hani',
    'HCH 158.2': 'Hani',
    'HCH 160': 'Hani',
    'HCH 164': 'Hani',
    'HCH 183': 'Hani',
    'HCH 184': 'Hani',
    'HCH 195': 'bei Safawi',
    'HCH 22': 'Hani',
    'HCH 31.1': 'Hani',
    'HCH 38': 'Hani',
    'HCH 75': 'Hani',
    'HCH 99': 'Hani',
    'HNSD 13': 'Jordanien (allg.)',
    'HSNS 1': 'Jordanien (allg.)',
    'HSNS 5': 'Jordanien (allg.)',
    'HaNS 708': 'Cairn 10',
    'HaNSB 319': 'Cairn 9',
    'HaNSB 346': 'Cairn 9',
    'ISB 57': 'Site 4',
    'Is.L 202': 'al-ʿĪsāwī',
    'Is.Mu 242': 'al-ʿĪsāwī',
    'Is.Mu 255': 'al-ʿĪsāwī',
    'Is.Mu 484': 'al-ʿĪsāwī',
    'Is.Mu 88': 'al-ʿĪsāwī',
    'JaS 13': 'Km 612',
    'JaS 15': 'Km 612',
    'JaS 16': 'Km 612',
    'JaS 21': 'Km 612',
    'JaS 22': 'Km 612',
    'JaS 23': 'Km 612',
    'JaS 4': 'Km 612',
    'JaS 5': 'Km 612',
    'KRS 1586': 'Al-Mafraq',
    'KRS 17': 'Wādī Salma',
    'KRS 2919': 'Al-Mafraq',
    'KRS 813': 'Al-Mafraq',
    'KRS 941': 'Al-Mafraq',
    'KWQ 113': 'Tell 5',
    'LP 1196': 'Rif Dimašq',
    'LP 1267': 'Al-Suwaydā',
    'LP 1291': 'Syrien (allg.)',
    'LP 243': 'Al-Mrōshan',
    'LP 254': 'Al-Mrōshan',
    'LP 308': 'al-ʿĪsāwī',
    'LP 461': 'al-ʿĪsāwī',
    'LP 540': 'al-ʿĪsāwī',
    'LP 653': 'Rif Dimašq',
    'MKJS 80': 'Al-Mafraq',
    'RQ.A 5': 'Riǧm Qaʿqūl',
    'RQ.D 3': 'Riǧm Qaʿqūl',
    'RQ.D 6': 'Riǧm Qaʿqūl',
    'RSIS 110': 'Tall aḍ-Ḍabiʿ',
    'RSIS 132': 'Tall aḍ-Ḍabiʿ',
    'RSIS 322': 'Tall aḍ-Ḍabiʿ',
    'RSIS 324': 'Tall aḍ-Ḍabiʿ',
    'RSIS 351': 'Tall aḍ-Ḍabiʿ',
    'RVP 1': 'Fundort unbekannt',
    'RVP 10': 'Fundort unbekannt',
    'RWQ 120': 'Wādī Salma',
    'RWQ 187': 'Wādī Salma',
    'RWQ 304': 'Wādī Salma',
    'RWQ 342': 'Wādī Salma',
    'Rees 150': 'Ḥarrat al-Raǧil',
    'Rees 151': 'Ḥarrat al-Raǧil',
    'Rees 155': 'Ḥarrat al-Raǧil',
    'Rees 161 4': 'Ḥarrat al-Raǧil',
    'Rees 176': 'Ḥarrat al-Raǧil',
    'SIJ 10': 'Jathum',
    'SIJ 1001': 'bei Ruwayshid',
    'SIJ 14': 'Jathum',
    'SIJ 291': 'Jawa',
    'SIJ 30': 'Jathum',
    'SIJ 323': 'Jawa',
    'SIJ 811': 'Tell al-ʿAbd',
    'SSWS 28': 'Wādī Sārah',
    'WAMS 19.2': 'Km 910',
    'WAMS 4': 'Fundort unbekannt',
    'WH 1116': 'Fundort unbekannt',
    'WH 1501.2': 'Fundort unbekannt',
    'WH 1517': 'Fundort unbekannt',
    'WH 175': 'WH Cairn 7',
    'WH 1851': 'Fundort unbekannt',
    'WH 1867.1': 'Fundort unbekannt',
    'WH 1916': 'Fundort unbekannt',
    'WH 2825': 'Fundort unbekannt',
    'WH 3029': 'Fundort unbekannt',
    'WH 368': 'Fundort unbekannt',
    'WH 3829': 'Fundort unbekannt',
    'ZN 1': 'Zimlet Nāṣir',
    'ZN 4': 'Fundort unbekannt',
}


def v5_poem_lines(raw):
    """Aus der v5-document.xml: Sigle -> Verszeilen (Prosa >90 Zeichen ausgefiltert)."""
    body = ET.fromstring(raw).find(f"{W}body")
    def text(p): return "".join((t.text or "") for r in p.findall(f"{W}r") for t in r.findall(f"{W}t"))
    def sz22(p):
        for r in p.findall(f"{W}r"):
            rpr = r.find(f"{W}rPr")
            if rpr is not None:
                s = rpr.find(f"{W}sz")
                if s is not None and s.get(f"{W}val") == "22":
                    return True
        return False
    out, buf = {}, []
    for e in list(body):
        if e.tag != f"{W}p":
            continue
        t = text(e)
        if t.startswith("Sigle "):
            out[t[6:].split(" · ")[0].strip()] = buf
            buf = []
        elif sz22(e) and len(t) <= 90:
            buf.append(t)
    return out

UNKNOWN_FS = "Fundort unbekannt"

def num_key(sg):
    """Sortierschlüssel einer Sigle: (Präfix, Zahlenfolge) — für die Ordnung
    nach Nummerierung innerhalb eines Fundorts (z. B. RWQ 187 vor RWQ 342)."""
    m = re.match(r"^(.*?)(\d.*)$", sg)
    prefix = (m.group(1) if m else sg).strip()
    nums = tuple(int(x) for x in re.findall(r"\d+", sg)) if m else ()
    return (prefix, nums)

def order_chapter(entries):
    """Ordnet die Einträge eines Kapitels: nach Fundort gruppiert (in der
    Reihenfolge des ersten Auftretens), innerhalb eines Fundorts nach der
    Nummerierung; Inschriften mit unbekanntem Fundort ans Kapitelende."""
    groups, order = {}, []
    for sg, lines in entries:
        fs = FINDSPOT.get(sg, UNKNOWN_FS)
        if fs not in groups:
            groups[fs] = []; order.append(fs)
        groups[fs].append((sg, lines))
    known = [fs for fs in order if fs != UNKNOWN_FS]
    result = []
    for fs in known + ([UNKNOWN_FS] if UNKNOWN_FS in groups else []):
        result += sorted(groups[fs], key=lambda e: num_key(e[0]))
    return result

def defitem(term, desc):
    """Ein Eintrag einer Definitionsliste (Nachwort): fetter Term + Erklärung."""
    return para(run(term, '<w:b/><w:sz w:val="22"/><w:szCs w:val="22"/>')
                + run(": " + desc, '<w:sz w:val="22"/><w:szCs w:val="22"/>'),
                f'<w:pPr>{sp(after="120", line="300")}</w:pPr>')

def main():
    raw = zipfile.ZipFile(V5).read("word/document.xml").decode("utf-8")
    decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    root_open = raw[raw.find("<w:document"):raw.find(">", raw.find("<w:document"))+1]
    sect = raw[raw.find("<w:sectPr"):raw.find("</w:body>")]
    v5lines = v5_poem_lines(raw)

    # Frontmatter: Titel + Vorwort
    xml = [title("Antike safaitische Inschriften"),
           tsub("nomadischer Beduinen Nordarabiens · 1. Jh. v. Chr. – 4. Jh. n. Chr.", 22, "7A5C3E"),
           tsub("»Wer dies liest, lebe lang« — in deutscher Nachdichtung", 20),
           tsub("Acht Register · nach Sprechakten geordnet", 20)]
    xml += [PAGEBREAK, head("Vorwort")] + [body(p) for p in VORWORT]

    def entry(sg, lines):
        ort = FINDSPOT.get(sg, UNKNOWN_FS)
        return [titel_ueber(f"{ort} · {sg}")] + [line(l) for l in lines]

    total = 0
    for rom, name, sub, v5head, poems in REGISTERS:
        xml.append(PAGEBREAK)
        xml += [roman(rom), regname(name)]
        merged = []                             # v5-Kopfstücke + Korpus-Stimmen
        for sg in v5head:
            lines = v5lines.get(sg)
            if not lines:
                raise SystemExit(f"v5-Kopfstück fehlt: {sg}")
            merged.append((sg, lines))
        merged += poems
        for sg, lines in order_chapter(merged): # nach Fundort/Nummer, Unbekannte ans Ende
            xml += entry(sg, lines)
            total += 1

    # Backmatter: Nachwort
    xml += [PAGEBREAK, head("Nachwort"),
            subhead("Das OCIANA-Korpus")] + [body(p) for p in NW_OCIANA]
    xml += [subhead("Die editorischen Siglen (Ergänzung)"), body(NW_SIGLEN_INTRO)]
    xml += [defitem(t, d) for t, d in NW_SIGLEN] + [EMPTY]
    xml += [subhead("Die Fundorte"), body(NW_FUNDORT_INTRO)]
    xml += [defitem(t, d) for t, d in NW_FUNDORTE] + [EMPTY]
    doc = decl + root_open + "<w:body>" + "".join(xml) + sect + "</w:body></w:document>"

    with zipfile.ZipFile(V5) as zin:
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            if info.filename == "word/document.xml":
                data = doc.encode("utf-8")
            zout.writestr(info, data)
    print(f"geschrieben: {OUT}  ({total} Stücke, bildfrei)")

if __name__ == "__main__":
    main()
