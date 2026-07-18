# Grafische Elemente (Felszeichnungen) im Register-Band

Stand: 2026-07-05 · Quelle: OCIANA-Feld **„Associated Drawings"** je Inschrift, ergänzt um Text-/Commentary-Belege. Alle 134 Seiten wurden erfolgreich geladen (HTTP 200), die Auswertung ist daher **vollständig**, keine Untergrenze.

> **Editorische Entscheidung (2026-07-18): Der Band ist bildfrei.** Weil nur ~5 % der Steine überhaupt eine Zeichnung tragen, überrepräsentiert ihre Aufnahme eine Ausnahme und ist einem Gedichtband nicht angemessen. Die sieben unten dokumentierten Bildsteine sind aus dem Manuskript **entfernt** und durch bildlose Inschriften **gleicher Registerfunktion** ersetzt (v5, Stückzahl bleibt 134). Ersetzungen: HYGQ 24→Is.Mu 484 · KRS 1341→SIJ 291 · KRS 3051→RWQ 120 · HCH 85→RSIS 132 · C 286→KRS 2919 · C 1658→C 1087 · C 2670→LP 254 (Details: `REGISTER_BAND_AUSWAHL.md`, Abschnitt „Bildfreie Fassung (v5)“). Diese Übersicht bleibt als **Korpus-Befund** und Begründung der Entscheidung stehen; die Abschnitte zum Bild-Einbau sind damit historisch.

## Kernbefund

**7 von 134** Steinen (≈ 5 %) tragen ein assoziiertes grafisches Element. Das entspricht der Realität des Korpus: safaitische Inschriften sind ganz überwiegend reiner Text; Bildbeigaben sind die Ausnahme.

| Motiv | Anzahl | Siglen |
|-------|:------:|--------|
| Löwe | 2 | KRS 1341, HYGQ 24 |
| Kamel(e) | 2 | KRS 3051 (junge Kamelstute), C 1658 (zwei Kamele + Krieger-Szene) |
| Oryx | 1 | C 2670 |
| Menschl./göttl. Figur | 1 | C 286 (Göttin Rḍy / weibliche Figuren) |
| unbenannt (zwei Zeichnungen) | 1 | HCH 85 |
| **Summe** | **7** | |

## Nach Register

| Register | mit Zeichnung |
|----------|---------------|
| I stehe | 0 |
| II schreibe | 2 (KRS 1341, HYGQ 24) |
| III warte | 1 (KRS 3051) |
| IV bitte | 0 |
| V schweige | 0 |
| VI klage | 0 |
| VII fluche | 3 (C 1658, C 286, HCH 85) |
| VIII bezeuge | 1 (C 2670) |

## Einzelnachweis

| Register | Sigle | Fundort | Motiv | Quelle (OCIANA) | im Band benannt? |
|----------|-------|---------|-------|-----------------|:----------------:|
| II schreibe | **KRS 1341** | Al-Mafraq | Löwe | Associated Drawings (d/1) + Text „drawing of the lion" | ja („Die Zeichnung des Löwen") |
| II schreibe | **HYGQ 24** | unbek. | Löwe | Text ist Bildunterschrift „is [the drawing of] the lion" | ja („Der Löwe") |
| III warte | **KRS 3051** | Al-Mafraq | junge Kamelstute | Associated Drawings (d/1) + Text „is the young she-camel" | ja („Die junge Kamelstute") |
| VII fluche | **C 1658** | Zalaf | Szene: zwei Kamele + Mann mit Schwert und Schild (in Kartusche) | Associated Drawings | ja („Die beiden Kamele …") |
| VII fluche | **C 286** | Rif Dimašq | Göttin Rḍy / nackte weibliche Figur, dazu eine zweite Frau | Associated Drawings | nein |
| VII fluche | **HCH 85** | Hani | zwei Zeichnungen (Motiv nicht benannt); Inschrift in einer Kartusche | Commentary | nein |
| VIII bezeuge | **C 2670** | Zalaf | Oryx (Umriss) | Associated Drawings | nein |

## Abgrenzung — was NICHT als Bild zählt

Mehrere Inschriften nennen „the carving" oder „carved", meinen damit aber die **Inschrift selbst** (das Gemeißelte), nicht ein Bild:
- **C 2775**, **RSIS 351** — „scratch out **the carving**" = die Schrift austilgen (Fluchformel).
- **C 2551** — „another of **the carvings**" = andere Ritzungen am Ort (kein eigenes Bild des Steins).
- **Is.Mu 88** — „must have been **carved** after …" = Datierung der Schrift.

## Auffälligkeit

Vier der sieben Fälle (KRS 1341, HYGQ 24, KRS 3051, C 1658) sind **Bildunterschriften**: Der Inschriftentext benennt die daneben geritzte Figur selbst („ist [die Zeichnung] des Löwen", „ist die junge Kamelstute", „sind die zwei Kamele"). Bei ihnen sind Schrift und Bild **ein Akt** — der Stein beschriftet sein eigenes Bild. Unsere Nachdichtungen geben genau das schon wieder. Bei den übrigen drei (C 286, HCH 85, C 2670) steht das Bild **neben** dem Text, ohne im Text erwähnt zu werden.

Datengrundlage: `ociana_rockart_result.csv` (alle 134), Rohseiten in `ociana_pages.zip`.

## Einbau der Abbildungen in den Band (historisch — in v5 rückgängig gemacht)

> Diese Mechanik gehörte zur Fassung **v4**. In der aktuellen bildfreien **v5** ist sie entfernt: `build_register.py` bettet keine Bilder mehr ein, der Bildnachweis ist aus dem Nachwort gestrichen, und die sieben Bildsteine sind ersetzt (siehe Kopfnotiz). Der folgende Ablauf ist als Historie dokumentiert (die v4-Datei und die Bilddaten bleiben im Ordner erhalten).

`build_register.py` (v4) bettete die 7 Zeichnungen als **rechts schwebende Abbildungen** (~4,6 cm, Text läuft links daneben) neben die jeweilige Inschrift ein; die Herkunft stand gesammelt im **Bildnachweis** am Ende des Nachworts. Ablauf:

1. **Bilder holen** (Netz nötig, z. B. Cowork): `python3 register/scripts/download_rockart_images.py` lädt die 18 OCIANA-JPGs aus `rockart_images_manifest.csv` nach `register/rockart_images/`.
2. **Bauen**: `python3 register/scripts/build_register.py` bettet je Stein automatisch das erste vorhandene Bild ein und schreibt `wer_dies_liest_register_v4.docx` (mit Abbildungen); liegt kein Bild vor, entsteht wie bisher `…_v3.docx` (ohne). Zum gezielten Auswählen eines Motivs: das gewünschte Bild als `register/rockart_images/<Sigle>.jpg` ablegen (hat Vorrang, z. B. `C_286.jpg`).

Die 7 echten OCIANA-Fotos liegen in `register/rockart_images/` (7 kuratierte `<Sigle>.jpg` + 18 Rohbilder); `wer_dies_liest_register_v4.docx` ist damit gebaut. Die Bildmechanik (Media-Part + Relationship + schwebendes DrawingML-Anchor) ist verifiziert (docx wohlgeformt, 7 Bilder korrekt verknüpft).

**Rechte:** Die OCIANA-Fotos/Squeezes unterliegen den OCIANA-Nutzungsbedingungen (Herkunft je Stein im Bildnachweis, z. B. „Dunand", CIS). Für einen internen Arbeitsstand unkritisch; vor einer Veröffentlichung des Bandes sind Genehmigung und Bildnachweis zu klären.
