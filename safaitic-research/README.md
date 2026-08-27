# „Wer dies liest, lebe lang" — Safaitic Poetics

Ein Lyrikband aus safaitischen Felsinschriften (1.–4. Jh. n. Chr., Wüsten Harra und Ṣafā, heutiges Syrien/Jordanien/Saudi-Arabien). Datengrundlage: der digitale OCIANA-Referenzkorpus der Universität Oxford. Die Inschriften werden ins Deutsche übertragen und zu einem Gedichtband komponiert.

## Wo ist was

| Ordner | Status | Inhalt |
|---|---|---|
| **`register/`** | **aktuell — hier weiterarbeiten** | Das Werk selbst, Fassungen v1–v8. Maßgeblich: `wer_dies_liest_register_v8.docx`. Alle Texte, das Build-Skript und die Lektorats-/Konzeptdokumentation. |
| `rahmen/` | verworfen | v7-Versuch: ein erzählender Rahmen („Die Sache"), der Vorwort und Nachwort verdrängte. Trug nicht; v8 setzt bei v6 an. Zur Nachvollziehbarkeit erhalten. |
| `archiv/` | abgelöst | Frühere Entwicklungsstufen — siehe Zeitachse unten. Nicht mehr in Bearbeitung, aus Nachvollziehbarkeit erhalten. |

**Direkter Einstieg:** [`register/REGISTER_BAND_AUSWAHL.md`](register/REGISTER_BAND_AUSWAHL.md) beschreibt Konzept, Aufbau und Fassungsgeschichte des aktuellen Bandes im Detail.

## Zeitachse

Das Projekt durchlief mehrere Konzepte, bevor sich die heutige Form (acht Sprechakt-Register, v1–v6) herausbildete:

1. **`archiv/band1/`** — Erstausgabe „Wer dies liest, lebe lang". Frühester Versuch: 69 Nachdichtungen in einem Jahresbogen, Ich-Form.
2. **`archiv/corpus-parser/`** — Werkzeuge, die das OCIANA-XML in Tabellenform (Invokationen, Narrative, Auswahllisten) aufbereiten. Lieferte die Datengrundlage für die frühen Stufen.
3. **`archiv/erweitert/`** — Zweiter Anlauf, eigene v1–v5-Zählung (nicht identisch mit der Zählung des heutigen Bandes). Erweiterte Ausgabe mit reduziertem Apparat, Er-Form.
4. **`archiv/neues-konzept/`** — Konzeptwechsel: Ordnung nicht mehr nach Jahresbogen, sondern nach **Sprechakt-Registern** (Searles Illokutionsklassen). Enthält den ersten Register-Band-Entwurf (Konzept A) und die Vollkorpus-Datenexporte.
5. **`register/`** — Realisierung von Konzept A als eigenständiger Ordner, seither die alleinige aktive Linie. Formfassungen v1 (generiert) → v2 → v3 → v4 (mit Felszeichnungen) → **v5** (erste handbearbeitete Fassung) → **v6** → *(v7 verworfen, siehe `rahmen/`)* → **v8** (aktuelle Fassung, s. u.).

Details, Commits und Begründungen einzelner Änderungen: `register/REGISTER_BAND_AUSWAHL.md` (Abschnitt „Historie") und die Git-Historie des jeweiligen Ordners.

## Die aktuelle Fassung (v8)

- Acht Register im Infinitiv: **I stehen · II ritzen · III harren · IV fehlen · V bitten · VI klagen · VII fluchen · VIII bezeugen** — 138 Stücke, gegen die safaitischen Originaltranskriptionen abgeglichen (siehe `register/LEKTORAT_v6.md`; die Stücke sind seit v6 unverändert).
- Manuskript: [`register/wer_dies_liest_register_v8.docx`](register/wer_dies_liest_register_v8.docx)
- v8 überarbeitet Vorwort und Nachwort sprachlich: Das Wort „Band" entfällt, Museums- und Verwaltungssprache ist aufgelöst. Was genau, steht in `register/REGISTER_BAND_AUSWAHL.md` („Was v8 gegenüber v6 ändert").
- Reproduzierbar aus `register/scripts/build_register.py` (aus `safaitic-research/` ausführen — Details in `register/REGISTER_BAND_AUSWAHL.md`).
