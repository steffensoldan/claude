# Lektorat v6 — Abgleich gegen die safaitischen Originale

Stand: 2026-08-20 · Fassung: `wer_dies_liest_register_v6.docx` (138 Stücke)

**Methode.** Jedes der 138 Gedichte wurde gegen die **safaitische Transliteration** der OCIANA-Edition abgeglichen (nicht nur gegen die englische Übersetzung). Quelle: der vollständige OCIANA-Korpus als EpiDoc/XML (`ociana_corpus.xml`, 37.871 Inschriften, aus dem GitHub-Release `v01-data` dieses Repos, SHA-256 verifiziert) — er liefert je Inschrift **Transliteration · englische Edition · Apparatus Criticus · Kommentar**. Alle konkreten Textänderungs-Vorschläge unten sind programmatisch gegen Original + Transliteration gegengeprüft.

**Gesamtbefund.** Der Band ist überwiegend quellentreu. Die Litaneien („Er weinte vor Kummer" ×; „dass er sicher sei"; das ʿwr-Wortspiel „blind macht" ×14) sind in sich stimmig; historische Namen (Germanicus, Agrippa, Herodes, Rabbel, Taymāʾ) sind korrekt identifiziert; Genealogie- und Lücken-Regeln werden eingehalten. Die Vorschläge betreffen **zwei echte Fehler**, eine **systematische Götternamen-Uneinheitlichkeit** und einige **Wortlaut-Konsistenzen**.

> **Umsetzungsstand (2026-08-20):** Punkte **1–17 umgesetzt** — A + B + C (mit s¹lm → „Sicherheit"), D (Diakritika 12–13) und E (14–17) vollständig eingearbeitet, v6 neu gebaut. Die Tabellen unten dokumentieren den Befund; die Spalte „Aktuell" beschreibt den Stand *vor* der jeweiligen Korrektur.
>
> **Punkt 17 (Oheim) — aufgelöst.** „Oheim" kam 5× vor und stand undifferenziert für zwei verschiedene Verwandtschaftsgrade. Jetzt nach dem Original getrennt:
>
> | Sigle | Original | Gloss | neu im Band |
> |---|---|---|---|
> | ritze · SIJ 291 | `ḫzʾ` / Var. `ḫl` | mütterlicher Onkel | **Mutterbruder** |
> | fluche · RSIS 351 | `dd -h` | väterlicher Onkel | **Vaterbruder** |
> | fluche · LP 243 | `dd -h` | väterlicher Onkel | **Vaterbruder** |
> | bezeuge · C 2190 | `{d}{d} -h` | väterlicher Onkel | **Vaterbruder** |
> | bezeuge · RQ.D 3 | `ʾm -h qtlt` (fem.) | Mutter | **Mutter** (Punkt 14) |
>
> „Oheim" steht danach 0× im Band; HSNS 5 („Mutterbrüder" für `ʾḫwl`) bleibt unverändert korrekt.

---

## A · Echte Fehler (korrektur-sicher)

| # | Register · Sigle | Aktuell | Vorschlag | Original-Beleg | Begründung |
|---|---|---|---|---|---|
| 1 | I stehe · **HCH 38** | „Von **Sʿd**, Sohn des Ẓn …" | „Von **ʾsd** …" | Translit `l **ʾs¹d** bn ẓn bn ṯlm`; EN „By **ʾs¹d** …" | Falscher Name. Der Verfasser heißt `ʾs¹d` (→ „ʾsd"), nicht „Sʿd". Verwechslung mit dem echten `s¹ʿd`→„Sʿd" (vgl. HCH 158.2, RQ.A 5). |
| 2 | VII fluche · **C 4803** | „Sohn des **Ḍkr**" | „Sohn des **Ḏkr**" | Translit `bn ḏk{r}`; EN „son of **Ḏkr**" | Falscher Buchstabe: `ḏ` (ḏāl) ≠ `ḍ` (ḍād) — zwei verschiedene Konsonanten. Original hat `ḏ`. |

## B · Götternamen nicht eingedeutscht (systematisch, wichtig)

Der Band deutscht Götternamen durchgängig ein (Allat, Rudā, Duschara, Baalschamin, Schaihaqaum, Yaṯaʿ, Yalt, Nasr). **Fünf Einzelstellen** — überwiegend die langen v5-Kopfstücke — sind durchgerutscht:

| # | Register · Sigle | Aktuell | Vorschlag | Original | Begründung |
|---|---|---|---|---|---|
| 3 | VIII bezeuge · **HSNS 5** | „**Lt**" | „**Allat**" | `w h … lt` | `lt`/`ʾlt` = Allat — überall sonst „Allat". |
| 4 | VIII bezeuge · **HSNS 5** | „**Dšry**" | „**Duschara**" | `ds²ry` | `ds²r`/`ds²ry` = Duschara (vgl. Is.Mu 242, LP 461). |
| 5 | VII fluche · **C 4803** | „**Bʿlsmn** — gib Sicherheit" | „**Baalschamin** — …" | `b{ʿ}ls¹mn` | Sonst „Baalschamin" (BS 209, Is.Mu 88). |
| 6 | III harre · **Is.Mu 255** | „**Jaʾlat** — gib Sicherheit" | „**Yalt** — …" | `y{ʾ}lt` | Dieselbe Gottheit `yʾlt`/`ylt` steht sonst als „Yalt" (C 2194, C 1629). Eine Schreibung wählen (Empf. „Yalt"). |

## C · Wortlaut-Konsistenz (mittel)

| # | Register · Sigle | Aktuell | Vorschlag | Original | Begründung |
|---|---|---|---|---|---|
| 7 | V bitte · **C 134** | „schenke **Befreiung**" | „schenk **Errettung**" | `h rḍw flṭ` | `flṭ` sonst „Errettung/errette" (C 805, WAMS 19.2, SIJ 10, C 1629). Setzt die schon für C 1629 begonnene Harmonisierung fort. |
| 8 | V bitte · **MKJS 80** | „**nimm die Not**" | „**errette aus der Not**" | `flṭ m- bʾs¹` | s. o. — `flṭ` = errette/Errettung, nicht „nimm" (das ist die rwḥ-Wendung aus Is.Mu 88). |
| 9 | VII fluche · **Is.Mu 242** | endet auf „Blutrache." | „Blutrache. / **Und blende, wer dies blind macht.**" | `ṯʾr w **ʿwr ḏ yʿwr**` | Fast identischer Parallelstein **LP 461** (derselbe Autor Whblh) behält die Blindheits­zeile; Is.Mu 242 lässt sie weg. Angleichen. |
| 10 | VII fluche · **KRS 941** | endet ohne Fluch („… wer überlebt, verzweifelt.") | Fluchzeile ergänzen: „**Allat — blende, wer die Schrift blind macht.**" | `w h lt **ʿwr ḏ yʿwr h- s¹fr**` | Steht im Fluch-Register, hat im Original einen ʿwr-Fluch, im Band aber keinen — liest sich als Klage. (Alternativ Platzierung in „klage" erwägen.) |
| 11 | V bitte (+ C 4681) · **s¹lm** | „gib Sicherheit" (AbSWS 42, C 64) / „dass er sicher sei" (6×) / „Sicherheit" (C 4681) | eine Fassung wählen | `h lt s¹lm` | Gleiche Konstruktion, drei Fassungen. Spiegelt OCIANA-Varianz — daher mittel/niedrig; für ein einheitliches Bild vereinheitlichen (Empf. „dass er sicher sei"). |

## D · Diakritika (niedrig, optional)

Einige Namen droppen einen emphatischen Punkt, den die **Transliteration** führt (OCIANA-Englisch droppt teils mit). Für ein sauberes Diakritika-Bild angleichen:

| # | Register · Sigle | Aktuell | Vorschlag | Original |
|---|---|---|---|---|
| 12 | I stehe · **JaS 15** | „Bnġ**d**w" | „Bnġ**ḍ**w" | `bnġḍw` |
| 13 | IV fehle · **HCH 125** | „K**s**t" | „Ks**ṭ**" | `ks¹ṭ` (C 2775 hat korrekt „Ksṭ") |

## E · Philologische Einzelfragen (niedrig, zur Prüfung)

| # | Register · Sigle | Stelle | Anmerkung |
|---|---|---|---|
| 14 | VIII bezeuge · **RQ.D 3** | „den **Oheim**, den sie erschlugen" | Original `ʾm -h **qtlt**` (feminine Form „getötet") liest sich eher als „seine **Mutter**, die getötet wurde". OCIANA glossiert „paternal uncle" — der Band folgt OCIANA. Prüfen. |
| 15 | VII fluche · **LP 243** | Rache-Anrufung fehlt | `f h ylh **ṯʾr**` (O Lh — Rache) getilgt; in einem Fluche-Stück könnte die Rache-Zeile ergänzt werden. |
| 16 | VIII bezeuge · **RQ.D 6** | „im Jahr der **Rm**" | `rm` transliteriert; C 4439 hat für `rm` „die **Römer**". (OCIANA unterscheidet hier selbst — daher offen gelassen.) |
| 17 | mehrere · **„Oheim"** | ḫl vs dd | „Oheim" steht für mütterlichen (`ḫl`, SIJ 291) UND väterlichen Onkel (`dd`, RSIS 351, LP 243). HSNS 5 nutzt präzise „Mutterbrüder". Bei Bedarf differenzieren. |

---

## Bewusst NICHT beanstandet (kuratorisch vertretbar)

- **Genealogie-Kürzungen** in „ritze"/„harre"/„bitte" (nur Erstname o. „…") — registerkonform.
- **`nqmt`=„Beute"** (C 2194) und **`s²ml`=„sah…Nordseite"** (RWQ 187): folgen der OCIANA-Glosse, wie vom Band-Prinzip vorgesehen.
- **`[?]`-Unsicherheiten** (Is.Mu 484) nicht markiert — registerkonform (Klammern nur, wo Lücke).

## Ausschnitte — welche Inschriften nicht vollständig wiedergegeben sind

Zwei Ebenen der Verknappung sind zu unterscheiden:

**1. Genealogie-Kürzung (registerkonform, kein inhaltlicher Ausschnitt).** 116 der 138 Originale tragen eine Namenskette (`bn … bn …`). In „ritze/harre/bitte" u. a. wird sie regelhaft auf den Erstnamen oder „…" verknappt. Das ist das Bauprinzip des Bandes und gilt nicht als inhaltlicher Ausschnitt.

**2. Inhaltlicher Ausschnitt (eine Sachaussage des Originals fehlt).** Nach Einarbeitung von Punkt 9, 10, 15 (Is.Mu 242, KRS 941, LP 243) **und der Vollausführung der zuvor gekürzten fünf Stücke** verbleibt **kein inhaltlicher Ausschnitt** mehr. Die folgenden fünf waren die letzten und sind jetzt vollständig ausgeführt:

| # | Register · Sigle | Ergänzt | Original |
|---|---|---|---|
| 1 | harre · **RSIS 110** | Vatertrauer + Schluss-Anrufung („Allat — Sicherheit und Fülle dem, der die Schrift achtet") | `w wgm ʿl- ʾb -h … f y ʾlt s¹lm w ġnyt l- ḏ s²ws¹` |
| 2 | harre · **RSIS 322** | Schluss-Anrufung („Allat — Schutz") | `f h lt wqyt` |
| 3 | harre · **LP 1196** | Schluss-Anrufung („Yalt — Sicherheit und Beute, dem Feind abgenommen") | `f h ylt s¹lm w ġnmt m- s²nʾ` |
| 4 | klage · **KRS 17** | Jahresformel + zweite Trauer-Namensliste (Rb, Yʿly, ----ḥ) | `s¹nt ws¹q ʾl mʿṣ w wgm ʿl- rb w ʿl- yʿly w ʿl- ----ḥ` |
| 5 | fluche · **C 2551** | Schluss-Fluch („und blende, wer dies blind macht") | `w ʿwr l- ḏ yʿwr` |

**Befund: alle 138 Stücke geben den inhaltlichen Kern des Originals jetzt vollständig wieder.** Es verbleibt nur die registerkonforme Genealogie-Kürzung (Ebene 1), die kein inhaltlicher Ausschnitt ist.

## Empfohlene Umsetzungs-Reihenfolge

1. **A (Fehler)** + **B (Götternamen)** — klar richtig und wichtig; sofort umsetzbar.
2. **C 7–10** (flṭ, Is.Mu 242, KRS 941) — Konsistenz/Vollständigkeit; empfohlen.
3. **C 11 (s¹lm), D, E** — optional, nach Geschmack.
