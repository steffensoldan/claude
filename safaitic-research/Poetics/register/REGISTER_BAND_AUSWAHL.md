# Register-Band — Auswahl aus dem Vollkorpus

Stand: 2026-06-28 · Konzept A: eigener Band nach den sieben Sprechakt-Registern · Ordner `register/`

## Idee

Nicht der Jahresbogen der erweiterten Ausgabe, sondern die **Sprechhaltung** ordnet: jedes Kapitel ein anderer Akt am Stein (Searles Illokutionsklassen, eigene Prägungen). Anders als beim Umsortieren der erweiterten Ausgabe (wo drei Register überfüllt, drei fast leer blieben) wird **jedes Register gezielt aus dem Vollkorpus gespeist** — darum tragen jetzt alle sieben.

## Datengrundlage & Methode

Quellen: `neues-konzept/data/safaitic_full_corpus.xlsx` (31.768 safaitische, mit Typ-Spalte) für I + VII; `safaitic_invocations.xlsx` (2.018, thematische Blätter) für III + V; `band1/data/…auswahl.xlsx` (Longlist, 2.448 gerankt) für II, IV, VI. **Ausgeschlossen:** alle 180 bereits in der erweiterten Ausgabe (v5) verbauten Siglen — der Register-Band ist materiell eigenständig (0 Überschneidung).

## Stand des Manuskripts (gebaut: `wer_dies_liest_register.docx`)

Realisiert sind **134 Stücke** in **acht** Registern, gestaltet wie die erweiterte Ausgabe v5 (Georgia, Er-Form). Über die Korpus-Ausgangsauswahl unten hinaus enthält der Band:

**Kapitelüberschriften** = Verb in der Ich-Form (das einzige Ich im Band): **stehe · schreibe · warte · bitte · klage · verfluche · bezeuge · schweige**. Kapitel I „stehe“ (die Ahnenreihen) und VIII „schweige“ (das Verstummen) rahmen den Band. Unterüberschriften sind vorerst **entfernt** (bis eine bessere Fassung feststeht).

**Aufteilung des alten Kapitels I:** Die Genealogie-Gedichte („Von X, Sohn des Y …“) bilden jetzt das eigene Kapitel **I „stehe“**; die „X war hier“-Litanei der reinen Signaturen wird Kapitel **II „schreibe“**.

**v5-Kopfstücke** je Register (lange Inschriften zuerst, aus der erweiterten Ausgabe — der Band ist dadurch nicht mehr überschneidungsfrei zur erweiterten Ausgabe):
- I stehe: — (keine; nur Korpus-Genealogien)
- II schreibe: RWQ 342, RWQ 187, HYGQ 24, KRS 1341
- III warte: **ASWS 73** (zurück aus VI), RSIS 110, Is.Mu 255, SIJ 30
- IV bitte: BS 209, MKJS 80, LP 1267, Is.Mu 88
- V klage: LP 540, KRS 17, AbaNS 361, C 4273
- VI verfluche: C 4803, RSIS 351, LP 243, C 2775
- VII bezeuge: HSNS 5, LP 653, C 2670, ISB 57
- VIII schweige: RQ.A 5, WH 1867.1, WH 1501.2

**Kapitel II** als „X war hier“-Litanei: die fünf reinen Signaturen auf „X war hier“ umgestellt + 8 neue (HCH 75/158.2/31.1, Rees 150/151/155/161 4/176) — geografisch dicht (Hani, Km 612, Ḥarrat al-Raǧil). **Kapitel III**: Genealogie-Gedicht **LP 1196** (sieben Generationen + Späh-Verb) neu.

**Einleitung + Nachwort** stehen zusammen in einem Schluss-Kapitel „Nachwort“ **nach** den Gedichten, mit zwei Tabellen: **Corpus-Siglen** (Auflösung der Abkürzungen) und **Fundorte** (Erklärung, inkl. generischer Angaben wie „Jordanien“, „Km 612“).

### Fundort-Beizeilen (Normalisierung)

Am Fuß jedes Gedichts steht **zuerst der Fundort, dann die Corpus-Sigle** (das Wort „Sigle“ gestrichen), z. B. „Hani · HCH 117“. „Cairn of Haniʾ“ ist zu **„Hani“** verkürzt. Regeln: Survey-Apparat (Seitenrefs, Anführungszeichen, „Unknown,“) gestrichen; spezifischster benannter Ort gewählt; zwei Zonen — **NO-Jordanien (Ḥarrah)** / **Süd-Syrien (Ṣafā)**. Mapping als statisches `FINDSPOT`-Dict im Build-Skript. Größte Cluster: Hani (HCH), Km 612 (JaS), Zalaf (C), Wādī Salma, al-ʿĪsāwī, Ḥarrat al-Raǧil, Riǧm Qaʿqūl, Tall aḍ-Ḍabiʿ.

**8 ortlose Korpus-Stimmen → verortete Ersätze aus starken Clustern:** WH 1116→**RSIS 322** (Tall aḍ-Ḍabiʿ) · AWS 379→**AbSWS 15** (Wādī Salma) · WH 1916→**C 2194** (Zalaf) · RVP 1→**AbSWS 42** (Wādī Salma) · ZN 4→**C 2190** (Zalaf) · WH 1851→**RWQ 304** (Wādī Salma) · RVP 10→**C 1146** (Riǧm Qaʿqūl) · WAMS 4→**SIJ 10** (Jathum).

**Bewusst „Fundort unbekannt“ belassen (8):** die vier IV-Klage-Litanei-Verse (Anonymität passt zum Chor), der Fluchkatalog WH 368, die drei v5-Kopfstücke HYGQ 24, WH 1867.1, WH 1501.2.

## Korpus-Ausgangsauswahl — 14 je Register (98)

Die Basis-Auswahl aus dem Vollkorpus (vor v5-Kopfstücken, war-hier-Erweiterung und den 8 Verortungs-Ersätzen oben). Englische OCIANA-Glosse; Genealogien werden (außer in I und VII, wo sie Pointe sind) getilgt.

### I. Er war hier
*Präsentativ — Dasein als Akt: der bloße Name (oder die Ahnenkette), kein Verb. Aus den ~19.800 Signaturen + ~6.300 Minimal-Texten des Vollkorpus, die in keinem bisherigen Band vorkamen.*

- **JaS 16** — By Bnḥt
- **HCH 117** — By ʾnʿm
- **HCH 156** — By {s¹ḫr}
- **HCH 160** — By Gḥs²
- **HCH 158.1** — By Gḥs²
- **JaS 4** — By Msk son of S²dt son of Mḥlm son of S²dt son of Mḥlm of the lineage of Tm
- **JaS 5** — By Tm son of Mḥlm son of S²dt son of Mḥlm of the lineage of Tm
- **JaS 15** — By Ḥmr son of Bnġdw son of S¹fʾ son of Ḥnf
- **JaS 22** — By Hnʾ son of S²nʾ son of Gmr son of Ḍʾ
- **JaS 13** — By Gs²m son of S¹mr of the lineage of Bs¹ʾ and he grieved for Nḥṭ
- **JaS 21** — By tʾl son of ʿz and he grieved for his father
- **HCH 99** — By ʿrb son of Hrs¹ and he grieved* for Hnʾ
- **HCH 22** — By Tm son of Ḫlṣ son of Tm son of S²ʿ and he grieved for Hnʾ
- **HCH 38** — By S¹ʿd son of Ẓn son of Ṯlm and he grieved for Hnʾ

### II. Er wartet
*Expressiv-Deferred — Ausschau, Warten, Sehnsucht; der Augenblick im Stein konserviert.*

- **KRS 3051** — By {Ns²lʾl} son of Wdq son of {Mrʾt} is the young she-camel he went forth [in] the clear and spacious tract of land and he despaired whilst on the loo
- **CSNS 796** — By ʿg and he awaited the successful raid
- **C 2756** — By S¹d son of S²zr son of Rbn and he grieved for the group of men in the look-out post
- **C 2753** — By {Mġṯ} son of Bhs² son of Kft and he grieved for the group of men in the look-out post
- **WH 1116** — By Qdmʾl son of Wdmʾl son of Grmʾl son of Nḫr son of Ġrb son of S¹lm and he was on the look-out and he grieved 
- **WH 175** — By S¹krn son of ʿqrb and he migrated to the inner desert and he was on the look-out
- **AWS 379** — By Tm son of ʾnʿm and he pastured and he was on the look-out for Ks¹ṭ of the tribe of Ḍf
- **KWQ 113** — By Bdḥ son of ʿlg and he walked with goats and was on the look-out
- **ASWS 183** — By Qrs²t son of Ḥbb and he was on the look-out for the lion
- **CEDS 226** — By Bġyḍ son of Zʿn and he was on the look-out for the horses
- **SIJ 323** — By Rfʾt son of ʾnʿm son of Rfʾt of the tribe of Ḥẓy and he followed after the camels and was on the look-out
- **SIJ 14** — By Khl son of Rġḍ son of Hḏr and he was on the look-out for the lion
- **GSSH 1** — By Grm son of Zd son of Rkb son of Ḥrb son of ʿqrb son of ʾs¹ son of Yṣḥḥ and he lay in wait at the look-out for enemies with camels
- **WH 1916** — This look-out belongs to Wgl the {Mkbly} year after year

### III. Er bittet
*Intermediär-Direktiv — die Anrufung als Kern; das Gebet, das im Stein steht. Quelle: Anrufungs-Workbook (2.018), Blatt „Security & Protection“ + „Prosperity & Gain“.*

- **RVP 1** — O Rḍy {give help} to {Ḥṣb}
- **WAMS 19.2** — ..ḥ son of Gḥr and he awaited Fate. So O Rḍw deliver him.
- **C 64** — By Frhz son of Khl son of Frhz {son of} ʿbd; so O Lt [grant] security and ----
- **C 134** — By ʿbd son of Mlk O Rḍw [grant] liberation
- **C 218** — By S²dy son of Hʿbd son of Ys¹mʿl and, O Yṯʿ, remove from him [these] misfortunes.
- **C 1412** — By Ẓnʾl son of Rb son of Rb {son of} {Mqd} {and so} O Lt may he be secure and O Lt
- **C 805** — By Ys¹ʿd son of Mṯn son of Brʾ O Lt [grant] deliverance
- **C 885** — By Ḥwlt and so O Rḍy {may he be secure}
- **C 898** — By Mnrt son of ʿbṭ and he pastured the donkeys {and so} O Lt may he be secure ---
- **C 907** — By S¹lmlh son of Zqm and he was on a journey and so O Lt may he be secure
- **C 1086** — By Mlt son of Hrmṯ (and so) O Lt may he be secure dyqḥgwrs²yḥnnm
- **C 1496** — O Rḍw {help} ʾlh son of Bdn son of Kn
- **C 1629** — By Gfft son of Dbb and, O Ylt, let there be escape from evil in this year.
- **C 1660** — By Frʾ son of Ḫr son of S¹krn son of Ṣbḥ and O Lt may he be secure

### IV. Er klagt
*Memorativ-Expressiv — Totenklage als Denkmal; die wiederkehrende Zeile „und er weinte vor Kummer“ als bewusster Chor.*

- **CSNS 781** — By ʿm son of Qdm and he wept with grief
- **WH 1517** — By ʿzz son of Rfln and he wept with grief
- **AbaNS 453** — By Glhm son of ʿs²q and he wept with grief
- **WH 3829** — By S²dy son of Zkk and he wept with grief
- **WH 3029** — By Tmlh son of ʿmr and he wept with grief for Fly
- **WH 2825** — By Rṯm son of Mḍn and he wept with grief
- **HaNSB 319** — By ʿqrb son of ʿys¹ and he wept with grief
- **HaNS 708** — By ʿhd son of Gml and he wept with grief
- **HaNSB 346** — By Mrʾt son of H̲lʾl and he wept with grief for his son Wlym
- **HNSD 13** — By S²fr son of ʿḏrʾl and he wept with grief
- **SIJ 1001** — By Mʾd son of Ḥn and they wept with grief
- **SIJ 811** — By Hs²yz son of Qhr and he wept with grief for ---Gh
- **SSWS 28** — By Ns²l son of ʾs¹d and he wept with grief
- **C 5367** — By ʾs¹b son of Kf and he wept with grief

### V. Er verflucht
*Magisch-Deklarativ — der Fluch, der nie endet; Kataloge aus Blindheit, Lähmung, Stummheit, Austreibung aus dem Grab. Quelle: Blatt „Vengeance & Cursing“ (273).*

- **WH 368** — By Bny son of S¹hm son of Qḥs² is this writing and, O Lt, let there be blindness and lameness and dumbness and scab and mange to him who would efface 
- **LP 461** — By Whblh son of Mlk son of Whblh son of Mrʾlh son of ʾḥlm son of Lbb and he grieved for Mlk and for Ḫrg and for Gm and for ʾys¹ and for Ẓn. So, O Lt a
- **KRS 813** — By Drʾl son of ʾnʿm son of Mḥlm son of ʿbdʾl son of Hḏr son of Grmʾl and he grieved for Ṣʿd and O Lt blind whoever scratches out [the writing] and [in
- **KRS 941** — By Nʿmn son of Ṣʿd son of Ys¹mʿl and he found the traces of Ṣʿd and so he grieved in pain and for those who remain despair and he [Ṣʿd] had been struc
- **Is.Mu 242** — By Whblh son of Mlk son of Whblh son of Mrʾlh son of ʾḥlm son of Lbṣrh and he grieved for Mlk and for Ḫrg and for Gḥmn and for ʾys¹ and for Ẓn. So, O 
- **HCH 85** — By ʾs¹lh son of S²rd son of Grm and he grieved for Hnʾ and for Gls¹ and O Lt and Ds²r [inflict] blindness on whoever scratches out [the] writing
- **C 286** — By Nʿmn son of Mty son of Nʿmn the slave girl so, O Rḍy, may he who would efface go blind.
- **C 1658** — By {Wqr} son of Yʿl are the two camels which have been dedicated to ʾlt and to Rḍw, so, O Yṯʿ, blind whosoever would efface this [writing].
- **C 1845** — By Ns²l son of Mqm son of Ḥml son of Ns²bt and O Lt blind whoever scratches out [the inscription]
- **C 2551** — By Ṣrmt son of ʿbd son of Ṣʿd son of ʿḏ son of S²rb and he recognized another of {the} carvings {alas} and so despair for those who remain and so O Lt
- **C 3138** — By S²hyt son of S¹ny son of Ks¹ṭ son of ʿbdhm and O Rḍy blind whoever scratches out
- **C 4439** — By {Mzn} son of ʾs¹ son of Ys¹mʿl of the lineage of Ḍf and he returned to water the year that the Romans smote S²mt son of ʾs¹ the Qʿs²ite and so O Lt
- **C 5299** — By Hʾs¹ son of ʾhwd son of Yʿly and O Rḍy blind whoever scratches out {the writing}
- **LP 308** — By Ns²l son of Mqm son of Ḥml son of Ns²bt and grieved for Mqm and for ʿqrb and for S¹ḫr and for Tmʾl and for Mqm and for Ḥml and O Lt [inflict] blind

### VI. Er bezeugt
*Assertiv-Deferred — Datierung durch ein Ereignis; Zeugnis für Fremde, die später kommen.*

- **HSNS 1** — By Qḥs² son of S²mt son of Zkr son of Ġyrʾl son of Zkr and he migrated to the inner desert the year Agrippa died
- **RQ.D 3** — By ʿm son of ʿmrn son of ʿbṭ and he grieved for his paternal uncle who was killed the year of ʾrm
- **LP 1291** — By S¹wd son of Mḥlm son of {Rbʾlh} son of ʾnʿm and he spent the season of the later rains in this valley, in the year in which the torrent passed alon
- **ZN 4** — By S²rk son of Ṣʿd son of S²rk son of ʾnʿm son of Lʿṯmn and he grieved for his brother who was killed in the year of Qbr
- **RQ.D 6** — By ʾḏnt son of Wrd son of ʾnʿm son of Khl of the lineage of Nġbr and he grieved in pain for S²rk who was killed and for ʿyḏ who was a prisoner the yea
- **Is.L 202** — By Zkr son of Ẓnʾl son of S¹b and he pastured in this valley on spring herbage the year of Taymāʾ
- **ASFF 267** — By S²rk son of Gmr son of Ġr and he returned to the watering place from S¹mwt the year of the struggle of Mʿṣ
- **KRS 1586** — The shelter belongs to ʿzgd son of Frʾn he came to a watering-place the year of ṣh
- **C 4681** — By Ḫlṣ son of Gʿl son of Mṭr and he built the small shelter the year the torrents [resulting from] much rain [came] to this raḥaba, so Lt, may he be s
- **ZN 1** — By S²rk son of Ṣʿd son of {s²rd} son of ʾnʿm son of Lʿṯmn and he grieved for his brother who had been killed in the year of qbr
- **WH 1851** — By Ḫrg son of S¹ny son of Nẓr son of S¹ny and he migrated to the inner desert the year of Hnʾ
- **BWM 3** — By Frds¹ was here [in] the year that Ḥrb and ʾlmn were killed and he migrated to ʾnks¹r
- **RSIS 324** — By S²ʿṯm son of Wtr son of ʾbgr of the lineage of Frṯ and he (?) pastured the sheep the year of the war of the Jews.
- **C 4902** — {Mʿdʾl} {was here} the year of much rain and he hunted on the level ground

### VII. Er schweigt
*Abwesenheitsakt — Lücken, getilgte Namen, Abbruch. Genau das Material, das die erweiterte Ausgabe glättete; hier offen belassen (----).*

- **JaS 23** — ---- son of br son of ---- ʿbkz ---- ʾl ʿmn
- **HCH 102** — By Mʿn son of Zbd son of ʿtk son of Zbd and he kept watch for his brother [who was] following {his} camels. So O Lt and ---- S²ʿh ----
- **HCH 125** — By ʾs²ym son of Drʾl son of ʾs²ym son of Drʾl son of Ks¹t son of ʿbd son of ʾs²ym son of ʾs¹ son of ʾʾs¹d son of S²rk w ḥḍr ḫrs¹ ḫrṣʿ----ḫl----rʿwr---
- **HCH 151** — ----lkt of the lineage of Fḍg and he grieved for ---- {built} {h}r---- mʿ----
- **HCH 157** — ---- son of ʾs¹lh son of Ytm b [----] ʾs¹{ʾ}
- **HCH 164** — By Ġṯ son of ʾḫ and he grieved for his brother w ----m----thrmnhs¹ʿdlm
- **HCH 183** — By S¹ny son of Ḥwr son of N----lt of {the lineage of} Fṣ----
- **HCH 184** — By ʿbs¹ son of S²ẓr and q----ys¹r f ṣyr ḥg w----lḥmrn
- **HCH 195** — By Wrs¹ son of ʾglḥ son of Ys¹lm son of ʾglḥ son of ʾs¹l [----]ʿh and he waited for the rains [----]ṯt
- **RVP 10** — By Rḥb son of {Ḥl----} [and] {he was on the lookout} on behalf of his brother {Ṣʿdʾl} ----nly
- **WAMS 4** — By ʾs¹d son of Dmt and he grieved for ----n{w}{y} and for Nqd and for Wḥf and for S²----
- **C 12** — By ʾlf son of ʿms son of Bwk and O Rḍw [grant] {booty}---- from {enemies} ---- and to him who is suffering from lack of milk. So O Lt and S²ʿhqm ----
- **C 1312** — By Ḥḍg son of S¹wr ---- and {he kept watch} ----
- **C 1368** — By Ḫlṣ ---- son of Qdm son of {ʾnʿm} son of Rʿ of the lineage of ----

## Stand & nächste Schritte
- [x] Nachdichtung ins deutsche Er-Form, je „Sigle“-Zeile darunter.
- [x] Manuskript gebaut (`wer_dies_liest_register.docx`, 134 Stücke): Vorwort nach dem Sprechakt-Prinzip, sieben Register, v5-Kopfstücke.
- [x] Kapitel I als „X war hier“-Litanei erweitert; Ich-Form-Überschriften.
- [x] Fundort-Beizeilen normalisiert; 8 ortlose Stimmen verortet ersetzt.
- [ ] Optional: Fundort-Anhang im Backmatter (alle Stücke nach Zonen/Clustern gruppiert).
- [ ] Optional: Intra-Register-Clustering (same-site-Stücke benachbart).
- [ ] Optional: echte Karte via OCIANA-Koordinaten (externer Abruf).
- [ ] Lektorat der Nachdichtungen gegen die OCIANA-Einträge.

Build: `scripts/build_register.py` (Auswahl, Verstexte und `FINDSPOT`-Dict inline; liest die v5-Kopfstücke faithful aus `erweitert/…_v5.docx`).
