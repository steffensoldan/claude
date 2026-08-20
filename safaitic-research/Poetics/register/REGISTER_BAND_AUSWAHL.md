# Register-Band — Auswahl aus dem Vollkorpus

Stand: 2026-08-19 · Konzept A: eigener Band nach Sprechakt-Registern · Ordner `register/` · **maßgebliche Fassung: Handfassung v6** (`wer_dies_liest_register_v6.docx`)

> **Fassungsgeschichte kurz:** v1–v4 (generierte Linie, siehe „Historie" unten) → **v5** eine vom Autor händisch überarbeitete Fassung, die die v3/v4-Linie ablöste → **v6** eine weitere Handfassung mit Übersetzungs-Feinschliff, geänderter Registerfolge und neu gefasstem Vor-/Nachwort. `scripts/build_register.py` ist **auf v6 nachgezogen**: es bettet den kompletten v6-Textbestand als Datenblock ein und schreibt daraus `word/document.xml` neu; das Docx-Skelett (Georgia-styles, `sectPr`) stammt aus der bestehenden v6 selbst. Idempotent. Die committete v6-docx ist die **Skript-Ausgabe** (saubere Einzel-Runs, zwei Vorwort-Tippfehler korrigiert) — inhaltsgleich zur Handfassung des Autors.

## Idee

Nicht der Jahresbogen der erweiterten Ausgabe, sondern die **Sprechhaltung** ordnet: jedes Register ein anderer Akt am Stein (Searles Illokutionsklassen, eigene Prägungen). Jedes Register ist gezielt aus dem Vollkorpus gespeist — darum tragen alle acht.

## Was v6 gegenüber v5 ändert

**Registernamen & -folge:**
- **III „warte" → „harre"** (näher an der Ausschau-/Wart-Haltung der Stücke).
- **V „schweige" → „fehle"** — und **an Position IV gerückt**; „bitte" wandert auf **V**. Neue Folge: **I stehe · II ritze · III harre · IV fehle · V bitte · VI klage · VII fluche · VIII bezeuge**. Der Akt der Leerstelle bleibt damit in der Mitte des Bandes.

**Auswahl:** **RSIS 324** („im Jahr des Krieges gegen die Juden") entfernt → **138 Stücke** (Vorwort-Zahl entsprechend auf 138 angeglichen).

**Vorwort & Nachwort** neu gefasst: Vorwort in acht nummerierten Absätzen; Nachwort mit überarbeitetem OCIANA-Absatz und Zwischentitel „Die Erstausgaben". Titelzeile ohne Guillemets (»«), Untertitel „…**im** antiken Arabien".

**Übersetzungs-Feinschliff** (im Chat einzeln gegen die OCIANA-Editionen geprüft):
- **VII fluche — Wortspiel `ʿwr`:** das defacierende Verb ist im Original durchweg `ʿwr` „blenden", identisch mit der Strafe. Statt „auskratzt/austilgt" nun **„blind macht"** an 14 Stellen → „blende/Blindheit … blind macht" bildet das Talions-Wortspiel des Steins nach. **RSIS 351** trägt stattdessen **„auslöscht"** — dort ist die Strafe Krätze/Grab (keine Blindheit), also kein Blind-Wortspiel.
- **LP 653: `Grmnqṣ` → „Germanicus"** (der röm. Feldherr; datiert ~18–19 n. Chr.).
- **„innere Wüste" → „tief in die Wüste"** (4×; `ʾs²rq`, geografisch, nicht seelisch).
- **MSTY → „an jenem Ort"** (unübersetzbares `h-ms¹ty` neutralisiert); **Raḥaba → „weite Senke"**.
- **C 2194** „Beute, den Feinden abgenommen" · **Is.Mu 88** „Not und Ungewissheit" (statt „Angst/Nichtwissen") · **C 1629** „Errettung vom Bösen" (statt „Entkommen") · **LP 254** „vom Schicksal bezwungen" (statt „gebeugt") · **GSSH 1** „mit ihren Kamelen" · **LP 1291** „kam mit seinen Kamelen heil davon" (Bezug geklärt) · **C 2753/2756** wortgleich angeglichen · **KRS 941** „den das Schicksal bezwungen hatte" (Bezug auf den Toten) + „wer überlebt, verzweifelt".
- **HCH 157:** das einzelne `[----]` zu bloßem `----` vereinheitlicht (keine eckigen Klammern mehr im Band).

## Aufbau

Titelblatt (2 Zeilen) → Vorwort → **acht Register** → Nachwort (Siglen + Fundorte) → **„Zur Aussprache"** (Sonderzeichen-Übersicht mit Aussprachehilfe, ganz am Bandende).

**Kapitelüberschriften** = Verb in der Ich-Form (das einzige Ich im Band), infinit-mehrdeutig (zugleich 1. Ps. Präsens, 3. Ps. Konjunktiv, Imperativ, teils Nomen):

**I stehe · II ritze · III harre · IV fehle · V bitte · VI klage · VII fluche · VIII bezeuge.**

„fehle" (die Leerstelle/das Verstummen) steht bewusst zentral (IV), damit der Band nicht auf das Fehlen zuläuft. Jeder Eintrag: Kopfzeile **„Fundort · Sigle"** (8 pt braun) über Verszeilen (Georgia 11 pt). Genealogien bleiben, wo sie der Akt sind (I „stehe"; IV „fehle"); sonst getilgt. Lücken (`----`) bleiben in IV offen.

## Die 138 Stücke je Register

**I stehe** (14) — Ahnenreihen, das Dasein als Akt:
JaS 4, JaS 5, JaS 13, JaS 15, JaS 21, JaS 22, HCH 22, HCH 38, HCH 99, AAEK 102, AAEK 120, ASFF 244, ASFF 390, ASFF 392.

**II ritze** (17) — der Schreibakt selbst, dann reine Signaturen:
RWQ 187, RWQ 342, Is.Mu 484, SIJ 291, JaS 16, HCH 31.1, HCH 75, HCH 117, HCH 156, HCH 158.1, HCH 158.2, HCH 160, Rees 150, Rees 151, Rees 155, Rees 161 4, Rees 176.

**III harre** (19) — Ausschau, Sehnsucht, im Stein konserviert:
ASWS 73, ASWS 183, RSIS 110, RSIS 322, Is.Mu 255, SIJ 14, SIJ 30, LP 1196, AbSWS 15, RWQ 120, CSNS 796, C 2194, C 2753, C 2756, WH 175, KWQ 113, CEDS 226, SIJ 323, GSSH 1.

**IV fehle** (17) — Lücken, getilgte Namen, Abbruch:
C 1146, C 1312, C 1368, RQ.A 5, JaS 23, HCH 102, HCH 125, HCH 151, HCH 157, HCH 164, HCH 183, HCH 184, HCH 195, SIJ 10, C 12, WH 1501.2, WH 1867.1.

**V bitte** (18) — das Gebet, das im Stein steht:
BS 209, MKJS 80, LP 1267, Is.Mu 88, AbSWS 42, WAMS 19.2, C 64, C 134, C 218, C 805, C 1086, C 1412, C 885, C 898, C 907, C 1496, C 1629, C 1660.

**VI klage** (18) — die Trauer als Denkmal:
LP 540, KRS 17, AbaNS 361, C 4273, CSNS 781, AbaNS 453, HaNSB 319, HaNSB 346, HaNS 708, HNSD 13, SIJ 1001, SIJ 811, SSWS 28, C 5367, WH 1517, WH 2825, WH 3029, WH 3829.

**VII fluche** (18) — der Fluch, der nie endet:
C 1845, C 2551, C 2775, C 3138, C 4803, RSIS 132, RSIS 351, LP 243, Is.Mu 242, LP 308, LP 461, KRS 813, KRS 941, KRS 2919, C 1087, C 4439, C 5299, WH 368.

**VIII bezeuge** (17) — Datierung als Akt, Zeugnis für Fremde:
HSNS 1, HSNS 5, C 4681, C 4902, LP 653, ISB 57, LP 254, RQ.D 3, RQ.D 6, LP 1291, C 2190, Is.L 202, ASFF 267, KRS 1586, ZN 1, RWQ 304, BWM 3.

## Reproduktion (Skript = v6)

```bash
# aus Poetics/
python3 register/scripts/build_register.py
# -> register/wer_dies_liest_register_v6.docx  (138 Stücke, 8 Register)
```

Das Skript enthält den v6-Textbestand als Datenblock (`TITLE`, `VORWORT`, `REGISTERS`, `NACHWORT_INTRO`, `ERSTAUSGABEN_LABEL`, `SIGLEN`, `FUNDORTE_HEAD`, `FUNDORTE`, `ZEICHEN_HEAD`, `ZEICHEN_INTRO`, `ZEICHEN`) und die Format-Bausteine (Titelzeile 13 pt zentriert, Zeile 1 **kursiv** · Register-Ziffer 20 pt braun · Register-Name 15 pt · Kopfzeile 8 pt braun · Verszeile 11 pt · Nachwort-Listeneintrag „**Marke**: Text" · „Die Fundorte" 12 pt fett). Es ersetzt nur `word/document.xml`; alles Übrige stammt aus der vorhandenen v6. **Textänderungen erfolgen im Datenblock** (dann neu bauen), Formatänderungen in den Bausteinfunktionen.

### Leseform der Transliteration

Die Leseform (`˥`→`ʿ`, `s¹`→`s`, `s²`→`š`) ist im v6-Datenblock **bereits angewandt** — der Datenblock hält also die Lesefassung, nicht mehr die philologische Rohform. Die Ersetzungsregeln und die Rohform (`s¹`/`s²`/`˥` samt der Funktion `readable()`) sind im **v5-Stand des Skripts** (Git-Historie) erhalten:

| von | nach | Begründung |
|---|---|---|
| `˥` (U+02E5) | `ʿ` | Vereinheitlichung — `˥` war durchgängig ein verunglücktes `ʿ` (dieselben Namen in beiden Schreibungen: `S¹˥d`/`S¹ʿd`). Fehlerbereinigung. |
| `s¹` | `s` | Auflösung der hochgestellten Ziffer (dezent). |
| `s²` | `š` | Auflösung als Einzelglyph statt „sch". |

Alle übrigen Diakritika (ṯ ḫ ḍ ṣ ṭ ẓ ġ ḥ) bleiben **bewusst unangetastet** — tragbares Mischsystem (`Šdt` neben `Mḥlm`).

## Offene Punkte / Feinschliff

- [x] **Zählung im Vorwort** stimmt mit dem Bandumfang überein (v6: **138**).
- [x] **Lektorat der neuen Stücke** gegen die OCIANA-Editionen (AAEK/ASFF-Reihen, RWQ 187/342, Is.Mu 484, SIJ 291, RWQ 120, RSIS 132, KRS 2919, C 1087, LP 254) — inhaltlich getreu.
- [x] **Einzel-Feinschliff** vieler Stücke gegen OCIANA (siehe „Was v6 ändert").
- [x] **Vorwort-Tippfehler** korrigiert („konservierten sie."; „beruht **nicht** auf Handlung … sondern auf …").
- [x] **Build-Skript auf v6 nachgezogen** (Registernamen/-folge, 138 Stücke, kursiver Titel, neue Nachwort-Struktur; committete v6 = Skript-Ausgabe).
- [x] **RSIS 351** auf „auslöscht" zurückgesetzt (dort keine Blind-Strafe, daher kein Wortspiel).
- [ ] Lektorat der übrigen (aus v3/v4 übernommenen) Nachdichtungen gegen OCIANA.
- [ ] Optional: Fundort-Anhang / Intra-Register-Clustering / echte Karte via OCIANA-Koordinaten.

---

## Historie (v1–v4)

Die generierte Linie vor den Handfassungen. Der detaillierte Stand samt Korpus-Ausgangsauswahl (14 Stimmen je Register mit englischen OCIANA-Glossen) und den Formfassungs-Iterationen ist in der Git-Historie dieses Dokuments erhalten; hier nur die Eckpunkte.

- **Konzept:** Ordnung nach acht Sprechakt-Registern, materiell aus dem Vollkorpus gespeist, ursprünglich überschneidungsfrei zur erweiterten Ausgabe (v5-Kopfstücke hoben das später auf). Datengrundlage: `neues-konzept/data/safaitic_full_corpus.xlsx`, `corpus-parser/…invocations`, `band1/data/…auswahl.xlsx`.
- **Formfassungen:** v1 Verszeilen + „Sigle …" am Fuß → v2 Fließtext + Kopfzeile → **v3** Verszeilen zurück, Kopfzeile „Fundort · Sigle", Register II als „Von X", „schweige" von VIII in die Mitte → **v4** = v3 + 7 eingebettete Felszeichnungen (`rockart_images/`, `ROCKART_UEBERSICHT.md`).
- **Kapiteltitel-Notiz** (Infinitiv minus „n", bewusst mehrdeutig/„infinit") und das *l-*-Argument („von / für / gehörig zu") stammen aus dieser Phase und leben in Vor-/Nachwort weiter.
- Das damalige Build-Skript baute die Kopfstücke faithful aus `erweitert/…_v5.docx` und trug die Rock-Art-Einbettung; die v5-Fassung des Skripts hat beides abgelöst.
