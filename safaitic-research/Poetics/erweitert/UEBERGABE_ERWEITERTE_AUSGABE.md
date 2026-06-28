# ÜBERGABE — Erweiterte Ausgabe „Wer dies liest, lebe lang”

Stand: 2026-06-28 · Status: Drei Manuskript-Fassungen
- v1: `wer_dies_liest_lebe_lang_erweitert.docx` (22 S., Stand 2026-06-10)
- v2: `wer_dies_liest_lebe_lang_erweitert_v2.docx` (reduzierter Apparat — siehe Abschnitt 0)
- **v3: `wer_dies_liest_lebe_lang_erweitert_v3.docx`** (jedes Kapitel auf 15 Stücke — siehe Abschnitt 0a)

## 0a. Version 3 — Aufstockung auf 15 je Kapitel

Baut auf v2 auf. Jedes der 12 Kapitel wird auf **15 Stücke** gebracht (Band = 180).
Die 104 neuen Nachdichtungen stehen je Kapitel **in Reihenfolge ihrer Eignung**
(OCIANA-LiteraryScore absteigend) ans Kapitelende angehängt — so lässt sich von
hinten her kürzen, ohne die Spitze zu verlieren. Bei XII vor dem Schlussstein.

Materialdecke (Prüfung in `VORSCHLAG_15ER_AUSGABE.md`): 8 Kapitel tragen 15 ohne
Wiederholung; in 4 Kapiteln (Klage, Angst, Zeichen, Sehnsucht) wird gegen das
Kapitelende **bewusst Motiv-Wiederholung** in Kauf genommen (Litanei „weinte vor
Kummer“, „in Not“, „die Zeichnung des Löwen“) — als Reiz und als Kürzungsreserve.
Sehnsucht (X) ist um Querschnitt-Texte aus der größeren Narrativ-Tabelle ergänzt
(longing/love als Nebenmotiv), da das Eigenthema erschöpft war.

Stil der neuen Stücke wie der Bestand: Ich-Form, Genealogie getilgt, Lücken
geglättet, Gottesnamen eingedeutscht (Allat, Baalschamin, Schaihaqaum, Gad-ʿAud,
Rudā, Duschara), je eine „Sigle …“-Zeile darunter. Vorwort: Stückzahl von
„wenige Dutzend“ auf „gegen zweihundert“ angepasst.

Build: `scripts/build_v3.py` (direktes XML-Transform von v2; die Auswahl- und
Verstexte stehen als Datenblock im Skript). Offen: Lektorat der 104 neuen
Nachdichtungen gegen die OCIANA-Einträge; Endkürzung je Kapitel von hinten.

## 0. Version 2 — Änderungen gegenüber v1

Zweite Fassung mit zurückgenommenem redaktionellem Apparat. Inhalt der Nachdichtungen und Steine unverändert; geändert ist nur, was *um* die Texte herum steht. Fünf Eingriffe:

1. **Namens-Zwischenüberschriften entfernt.** Der fett gesetzte Schreibername am Kopf der Steine (S¹ḫr., N˥mn., ˥my., Mġyr., Ḥnn.) ist gestrichen. Die Steine mit getilgter Genealogie beginnen jetzt direkt mit der Erzählung; die beiden Toledot-Steine (RQ.A 5, HSNS 5) behalten ihre volle „Von … Sohn des …“-Kette.
2. **Poetische Kapitel-Untertitel entfernt.** Die gedeckten Zeilen unter jedem Kapitelnamen (z. B. „Heimkehr zur Tränke, quer durch die Wüste.“) sind gestrichen — Kapitel = Ziffer + Name.
3. **Quellenangabe unter jedem Gedicht, einheitlich „Sigle xy“.** Die Bezeichnungen „Quellsigle“ und der Kopf-Kicker „STEIN · …“ entfallen. Jedes Stück — Gedicht *und* Stein — trägt seine Quelle als schlichte Zeile „Sigle xy“ darunter (67 umbenannt, 9 neu unter den Steinen ergänzt).
4. **Echo aufgelöst.** Die Doppelung „verknapptes Gedicht + ganzer Stein nebeneinander“ funktionierte nicht. An den beiden Echo-Stellen steht jetzt nur noch der ganze Stein, die verknappte Fassung ist gestrichen: ASWS 73 (eröffnet Kap. VI), C 4803 (Schlussstein). Damit entfällt auch die verknappte C-4803-Fassung aus Kap. X.
5. **Wiederkehrende Schlussformeln entfernt.** Die drei zwischen die Kapitel gesetzten Refrain-Seiten („nach RSIS 110“, „nach Al-Namārah.H 61“, „nach C 2770“) sind gestrichen — sie waren nur nachgedichtet und stehen für kein konkretes Original. Fluch/Segen bleibt dort, wo er im Original eines Steins oder Gedichts tatsächlich vorkommt (RSIS 351, C 4803, LP 243 u. a.).

Mitgezogene Doku im Manuskript: Vorwort (Refrain-„Rad“-Satz neutralisiert), editorische Notiz (Echo-Absatz durch Schlussstein-Satz ersetzt; Satz zum „bloßen Namen als Kopf“ gestrichen; „sieben Steine am Kopf“ → „am Kopf der Abschnitte und am Schluss“), Glossar-Überschrift („Glossar der Quellsiglen“ → „Glossar der Siglen“), „Zu den Quellen“ (Quellsigle → Sigle).

Build: Direktes XML-Transform von v1 (`scripts/build_v2.py`), kein Neusatz — alle nicht berührten Absätze bleiben byte-genau. Der Abschnitt 3 (Echo-Konzept) und die Register-Tabelle in Abschnitt 2 beschreiben den Stand v1.

## 1. Konzeptentscheidung (ersetzt das alte Band-2-Konzept)

Kein separater Band 2. Befund: Die Längenfilterung (Erzählkern ≥ 25 W) reproduziert am oberen Ende die Band-1-Auswahl — 20 der 130 Pool-Texte stehen bereits in Band 1, darunter 9 der 26 Solitäre (Kern ≥ 40); die Doppler besetzen die Longlist-Ränge 1, 6, 7, 8, 9, 11, 12, 15, 22, 24. Ursache: Länge und literarische Dichte korrelieren an der Korpus-Spitze (emo 1,25 vs. 0,22 Mittel; scene 1,8 vs. 0,67). Stattdessen: **erweiterte Ausgabe von Band 1** mit zweitem Register.

## 2. Zwei Register

|           |Gedichte (Band-1-Bestand)      |Steine (neu)                                                                                              |
|-----------|-------------------------------|----------------------------------------------------------------------------------------------------------|
|Stimme     |Ich (Aneignung)                |Er (Dokument; Original: l-Fulān + 3. Person)                                                              |
|Genealogie |getilgt                        |getilgt, **bloßer Autorname als Kopf**; volle Kette nur RQ.A 5 + HSNS 5 + Echos                           |
|Lücken     |geglättet                      |in Sprache verwandelt („einer, dessen Name fehlt”; „Station um Station”) — nichts erfunden, Fehlen benannt|
|Fluch/Segen|als Refrain-Klammer            |behalten, wo im Original vorhanden                                                                        |
|Form       |verknappt                      |treue Langzeile                                                                                           |
|Auswahl    |Band-1-Score (mit Kürze-Prämie)|ZScore = Band-1-Gewichte **ohne** brevity/geneal_pen; Eintritt: Kern ≥ 25 W; nur Safaitisch               |

Begründung Er-Form: epigraphische Originalform; Registerunterschied wird hörbar (Ich vs. Er), nicht nur typografisch.

Genealogie-Ausnahmen (bewusst, „biblisches” Register — Toledot-Analogie):

- **RQ.A 5**: Ahnenkette (5) spiegelt Totenliste (14) — Namen in beide Zeitrichtungen.
- **HSNS 5**: 12 Generationen Tiefenzeit gegen ein datiertes Jahr (Agrippa/Herodes).
- **Echos** (zwingend): „der ganze Stein” ohne Kette wäre konzeptwidrig.

## 3. Platzierung der Steine (an den Abschnittsköpfen)

|Abschnitt           |Stein   |Register                                                                                |
|--------------------|--------|----------------------------------------------------------------------------------------|
|I Dürre & Lager     |RSIS 351|Winterklage, Grab-Fluch                                                                 |
|II Wege & Wasser    |KRS 900 |Spuren + Tränken-Itinerar                                                               |
|III Spähen & Warten |CEDS 230|Jahreslauf, Ausschau                                                                    |
|V Raub & Krieg      |LP 653  |Germanicus-Legionen, Totenliste (kuratorischer Override: Score unterschätzt wg. Lakunen)|
|VII Tod & Gewalt    |LP 540  |Grabbau, Flucht vor „Nmrt der Regierung”                                                |
|VIII Klage          |RQ.A 5  |Litanei, **mit Genealogie**                                                             |
|XII Das Jahr, in dem|HSNS 5  |Königsdatierung, **mit Genealogie**                                                     |

Echos (D-Element, genau 2):

- **VI**: ASWS 73 — Langfassung direkt nach der Band-1-Verknappung („Echo · derselbe Stein, ganz”).
- **Schluss**: C 4803 als **Schlussstein**, ersetzt die alte Schlussformel-Seite (Formel = letzte Zeilen des Steins; Titelquelle).

Reserve (nicht verbaut): TaNS 1 (V), C 2775 (VI), C 1156 (I), AWS 340 (III), LP 406 (I — Motivdopplung „Jahr, als Wdn floh” mit Is.Mu 88 beachten).

## 4. Manuskript-Aufbau

Titel (+ „Erweiterte Ausgabe · mit den Steinen”) → Vorwort (Original + 1 Überleitungsabsatz) → I–XII mit Steinen/Echo → Schlussstein → **Editorische Notiz** (Register, Er-Form, Genealogie-Politik, Echo, Lückenbehandlung, Auswahlmethodik) → **Glossar der Quellsiglen** → Zu den Quellen (Original + 1 Satz).

Typografie: einheitlich Georgia, **keine Kursive**; Kicker/Siglen in gedecktem Braun (#7A5C3E), Sperrsatz-Kicker.

## 5. Glossar — Verifikationsstand

Belegt (OCIANA/Literatur): C (CIS V, Ryckmans 1950) · LP (Littmann 1943) · WH (Winnett & Harding 1978) · KRS (G. King, Basalt Desert Rescue Survey 1989) · ISB (Oxtoby 1968) · HCH (Harding 1953) · CSNS (Clark 1979).
**Unverifiziert** (nur als Sigle gelistet, Nachweis via OCIANA-Eintrag): AAEK, AbaNS, Al-Namārah.H, AMSI, ASWS, AWS, BS, CEDS, HaNSB, HSNS, Is.Mu, KJB, KnGQ, MKJS, NSR, NST, RM.A, RQ.A, RR, RSIS, RWQ, SSWS, TaSTF. Nicht raten — bei Bedarf einzeln über OCIANA auflösen.

## 6. Offene Punkte

- [ ] Lektorat der 9 Stein-Nachdichtungen gegen OCIANA-EN (insb. LP 540 „Nmrt of the Government” — Deutung unsicher; RSIS 351 „nqʾt” Grab-Fluch-Lesart).
- [ ] Inhaltsverzeichnis ja/nein.
- [ ] Glossar-Restsiglen ggf. auflösen (OCIANA-Einzelabfrage).
- [ ] Druckbild: Blocksatz/Flattersatz der Notiz, Seitenzahlen, Recto-Start der Abschnitte.

## 7. Reproduzierbarkeit

- Pool-Filter + Tags: Kern-Regex wie `scripts/score.py` (führende Genealogie ab); Pool n=130 (Dedup 2487→2451). Tags heuristisch: datiert 54 · Fluch/Segen 40 · Litanei 26 · astronomisch 4 (Arbeitsliste: `safaitic_band2_pool_kern25.xlsx`).
- ZScore = 3·emo + 2,5·scene + 3·rarity + 1,5·meta + 1·anchor + 2·integrity + 1,5·clarity (= Gewichtungsblatt ohne brevity, ohne geneal_pen).
- Build: `build_band.js` (docx-js), Quelle Band-1-Absätze: `band1_paras.json` aus `safaitic_gedichtband.docx`.