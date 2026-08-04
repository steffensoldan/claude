# Register-Band — Auswahl aus dem Vollkorpus

Stand: 2026-08-04 · Konzept A: eigener Band nach Sprechakt-Registern · Ordner `register/` · **maßgebliche Fassung: Handfassung v5** (`wer_dies_liest_register_v5.docx`) · reproduzierbar über `scripts/build_register.py`

> **Fassungsgeschichte kurz:** v1–v4 (generierte Linie, siehe „Historie" unten) → **v5** ist eine vom Autor **händisch überarbeitete** Fassung, die die v3/v4-Linie ablöst. Das Build-Skript ist auf v5 nachgezogen: es bettet den kompletten (aus der Handfassung extrahierten) Textbestand als Datenblock ein und schreibt daraus `word/document.xml` neu; das Docx-Skelett (Georgia-styles, Theme, A4-`sectPr`) übernimmt es aus der bestehenden v5 selbst. Das Skript ist **idempotent** (mehrfaches Ausführen erzeugt eine byte-identische Datei).

## Idee

Nicht der Jahresbogen der erweiterten Ausgabe, sondern die **Sprechhaltung** ordnet: jedes Register ein anderer Akt am Stein (Searles Illokutionsklassen, eigene Prägungen). Jedes Register ist gezielt aus dem Vollkorpus gespeist — darum tragen alle acht.

## Was v5 gegenüber v3/v4 ändert

- **Titelblatt zweizeilig, schlicht:** poetischer Titel »Wer dies liest, lebe lang« + beschreibender Untertitel „nomadische Inschriften des antiken Arabien" (beide Georgia 13 pt, zentriert). Der große Haupttitel „Antike safaitische Inschriften", die braune/graue Untertitel­kaskade und die Zeile „Acht Register · nach Sprechakten geordnet" entfallen.
- **Vorwort als Front-Matter** *vor* den Registern (in v3/v4 stand Einleitung + Nachwort zusammen hinten). Sieben Absätze über Wesen, Datierung, Region und Machart der Inschriften.
- **Register II umbenannt: „schreibe" → „ritze".** Und um vier ausdrucksstarke Kopfstücke erweitert (RWQ 187 „Er war hier und sah den Löwen", RWQ 342 „Hier. Und der Himmel regnete …", Is.Mu 484, SIJ 291), bevor die reinen „Von X"-Signaturen folgen.
- **Register I um Qāʿ Fahadah erweitert:** fünf lange Ahnenreihen (AAEK 102, AAEK 120, ASFF 244, ASFF 390, ASFF 392) neu.
- **Weitere neue Stimmen** verteilt (u. a. RWQ 120 in III; RSIS 132, KRS 2919, C 1087 in VII; LP 254 in VIII).
- **Keine Felszeichnungen mehr** — die 7 eingebetteten Rock-Art-Abbildungen der v4 sind entfallen (Band jetzt rein typografisch, ohne Bildrechte-Frage).
- **Nachwort** hinten: Fließtext + **Corpus-Siglen-Liste** + **Fundort-Liste** — jetzt als fettmarkierte Absätze („**Sigle**: Erklärung."), nicht mehr als Tabellen. Unterüberschrift „Die Fundorte" (12 pt fett) über der Fundort-Liste.

## Aufbau der v5

Titelblatt (2 Zeilen) → Vorwort → **acht Register** → Nachwort (Siglen + Fundorte).

**Kapitelüberschriften** = Verb in der Ich-Form (das einzige Ich im Band), infinit-mehrdeutig (zugleich 1. Ps. Präsens, 3. Ps. Konjunktiv, Imperativ, teils Nomen):

**I stehe · II ritze · III warte · IV bitte · V schweige · VI klage · VII fluche · VIII bezeuge.**

„schweige" steht bewusst in der **Mitte** (V), damit der Band nicht auf das Verstummen zuläuft. Jeder Eintrag: Kopfzeile **„Fundort · Sigle"** (8 pt braun) über Verszeilen (Georgia 11 pt). Genealogien bleiben, wo sie der Akt sind (I „stehe"; V „schweige"); sonst getilgt. Lücken (`----`) bleiben in V offen.

## Die 139 Stücke je Register

**I stehe** (14) — Ahnenreihen, das Dasein als Akt:
JaS 4, JaS 5, JaS 13, JaS 15, JaS 21, JaS 22, HCH 22, HCH 38, HCH 99, AAEK 102, AAEK 120, ASFF 244, ASFF 390, ASFF 392.

**II ritze** (17) — der Schreibakt selbst, dann reine Signaturen:
RWQ 187, RWQ 342, Is.Mu 484, SIJ 291, JaS 16, HCH 31.1, HCH 75, HCH 117, HCH 156, HCH 158.1, HCH 158.2, HCH 160, Rees 150, Rees 151, Rees 155, Rees 161 4, Rees 176.

**III warte** (19) — Ausschau, Sehnsucht, im Stein konserviert:
ASWS 73, ASWS 183, RSIS 110, RSIS 322, Is.Mu 255, SIJ 14, SIJ 30, LP 1196, AbSWS 15, RWQ 120, CSNS 796, C 2194, C 2753, C 2756, WH 175, KWQ 113, CEDS 226, SIJ 323, GSSH 1.

**IV bitte** (18) — das Gebet, das im Stein steht:
BS 209, MKJS 80, LP 1267, Is.Mu 88, AbSWS 42, WAMS 19.2, C 64, C 134, C 218, C 805, C 1086, C 1412, C 885, C 898, C 907, C 1496, C 1629, C 1660.

**V schweige** (17) — Lücken, getilgte Namen, Abbruch:
C 1146, C 1312, C 1368, RQ.A 5, JaS 23, HCH 102, HCH 125, HCH 151, HCH 157, HCH 164, HCH 183, HCH 184, HCH 195, SIJ 10, C 12, WH 1501.2, WH 1867.1.

**VI klage** (18) — die Trauer als Denkmal:
LP 540, KRS 17, AbaNS 361, C 4273, CSNS 781, AbaNS 453, HaNSB 319, HaNSB 346, HaNS 708, HNSD 13, SIJ 1001, SIJ 811, SSWS 28, C 5367, WH 1517, WH 2825, WH 3029, WH 3829.

**VII fluche** (18) — der Fluch, der nie endet:
C 1845, C 2551, C 2775, C 3138, C 4803, RSIS 132, RSIS 351, LP 243, Is.Mu 242, LP 308, LP 461, KRS 813, KRS 941, KRS 2919, C 1087, C 4439, C 5299, WH 368.

**VIII bezeuge** (18) — Datierung als Akt, Zeugnis für Fremde:
HSNS 1, HSNS 5, C 4681, C 4902, LP 653, ISB 57, LP 254, RQ.D 3, RQ.D 6, LP 1291, C 2190, Is.L 202, ASFF 267, KRS 1586, ZN 1, RWQ 304, BWM 3, RSIS 324.

## Reproduktion

```bash
# aus Poetics/
python3 register/scripts/build_register.py
# -> register/wer_dies_liest_register_v5.docx  (139 Stücke, 8 Register)
```

Das Skript enthält den vollständigen Textbestand als Datenblock (`TITLE`, `VORWORT`, `REGISTERS`, `NACHWORT_INTRO`, `SIGLEN`, `FUNDORTE`) und die Format-Bausteine (Titelzeile 13 pt zentriert · Register-Ziffer 20 pt braun · Register-Name 15 pt · Kopfzeile 8 pt braun · Verszeile 11 pt · Nachwort-Listeneintrag „**Marke**: Text"). Es ersetzt nur `word/document.xml`; alles Übrige (styles.xml, Theme, `sectPr`) stammt aus der vorhandenen v5. **Textänderungen erfolgen im Datenblock des Skripts** (dann neu bauen), Formatänderungen in den Bausteinfunktionen.

### Leseform der Transliteration (`readable()` / `READABLE`)

Der Datenblock hält die **exakte philologische Transliteration** (OCIANA: s-Sibilanten als `s¹`/`s²`, Diakritika). Für bessere Lesbarkeit nimmt das Skript beim Bau drei minimale Ersetzungen vor — **still, ohne Erklärung im Vor- oder Nachwort**:

| von | nach | Begründung |
|---|---|---|
| `˥` (U+02E5) | `ʿ` | Vereinheitlichung — `˥` ist durchgängig ein verunglücktes `ʿ`; dieselben Namen standen im Korpus in beiden Schreibungen (`S¹˥d`/`S¹ʿd`, `ʾn˥m`/`ʾnʿm`). Reine Fehlerbereinigung (14 Stellen). |
| `s¹` | `s` | Auflösung der hochgestellten Ziffer (dezent). |
| `s²` | `š` | Auflösung als Einzelglyph statt „sch" — fügt sich ins übrige Diakritika-Bild ein. |

Alle übrigen Diakritika (ṯ ḫ ḍ ṣ ṭ ẓ ġ ḥ) bleiben **bewusst unangetastet** — es entsteht ein tragbares Mischsystem (`Šdt` neben `Mḥlm`, `Ḫlṣ`). Einzige s-Kollision: `Ms¹k`→`Msk` fällt mit dem schon ziffernlosen `Msk` zusammen (dieselbe Person, kein Verlust). Der Transform steckt in der Funktion `readable()`; `READABLE = False` liefert die rein wissenschaftliche Fassung. Die Datenquelle bleibt unverändert — die Leseform ist jederzeit umkehrbar.

## Offene Punkte / Feinschliff

- [x] **Zählung im Vorwort** auf **139** angeglichen.
- [x] **Lektorat der neuen v5-Stücke** gegen die OCIANA-Editionen (Vollkorpus `neues-konzept/data/safaitic_full_corpus.xlsx`, Spalte *Full Translation*): AAEK 102/120, ASFF 244/390/392, RWQ 187/342, Is.Mu 484, SIJ 291, RWQ 120, RSIS 132, KRS 2919, C 1087, LP 254 — **alle 14 inhaltlich getreu** (Namen, Reihenfolge, Sprechakt korrekt; Genealogien registerkonform getilgt bzw. in „stehe" vollständig). Zwei Randnotizen: bei **Is.Mu 484** ist die Ahnenkette auf eine Generation gekürzt und die OCIANA-Lesungsunsicherheit `[?]` (bei „schrieb seinen Namen zum ersten Mal") nicht markiert — beides registerkonform, kein Fehler.
- [ ] Lektorat der übrigen (aus v3/v4 übernommenen) Nachdichtungen gegen OCIANA steht noch aus.
- [ ] Optional: Fundort-Anhang / Intra-Register-Clustering / echte Karte via OCIANA-Koordinaten.
- [ ] Falls die Felszeichnungen zurück sollen: Bild-Einbettung aus der v4-Historie (Skript-Stand `af27eff`) reaktivieren; Bildrechte klären.

---

## Historie (v1–v4)

Die generierte Linie vor der Handfassung. Der detaillierte Stand samt Korpus-Ausgangsauswahl (14 Stimmen je Register mit englischen OCIANA-Glossen) und den Formfassungs-Iterationen ist in der Git-Historie dieses Dokuments erhalten; hier nur die Eckpunkte.

- **Konzept:** Ordnung nach acht Sprechakt-Registern, materiell aus dem Vollkorpus gespeist, ursprünglich überschneidungsfrei zur erweiterten Ausgabe (v5-Kopfstücke hoben das später auf). Datengrundlage: `neues-konzept/data/safaitic_full_corpus.xlsx` (I + V/„schweige"), `corpus-parser/…invocations` (bitte/fluche), `band1/data/…auswahl.xlsx` (warte/klage/bezeuge).
- **Formfassungen:** v1 Verszeilen + „Sigle …" am Fuß → v2 Fließtext + Kopfzeile → **v3** Verszeilen zurück, Kopfzeile „Fundort · Sigle", Register II als „Von X", „schweige" von VIII in die Mitte (V) → **v4** = v3 + 7 eingebettete Felszeichnungen (`rockart_images/`, `ROCKART_UEBERSICHT.md`).
- **Kapiteltitel-Notiz** (Infinitiv minus „n", bewusst mehrdeutig/„infinit") und das *l-*-Argument („von / für / gehörig zu") stammen aus dieser Phase und leben in Vor-/Nachwort weiter.
- Das damalige Build-Skript baute die Kopfstücke faithful aus `erweitert/…_v5.docx` und trug die Rock-Art-Einbettung; die aktuelle v5-Fassung des Skripts hat beides abgelöst.
