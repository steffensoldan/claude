#!/usr/bin/env python3
"""
Baut den Register-Band in der Handfassung v5:
»Wer dies liest, lebe lang« — nomadische Inschriften des antiken Arabien.

Diese Fassung loest die aeltere v3/v4-Linie ab (siehe REGISTER_BAND_AUSWAHL.md):

  * Titelblatt zweizeilig (poetischer Titel + beschreibender Untertitel),
    kein grosser Haupttitel, keine Rock-Art-Abbildungen mehr.
  * Vorwort als Front-Matter VOR den Registern (frueher stand alles hinten).
  * Acht Register, umbenannt/umgestellt:
        I stehe . II ritze . III warte . IV bitte .
        V schweige . VI klage . VII fluche . VIII bezeuge
    (Register II hiess frueher "schreibe"; jetzt "ritze".)
  * Register I um die langen Ahnenreihen aus Qaa Fahadah (AAEK/ASFF) erweitert.
  * Nachwort hinten: Fliesstext + Sigle-Liste + Fundort-Liste als
    fettgesetzte Absaetze (frueher Tabellen).

Der komplette Textbestand steht als MODELL-Datenblock unten (aus der
handbearbeiteten v5 extrahiert). Nur word/document.xml wird neu geschrieben;
das uebrige Docx-Skelett (styles.xml mit Georgia-Default, Theme, sectPr mit
A4-Seitenformat) wird aus der bestehenden Register-v5 selbst uebernommen —
das Skript ist damit idempotent (mehrfaches Ausfuehren aendert nur den Text).
Die Datei muss also existieren; sie liegt versioniert im Repo.

Aufruf (aus Poetics/):
  python3 register/scripts/build_register.py

Ausgabe: register/wer_dies_liest_register_v5.docx
"""

import zipfile

# Skelett-Vorlage = die Register-v5 selbst (nur der Text-Body wird ersetzt).
TEMPLATE = "register/wer_dies_liest_register_v5.docx"
OUT      = "register/wer_dies_liest_register_v5.docx"

# --------------------------------------------------------------------------
# Format-Bausteine (entsprechen exakt der bereinigten Handfassung v5)
# --------------------------------------------------------------------------
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _run(t, rpr=""):
    return f'<w:r>{("<w:rPr>"+rpr+"</w:rPr>") if rpr else ""}<w:t xml:space="preserve">{esc(t)}</w:t></w:r>'

def _p(runs, ppr=""):
    return f'<w:p>{ppr}{runs}</w:p>'

PAGEBREAK = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
EMPTY     = '<w:p/>'

def titleline(t):   # zwei Titelzeilen: zentriert, 13 pt
    rpr = '<w:sz w:val="26"/><w:szCs w:val="26"/>'
    return _p(_run(t, rpr), f'<w:pPr><w:jc w:val="center"/><w:rPr>{rpr}</w:rPr></w:pPr>')

def title_spacer():
    rpr = '<w:sz w:val="26"/><w:szCs w:val="26"/>'
    return _p("", f'<w:pPr><w:jc w:val="center"/><w:rPr>{rpr}</w:rPr></w:pPr>')

def head(t):        # Vorwort / Nachwort, 15 pt fett
    return _p(_run(t, '<w:b/><w:sz w:val="30"/><w:szCs w:val="30"/>'))

def body(t):        # Fliesstext (Georgia 11 pt via Default)
    return _p(_run(t), '<w:pPr><w:spacing w:after="200" w:line="320" w:lineRule="auto"/></w:pPr>')

def roman(t):       # Register-Ziffer, 20 pt fett braun
    return _p(_run(t, '<w:b/><w:color w:val="7A5C3E"/><w:sz w:val="40"/><w:szCs w:val="40"/>'),
              '<w:pPr><w:spacing w:before="240"/></w:pPr>')

def regname(t):     # Register-Name (Ich-Verb), 15 pt fett
    return _p(_run(t, '<w:b/><w:sz w:val="30"/><w:szCs w:val="30"/>'),
              '<w:pPr><w:spacing w:after="40"/></w:pPr>')

def header(t):      # Fundort . Sigle als Kopfzeile, 8 pt braun
    return _p(_run(t, '<w:color w:val="7A5C3E"/><w:sz w:val="16"/><w:szCs w:val="16"/>'),
              '<w:pPr><w:spacing w:before="260" w:after="40"/></w:pPr>')

def line(t):        # Verszeile (Georgia 11 pt via Default)
    return _p(_run(t), '<w:pPr><w:spacing w:after="40"/></w:pPr>')

def subhead(t):     # "Die Fundorte", 12 pt fett
    return _p(_run(t, '<w:b/><w:sz w:val="24"/><w:szCs w:val="24"/>'),
              '<w:pPr><w:spacing w:before="200" w:after="80"/></w:pPr>')

def listitem(label, rest):   # Sigle-/Fundort-Eintrag: fette Marke + Erklaerung
    return _p(_run(label, '<w:b/>') + _run(rest),
              '<w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr>')

# --------------------------------------------------------------------------
# INHALT (aus der handbearbeiteten v5 extrahiert)
# --------------------------------------------------------------------------
TITLE = [
    '»Wer dies liest, lebe lang« — ',
    'nomadische Inschriften des antiken Arabien',
]

VORWORT = [
    'Der Band fasst antike Inschriften arabischer Nomaden. Beduinen ritzten sie zwischen dem ersten vor und dem vierten Jahrhundert nach Christus in den Basalt der Wüsten Harra und Ṣafā.',
    'Viele tausend Steine auf dem Gebiet des heutigen Syrien, Saudi-Arabien, Jordanien und Irak tragen Markierungen von Hirten, Händlern und Viehzüchtern, konservierten sie über zwei Jahrtausende und extreme Temperaturen hinweg. Ihr Reiz beruht auf wenig Handlung oder Drama, auf dem faktisch überlebten Schreiben.',
    'Die Autoren der in safaitischer Schrift verfassten Inschriften waren Mitglieder von Nomadengruppen. Meist Männer während alltäglicher Arbeiten abseits der zentralen Zeltlager – beim Hüten, Warten und Wachehalten. Safaitisch, Konsonantenschrift ohne Vokale, hinterlässt Mehrdeutiges, nur aus Kontexten zu erschließen. Erosion macht Zeichenfolgen manchmal unkenntlich. sichtbare Lücken einer Schädigung. Auch fehlende Namen artikulieren sich über ihre Leerstelle. Die Abhängigkeit vom Kontext lässt sich heute noch in den arabischen Schriftzeichen für Orte und Namen nachspüren.',
    'Zu einem kleinen Teil der Inschriften gehören Zeichnungen, eine Art antiker Graffiti, direkt in die Schrift integriert. Dieser Band ist auf die verdichtete Form der bloßen Schriftfirm aus, die den allermeisten Inschriften zueigen ist.',
    'Die Auswahl dieses Bandes umfasst 134 Inschriften und durchläuft acht Register verschiedener Akte: vom Stehen am Stein, über Wünsche, Flüche, hin zu Entzug und Zeugnis. Fundorte sind jeweils über den einzelnen Inschriften aufgeführt. Analyse, Sortierung der Inschriften wurde durch Claude Code erleichtert, wiederkehrende Formeln klassifiziert; die Zuordnung erfolgte per Hand, dem dominanten Sprechakt folgend.',
    'Der Band ist ein Experiment zwischen Epigraphik und Lyrik. Die acht Register erzeugen eine Grammatik der Handlungen, die Nomaden im Stein fixieren. Akte gegen das Verschwinden, für das Überleben des Geschriebenen. ',
    'Wer seinen Namen in Stein ritzt, ist durch das Schreiben, ein Existenzakt. Ankunft, Mangel, Hinterlassenschaft. Finde, danke, freue finden im gemeinsamen Lager statt, nicht außerhalb beim Schreiben.',
]

NACHWORT_INTRO = [
    'Sämtliche Textgrundlagen, Siglen und Ortsbestimmungen dieses Bandes beziehen sich auf den an der Universität Oxford entwickelte digitale Referenzkorpus für die epigraphischen Zeugnisse des antiken Nordarabiens  (OCIANA). Er erfasst, ediert und systematisiert zehntausende Inschriften – darunter das gesamte bekannte safaitische Korpus – und stellt die wissenschaftliche Nomenklatur, Lesarten sowie Geodaten bereit. Das System dient in diesem Band als philologische Datenbasis und Ausgangspunkt für die poetische Verdichtung und Reduktion.',
    'Die im Band verwendeten dreistelligen Buchstabencodes (z. B. KRS, HCH, WH) verweisen auf die wissenschaftlichen Standard-Editionen und historischen Entdecker-Korpora, in denen die Inschriften erstmals dokumentiert wurden. Sie dienen im Online Corpus of the Inscriptions of Ancient North Arabia (OCIANA) als eindeutige Identifikatoren:',
]

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

# REGISTERS: [ [Ziffer, Name, [ [Kopfzeile 'Fundort . Sigle', [Verszeilen...]], ... ]], ... ]
REGISTERS = [
    [
        'I',
        'stehe',
        [
            [
                'Km 612 · JaS 4',
                [
                    'Von Msk, Sohn des S²dt,',
                    'Sohn des Mḥlm, Sohn des S²dt,',
                    'Sohn des Mḥlm,',
                    'vom Stamm Tm.',
                ],
            ],
            [
                'Km 612 · JaS 5',
                [
                    'Von Tm, Sohn des Mḥlm,',
                    'Sohn des S²dt, Sohn des Mḥlm,',
                    'vom Stamm Tm.',
                ],
            ],
            [
                'Km 612 · JaS 13',
                [
                    'Von Gs²m, Sohn des S¹mr,',
                    'vom Stamm Bs¹ʾ.',
                    'Und er trauerte um Nḥṭ.',
                ],
            ],
            [
                'Km 612 · JaS 15',
                [
                    'Von Ḥmr, Sohn des Bnġdw,',
                    'Sohn des S¹fʾ, Sohn des Ḥnf.',
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
                    'Von Hnʾ, Sohn des S²nʾ,',
                    'Sohn des Gmr, Sohn des Ḍʾ.',
                ],
            ],
            [
                'Hani · HCH 22',
                [
                    'Von Tm, Sohn des Ḫlṣ,',
                    'Sohn des Tm, Sohn des S²ʿ.',
                    'Und er trauerte um Hnʾ.',
                ],
            ],
            [
                'Hani · HCH 38',
                [
                    'Von S¹ʿd, Sohn des Ẓn, Sohn des Ṯlm.',
                    'Und er trauerte um Hnʾ.',
                ],
            ],
            [
                'Hani · HCH 99',
                [
                    'Von ʿrb, Sohn des Hrs¹.',
                    'Und er trauerte um Hnʾ.',
                ],
            ],
            [
                'Qāʿ Fahadah · AAEK 102',
                [
                    'Von Dʾyt,',
                    'Sohn des Mʿdʾl, Sohn des ʾḏnt,',
                    'Sohn des Hs¹m, Sohn des Gḥs²t,',
                    'Sohn des S¹dy, Sohn des Wṭy,',
                    'Sohn des Byq, Sohn des Ngrt,',
                    'Sohn des Qnfḏ.',
                ],
            ],
            [
                'Qāʿ Fahadah · AAEK 120',
                [
                    'Von ʾzr, Sohn des Ftn,',
                    'Sohn des Gṯ, Sohn des S²ʿr,',
                    'Sohn des Rḥmʾl,',
                    'Sohn des Mrʾt, Sohn des Gryt.',
                ],
            ],
            [
                'Qāʿ Fahadah · ASFF 244',
                [
                    'Von ʾzr, Sohn des Ftn,',
                    'Sohn des Mṯn, Sohn des S²ʿhm,',
                    'Sohn des Rḥhl,',
                    'Sohn des Mrʾt, Sohn des Gryt.',
                ],
            ],
            [
                'Qāʿ Fahadah · ASFF 390',
                [
                    'Von Hnʾt, Sohn des S¹lmt,',
                    'Sohn des Lḏn, Sohn des S¹krn,',
                    'Sohn des Ndbn, Sohn des Ṣrm.',
                ],
            ],
            [
                'Qāʿ Fahadah · ASFF 392',
                [
                    'Von Kmn, Sohn des S¹lmt,',
                    'Sohn des Lḏn, Sohn des S¹krn,',
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
                    'Von S²rk —',
                    'und er schrieb für den Oheim,',
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
                    'Von ʿṭs¹.',
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
                    'Von S¹ḫr.',
                ],
            ],
            [
                'Hani · HCH 158.1',
                [
                    'Von Gḥs².',
                ],
            ],
            [
                'Hani · HCH 158.2',
                [
                    'Von S¹ʿd.',
                ],
            ],
            [
                'Hani · HCH 160',
                [
                    'Von Gḥs².',
                ],
            ],
            [
                'Ḥarrat al-Raǧil · Rees 150',
                [
                    'Von S¹lf.',
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
                    'Von S²d.',
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
                    'Von S¹drt.',
                ],
            ],
        ],
    ],
    [
        'III',
        'warte',
        [
            [
                'Wādī Sārah · ASWS 73',
                [
                    'Von Rbʾl, Sohn des Ḥnn, Sohn des Ẓ˥n,',
                    'Sohn des Ḫyḏ, Sohn des ˥ḏr.',
                    'Und er zog zum Wasser, der Dürre gewärtig —',
                    'dann wieder im Wassermann, dann im Widder,',
                    'dann in der Waage, dann abermals in der Waage,',
                    'zwei Jahre in Folge —,',
                    'und in dieser Zeit trauerte er vor Schmerz',
                    'um einen, den er liebte,',
                    'und um die Kamele, die er weidete,',
                    'hinausgezogen aus der inneren Wüste,',
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
                    'Er war an diesem Ort',
                    'und hielt Ausschau nach den Brüdern.',
                    'Sie fehlten ihm.',
                ],
            ],
            [
                'Tall aḍ-Ḍabiʿ · RSIS 322',
                [
                    'Er hielt Wache,',
                    'auf der Lauer nach dem Löwen.',
                ],
            ],
            [
                'al-ʿĪsāwī · Is.Mu 255',
                [
                    'Er hielt Ausschau',
                    'nach der Geliebten.',
                    'Jaʾlat — gib Sicherheit.',
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
                    'Von Ms¹wd, Sohn des Whbn,',
                    'Sohn des Hrṯ, Sohn des Ms¹k,',
                    'Sohn des Qmr, Sohn des ʿwḏ,',
                    'Sohn des Whbʾl —',
                    'und er hielt Ausschau',
                    'nach dem Reiterzug.',
                ],
            ],
            [
                'Wādī Salma · AbSWS 15',
                [
                    'Von S¹ʿd, Sohn des Ġyrʾl,',
                    'Sohn des S¹krn, Sohn des Zkr,',
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
                    'Yalt — Beute von den Feinden.',
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
                    'Er trauerte',
                    'um die Männer',
                    'im Späherposten.',
                ],
            ],
            [
                'WH Cairn 7 · WH 175',
                [
                    'Er zog in die innere Wüste',
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
                    'Er lag auf der Lauer',
                    'am Späherplatz,',
                    'nach Feinden mit Kamelen.',
                ],
            ],
        ],
    ],
    [
        'IV',
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
                    'und nimm die Not.',
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
                    'nimm ihm die Angst und das Nichtwissen.',
                ],
            ],
            [
                'Wādī Salma · AbSWS 42',
                [
                    'Er blieb die Trockenzeit.',
                    'Allat — gib Sicherheit.',
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
                    'gib Sicherheit.',
                ],
            ],
            [
                'Ǧabal Says · C 134',
                [
                    'Rudā —',
                    'schenk Befreiung.',
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
                    'dass er sicher sei.',
                ],
            ],
            [
                'Riǧm Qaʿqūl · C 1412',
                [
                    'Allat —',
                    'dass er sicher sei,',
                    'Allat —',
                ],
            ],
            [
                'Khirbat al-Umbāšī · C 885',
                [
                    'Rudā —',
                    'dass er sicher sei.',
                ],
            ],
            [
                'Khirbat al-Hubayrīyah · C 898',
                [
                    'Er weidete die Esel.',
                    'Allat — dass er sicher sei.',
                ],
            ],
            [
                'Khirbat al-Hubayrīyah · C 907',
                [
                    'Er war auf der Reise.',
                    'Allat — dass er sicher sei.',
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
                    'Entkommen vom Bösen',
                    'in diesem Jahr.',
                ],
            ],
            [
                'Zalaf · C 1660',
                [
                    'Allat —',
                    'dass er sicher sei.',
                ],
            ],
        ],
    ],
    [
        'V',
        'schweige',
        [
            [
                'Riǧm Qaʿqūl · C 1146',
                [
                    'Von Nḏr, Sohn des ʾs¹,',
                    'Sohn des Bḥṯ,',
                    'und wg----',
                ],
            ],
            [
                'Riǧm Qaʿqūl · C 1312',
                [
                    'Von Ḥḍg, Sohn des S¹wr ----.',
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
                    'Von S¹˥d, Sohn des Gls¹, Sohn des Ṣ˥d,',
                    'Sohn des Mḥlm, Sohn des ʾn˥m, Sohn des L˥ṯmn.',
                    'Und er trauerte um seinen Vater,',
                    'und um einen, dessen Name fehlt,',
                    'und um seine Schwester,',
                    'und um eine, deren Name fehlt,',
                    'und um ʾlṣqt,',
                    'und um ʾn˥m,',
                    'und um Ḥg, den er liebte,',
                    'und um Rq, im Jahr des Qbr,',
                    'und um Ġfr,',
                    'und um ˥ḥmn, der gefangen war, im Jahr des Qbr,',
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
                    'S²ʿh ----',
                ],
            ],
            [
                'Hani · HCH 125',
                [
                    'Von ʾs²ym, Sohn des Drʾl,',
                    'Sohn des ʾs²ym, Sohn des Drʾl,',
                    'Sohn des Ks¹t, Sohn des ʿbd …',
                    'Sohn des S²rk —',
                    'ḫrs¹ ----ḫl----',
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
                    '----, Sohn des ʾs¹lh,',
                    'Sohn des Ytm,',
                    '[----] ʾs¹ʾ',
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
                    'Von S¹ny, Sohn des Ḥwr,',
                    'Sohn des N----lt,',
                    'vom Stamm Fṣ----',
                ],
            ],
            [
                'Hani · HCH 184',
                [
                    'Von ʿbs¹, Sohn des S²ẓr,',
                    'und q----ys¹r —',
                    '----',
                ],
            ],
            [
                'bei Safawi · HCH 195',
                [
                    'Von Wrs¹, Sohn des ʾglḥ,',
                    'Sohn des Ys¹lm, Sohn des ʾglḥ,',
                    'Sohn des ʾs¹l ----.',
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
                    'Er weidete die MSTY',
                    'in einem Jahr,',
                    'dessen Name fehlt.',
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
                    'zum Stamm ˥wḏ.',
                ],
            ],
            [
                'Wādī Salma · KRS 17',
                [
                    'Er fand die Schrift des Ms¹k',
                    'und weinte,',
                    'und die Trauer legte sich über ihn.',
                    'Er dachte an den Bruder, den sie fortführten,',
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
                    'blende, wer dies auskratzt.',
                ],
            ],
            [
                'Zalaf · C 2551',
                [
                    'Er erkannte eine weitere der Ritzungen —',
                    'Verzweiflung denen, die bleiben.',
                    'Allat —',
                    'Rache an dem, der die Tat beging.',
                ],
            ],
            [
                'Zalaf · C 2775',
                [
                    'Er trauerte vor Schmerz',
                    'um Nr, um Ṣfwn, um Ks¹ṭ,',
                    'und war verstört um die Gefährten.',
                    'Wer dies auskratzt: erblinde.',
                ],
            ],
            [
                'Zalaf · C 3138',
                [
                    'Rudā —',
                    'blende, wer dies auskratzt.',
                ],
            ],
            [
                'Zalaf · C 4803',
                [
                    'Von ʾlwhb, Sohn des Zmr, Sohn des Ḍkr.',
                    'Und er dachte an sein Lamm,',
                    'das der Wolf geschlagen hatte.',
                    'B˥ls¹mn — gib Sicherheit,',
                    'dass das Lagern leicht werde.',
                    'Und wer diese Schrift austilgt: erblinde.',
                    'Wer diese Schrift liest: lebe lang.',
                ],
            ],
            [
                'Tall aḍ-Ḍabiʿ · RSIS 132',
                [
                    'Er trauerte um Ṣʿd.',
                    'Allat —',
                    'Blindheit dem, der die Schrift auskratzt.',
                ],
            ],
            [
                'Tall aḍ-Ḍabiʿ · RSIS 351',
                [
                    'Er gedachte des Ḍr',
                    'und weinte um den Vater, um ˥bd, um den Oheim,',
                    'und verstörte sich über die,',
                    'die zu Schaden kamen und verloren gingen.',
                    'Und er überwinterte abermals in der Ḥarrah',
                    'und lagerte an diesem Ort.',
                    'Wer diese Schrift austilgt:',
                    'den befalle die Krätze,',
                    'und man werfe ihn aus dem Grab.',
                ],
            ],
            [
                'Al-Mrōshan · LP 243',
                [
                    'Er weinte, er trauerte',
                    'um den Vater, den sie ermordeten.',
                    'Er sehnte sich nach dem Oheim',
                    'und allen Gefährten.',
                    'Wer dies austilgt: erblinde.',
                ],
            ],
            [
                'al-ʿĪsāwī · Is.Mu 242',
                [
                    'Er trauerte um Mlk,',
                    'um Ḫrg, um Gḥmn, um ʾys¹, um Ẓn.',
                    'Allat und Duschara —',
                    'Blutrache.',
                ],
            ],
            [
                'al-ʿĪsāwī · LP 308',
                [
                    'Er trauerte um Mqm,',
                    'um ʿqrb, um S¹ḫr,',
                    'um Tmʾl, um Mqm, um Ḥml.',
                    'Allat —',
                    'Blindheit dem, der dies auskratzt.',
                ],
            ],
            [
                'al-ʿĪsāwī · LP 461',
                [
                    'Er trauerte um Mlk,',
                    'um Ḫrg, um Gm, um ʾys¹, um Ẓn.',
                    'Allat und Duschara —',
                    'Blutrache!',
                    'Und blende, wer dies austilgt.',
                ],
            ],
            [
                'Al-Mafraq · KRS 813',
                [
                    'Er trauerte um Ṣʿd.',
                    'Allat — blende, wer dies auskratzt,',
                    'und werfe ihn aus dem Grab.',
                ],
            ],
            [
                'Al-Mafraq · KRS 941',
                [
                    'Er fand die Spuren des Ṣʿd',
                    'und trauerte vor Schmerz —',
                    'Verzweiflung denen, die bleiben.',
                    'Das Schicksal schlug ihn nieder.',
                ],
            ],
            [
                'Al-Mafraq · KRS 2919',
                [
                    'Rudā —',
                    'blende, wer die Schrift auskratzt.',
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
                    'im Jahr, als die Römer S²mt erschlugen.',
                    'Allat —',
                    'Blindheit dem, der dies auskratzt.',
                ],
            ],
            [
                'Ḥarrat al-Raǧil · C 5299',
                [
                    'Rudā —',
                    'blende, wer die Schrift auskratzt.',
                ],
            ],
            [
                'Fundort unbekannt · WH 368',
                [
                    'Diese Schrift.',
                    'Allat —',
                    'dem, der sie austilgt:',
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
                    'Er zog in die innere Wüste',
                    'im Jahr, als Agrippa starb.',
                ],
            ],
            [
                'Jordanien (allg.) · HSNS 5',
                [
                    'Von Lbʾt, Sohn des Ḫṭs¹t, Sohn des Flṭt,',
                    'Sohn des Bhs², Sohn des ʾḏnt, Sohn des ʾs¹lm,',
                    'Sohn des Zkr, Sohn des Rfʾt, Sohn des Ws²yt,',
                    'Sohn des Ḍf, Sohn des ˥gd, Sohn des T˥wḏ.',
                    'Und er war an diesem Ort',
                    'im Jahr, als Agrippa König war, der Sohn des Herodes,',
                    'und er fand die Spuren seiner Mutterbrüder',
                    'vom Stamm ʾs²ll —',
                    'Tm und Grmʾ und ʾḥwḍ und Zbd —',
                    'und trauerte vor Schmerz.',
                    'Ds²ry und Lt:',
                    'Beute dem, der die Schrift unversehrt lässt,',
                    'Leid dem, der sie zerstört.',
                ],
            ],
            [
                'Rif Dimašq · C 4681',
                [
                    'Er baute den kleinen Unterstand',
                    'im Jahr, als die Sturzfluten',
                    'in diese Raḥaba kamen.',
                    'Allat — Sicherheit;',
                    'Blindheit dem, der dies auskratzt.',
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
                    'im Jahr, als die Legionen des Grmnqṣ bei Nqʾt standen.',
                    'Und er trauerte:',
                    'um Glḥn, erschlagen,',
                    'um ʾbn, erschlagen,',
                    'um M˥z, erschlagen,',
                    'um Mlk, erschlagen,',
                    'um Ns¹m,',
                    'und um Ṭr aus dem Stamm S¹mw.',
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
                    'zu früh gestorben, vom Schicksal gebeugt.',
                ],
            ],
            [
                'Riǧm Qaʿqūl · RQ.D 3',
                [
                    'Er trauerte um den Oheim,',
                    'den sie erschlugen,',
                    'im Jahr des ʾrm.',
                ],
            ],
            [
                'Riǧm Qaʿqūl · RQ.D 6',
                [
                    'Er trauerte vor Schmerz',
                    'um den getöteten S²rk',
                    'und den gefangenen ʿyḏ,',
                    'im Jahr der Rm.',
                ],
            ],
            [
                'Syrien (allg.) · LP 1291',
                [
                    'Er blieb die späten Regen in diesem Tal,',
                    'im Jahr, als der Sturzbach',
                    'mit seinen Kamelen vorüberzog.',
                ],
            ],
            [
                'Zalaf · C 2190',
                [
                    'Er zog in die innere Wüste,',
                    'im Jahr, als der Oheim starb,',
                    'und trauerte um Ks¹ṭ.',
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
                    'Er kam zurück von S¹mwt',
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
                    'und zog nach ʾnks¹r.',
                ],
            ],
            [
                'Tall aḍ-Ḍabiʿ · RSIS 324',
                [
                    'Er weidete die Schafe',
                    'im Jahr des Krieges gegen die Juden.',
                ],
            ],
        ],
    ],
]


# --------------------------------------------------------------------------
def main():
    xml = [titleline(TITLE[0]), titleline(TITLE[1]), title_spacer(), PAGEBREAK]

    xml.append(head("Vorwort"))
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

    xml.append(PAGEBREAK)
    xml.append(head("Nachwort"))
    xml += [body(p) for p in NACHWORT_INTRO]
    xml += [listitem(a, b) for a, b in SIGLEN]
    xml.append(EMPTY)
    xml.append(subhead("Die Fundorte"))
    xml += [listitem(a, b) for a, b in FUNDORTE]
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
