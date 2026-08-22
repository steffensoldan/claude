# Vorgehen

Methodik der Auswahl und Verdichtung — von 38.000 Inschriften zu einem Gedichtband.

## Ausgangslage

- OCIANA-Gesamtkorpus: ~38.000 Inschriften.
- Arbeitsausschnitt: 2.487 erzählende Inschriften (14 thematische Blätter).
- Sprachliche Grundlinie ist formelhaft („By X son of Y and he …", Median 12 Wörter).
  Das Interessante ist die Abweichung von der Formel, nicht der Durchschnitt.
- Gemessener Bereinigungsbedarf: 36 exakte Dubletten; 310 Inschriften mit Textlücke (`----`);
  712 mit unsicherer Lesung (`{}`); 444 mit Herausgeber-Ergänzung (`[]`).

## Leitprinzip (Carmina-Burana-Analogie)

Zwei Ebenen werden getrennt:

1. **Sammlung + Klassifikation** — bei diesem Material durch die 14 Themenblätter weitgehend erledigt.
2. **Kuratierung + Rahmungskonzept** — die eigentliche Leistung: kleine, kohärente Auswahl,
   geordnet in einem Bogen, gehalten durch einen wiederkehrenden Refrain (analog zu *O Fortuna*).

## Phase 0 — Bereinigung

- Exakte Dubletten entfernt (2.487 → 2.451).
- Pro Inschrift berechnet: Lückenquote (`----`) und Unsicherheitsdichte (`{}`/`[]` pro Wort).
- Entkernung naheliegender Formelvarianten über eine „Signatur" des Kerntexts
  (max. 2 Stücke pro identischer Formel), damit nicht zehn Varianten derselben Zeile erscheinen.

## Phase 1 — Bewertungsraster

„Interessant" wird über gewichtete, teils maschinell berechenbare Kriterien operationalisiert:

| Baustein     | Erfasst                                              | Maschinell |
|--------------|-----------------------------------------------------|------------|
| emo          | Affekt: weinen, Sehnsucht, Angst, Trauer, Erbarmen  | ja         |
| scene        | konkretes Bild: Löwe, Wolf, Schnee, Flut, Stern     | teils      |
| rarity       | Seltenheit des Themas (kleine Cluster bevorzugt)    | ja         |
| meta         | Selbstbezug: Fluch-/Segensformel gegen Tilgung      | ja         |
| anchor       | Verankerung: Jahr-/Königsnennung                    | ja         |
| brevity      | verknappte Dichte (Kernwörter im Bereich ~6–22)     | ja         |
| integrity    | wenig Textlücken                                    | ja         |
| clarity      | wenig unsichere Lesung                              | ja         |
| geneal_pen   | Abzug für lange Ahnenketten („son of … son of …")   | ja         |

### Gewichtung (literarische Variante)

```
LiteraryScore =  emo·3.0 + scene·2.5 + rarity·3.0 + meta·1.5 + anchor·1.0
               + brevity·2.5 + integrity·2.0 + clarity·1.5 − geneal_pen·2.0
```

Die Gewichte sind eine Wertentscheidung. In `data/…auswahl.xlsx` liegen sie im Blatt
**Gewichtung** als veränderbare Zellen; die Longlist rechnet den Score per Formel neu.
Begründung der Setzung: Affekt, konkretes Bild und Knappheit tragen einen Gedichtband;
Verankerung ist erwünscht, aber bewusst niedriger gewichtet („verankert, nicht wissenschaftlich").

## Phase 2 — Selektion

- Shortlist: 150 Stück, entkernt, je Phase mindestens 6 / ~10 % der großen Cluster.
- Schutz der Raritäten: kleine Themen (Sehnsucht 4, Angst, Zeichen) vollständig bzw. bevorzugt.
- Manuskript: 69 Gedichte, balanciert über die 12 Phasen.
- Mischung: überwiegend vivid/emotional/singulär, dazu bewusst Typisches zur Erdung.

## Phase 3 — Architektur

Makrostruktur = **Jahreszyklus der Steppe** (Fortuna-Analogon):

Dürre → Wege/Wasser → Spähen → Weide → Raub/Krieg → Krankheit → Tod → Klage → Angst →
Sehnsucht → Zeichen → das Jahr selbst → (zurück zur Dürre).

Refrain = Fluch-/Segensformel, als wiederkehrende Klammer zwischen Abschnitten und als Envoi:
„Wer dies austilgt: erblinde. / Wer dies liest: lebe lang." — zugleich der reflexive Kern:
ein Stein, der bittet, nicht getilgt zu werden, in einem Buch, das ihn neu wählt.

Detail-Zuordnung Thema → Phase: siehe `struktur.md`.

## Phase 4 — Nachdichtung & Apparat

- Übersetzungsrichtung: OCIANA-Englisch → deutsche Nachdichtung (verknappt, klanghaft).
- Genealogien getilgt; Eigennamen in wissenschaftlicher Umschrift belassen, wo sie verankern.
- Lücken im Stein in den Gedichten geglättet; Originale (und die Tabelle) zeigen sie offen.
- Apparat literarisch minimal: pro Gedicht nur die Quellsigle.

## Grenzen (offen markiert)

- **Übersetzungsabhängigkeit:** Wirkung hängt an der OCIANA-Übersetzung; `{}`/`[]` zeigen den
  Anteil an Konjektur. „Schön" kann „unsicher" bedeuten.
- **Romanzisierungsgefahr:** Affektkriterien bevorzugen, was *uns* berührt — nicht das kulturell
  Repräsentative. Gegenmaßnahme: Anteil typischer Stücke.
- **Repräsentativität:** Eine Highlight-Sammlung verzerrt das Bild des Alltags bewusst; im
  Vorwort benannt.
