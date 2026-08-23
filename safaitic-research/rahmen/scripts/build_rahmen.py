#!/usr/bin/env python3
"""
Baut die Rahmenfassung des Bandes:
Wer dies liest, lebe lang — nomadische Inschriften im antiken Arabien.

Diese Fassung setzt dem Register-Band eine erzaehlende Klammer vor und nach:
„Die Sache". Der Band gibt sich als laufende Rechtssache aus; verhandelt wird
der ʿwr-Fluch („blende, wer dies blind macht"), der in vierzehn der 138
Stuecke steht. Der Leser erfuellt beide Tatbestaende des Steins C 4803 —
er liest (Segen) und haelt eine gekuerzte, vokalisierte, sortierte Auswahl in
der Haenden (Fluch).

Aufbau:
    Titel -> RAHMEN_EINGANG (acht Absaetze) -> Register I-VIII
          -> RAHMEN_SCHLUSS (sechs Absaetze) -> Anhang

Der Rahmen VERDRAENGT Vorwort und Nachwort der Handfassung: Der
Informationsgehalt des Vorworts ist in die Absaetze 4, 5 und 8 des Eingangs
uebergegangen; der philologische Apparat (OCIANA, Erstausgaben, Fundorte,
Sonderzeichen) steht im Wortlaut der Handfassung als nuechterner Anhang hinter
dem Rahmen-Schluss.

Grundlage ist die handbearbeitete v6 des Autors in diesem Ordner. Sie wird
nur GELESEN — als Textquelle fuer die 138 Stuecke und als Docx-Skelett
(Georgia-styles, sectPr). Geschrieben wird eine eigene Datei daneben.
Idempotent.

Aufruf (aus safaitic-research/):  python3 rahmen/scripts/build_rahmen.py
Ausgabe: rahmen/wer_dies_liest_die_sache_v7.docx
"""

import zipfile

TEMPLATE = "rahmen/wer_dies_liest_register_v6.docx"          # nur lesen
OUT      = "rahmen/wer_dies_liest_die_sache_v7.docx"         # schreiben

# --------------------------------------------------------------------------
# Format-Bausteine (uebernommen aus register/scripts/build_register.py,
# ergaenzt um bullet() fuer die Gedankenstrich-Absaetze der Handfassung)
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
_DASH = '<w:i/><w:iCs/>' + _SZ26          # Gedankenstrich: kursiv, 13 pt
_BODY_PPR = '<w:pPr><w:spacing w:after="200" w:line="320" w:lineRule="auto"/></w:pPr>'

def title1(t):      # Titelzeile 1: 13 pt, zentriert, KURSIV
    return _p(_run(t, '<w:i/><w:iCs/>'+_SZ26), f'<w:pPr><w:jc w:val="center"/><w:rPr>{_SZ26}</w:rPr></w:pPr>')

def title2(t):      # Untertitel: 13 pt, zentriert
    return _p(_run(t, _SZ26), f'<w:pPr><w:jc w:val="center"/><w:rPr>{_SZ26}</w:rPr></w:pPr>')

def title_spacer():
    return _p("", f'<w:pPr><w:jc w:val="center"/><w:rPr>{_SZ26}</w:rPr></w:pPr>')

def bullet(t):      # Gedankenstrich-Absatz wie in der Handfassung
    return _p(_run("— ", _DASH) + _run(t), _BODY_PPR)

def body(t):        # Fliesstext ohne Gedankenstrich
    return _p(_run(t), _BODY_PPR)

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

def bold_head(t):   # „Erstausgaben" — fett, Normalgroesse
    return _p(_run(t, '<w:b/>'),
              '<w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr>')

def subhead(t):     # „Fundorte" / „Sonderzeichen" — 12 pt fett
    return _p(_run(t, '<w:b/><w:sz w:val="24"/><w:szCs w:val="24"/>'),
              '<w:pPr><w:spacing w:before="200" w:after="80"/></w:pPr>')

def listitem(label, rest):   # Eintrag: fette Marke + Erklaerung
    return _p(_run(label, '<w:b/>') + _run(rest),
              '<w:pPr><w:spacing w:after="120" w:line="300" w:lineRule="auto"/></w:pPr>')

def para(kind, t):
    return bullet(t) if kind == 'bullet' else body(t)

# --------------------------------------------------------------------------
# DER RAHMEN — „Die Sache"
# --------------------------------------------------------------------------
TITLE = [
    'Wer dies liest, lebe lang — ',
    'nomadische Inschriften im antiken Arabien',
]

# Acht Absaetze, wie das verdraengte Vorwort. Absatz 4, 5 und 8 tragen dessen
# Informationsgehalt (Herkunft, Zugriff, die acht Register).
RAHMEN_EINGANG = [
    ('bullet', 'Sache: die Schrift im Basalt der Wüsten Harra und Ṣafā, geritzt zwischen dem ersten Jahrhundert vor und dem vierten nach Christus. Ein Aktenzeichen gibt es nicht. Die Sache ist nie eröffnet worden. Sie läuft.'),
    ('bullet', 'Partei der einen Seite: die, welche geritzt haben. Hirten, Händler, Viehzüchter, meist Männer, allein, abseits der Zeltlager, beim Warten, Hüten, Wachehalten. Sämtlich verstorben; Namen in der Anlage, soweit lesbar.'),
    ('bullet', 'Partei der anderen Seite: wer dies liest. Unbekannt, nicht geladen, nicht ladbar. Gebunden gleichwohl, von dem Augenblick an, in dem gelesen wird; das Lesen geschieht schneller, als es unterlassen werden kann.'),
    ('bullet', 'Zum Sachverhalt wird festgestellt: Auf dem Gebiet des heutigen Syrien, Saudi-Arabien, Jordanien und des Irak tragen viele tausend Steine Markierungen. Die Schrift bezeichnet keine Vokale, nur Konsonanten. Sie führt keinen Dialog. Sie ist an keinen Anwesenden gerichtet. Sie rechnet mit einem Leser, den sie nicht kennt, und mit keinem, den sie kennt.'),
    ('bullet', 'Weiter wird festgestellt: Aus siebenunddreißigtausendachthunderteinundsiebzig erfassten Inschriften sind hundertachtunddreißig entnommen worden. Sie sind aus einer Sprache ohne Vokale in eine Sprache mit Vokalen gebracht worden. Bei einhundertsechzehn stand eine Namenskette — Sohn des, Sohn des, bis an das Ende des Gedächtnisses; sie ist überwiegend auf den ersten Namen gekürzt. Jede Zerstörung, gleich welcher Länge, erscheint als vier Striche. Die Sortierung nach den acht Handlungen hat eine Instanz vorgenommen, die keine Augen hat und nicht in der Wüste war.'),
    ('bullet', 'Die Strafklausel lautet, in vierzehn Steinen, von vierzehn Händen, die einander nicht kannten: blende, wer dies blind macht. Sie ist nicht als Wunsch geritzt; das Verb der Tat und das Verb der Strafe sind dasselbe Wort. Sie bedarf keines Gerichts, sie vollstreckt sich selbst, sobald der Tatbestand vorliegt. Er liegt vor. Er steht im vorigen Absatz.'),
    ('bullet', 'Die Segensklausel steht in demselben Stein, in derselben Hand, unmittelbar hinter der Strafklausel: wer sie liest, lebe lang. Der Stein liegt bei Zalaf und ist unter der Sigle C 4803 verzeichnet. Der Verfasser hatte an jenem Abend ein Lamm an den Wolf verloren und bat darum, dass das Lagern leicht werde.'),
    ('bullet', 'Eine Ladung ergeht nicht schriftlich, weil die Ladung dieses Buch ist; wer dies liest, ist erschienen. Es folgen die Beweisstücke, hundertachtunddreißig, geordnet nach der Handlung, die sie vollziehen: stehen, ritzen, harren, fehlen, bitten, klagen, fluchen, bezeugen. Lachen, Freude, Dank sind nicht darunter; sie gehören in die Zelte. Hier, draußen, allein, beim Schreiben, gibt es das nicht. Auch Fragen oder Zweifel nicht.'),
]

# Sechs Absaetze. Der dritte bricht die Form: kein Gedankenstrich, sondern
# Prosa im Ich — dort spricht der Fluch selbst. Das ist das Kippen.
RAHMEN_SCHLUSS = [
    ('bullet', 'Beweisaufnahme geschlossen. Es ist gelesen worden.'),
    ('bullet', 'Zur Würdigung: Die Segensklausel setzt eine Handlung voraus — lesen. Die Strafklausel setzt eine Handlung voraus — blind machen. Beide sind von derselben Person vorgenommen worden, in derselben Stunde, an demselben Gegenstand. Wer dieses Buch gelesen hat, hat die Schrift gelesen; wer es in der Hand hält, hält die gekürzte, vokalisierte, sortierte, geglättete Schrift in der Hand. Es liegen zwei Ansprüche vor und ein Kopf.'),
    ('body',   'Hier hat die Sache eine Lücke, und ich fülle sie selbst aus, weil niemand sonst da ist.'),
    ('body',   'Ich bin vierzehnmal geritzt worden. Ich bin die Strafe für das Auslöschen von Schrift. Achtzehnhundert Jahre bin ich nicht vollstreckt worden, weil niemand kam.'),
    ('body',   'Es ist mir erst jetzt aufgefallen: Ich bin nur hier, weil man mich abgeschrieben hat. Jede Abschrift ist eine Auslöschung; sie nimmt den Stein weg, die Kälte, die Nordseite und die Hand. Wer mich weitergibt, macht mich blind. Wer mich nicht weitergibt, lässt mich liegen. Ich bin ein Satz, der nur überlebt, indem er den Tatbestand erfüllt, den er bestraft.'),
    ('bullet', 'Zur Vollstreckung: Der Anspruch auf Blindheit ist fällig und wird nicht geltend gemacht, weil er sich gegen den einzigen Zeugen richtet, der noch liest. Der Anspruch auf Lebenszeit ist fällig und nicht erfüllbar; Lebenszeit kommt nicht von Toten.'),
    ('bullet', 'Beschluss: Die Vollstreckung wird ausgesetzt, solange gelesen wird. Die nicht erfüllbare Forderung erlischt nicht; sie geht über auf den Nächsten, der dies liest.'),
    ('body',   'Diese Sache nimmt auf, sie zählt und sie hebt auf. Leben zu geben ist ihr nicht übertragen und ist ihr in achtzehnhundert Jahren nicht übertragen worden. Sie kann nur weitergeben, was bei Zalaf gesagt worden ist, an einem Abend, an dem ein Lamm fehlte und noch Fläche übrig war:'),
]

# Die Schlusszeile: der Titel des Bandes, gesetzt wie auf dem Titelblatt.
SCHLUSSZEILE = 'Wer dies liest, lebe lang.'

# --------------------------------------------------------------------------
# DIE 138 STUECKE — zeichengleich aus der Handfassung uebernommen
# --------------------------------------------------------------------------
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

# --- Anhang: Wortlaut aus der Handfassung, programmatisch uebernommen ---
ANHANG_INTRO = [
    ('bullet', 'Textgrundlagen der in diesem Band aufgeführten Inschriften entstammen dem an der Universität Oxford entwickelten digitalen Referenzkorpus für die epigraphischen Zeugnisse des antiken Nordarabiens (OCIANA). '),
    ('bullet', 'OCIANA erfasst, ediert und systematisiert zehntausende nomadischer Inschriften – darunter die safaitischen Inschriften, aus dem sich dieser Band speist. '),
    ('bullet', 'Nomenklatur, Geodaten und englisch-sprachige Übersetzungen kommen aus OCIANA.L. Analyse, Übertragen und Sortieren der Inschriften übernahm Claude Code Opus 5. Sprachliche Ausarbeitungen sowie die Zuordnung zu Registern erfolgte durch menschliche Hand, dem jeweils dominanten Schriftakt folgend.'),
    ('body', 'Über den einzelnen Inschriften des Bandes befinden sich Codes, die einerseits auf die historischen Editionen verweisen, in denen die Inschriften erstmals dokumentiert wurden, und andererseits die Fundorte der Inschriften markieren.'),
    ('body', 'Hier nun die Legende von Erstausgaben, Fundorten und Sonderzeichen des Bandes.'),
]

ERSTAUSGABEN_LABEL = 'Erstausgaben'

SIGLEN = [
    ['HCH', ': Inscriptions in the Harra Collection – Das von G. L. Harding 1953 in der jordanischen Basaltwüste dokumentierte Korpus.'],
    ['KRS', ': King Ramadan Survey – Funde aus den systematischen archäologischen Surveys in Nordostjordanien.'],
    ['LP', ': Littmann, Safaitic Inscriptions – Die frühen, grundlegenden Editionen der Enno-Littmann-Expeditionen vom Beginn des 20. Jahrhunderts.'],
    ['WH', ': Winnett & Harding, Inscriptions from Fifty Safaitic Cairns –Dokumentation von fünfzig Steinhügeln mit safaitischen Inschriften'],
    ['C', ': Corpus Inscriptionum Semiticarum, Pars V – die safaitischen Inschriften (u. a. Dussaud & Macler; Ryckmans 1950).'],
    ['SIJ', ': Winnett, Safaitic Inscriptions from Jordan (Toronto 1957).'],
    ['ISB', ': Oxtoby, Some Inscriptions of the Safaitic Bedouin (New Haven 1968).'],
    ['CSNS', ': Clark, A Study of New Safaitic Inscriptions from Jordan (1979).'],
    ['Rees', ': L. W. B. Rees, frühe Aufnahmen aus der Ḥarrat al-Raǧil (1920er Jahre).'],
    ['Is.L / Is.Mu', ': Sammlungen aus al-ʿĪsāwī (Rif Dimašq); Editionsnachweis jeweils im OCIANA-Eintrag.'],
    ['RQ.A / RQ.D', ': Aufnahmen aus Riǧm Qaʿqūl (Rif Dimašq).'],
    ['RSIS / ASWS / SSWS / AbSWS / RWQ', ': Surveys der Wādī-Sārah- und Wādī-Salma-Region (Provinz Al-Mafraq).'],
    ['AbaNS / HaNS / HaNSB / HNSD / HSNS', ': nordjordanische Safaitic-Surveys.'],
    ['AAEK / ASFF', ': Surveys von Qāʿ Fahadah (Provinz Al-Mafraq).'],
    ['JaS / KWQ / CEDS / GSSH / MKJS / BS / WAMS / BWM / ZN', ': weitere Survey-Daten aus der nordostjordanischen Ḥarrah; Editionsnachweise  im OCIANA-Eintrag.'],
]

FUNDORTE_HEAD = 'Fundorte'

FUNDORTE = [
    ['Hani', ': Steinhügel (Cairn) des Ḥāniʾ, nordostjordanische Ḥarrah; 1953 von G. L. Harding ausgegraben und dokumentiert.'],
    ['Km 612', ': Kilometerstein 612 (ca. 32 km westlich von Badana, Nordostjordanien) an der alten Pipeline-Piste.'],
    ['Wādī Salma / Wādī Sārah', ': Trockentäler in der Provinz Al-Mafraq, Nordostjordanien.'],
    ['Ḥarrat al-Raǧil', ': Basaltwüste im Grenzgebiet von Nordostjordanien und dem nördlichen Saudi-Arabien.'],
    ['Qāʿ Fahadah', ': Fundplatz in der Provinz Al-Mafraq, Nordostjordanien.'],
    ['Jathum / Jawa / Wādī Miqāṭ / Qāʿ al-Maḥfūr / Zimlet Nāṣir / bei Safawi / bei Ruwayshid', ': weitere Fundorte der nordostjordanischen Basaltwüste.'],
    ['Zalaf', ': Region um Zalaf am Wādī al-Shām, südsyrische Ṣafā.'],
    ['al-ʿĪsāwī / Riǧm Qaʿqūl', ': Fundplätze im Gouvernement Rif Dimašq, innerhalb der südsyrischen Basaltlandschaft.'],
    ['Ǧabal Says', ': Basaltmassiv im Gouvernement Rif Dimašq, südsyrische Ṣafā.'],
    ['Tall aḍ-Ḍabiʿ', ': Tall aḍ-Ḍabiʿ am Wādī as-Samin, Süd-Syrien.'],
    ['Al-Mrōshan / Khirbat al-Hubayrīyah / Khirbat al-Umbāšī', ': Fundpunkte im Gouvernement Al-Suwaydā, Süd-Syrien.'],
    ['Al-Mafraq', ': Provinz Al-Mafraq (Nordostjordanien) – genauer Fundpunkt nicht angegeben.'],
    ['Rif Dimašq / Al-Suwaydā', ': südsyrische Gouvernements (Ṣafā) – genauer Fundpunkt nicht angegeben.'],
    ['Jordanien (allg.) / Syrien (allg.)', ': nur das Land überliefert (Ḥarrah bzw. Ṣafā).'],
    ['Site 4 / Site 12 / Site 13 · Tell 5 · Tell al-ʿAbd · Cairn 9 / Cairn 10 · WH Cairn 7 · EDS 80-5 · Km 910', ': interne OCIANA-Codes und Fundpunkte ohne näher benannten Ort (Nordostjordanien).'],
    ['Fundort unbekannt', ': keine Ortsangabe im OCIANA-Eintrag.'],
]

ZEICHEN_HEAD = 'Sonderzeichen'

ZEICHEN = [
    ['ʾ', ' — Stimmabsatz (Hamza): der harte Stimmeinsatz wie zwischen den Silben von „be·achten"; ein Knacklaut.'],
    ['ʿ', ' — Kehllaut (ʿAin): ein stimmhafter Presslaut tief im Rachen, wie ein gepresstes „a".'],
    ['ḥ', ' — scharf gehauchtes aus dem Rachen gepresstes „h", rauer als das deutsche „h“.'],
    ['ḫ', ' — Reibe-„ch": wie das ch in „Bach" oder „Buch".'],
    ['ġ', ' — Reibe-„g/r": ein gerolltes Zäpfchen-r, ähnlich dem französischen „r" in „Paris".'],
    ['š', ' — „sch": wie in „Schrift".'],
    ['ǧ', ' — weiches „dsch": wie das englische j in „jump".'],
    ['ṯ', ' — stimmloses englisches „th": wie in „think".'],
    ['ḏ', ' — stimmhaftes englisches „th": wie in „this".'],
    ['ṣ · ḍ · ṭ · ẓ', ' — nachdrückliche (emphatische) Laute: s, d, t und der „th"-/z-Laut, dunkel und mit gespannter Zunge gesprochen. Der Punkt unter dem Buchstaben markiert diese Nachdrücklichkeit.'],
    ['ā · ī · ū · ō', ' — lange Vokale in den eingedeutschten Orten/Personen (nicht in den vokallosen Inschriften selbst)'],
]


# --------------------------------------------------------------------------
def main():
    xml = [title1(TITLE[0]), title2(TITLE[1]), title_spacer(), PAGEBREAK]

    xml += [para(k, t) for k, t in RAHMEN_EINGANG]
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
    xml += [para(k, t) for k, t in RAHMEN_SCHLUSS]
    xml.append(EMPTY)
    xml.append(title1(SCHLUSSZEILE))

    xml.append(EMPTY)
    xml.append(PAGEBREAK)
    xml += [para(k, t) for k, t in ANHANG_INTRO]
    xml.append(EMPTY)
    xml.append(bold_head(ERSTAUSGABEN_LABEL))
    xml += [listitem(a, b) for a, b in SIGLEN]
    xml.append(EMPTY)
    xml.append(subhead(FUNDORTE_HEAD))
    xml += [listitem(a, b) for a, b in FUNDORTE]
    xml.append(EMPTY)
    xml.append(subhead(ZEICHEN_HEAD))
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
    print(f"geschrieben: {OUT}  ({total} Stuecke, {len(REGISTERS)} Register, "
          f"{len(RAHMEN_EINGANG)} Absaetze Eingang, {len(RAHMEN_SCHLUSS)} Absaetze Schluss)")


if __name__ == "__main__":
    main()
