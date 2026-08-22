#!/usr/bin/env python3
"""
Baut den Register-Band in der Handfassung v6:
Wer dies liest, lebe lang — nomadische Inschriften im antiken Arabien.

v6 loest die v5-Linie ab (siehe REGISTER_BAND_AUSWAHL.md):
  * Titel kursiv, keine »«-Guillemets; Untertitel „…im antiken Arabien".
  * KEINE „Vorwort"/„Nachwort"-Ueberschriften mehr; Vorwort = acht
    nummerierte Absaetze direkt nach dem Titel.
  * Registerfolge: I stehe . II ritze . III harre . IV fehle . V bitte .
    VI klage . VII fluche . VIII bezeuge  (III war „warte", IV war „schweige"
    und stand auf V; „bitte" auf V).
  * 138 Stuecke (RSIS 324 entfernt).
  * Nachwort: 3 Fliesstext-Absaetze, fette Marke „Die Erstausgaben" +
    Sigle-Liste, Zwischentitel „Die Fundorte" (12 pt) + Fundort-Liste.

Transliteration: Die Leseform (˥→ʿ, s¹→s, s²→š) ist im Datenblock unten
BEREITS ANGEWANDT. Regeln und die rein philologische Rohform (s¹/s²/˥) sind
in REGISTER_BAND_AUSWAHL.md und im v5-Stand dieses Skripts (Git-Historie,
Funktion `readable()`) dokumentiert.

Nur word/document.xml wird neu geschrieben; das Docx-Skelett (Georgia-styles,
sectPr) stammt aus der bestehenden v6 selbst. Idempotent.

Aufruf (aus safaitic-research/):  python3 register/scripts/build_register.py
Ausgabe: register/wer_dies_liest_register_v6.docx
"""

import zipfile

TEMPLATE = "register/wer_dies_liest_register_v6.docx"
OUT      = "register/wer_dies_liest_register_v6.docx"

# --------------------------------------------------------------------------
# Format-Bausteine (entsprechen exakt der Handfassung v6)
# --------------------------------------------------------------------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _run(t, rpr=""):
    return f'<w:r>{("<w:rPr>"+rpr+"</w:rPr>") if rpr else ""}<w:t xml:space="preserve">{esc(t)}</w:t></w:r>'

def _p(runs, ppr=""):
    return f'<w:p>{ppr}{runs}</w:p>'

PAGEBREAK = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
EMPTY     = '<w:p/>'
_SZ26 = '<w:sz w:val="26"/><w:szCs w:val="26"/>'

def title1(t):      # Titelzeile 1: 13 pt, zentriert, KURSIV
    return _p(_run(t, '<w:i/><w:iCs/>'+_SZ26), f'<w:pPr><w:jc w:val="center"/><w:rPr>{_SZ26}</w:rPr></w:pPr>')

def title2(t):      # Untertitel: 13 pt, zentriert
    return _p(_run(t, _SZ26), f'<w:pPr><w:jc w:val="center"/><w:rPr>{_SZ26}</w:rPr></w:pPr>')

def title_spacer():
    return _p("", f'<w:pPr><w:jc w:val="center"/><w:rPr>{_SZ26}</w:rPr></w:pPr>')

def body(t):        # Fliesstext (Vorwort-Absaetze, Nachwort-Intro)
    return _p(_run(t), '<w:pPr><w:spacing w:after="200" w:line="320" w:lineRule="auto"/></w:pPr>')

def roman(t):       # Register-Ziffer, 20 pt fett braun
    return _p(_run(t, '<w:b/><w:color w:val="7A5C3E"/><w:sz w:val="40"/><w:szCs w:val="40"/>'),
              '<w:pPr><w:spacing w:before="240"/></w:pPr>')

def regname(t):     # Register-Name, 15 pt fett
    return _p(_run(t, '<w:b/><w:sz w:val="30"/><w:szCs w:val="30"/>'),
              '<w:pPr><w:spacing w:after="40"/></w:pPr>')

def header(t):      # Fundort . Sigle, 8 pt braun
    return _p(_run(t, '<w:color w:val="7A5C3E"/><w:sz w:val="16"/><w:szCs w:val="16"/>'),
              '<w:pPr><w:spacing w:before="260" w:after="40"/></w:pPr>')

def line(t):        # Verszeile (Georgia 11 pt via Default)
    return _p(_run(t), '<w:pPr><w:spacing w:after="40"/></w:pPr>')

def bold_head(t):   # „Die Erstausgaben" — fett, Normalgroesse, Listen-Abstand
    return _p(_run(t, '<w:b/>'),
              '<w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr>')

def subhead(t):     # „Die Fundorte" — 12 pt fett
    return _p(_run(t, '<w:b/><w:sz w:val="24"/><w:szCs w:val="24"/>'),
              '<w:pPr><w:spacing w:before="200" w:after="80"/></w:pPr>')

def listitem(label, rest):   # Sigle-/Fundort-Eintrag: fette Marke + Erklaerung
    return _p(_run(label, '<w:b/>') + _run(rest),
              '<w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr>')

# --------------------------------------------------------------------------
# INHALT (aus der Handfassung v6 extrahiert; Vorwort-Tippfehler korrigiert)
# --------------------------------------------------------------------------
TITLE = [
    'Wer dies liest, lebe lang — ',
    'nomadische Inschriften im antiken Arabien',
]

VORWORT = [
    '1. Inschriften arabischer Nomaden. Beduinen ritzten sie zwischen dem ersten vor und dem vierten Jahrhundert nach Christus in den Basalt der Wüsten Harra und Ṣafā.',
    '2. Viele tausend Steine auf dem Gebiet des heutigen Syrien, Saudi-Arabien, Jordanien und des Irak tragen Markierungen und konservierten sie. Ihr Reiz beruht nicht auf Handlung oder Drama, sondern auf einer faktisch permanent gemachten Schrift.',
    '3. Die Autoren waren Mitglieder von Nomadengruppen: Hirten, Händler und Viehzüchter. Meist Männer während alltäglicher Arbeiten abseits der zentralen Zeltlager – Hüten, Warten, Wachehalten. ',
    '4. Die in safaitischer Schrift verfassten Artefakte führen keinen Dialog, tragen keine Vokale, nur die Konsonanten. Der vorliegende Band ist auf diese verdichtete Form aus, auf Sprache als Akte der Schrift in den Stein. ',
    '5. Einem kleinen Teil der Inschriften sind Zeichnungen von Tieren, Menschen und Gegenständen integriert, eine Art antikes Graffiti. Diese müssen in einem anderen Band behandelt werden.  ',
    '6. 138 ausgewählte Inschriften durchlaufen in diesem Band Schriftakte vom Stehen am Stein, über Wünsche, Flüche, hin zu Entzug und Zeugnis. Fundort und Sammlung leiten jeden Eintrag ein. ',
    '7. Die acht Register umreißen eine nomadische Grammatik. Lachen, Freude, Dank gehören (vermutlich) zum gemeinsamen Leben in den Zelten. Hier, draußen, allein, beim Schreiben, gibt es das nicht. Fragen oder Zweifel ebenfalls nicht. Akte des Lebens gegen das Verschwinden. Es steht geschrieben, worüber Anwesende schweigen.',
    '8. Die Analyse, das Übertragen und Sortieren der Inschriften übernahm Claude Code Opus 5. Die sprachliche Ausarbeitung und Zuordnung zu Registern erfolgte durch menschliche Hand, dem jeweils dominanten Schriftakt folgend.',
]

NACHWORT_INTRO = [
    'Sämtliche Textgrundlagen, Siglen und Ortsbestimmungen dieses Bandes beziehen sich auf den an der Universität Oxford entwickelten digitalen Referenzkorpus für die epigraphischen Zeugnisse des antiken Nordarabiens (OCIANA). ',
    'OCIANA erfasst, ediert und systematisiert zehntausende Inschriften – darunter das gesamten Korpus safaitischer Inschriften, aus dem sich dieser Band speist. OCIANA stellt dessen wissenschaftliche Nomenklatur, Geodaten sowie englisch-sprachige Übersetzungen bereit. ',
    'Die im Band verwendeten Buchstabencodes verweisen auf die wissenschaftlichen Editionen und historischen Korpora, in denen die Inschriften erstmals dokumentiert wurden. Sie dienen OCIANA als eindeutige Identifikatoren, ebenso wie die Fundorte und Geodaten der Inschriften.',
]

ERSTAUSGABEN_LABEL = 'Die Erstausgaben'

SIGLEN = [
    [
    'HCH',
    ': Inscriptions in the Harra Collection – Das von G. L. Harding 1953 in der jordanischen Basaltwüste dokumentierte Korpus.',
],
    [
    'KRS',
    ': King Ramadan Survey – Funde aus den systematischen archäologischen Surveys in Nordostjordanien.',
],
    [
    'LP',
    ': Littmann, Safaitic Inscriptions – Die frühen, grundlegenden Editionen der Enno-Littmann-Expeditionen vom Beginn des 20. Jahrhunderts.',
],
    [
    'WH',
    ': Winnett & Harding, Inscriptions from Fifty Safaitic Cairns – Die umfassende Dokumentation von fünfzig Steinhügeln, die als strukturelles Rückgrat der modernen safaitischen Epigraphik gilt.',
],
    [
    'C',
    ': Corpus Inscriptionum Semiticarum, Pars V – die safaitischen Inschriften (u. a. Dussaud & Macler; Ryckmans 1950).',
],
    [
    'SIJ',
    ': Winnett, Safaitic Inscriptions from Jordan (Toronto 1957).',
],
    [
    'ISB',
    ': Oxtoby, Some Inscriptions of the Safaitic Bedouin (New Haven 1968).',
],
    [
    'CSNS',
    ': Clark, A Study of New Safaitic Inscriptions from Jordan (1979).',
],
    [
    'Rees',
    ': L. W. B. Rees, frühe Aufnahmen aus der Ḥarrat al-Raǧil (1920er Jahre).',
],
    [
    'Is.L / Is.Mu',
    ': Sammlungen aus al-ʿĪsāwī (Rif Dimašq); Editionsnachweis jeweils im OCIANA-Eintrag.',
],
    [
    'RQ.A / RQ.D',
    ': Aufnahmen aus Riǧm Qaʿqūl (Rif Dimašq).',
],
    [
    'RSIS / ASWS / SSWS / AbSWS / RWQ',
    ': Surveys der Wādī-Sārah- und Wādī-Salma-Region (Provinz Al-Mafraq).',
],
    [
    'AbaNS / HaNS / HaNSB / HNSD / HSNS',
    ': nordjordanische Safaitic-Surveys.',
],
    [
    'AAEK / ASFF',
    ': Surveys von Qāʿ Fahadah (Provinz Al-Mafraq).',
],
    [
    'JaS / KWQ / CEDS / GSSH / MKJS / BS / WAMS / BWM / ZN',
    ': weitere OCIANA-Survey-Siglen aus der nordostjordanischen Ḥarrah; vollständiger Editionsnachweis jeweils im OCIANA-Eintrag.',
],
]

FUNDORTE_HEAD = 'Die Fundorte'

FUNDORTE = [
    [
    'Hani',
    ': Steinhügel (Cairn) des Ḥāniʾ, nordostjordanische Ḥarrah; 1953 von G. L. Harding ausgegraben (Sammlung HCH).',
],
    [
    'Km 612',
    ': Kilometerstein 612 (ca. 32 km westlich von Badana) an der alten Pipeline-Piste. Ein Survey-Fundpunkt in Nordostjordanien.',
],
    [
    'Wādī Salma / Wādī Sārah',
    ': Trockentäler in der Provinz Al-Mafraq, Nordostjordanien.',
],
    [
    'Ḥarrat al-Raǧil',
    ': Basaltwüste im Grenzgebiet von Nordostjordanien und dem nördlichen Saudi-Arabien.',
],
    [
    'Qāʿ Fahadah',
    ': Fundplatz in der Provinz Al-Mafraq, Nordostjordanien (Ahnenreihen in Kapitel I).',
],
    [
    'Jathum / Jawa / Wādī Miqāṭ / Qāʿ al-Maḥfūr / Zimlet Nāṣir / bei Safawi / bei Ruwayshid',
    ': weitere Fundpunkte und Surveys innerhalb der nordostjordanischen Basaltwüste.',
],
    [
    'Zalaf',
    ': Region um Zalaf am Wādī al-Shām, südsyrische Ṣafā.',
],
    [
    'al-ʿĪsāwī / Riǧm Qaʿqūl',
    ': Fundplätze im Gouvernement Rif Dimašq, innerhalb der südsyrischen Basaltlandschaft.',
],
    [
    'Ǧabal Says',
    ': Basaltmassiv im Gouvernement Rif Dimašq, südsyrische Ṣafā.',
],
    [
    'Tall aḍ-Ḍabiʿ',
    ': Tall aḍ-Ḍabiʿ am Wādī as-Samin, Süd-Syrien.',
],
    [
    'Al-Mrōshan / Khirbat al-Hubayrīyah / Khirbat al-Umbāšī',
    ': Fundpunkte im Gouvernement Al-Suwaydā, Süd-Syrien.',
],
    [
    'Al-Mafraq',
    ': Provinz Al-Mafraq (Nordostjordanien) – genauer Fundpunkt nicht angegeben.',
],
    [
    'Rif Dimašq / Al-Suwaydā',
    ': südsyrische Gouvernements (Ṣafā) – genauer Fundpunkt nicht angegeben.',
],
    [
    'Jordanien (allg.) / Syrien (allg.)',
    ': nur das Land überliefert (Ḥarrah bzw. Ṣafā).',
],
    [
    'Site 4 / Site 12 / Site 13 · Tell 5 · Tell al-ʿAbd · Cairn 9 / Cairn 10 · WH Cairn 7 · EDS 80-5 · Km 910',
    ': interne Survey-Codes und Fundpunkte ohne näher benannten Ort (Nordostjordanien).',
],
    [
    'Fundort unbekannt',
    ': keine Ortsangabe im OCIANA-Eintrag.',
],
]

ZEICHEN_HEAD = 'Zur Aussprache'

ZEICHEN_INTRO = [
    'Die Namen und Wörter dieses Bandes bewahren die Sonderzeichen der wissenschaftlichen Umschrift. Sie halten Laute fest, die das deutsche Alphabet nicht kennt. Die folgende Übersicht nennt zu jedem Zeichen den Laut und eine Aussprachehilfe. Großbuchstaben (Ḥ, Ṣ, Š …) klingen wie ihre kleinen Formen; die Punkte und Striche gehören zum Buchstaben und werden nicht eigens gesprochen.',
]

# ZEICHEN: [ Zeichen, Aussprachehilfe ] — Sonderzeichen der Umschrift
ZEICHEN = [
    [
    'ʾ',
    ' — Stimmabsatz (Hamza): der harte Stimmeinsatz wie zwischen den Silben von „be·achten"; ein Knacklaut, kein Buchstabe im deutschen Sinn.',
],
    [
    'ʿ',
    ' — Kehllaut (ʿAin): ein stimmhafter Presslaut tief im Rachen, ohne deutsche Entsprechung; wie ein gepresstes „a".',
],
    [
    'ḥ',
    ' — scharf gehauchtes „h": aus dem Rachen gepresst, kräftiger und rauer als das deutsche h.',
],
    [
    'ḫ',
    ' — Reibe-„ch": wie das ch in „Bach" oder „Buch".',
],
    [
    'ġ',
    ' — Reibe-„g/r" (Ġain): ein gerolltes Zäpfchen-r, ähnlich dem französischen „r" in „Paris".',
],
    [
    'š',
    ' — „sch": wie in „Schrift".',
],
    [
    'ǧ',
    ' — weiches „dsch": wie das englische j in „jump" (in Ortsnamen, z. B. Riǧm, Raǧil).',
],
    [
    'ṯ',
    ' — stimmloses englisches „th": wie in „think".',
],
    [
    'ḏ',
    ' — stimmhaftes englisches „th": wie in „this".',
],
    [
    'ṣ · ḍ · ṭ · ẓ',
    ' — nachdrückliche (emphatische) Laute: s, d, t und der „th"-/z-Laut, dunkel und mit gespannter Zunge gesprochen. Der Punkt unter dem Buchstaben markiert diese Nachdrücklichkeit.',
],
    [
    'ā · ī · ū · ō',
    ' — lange Vokale: langes a, i, u, o. Sie erscheinen nur in den eingedeutschten Fund- und Personennamen (z. B. Taymāʾ, al-ʿĪsāwī, Al-Mrōshan), nicht in den vokallosen Inschriften selbst.',
],
]

# REGISTERS: [ [Ziffer, Name, [ [Kopfzeile 'Fundort . Sigle', [Verszeilen...]], ... ]], ... ]
REGISTERS = [
    [
    'I',
    'stehe',
    [
    [
    'Km 612 · JaS 4',
    [
    'Von Msk, Sohn des Šdt,',
    'Sohn des Mḥlm, Sohn des Šdt,',
    'Sohn des Mḥlm,',
    'vom Stamm Tm.',
],
],
    [
    'Km 612 · JaS 5',
    [
    'Von Tm, Sohn des Mḥlm,',
    'Sohn des Šdt, Sohn des Mḥlm,',
    'vom Stamm Tm.',
],
],
    [
    'Km 612 · JaS 13',
    [
    'Von Gšm, Sohn des Smr,',
    'vom Stamm Bsʾ.',
    'Und er trauerte um Nḥṭ.',
],
],
    [
    'Km 612 · JaS 15',
    [
    'Von Ḥmr, Sohn des Bnġḍw,',
    'Sohn des Sfʾ, Sohn des Ḥnf.',
],
],
    [
    'Km 612 · JaS 21',
    [
    'Von Tʾl, Sohn des ʿz.',
    'Und er trauerte um den Vater.',
],
],
    [
    'Km 612 · JaS 22',
    [
    'Von Hnʾ, Sohn des Šnʾ,',
    'Sohn des Gmr, Sohn des Ḍʾ.',
],
],
    [
    'Hani · HCH 22',
    [
    'Von Tm, Sohn des Ḫlṣ,',
    'Sohn des Tm, Sohn des Šʿ.',
    'Und er trauerte um Hnʾ.',
],
],
    [
    'Hani · HCH 38',
    [
    'Von ʾsd, Sohn des Ẓn, Sohn des Ṯlm.',
    'Und er trauerte um Hnʾ.',
],
],
    [
    'Hani · HCH 99',
    [
    'Von ʿrb, Sohn des Hrs.',
    'Und er trauerte um Hnʾ.',
],
],
    [
    'Qāʿ Fahadah · AAEK 102',
    [
    'Von Dʾyt,',
    'Sohn des Mʿdʾl, Sohn des ʾḏnt,',
    'Sohn des Hsm, Sohn des Gḥšt,',
    'Sohn des Sdy, Sohn des Wṭy,',
    'Sohn des Byq, Sohn des Ngrt,',
    'Sohn des Qnfḏ.',
],
],
    [
    'Qāʿ Fahadah · AAEK 120',
    [
    'Von ʾzr, Sohn des Ftn,',
    'Sohn des Gṯ, Sohn des Šʿr,',
    'Sohn des Rḥmʾl,',
    'Sohn des Mrʾt, Sohn des Gryt.',
],
],
    [
    'Qāʿ Fahadah · ASFF 244',
    [
    'Von ʾzr, Sohn des Ftn,',
    'Sohn des Mṯn, Sohn des Šʿhm,',
    'Sohn des Rḥhl,',
    'Sohn des Mrʾt, Sohn des Gryt.',
],
],
    [
    'Qāʿ Fahadah · ASFF 390',
    [
    'Von Hnʾt, Sohn des Slmt,',
    'Sohn des Lḏn, Sohn des Skrn,',
    'Sohn des Ndbn, Sohn des Ṣrm.',
],
],
    [
    'Qāʿ Fahadah · ASFF 392',
    [
    'Von Kmn, Sohn des Slmt,',
    'Sohn des Lḏn, Sohn des Skrn,',
    'Sohn des Ndbn, Sohn des Ṣrm.',
],
],
],
],
    [
    'II',
    'ritze',
    [
    [
    'Wādī Salma · RWQ 187',
    [
    'Er war hier',
    'und sah den Löwen',
    'an der Nordseite.',
],
],
    [
    'Wādī Salma · RWQ 342',
    [
    'Hier.',
    'Und der Himmel regnete,',
    'nach langer Zeit ohne Regen.',
],
],
    [
    'al-ʿĪsāwī · Is.Mu 484',
    [
    'Von Nr, Sohn des Qdm —',
    'und er schrieb seinen Namen',
    'zum ersten Mal.',
],
],
    [
    'Jawa · SIJ 291',
    [
    'Von Šrk —',
    'und er schrieb für den Mutterbruder,',
    'und er schrieb für den wahren Freund.',
],
],
    [
    'Km 612 · JaS 16',
    [
    'Von Bnḥt.',
],
],
    [
    'Hani · HCH 31.1',
    [
    'Von ʿṭs.',
],
],
    [
    'Hani · HCH 75',
    [
    'Von ʿdy.',
],
],
    [
    'Hani · HCH 117',
    [
    'Von ʾnʿm.',
],
],
    [
    'Hani · HCH 156',
    [
    'Von Sḫr.',
],
],
    [
    'Hani · HCH 158.1',
    [
    'Von Gḥš.',
],
],
    [
    'Hani · HCH 158.2',
    [
    'Von Sʿd.',
],
],
    [
    'Hani · HCH 160',
    [
    'Von Gḥš.',
],
],
    [
    'Ḥarrat al-Raǧil · Rees 150',
    [
    'Von Slf.',
],
],
    [
    'Ḥarrat al-Raǧil · Rees 151',
    [
    'Von ʾḫwn.',
],
],
    [
    'Ḥarrat al-Raǧil · Rees 155',
    [
    'Von Šd.',
],
],
    [
    'Ḥarrat al-Raǧil · Rees 161 4',
    [
    'Von Hnb.',
],
],
    [
    'Ḥarrat al-Raǧil · Rees 176',
    [
    'Von Sdrt.',
],
],
],
],
    [
    'III',
    'harre',
    [
    [
    'Wādī Sārah · ASWS 73',
    [
    'Von Rbʾl, Sohn des Ḥnn, Sohn des Ẓʿn,',
    'Sohn des Ḫyḏ, Sohn des ʿḏr.',
    'Und er zog zum Wasser, der Dürre gewärtig —',
    'dann wieder im Wassermann, dann im Widder,',
    'dann in der Waage, dann abermals in der Waage,',
    'zwei Jahre in Folge —,',
    'und in dieser Zeit trauerte er vor Schmerz',
    'um einen, den er liebte,',
    'und um die Kamele, die er weidete,',
    'tief aus der Wüste hinausgezogen',
    'im Jahr, als Bnt starb.',
],
],
    [
    'Wādī Sārah · ASWS 183',
    [
    'Er war auf der Lauer',
    'nach dem Löwen.',
],
],
    [
    'Tall aḍ-Ḍabiʿ · RSIS 110',
    [
    'Er trauerte um den Vater',
    'und blieb an diesem Ort',
    'und hielt Ausschau nach den Brüdern.',
    'Sie fehlten ihm.',
    'Allat —',
    'Sicherheit und Fülle dem, der die Schrift achtet.',
],
],
    [
    'Tall aḍ-Ḍabiʿ · RSIS 322',
    [
    'Er hielt Wache,',
    'auf der Lauer nach dem Löwen.',
    'Allat — Schutz.',
],
],
    [
    'al-ʿĪsāwī · Is.Mu 255',
    [
    'Er hielt Ausschau',
    'nach der Geliebten.',
    'Yalt — Sicherheit.',
],
],
    [
    'Jathum · SIJ 14',
    [
    'Er hielt Ausschau',
    'nach dem Löwen.',
],
],
    [
    'Jathum · SIJ 30',
    [
    'Er wartete',
    'auf den Schnee',
    'über dem Hauran.',
],
],
    [
    'Rif Dimašq · LP 1196',
    [
    'Von Mswd, Sohn des Whbn,',
    'Sohn des Hrṯ, Sohn des Msk,',
    'Sohn des Qmr, Sohn des ʿwḏ,',
    'Sohn des Whbʾl —',
    'und er hielt Ausschau',
    'nach dem Reiterzug.',
    'Yalt —',
    'Sicherheit und Beute, dem Feind abgenommen.',
],
],
    [
    'Wādī Salma · AbSWS 15',
    [
    'Von Sʿd, Sohn des Ġyrʾl,',
    'Sohn des Skrn, Sohn des Zkr,',
    'Sohn des Ẓnʾl —',
    'und er hielt Ausschau.',
],
],
    [
    'Wādī Salma · RWQ 120',
    [
    'Er hielt Wache',
    'für seine Gefährten,',
    'während sie am beständigen Wasser lagerten,',
    'und trauerte um Yḥy.',
],
],
    [
    'Qāʿ al-Maḥfūr · CSNS 796',
    [
    'Er wartete',
    'auf den glückenden Raubzug.',
],
],
    [
    'Zalaf · C 2194',
    [
    'Er hielt Ausschau.',
    'Yalt — Beute, den Feinden abgenommen.',
],
],
    [
    'Zalaf · C 2753',
    [
    'Um die Männer im Späherposten',
    'trauerte er.',
],
],
    [
    'Zalaf · C 2756',
    [
    'Um die Männer im Späherposten',
    'trauerte er.',
],
],
    [
    'WH Cairn 7 · WH 175',
    [
    'Er zog tief in die Wüste',
    'und hielt Ausschau.',
],
],
    [
    'Tell 5 · KWQ 113',
    [
    'Er ging mit den Ziegen',
    'und hielt Ausschau.',
],
],
    [
    'EDS 80-5 · CEDS 226',
    [
    'Er hielt Ausschau',
    'nach den Pferden.',
],
],
    [
    'Jawa · SIJ 323',
    [
    'Er folgte den Kamelen',
    'und hielt Ausschau.',
],
],
    [
    'Al-Mafraq · GSSH 1',
    [
    'Er lag am Späherplatz,',
    'auf der Lauer nach Feinden ',
    'mit ihren Kamelen.',
],
],
],
],
    [
    'IV',
    'fehle',
    [
    [
    'Riǧm Qaʿqūl · C 1146',
    [
    'Von Nḏr, Sohn des ʾs,',
    'Sohn des Bḥṯ,',
    'und wg----',
],
],
    [
    'Riǧm Qaʿqūl · C 1312',
    [
    'Von Ḥḍg, Sohn des Swr ----.',
    'Und er hielt Wache ----',
],
],
    [
    'Riǧm Qaʿqūl · C 1368',
    [
    'Von Ḫlṣ ----,',
    'Sohn des Qdm,',
    'Sohn des ʾnʿm, Sohn des Rʿ,',
    'vom Stamm ----',
],
],
    [
    'Riǧm Qaʿqūl · RQ.A 5',
    [
    'Von Sʿd, Sohn des Gls, Sohn des Ṣʿd,',
    'Sohn des Mḥlm, Sohn des ʾnʿm, Sohn des Lʿṯmn.',
    'Und er trauerte um seinen Vater,',
    'und um einen, dessen Name fehlt,',
    'und um seine Schwester,',
    'und um eine, deren Name fehlt,',
    'und um ʾlṣqt,',
    'und um ʾnʿm,',
    'und um Ḥg, den er liebte,',
    'und um Rq, im Jahr des Qbr,',
    'und um Ġfr,',
    'und um ʿḥmn, der gefangen war, im Jahr des Qbr,',
    'und um Ṣḥrt,',
    'und um Gb,',
    'und um einen, dessen Name fehlt,',
    'und um Ṣrf.',
],
],
    [
    'Km 612 · JaS 23',
    [
    '----, Sohn des br,',
    'Sohn des ----,',
    'ʿbkz ----,',
    'vom Stamm ʿmn.',
],
],
    [
    'Hani · HCH 102',
    [
    'Er hielt Wache',
    'um den Bruder,',
    'der den Kamelen folgte.',
    'Allat und ----',
    'Šʿh ----',
],
],
    [
    'Hani · HCH 125',
    [
    'Von ʾšym, Sohn des Drʾl,',
    'Sohn des ʾšym, Sohn des Drʾl,',
    'Sohn des Ksṭ, Sohn des ʿbd …',
    'Sohn des Šrk —',
    'ḫrs ----ḫl----',
],
],
    [
    'Hani · HCH 151',
    [
    '----lkt,',
    'vom Stamm Fḍg.',
    'Und er trauerte um ----',
    'baute ----',
],
],
    [
    'Hani · HCH 157',
    [
    '----, Sohn des ʾslh,',
    'Sohn des Ytm,',
    '---- ʾsʾ',
],
],
    [
    'Hani · HCH 164',
    [
    'Von Ġṯ, Sohn des ʾḫ.',
    'Und er trauerte um den Bruder',
    '----',
],
],
    [
    'Hani · HCH 183',
    [
    'Von Sny, Sohn des Ḥwr,',
    'Sohn des N----lt,',
    'vom Stamm Fṣ----',
],
],
    [
    'Hani · HCH 184',
    [
    'Von ʿbs, Sohn des Šẓr,',
    'und q----ysr —',
    '----',
],
],
    [
    'bei Safawi · HCH 195',
    [
    'Von Wrs, Sohn des ʾglḥ,',
    'Sohn des Yslm, Sohn des ʾglḥ,',
    'Sohn des ʾsl ----.',
    'Und er wartete auf die Regen ----',
],
],
    [
    'Jathum · SIJ 10',
    [
    'Von Frʾ, Sohn des Frq.',
    'Und er hielt Wache ---- Feinde.',
    'Rudā — Errettung.',
],
],
    [
    'Ǧabal Says · C 12',
    [
    'Rudā — Beute ---- von Feinden ----,',
    'und dem, der ohne Milch darbt.',
    'Allat und Schaihaqaum ----',
],
],
    [
    'Fundort unbekannt · WH 1501.2',
    [
    'Ḥlb.',
    'Und er weinte vor Kummer.',
],
],
    [
    'Fundort unbekannt · WH 1867.1',
    [
    'Er weidete an jenem Ort',
    'in einem Jahr,',
    'dessen Name fehlt.',
],
],
],
],
    [
    'V',
    'bitte',
    [
    [
    'Al-Mafraq · BS 209',
    [
    'Allat, Baalschamin, Schaihaqaum —',
    'bringt ihm den Geliebten zurück.',
],
],
    [
    'Al-Mafraq · MKJS 80',
    [
    'Nasr —',
    'hilf dem, der liebt,',
    'und errette aus der Not.',
],
],
    [
    'Al-Suwaydā · LP 1267',
    [
    'Allat —',
    'schenk langes Leben',
    'dem Bruder Kʿmh.',
],
],
    [
    'al-ʿĪsāwī · Is.Mu 88',
    [
    'Der Winter brachte keinen Regen',
    'in dem Jahr, als Wdn floh.',
    'Baalschamin —',
    'nimm ihm Not und Ungewissheit.',
],
],
    [
    'Wādī Salma · AbSWS 42',
    [
    'Er blieb die Trockenzeit.',
    'Allat — Sicherheit.',
],
],
    [
    'Km 910 · WAMS 19.2',
    [
    'Er wartete auf das Schicksal.',
    'Rudā — errette ihn.',
],
],
    [
    'Ǧabal Says · C 64',
    [
    'Allat —',
    'Sicherheit.',
],
],
    [
    'Ǧabal Says · C 134',
    [
    'Rudā —',
    'schenk Errettung.',
],
],
    [
    'Rif Dimašq · C 218',
    [
    'Yaṯaʿ —',
    'nimm ihm dies Unheil.',
],
],
    [
    'Rif Dimašq · C 805',
    [
    'Allat —',
    'schenk Errettung.',
],
],
    [
    'Rif Dimašq · C 1086',
    [
    'Allat —',
    'Sicherheit.',
],
],
    [
    'Riǧm Qaʿqūl · C 1412',
    [
    'Allat —',
    'Sicherheit,',
    'Allat —',
],
],
    [
    'Khirbat al-Umbāšī · C 885',
    [
    'Rudā —',
    'Sicherheit.',
],
],
    [
    'Khirbat al-Hubayrīyah · C 898',
    [
    'Er weidete die Esel.',
    'Allat — Sicherheit.',
],
],
    [
    'Khirbat al-Hubayrīyah · C 907',
    [
    'Er war auf der Reise.',
    'Allat — Sicherheit.',
],
],
    [
    'Zalaf · C 1496',
    [
    'Rudā —',
    'hilf dem ʾlh,',
    'Sohn des Bdn.',
],
],
    [
    'Zalaf · C 1629',
    [
    'Yalt —',
    'Errettung vom Bösen',
    'in diesem Jahr.',
],
],
    [
    'Zalaf · C 1660',
    [
    'Allat —',
    'Sicherheit.',
],
],
],
],
    [
    'VI',
    'klage',
    [
    [
    'al-ʿĪsāwī · LP 540',
    [
    'Er trauerte um die Schwester',
    'und weinte um sie',
    'und baute ihr dieses Grab,',
    'im Jahr, als er floh',
    'vor Nmrt, dem Mann der Regierung,',
    'zum Stamm ʿwḏ.',
],
],
    [
    'Wādī Salma · KRS 17',
    [
    'Er fand die Schrift des Msk',
    'und weinte,',
    'und die Trauer legte sich über ihn.',
    'Er dachte an den Bruder, den sie fortführten,',
    'im Jahr des Kampfes des Mʿṣ,',
    'und trauerte um Rb, um Yʿly, um ----ḥ,',
    'und wurde schwer.',
],
],
    [
    'Site 12 · AbaNS 361',
    [
    'Er weinte vor Kummer',
    'um einen, den er liebte.',
],
],
    [
    'Al-Suwaydā · C 4273',
    [
    'Er trauerte um den Vater',
    'und um den Bruder, zu früh dahin,',
    'und um Ḫlṣ und um ʾtm.',
],
],
    [
    'Qāʿ al-Maḥfūr · CSNS 781',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'Site 13 · AbaNS 453',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'Cairn 9 · HaNSB 319',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'Cairn 9 · HaNSB 346',
    [
    'Er weinte vor Kummer',
    'um seinen Sohn Wlym.',
],
],
    [
    'Cairn 10 · HaNS 708',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'Jordanien (allg.) · HNSD 13',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'bei Ruwayshid · SIJ 1001',
    [
    'Sie weinten vor Kummer.',
],
],
    [
    'Tell al-ʿAbd · SIJ 811',
    [
    'Er weinte vor Kummer',
    'um ----Gh.',
],
],
    [
    'Wādī Sārah · SSWS 28',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'Ḥarrat al-Raǧil · C 5367',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'Fundort unbekannt · WH 1517',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'Fundort unbekannt · WH 2825',
    [
    'Er weinte vor Kummer.',
],
],
    [
    'Fundort unbekannt · WH 3029',
    [
    'Er weinte vor Kummer',
    'um Fly.',
],
],
    [
    'Fundort unbekannt · WH 3829',
    [
    'Er weinte vor Kummer.',
],
],
],
],
    [
    'VII',
    'fluche',
    [
    [
    'Zalaf · C 1845',
    [
    'Allat —',
    'blende, wer dies blind macht.',
],
],
    [
    'Zalaf · C 2551',
    [
    'Er erkannte eine weitere Ritzung —',
    'wer überlebt, verzweifelt. ',
    'Allat —',
    'Rache an dem, der die Tat beging,',
    'und blende, wer dies blind macht.',
],
],
    [
    'Zalaf · C 2775',
    [
    'Er trauerte vor Schmerz',
    'um Nr, um Ṣfwn, um Ksṭ,',
    'und war verstört um die Gefährten.',
    'Wer dies blind macht: erblinde.',
],
],
    [
    'Zalaf · C 3138',
    [
    'Rudā —',
    'blende, wer dies blind macht.',
],
],
    [
    'Zalaf · C 4803',
    [
    'Von ʾlwhb, Sohn des Zmr, Sohn des Ḏkr.',
    'Und er dachte an sein Lamm,',
    'das der Wolf geschlagen hatte.',
    'Baalschamin — gib Sicherheit,',
    'dass das Lagern leicht werde.',
    'Und wer diese Schrift blind macht, erblinde.',
    'Wer sie liest, lebe lang.',
],
],
    [
    'Tall aḍ-Ḍabiʿ · RSIS 132',
    [
    'Er trauerte um Ṣʿd.',
    'Allat —',
    'Blindheit dem, der die Schrift blind macht.',
],
],
    [
    'Tall aḍ-Ḍabiʿ · RSIS 351',
    [
    'Er gedachte des Ḍr',
    'und weinte um den Vater, um ʿbd, um den Vaterbruder,',
    'und verstörte sich über die,',
    'die zu Schaden kamen und verloren gingen.',
    'Und er überwinterte abermals in der Ḥarrah',
    'und lagerte an diesem Ort.',
    'Wer diese Schrift auslöscht:',
    'den befalle die Krätze,',
    'und man werfe ihn aus dem Grab.',
],
],
    [
    'Al-Mrōshan · LP 243',
    [
    'Er weinte, er trauerte',
    'um den Vater, den sie ermordeten.',
    'Lh — Blutrache!',
    'Er sehnte sich nach dem Vaterbruder',
    'und allen Gefährten.',
    'Wer dies blind macht: erblinde.',
],
],
    [
    'al-ʿĪsāwī · Is.Mu 242',
    [
    'Er trauerte um Mlk,',
    'um Ḫrg, um Gḥmn, um ʾys, um Ẓn.',
    'Allat und Duschara —',
    'Blutrache.',
    'Und blende, wer dies blind macht.',
],
],
    [
    'al-ʿĪsāwī · LP 308',
    [
    'Er trauerte um Mqm,',
    'um ʿqrb, um Sḫr,',
    'um Tmʾl, um Mqm, um Ḥml.',
    'Allat —',
    'Blindheit dem, der dies blind macht.',
],
],
    [
    'al-ʿĪsāwī · LP 461',
    [
    'Er trauerte um Mlk,',
    'um Ḫrg, um Gm, um ʾys, um Ẓn.',
    'Allat und Duschara —',
    'Blutrache!',
    'Und blende, wer dies blind macht.',
],
],
    [
    'Al-Mafraq · KRS 813',
    [
    'Er trauerte um Ṣʿd.',
    'Allat — blende, wer dies blind macht,',
    'und werfe ihn aus dem Grab.',
],
],
    [
    'Al-Mafraq · KRS 941',
    [
    'Er fand die Spuren des Ṣʿd,',
    'den das Schicksal bezwungen hatte, ',
    'und trauerte vor Schmerz —',
    'wer überlebt, verzweifelt.',
    'Allat —',
    'blende, wer die Schrift blind macht.',
],
],
    [
    'Al-Mafraq · KRS 2919',
    [
    'Rudā —',
    'blende, wer die Schrift blind macht.',
],
],
    [
    'Rif Dimašq · C 1087',
    [
    'Allat —',
    'Beute dem, der dies vorliest,',
    'Lähmung und schändliche Blindheit',
    'dem, der die Worte verletzt.',
],
],
    [
    'Al-Suwaydā · C 4439',
    [
    'Er kam zurück zum Wasser',
    'im Jahr, als die Römer Šmt erschlugen.',
    'Allat —',
    'Blindheit dem, der dies blind macht.',
],
],
    [
    'Ḥarrat al-Raǧil · C 5299',
    [
    'Rudā —',
    'blende, wer die Schrift blind macht.',
],
],
    [
    'Fundort unbekannt · WH 368',
    [
    'Diese Schrift.',
    'Allat —',
    'dem, der sie blind macht:',
    'Blindheit und Lähmung,',
    'Stummheit, Krätze und Räude.',
],
],
],
],
    [
    'VIII',
    'bezeuge',
    [
    [
    'Jordanien (allg.) · HSNS 1',
    [
    'Er zog tief in die Wüste',
    'im Jahr, als Agrippa starb.',
],
],
    [
    'Jordanien (allg.) · HSNS 5',
    [
    'Von Lbʾt, Sohn des Ḫṭst, Sohn des Flṭt,',
    'Sohn des Bhš, Sohn des ʾḏnt, Sohn des ʾslm,',
    'Sohn des Zkr, Sohn des Rfʾt, Sohn des Wšyt,',
    'Sohn des Ḍf, Sohn des ʿgd, Sohn des Tʿwḏ.',
    'Und er war an diesem Ort',
    'im Jahr, als Agrippa König war, der Sohn des Herodes,',
    'und er fand die Spuren seiner Mutterbrüder',
    'vom Stamm ʾšll —',
    'Tm und Grmʾ und ʾḥwḍ und Zbd —',
    'und trauerte vor Schmerz.',
    'Duschara und Allat:',
    'Beute dem, der die Schrift unversehrt lässt,',
    'Leid dem, der sie zerstört.',
],
],
    [
    'Rif Dimašq · C 4681',
    [
    'Er baute den kleinen Unterstand',
    'im Jahr, als die Sturzfluten',
    'in diese weite Senke kamen.',
    'Allat — Sicherheit;',
    'Blindheit dem, der dies blind macht.',
],
],
    [
    'Rif Dimašq · C 4902',
    [
    'Er war hier',
    'im Jahr des großen Regens',
    'und jagte auf flachem Land.',
],
],
    [
    'Rif Dimašq · LP 653',
    [
    'Er lagerte am beständigen Wasser',
    'im Jahr, als die Legionen des Germanicus bei Nqʾt standen.',
    'Und er trauerte:',
    'um Glḥn, erschlagen,',
    'um ʾbn, erschlagen,',
    'um Mʿz, erschlagen,',
    'um Mlk, erschlagen,',
    'um Nsm,',
    'und um Ṭr aus dem Stamm Smw.',
],
],
    [
    'Site 4 · ISB 57',
    [
    'Er trauerte um die Schwester',
    'und ritt zur Verfolgung aus,',
    'im Jahr des Königs Rabbel.',
],
],
    [
    'Al-Mrōshan · LP 254',
    [
    'Er lagerte am beständigen Wasser',
    'im Jahr, als der Stamm Qmr',
    'dem Stamm Ḥmy Schaden tat,',
    'und trauerte um Ġṯ,',
    'zu früh gestorben, vom Schicksal bezwungen.',
],
],
    [
    'Riǧm Qaʿqūl · RQ.D 3',
    [
    'Er trauerte um die Mutter,',
    'die getötet wurde,',
    'im Jahr des ʾrm.',
],
],
    [
    'Riǧm Qaʿqūl · RQ.D 6',
    [
    'Er trauerte vor Schmerz',
    'um den getöteten Šrk',
    'und den gefangenen ʿyḏ,',
    'im Jahr der Römer.',
],
],
    [
    'Syrien (allg.) · LP 1291',
    [
    'Er blieb die späten Regen in diesem Tal,',
    'im Jahr des Sturzbachs, ',
    'und kam mit seinen Kamelen heil davon.',
],
],
    [
    'Zalaf · C 2190',
    [
    'Er zog tief in die Wüste,',
    'im Jahr, als der Vaterbruder starb,',
    'und trauerte um Ksṭ.',
],
],
    [
    'al-ʿĪsāwī · Is.L 202',
    [
    'Er weidete auf dem Frühjahrsgras',
    'im Jahr von Taymāʾ.',
],
],
    [
    'Al-Mafraq · ASFF 267',
    [
    'Er kam zurück von Smwt',
    'im Jahr des Kampfes des Mʿṣ.',
],
],
    [
    'Al-Mafraq · KRS 1586',
    [
    'Der Unterstand gehört ʿzgd.',
    'Er kam ans Wasser',
    'im Jahr des ṣh.',
],
],
    [
    'Zimlet Nāṣir · ZN 1',
    [
    'Er trauerte um den Bruder,',
    'der getötet wurde,',
    'im Jahr des Qbr.',
],
],
    [
    'Wādī Salma · RWQ 304',
    [
    'Er nahm diesen Ort in Besitz',
    'im Jahr des ʾrzʾ.',
],
],
    [
    'Wādī Miqāṭ · BWM 3',
    [
    'Er war hier',
    'im Jahr, als Ḥrb und ʾlmn erschlagen wurden,',
    'und zog nach ʾnksr.',
],
],
],
],
]


# --------------------------------------------------------------------------
def main():
    xml = [title1(TITLE[0]), title2(TITLE[1]), title_spacer(), PAGEBREAK]
    xml += [body(p) for p in VORWORT]
    xml.append(EMPTY)

    total = 0
    for rom, name, entries in REGISTERS:
        xml.append(PAGEBREAK)
        xml += [roman(rom), regname(name)]
        for hdr, lines in entries:
            xml.append(header(hdr))
            xml += [line(l) for l in lines]
            total += 1

    xml.append(EMPTY)
    xml.append(PAGEBREAK)
    xml += [body(p) for p in NACHWORT_INTRO]
    xml.append(EMPTY)
    xml.append(bold_head(ERSTAUSGABEN_LABEL))
    xml += [listitem(a, b) for a, b in SIGLEN]
    xml.append(EMPTY)
    xml.append(subhead(FUNDORTE_HEAD))
    xml += [listitem(a, b) for a, b in FUNDORTE]
    xml.append(EMPTY)

    xml.append(subhead(ZEICHEN_HEAD))
    xml += [body(p) for p in ZEICHEN_INTRO]
    xml += [listitem(a, b) for a, b in ZEICHEN]
    xml.append(EMPTY)

    raw = zipfile.ZipFile(TEMPLATE).read("word/document.xml").decode("utf-8")
    decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    root_open = raw[raw.find("<w:document"):raw.find(">", raw.find("<w:document")) + 1]
    sect = raw[raw.find("<w:sectPr"):raw.find("</w:body>")]
    doc = decl + root_open + "<w:body>" + "".join(xml) + sect + "</w:body></w:document>"

    with zipfile.ZipFile(TEMPLATE) as zin:
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, dat in items:
            if info.filename == "word/document.xml":
                dat = doc.encode("utf-8")
            zout.writestr(info, dat)
    print(f"geschrieben: {OUT}  ({total} Stuecke, {len(REGISTERS)} Register)")


if __name__ == "__main__":
    main()
