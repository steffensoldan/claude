#!/usr/bin/env python3
"""
Baut den Register-Band (Konzept A): safaitische Inschriften nach den sieben
Sprechakt-Registern, gestaltet wie die erweiterte Ausgabe v5 (Georgia, Er-Form,
„Sigle …“-Zeilen), mit den Register-Unterüberschriften aus dem Konzept.

Kapitelüberschrift = Verb in der Ich-Form (schreibe/warte/bitte/klage/
verfluche/bezeuge/schweige), darunter die Konzept-Unterüberschrift.

Aufbau je Register:
  → Kopfstücke aus der erweiterten Ausgabe v5 (1 Kopfstein + 3 weitere; lange
    Inschriften zuerst), faithful aus v5 übernommen
  → knappe Stimmen aus dem Vollkorpus (Auswahl: REGISTER_BAND_AUSWAHL.md;
    Kapitel I als „X war hier“-Litanei erweitert)

Lücken (----) bleiben in Register VII offen.

Aufruf (aus Poetics/):
  python3 register/scripts/build_register.py
"""

import zipfile
import xml.etree.ElementTree as ET

V5 = "erweitert/wer_dies_liest_lebe_lang_erweitert_v5.docx"
OUT = "register/wer_dies_liest_register.docx"
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
def sigle(t, ort=None):
    label = "Sigle "+t if not ort else "Sigle "+t+" \u00b7 "+ort
    return para(run(label, '<w:color w:val="7A5C3E"/><w:sz w:val="16"/><w:szCs w:val="16"/>'), f'<w:pPr>{sp(after="280", before="60")}</w:pPr>')
PAGEBREAK = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

# Register: (Ziffer, Name · Sprechaktklasse, Konzept-Unterüberschrift,
#            [v5-Kopfstücke: Sigle], [(Sigle, [Verszeilen]) Korpus-Stimmen])
REGISTERS = [
("I","schreibe",
 "Dasein als Akt — Deixis, kein Verb des Fühlens. Die reinste Form: „dies ist”.",
 ["RWQ 342","RWQ 187","HYGQ 24","KRS 1341"],[
 ("JaS 16",["Bnḥt war hier."]),
 ("HCH 117",["ʾnʿm war hier."]),
 ("HCH 156",["S¹ḫr war hier."]),
 ("HCH 160",["Gḥs² war hier."]),
 ("HCH 158.1",["Gḥs² war hier."]),
 ("HCH 75",["ʿdy war hier."]),
 ("HCH 158.2",["S¹ʿd war hier."]),
 ("HCH 31.1",["ʿṭs¹ war hier."]),
 ("Rees 150",["S¹lf war hier."]),
 ("Rees 151",["ʾḫwn war hier."]),
 ("Rees 155",["S²d war hier."]),
 ("Rees 161 4",["Hnb war hier."]),
 ("Rees 176",["S¹drt war hier."]),
 ("JaS 4",["Von Msk, Sohn des S²dt,","Sohn des Mḥlm, Sohn des S²dt,","Sohn des Mḥlm,","vom Stamm Tm."]),
 ("JaS 5",["Von Tm, Sohn des Mḥlm,","Sohn des S²dt, Sohn des Mḥlm,","vom Stamm Tm."]),
 ("JaS 15",["Von Ḥmr, Sohn des Bnġdw,","Sohn des S¹fʾ, Sohn des Ḥnf."]),
 ("JaS 22",["Von Hnʾ, Sohn des S²nʾ,","Sohn des Gmr, Sohn des Ḍʾ."]),
 ("JaS 13",["Von Gs²m, Sohn des S¹mr,","vom Stamm Bs¹ʾ.","Und er trauerte um Nḥṭ."]),
 ("JaS 21",["Von Tʾl, Sohn des ʿz.","Und er trauerte um den Vater."]),
 ("HCH 99",["Von ʿrb, Sohn des Hrs¹.","Und er trauerte um Hnʾ."]),
 ("HCH 22",["Von Tm, Sohn des Ḫlṣ,","Sohn des Tm, Sohn des S²ʿ.","Und er trauerte um Hnʾ."]),
 ("HCH 38",["Von S¹ʿd, Sohn des Ẓn, Sohn des Ṯlm.","Und er trauerte um Hnʾ."]),
]),
("II","warte",
 "Sehnsucht, die bleibt — Warten auf Regen, auf Familie, auf Rückkehr; im Stein für einen Späteren konserviert.",
 ["RSIS 110","Is.Mu 255","SIJ 30"],[
 ("LP 1196",["Von Ms¹wd, Sohn des Whbn,","Sohn des Hrṯ, Sohn des Ms¹k,","Sohn des Qmr, Sohn des ʿwḏ,","Sohn des Whbʾl —","und er hielt Ausschau","nach dem Reiterzug."]),
 ("KRS 3051",["Die junge Kamelstute.","Er zog hinaus ins weite, offene Land","und verzweifelte","auf der Lauer nach der Raubschar."]),
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
("III","bitte",
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
("IV","klage",
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
("V","verfluche",
 "Der Fluch, der nie endet — der performativste Akt: ein gesprochener Fluch verhallt, ein gemeißelter gilt ewig.",
 ["C 4803","RSIS 351","LP 243","C 2775"],[
 ("WH 368",["Diese Schrift.","Allat —","dem, der sie austilgt:","Blindheit und Lähmung,","Stummheit, Krätze und Räude."]),
 ("LP 461",["Er trauerte um Mlk,","um Ḫrg, um Gm, um ʾys¹, um Ẓn.","Allat und Duschara —","Blutrache!","Und blende, wer dies austilgt."]),
 ("KRS 813",["Er trauerte um Ṣʿd.","Allat — blende, wer dies auskratzt,","und werfe ihn aus dem Grab."]),
 ("KRS 941",["Er fand die Spuren des Ṣʿd","und trauerte vor Schmerz —","Verzweiflung denen, die bleiben.","Das Schicksal schlug ihn nieder."]),
 ("Is.Mu 242",["Er trauerte um Mlk,","um Ḫrg, um Gḥmn, um ʾys¹, um Ẓn.","Allat und Duschara —","Blutrache."]),
 ("HCH 85",["Er trauerte um Hnʾ","und um Gls¹.","Allat und Duschara —","Blindheit dem, der dies auskratzt."]),
 ("C 286",["Rudā —","wer dies austilgt,","erblinde."]),
 ("C 1658",["Die beiden Kamele,","Allat und Rudā geweiht.","Yaṯaʿ —","blende, wer dies austilgt."]),
 ("C 1845",["Allat —","blende, wer dies auskratzt."]),
 ("C 2551",["Er erkannte eine weitere der Ritzungen —","Verzweiflung denen, die bleiben.","Allat —","Rache an dem, der die Tat beging."]),
 ("C 3138",["Rudā —","blende, wer dies auskratzt."]),
 ("C 4439",["Er kam zurück zum Wasser","im Jahr, als die Römer S²mt erschlugen.","Allat —","Blindheit dem, der dies auskratzt."]),
 ("C 5299",["Rudā —","blende, wer die Schrift auskratzt."]),
 ("LP 308",["Er trauerte um Mqm,","um ʿqrb, um S¹ḫr,","um Tmʾl, um Mqm, um Ḥml.","Allat —","Blindheit dem, der dies auskratzt."]),
]),
("VI","bezeuge",
 "Zeugnis für Unbekannte — die Datierung als Akt: er war dabei, es war dieses Jahr; geschrieben für Fremde, die später kommen.",
 ["HSNS 5","LP 653","ASWS 73","C 2670","ISB 57"],[
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
("VII","schweige",
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
]

VORWORT = [
 "Wer diese Texte liest, merkt bald: die meisten sind keine Gedichte. Viele sind kürzer als ein Satz, manche nur ein Name. Das ist kein Mangel, sondern die Form. Safaitisch schreiben heißt, an einen Stein zu klopfen, an dem man gerade vorbeikommt — für niemanden Bestimmten, weil der Stein bleibt, wenn man weitergeht.",
 "Was so entsteht, ist kein Literatur-System, sondern ein Verständigen anderer Art: eines, das nicht auf die Gleichzeitigkeit von Sender und Empfänger angewiesen ist, das die Gottheit als Zeugen einschließt und das Schweigen als eigene Aussage kennt.",
 "Dieser Band ordnet darum nicht nach Thema, sondern nach Sprechhaltung. Jedes der sieben Register ist eine andere Art, mit dem Stein zu sprechen — vom bloßen Dasein über die Bitte und die Klage bis zum Fluch, zum Zeugnis und zuletzt zum Verstummen. Jedes Register eröffnen einige lange Inschriften aus der erweiterten Ausgabe; danach folgen die knappen Stimmen des Vollkorpus.",
 "Die Texte stehen in der dritten Person, wie ihre Originale (l-Fulān, „Von X“, danach „und er …“). Genealogien sind getilgt — außer dort, wo der Name selbst der Akt ist (Register I) oder wo das Fehlen spricht (Register VII). Lücken werden hier nicht geglättet; die Striche ---- bleiben stehen.",
]
NOTE = [
 "Der Band schöpft aus dem Vollkorpus der ~31.800 safaitischen Inschriften (OCIANA), nicht aus einer Spitzenauswahl. Erschlossen sind damit auch die rund 18.500 reinen Signaturen und die Minimal-Texte, die in den bisherigen Bänden fehlten — sie tragen das Register „Er war hier“.",
 "Jedes Register ist gezielt aus seinem eigenen Korpus-Material gespeist: die Signaturen für I, die Anrufungen für III, die Fluchformeln für V, die fragmentarischen Steine für VII, die datierten für VI. Den Auftakt geben je Register Kopfstücke aus der erweiterten Ausgabe (lange Inschriften zuerst). Die Auswahl ist kuratiert und nicht repräsentativ; jede Nachdichtung trägt die OCIANA-Sigle ihrer Quelle.",
 "Übersetzungskette: gemeißelter Stein → philologische Lesung → englische OCIANA-Edition → deutsche Nachdichtung. Eckige Klammern und Striche ---- der Philologen bleiben in Register VII sichtbar.",
]

FINDSPOT = {
    'ASFF 267': 'Al-Mafraq',
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
    'C 1629': 'Zalaf',
    'C 1658': 'Zalaf',
    'C 1660': 'Zalaf',
    'C 1845': 'Zalaf',
    'C 218': 'Rif Dimašq',
    'C 2190': 'Zalaf',
    'C 2194': 'Zalaf',
    'C 2551': 'Zalaf',
    'C 2670': 'Zalaf',
    'C 2753': 'Zalaf',
    'C 2756': 'Zalaf',
    'C 2775': 'Zalaf',
    'C 286': 'Rif Dimašq',
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
    'HCH 102': 'Cairn of Haniʾ',
    'HCH 117': 'Cairn of Haniʾ',
    'HCH 125': 'Cairn of Haniʾ',
    'HCH 151': 'Cairn of Haniʾ',
    'HCH 156': 'Cairn of Haniʾ',
    'HCH 157': 'Cairn of Haniʾ',
    'HCH 158.1': 'Cairn of Haniʾ',
    'HCH 158.2': 'Cairn of Haniʾ',
    'HCH 160': 'Cairn of Haniʾ',
    'HCH 164': 'Cairn of Haniʾ',
    'HCH 183': 'Cairn of Haniʾ',
    'HCH 184': 'Cairn of Haniʾ',
    'HCH 195': 'S. of Aratain S. of HF/S',
    'HCH 22': 'Cairn of Haniʾ',
    'HCH 31.1': 'Cairn of Haniʾ',
    'HCH 38': 'Cairn of Haniʾ',
    'HCH 75': 'Cairn of Haniʾ',
    'HCH 85': 'Cairn of Haniʾ',
    'HCH 99': 'Cairn of Haniʾ',
    'HNSD 13': 'Jordanien (allg.)',
    'HSNS 1': 'Jordanien (allg.)',
    'HSNS 5': 'Jordanien (allg.)',
    'HYGQ 24': 'Fundort unbekannt',
    'HaNS 708': 'Cairn 10',
    'HaNSB 319': 'Cairn 9',
    'HaNSB 346': 'Cairn 9',
    'ISB 57': 'Site 4',
    'Is.L 202': 'al-ʿĪsāwī',
    'Is.Mu 242': 'al-ʿĪsāwī',
    'Is.Mu 255': 'al-ʿĪsāwī',
    'Is.Mu 88': 'al-ʿĪsāwī',
    'JaS 13': 'Km 612',
    'JaS 15': 'Km 612',
    'JaS 16': 'Km 612',
    'JaS 21': 'Km 612',
    'JaS 22': 'Km 612',
    'JaS 23': 'Km 612',
    'JaS 4': 'Km 612',
    'JaS 5': 'Km 612',
    'KRS 1341': 'Al-Mafraq',
    'KRS 1586': 'Al-Mafraq',
    'KRS 17': 'Wādī Salma',
    'KRS 3051': 'Al-Mafraq',
    'KRS 813': 'Al-Mafraq',
    'KRS 941': 'Al-Mafraq',
    'KWQ 113': 'Tell 5',
    'LP 1196': 'Rif Dimašq',
    'LP 1267': 'Al-Suwaydā',
    'LP 1291': 'Syrien (allg.)',
    'LP 243': 'Al-Mrōshan',
    'LP 308': 'al-ʿĪsāwī',
    'LP 461': 'al-ʿĪsāwī',
    'LP 540': 'al-ʿĪsāwī',
    'LP 653': 'Rif Dimašq',
    'MKJS 80': 'Al-Mafraq',
    'RQ.A 5': 'Riǧm Qaʿqūl',
    'RQ.D 3': 'Riǧm Qaʿqūl',
    'RQ.D 6': 'Riǧm Qaʿqūl',
    'RSIS 110': 'Tall aḍ-Ḍabiʿ',
    'RSIS 322': 'Tall aḍ-Ḍabiʿ',
    'RSIS 324': 'Tall aḍ-Ḍabiʿ',
    'RSIS 351': 'Tall aḍ-Ḍabiʿ',
    'RVP 1': 'Fundort unbekannt',
    'RVP 10': 'Fundort unbekannt',
    'RWQ 187': 'Wādī Salma',
    'RWQ 304': 'Wādī Salma',
    'RWQ 342': 'Wādī Salma',
    'Rees 150': 'Ḥarrat al-Raǧil',
    'Rees 151': 'Ḥarrat al-Raǧil',
    'Rees 155': 'Ḥarrat al-Raǧil',
    'Rees 161 4': 'Ḥarrat al-Raǧil',
    'Rees 176': 'Ḥarrat al-Raǧil',
    'SIJ 10': 'Jathum',
    'SIJ 1001': 'Cairn S. of the Baghdad ',
    'SIJ 14': 'Jathum',
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

def main():
    raw = zipfile.ZipFile(V5).read("word/document.xml").decode("utf-8")
    decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    root_open = raw[raw.find("<w:document"):raw.find(">", raw.find("<w:document"))+1]
    sect = raw[raw.find("<w:sectPr"):raw.find("</w:body>")]
    v5lines = v5_poem_lines(raw)

    xml = [title("Wer dies liest, lebe lang"),
           tsub("Safaitische Inschriften, nachgedichtet", 26),
           tsub("Aus der nordarabischen Steppe · 1. Jh. v. – 4. Jh. n. Chr.", 20, "7A5C3E"),
           tsub("Sieben Register · nach Sprechakten geordnet", 20),
           PAGEBREAK, head("Vorwort")] + [body(p) for p in VORWORT]

    total = 0
    for rom, name, sub, v5head, poems in REGISTERS:
        xml.append(PAGEBREAK)
        xml += [roman(rom), regname(name), subtitle(sub)]
        for sg in v5head:                       # Kopfstücke aus v5
            lines = v5lines.get(sg)
            if not lines:
                raise SystemExit(f"v5-Kopfstück fehlt: {sg}")
            xml += [line(l) for l in lines] + [sigle(sg, FINDSPOT.get(sg, "Fundort unbekannt"))]
            total += 1
        for sg, lines in poems:                 # Korpus-Stimmen
            xml += [line(l) for l in lines] + [sigle(sg, FINDSPOT.get(sg, "Fundort unbekannt"))]
            total += 1

    xml += [PAGEBREAK, head("Editorische Notiz")] + [body(p) for p in NOTE]
    doc = decl + root_open + "<w:body>" + "".join(xml) + sect + "</w:body></w:document>"

    with zipfile.ZipFile(V5) as zin:
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in items:
            zout.writestr(info, doc.encode("utf-8") if info.filename == "word/document.xml" else data)
    print(f"geschrieben: {OUT}  ({total} Stücke)")

if __name__ == "__main__":
    main()
