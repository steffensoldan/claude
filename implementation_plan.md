# Projektspezifikation — Wisskomm-Viz

**Interaktive Befund-Aufbereitung als Hausdienst für alle Forschenden des ZEW**

Version 0.1 (Entwurf) · Status: Pitch-Reife · Sprache der Ausgaben: Deutsch (umschaltbar)

> Dieses Dokument hat zwei Adressaten. **Teil A–E** ist die interne Pitch- und Entscheidungsgrundlage. **Teil F–K** ist eine präzise Programmiervorlage, die von Coding-Agenten (Cursor, Codex, Antigravity, Claude Code) direkt als Build-Anweisung gelesen werden kann. Das Referenzbeispiel (ZEW DP 26-021) ist mit vollständiger HTML-Umsetzung eingebettet.

-----

## A. Kurzfassung (Executive Summary)

Forschungsbefunde des ZEW erscheinen heute überwiegend als PDF und Folien. Für die Öffentlichkeit, Politik und Presse fehlt ein **niedrigschwelliger, skalierbarer Weg**, Kernbefunde als interaktive, scrollbare Web-Darstellung aufzubereiten — markenkonform, datenschutzkonform und ohne dass jede:r Forschende programmieren muss.

**Wisskomm-Viz** ist ein interner Dienst, der genau das leistet:

- **Output:** statisch-interaktive HTML-Seiten zum Durchscrollen/Klicken (keine Videos, kein Login, kein Tracking).
- **Betrieb:** quelloffene Werkzeuge, self-hosted auf einer ZEW-VM. Kein SaaS, kein Vendor-Lock-in, keine neue externe Schnittstelle.
- **Skalierung:** zentrale Haus-CD + Vorlagen; pro Befund ein Ordner; ein Python-Build. Forschende liefern Daten + Text, der Dienst rendert.
- **Datenhoheit:** reiner Build-Schritt; kein LLM und keine personenbezogenen Daten auf der VM nötig; Ausgabe ist eine eigenständige HTML-Datei ohne Laufzeit-Calls.

Der Aufwand pro Publikation sinkt von „Einzelanfertigung” auf „Vorlage befüllen”. Die Reputations- und Reichweitenwirkung steigt, weil Befunde öffentlich anschlussfähig werden.

-----

## B. Problem & Ziel

**Problem.** Wissenschaftskommunikation skaliert schlecht: interaktive Web-Darstellungen entstehen heute als teure Einzelstücke, uneinheitlich im Design, mit unklarer DSGVO-Lage bei SaaS-Tools.

**Ziel.** Ein wiederverwendbarer Dienst, mit dem **alle Forschenden** Kernbefunde publikumsgerecht als interaktive Webseite ausspielen — bei

- minimalem Aufwand je Befund,
- konsistenter Hausmarke,
- voller Datenhoheit (on-prem, EWR),
- ohne zusätzliche Werkzeug- und Schnittstellen-Last.

**Nicht-Ziel.** Kein Video-/Render-Stack (Remotion/ffmpeg/Headless-Chrome), solange statisch-interaktiv genügt. Keine SaaS-Visualisierungsplattform. Keine neue Dauer-Integration in den Betrieb.

-----

## C. Lösungsüberblick & Architektur

Drei sich ergänzende Ausbaustufen, **eine gemeinsame Datengrundlage**:

1. **Standalone-HTML (Einzel-Deliverable).** Eine dependency-freie HTML-Datei je Befund: Inline-SVG-Charts in Vanilla-JS, System-Schriften, keine externen Aufrufe. Sofort anzeigbar, per Mail/Intranet teilbar, 1:1 auf der VM hostbar. *(Referenz-Implementierung in Teil I.)*
2. **Stufe 1b. Standalone Web-Service (KI-gestützt).** Ein interner Web-Dienst auf der VM. Forschende laden ihr Papier (PDF) hoch. Das System extrahiert den Text, ruft die Claude-API auf, um strukturiert Text und Daten (gemäß Datenvertrag) zu generieren, und baut daraus direkt die Standalone-HTML-Seite.
3. **Quarto-Hausdienst (skalierbar).** Quarto rendert aus Markdown + Daten statisch-interaktive Seiten; zentrale CD über `_brand.yml`; Python orchestriert die Builds. *(Konfiguration in Teil J.)*

**Datenfluss (mit KI-gestütztem Web-Service):**

```
Papier (PDF) ─► Web-UI ─► Text-Extrakt ─► Claude-API ─► JSON-Daten/Story ─► Build-Skript ─► Standalone HTML
                                                                                 ▲
                                                                     (Validierung vs. Datenvertrag)
```

**Bewusste Festlegungen:**

- **Python orchestriert, nicht n8n.** Einzige Nicht-Python-Laufzeit ist die jeweilige Build-CLI/Engine. Keine zusätzliche Workflow-Software, kein eigener Credential-Store.
- **Claude-API auf der VM (verschlüsseltes EU-Routing):** Zur automatischen Generierung wird die API von Anthropic mit dem stärksten Modell **Claude 4.8 Opus (claude-opus-4-8)** verwendet. Die Datenverarbeitung erfolgt DSGVO-konform (kein Training auf Kundendaten). Der API-Key liegt als Umgebungsvariable (`ANTHROPIC_API_KEY`) auf der VM vor. Aufgrund des internen Reasoning-Prozesses dieses Modells ist die maximale Token-Länge auf 8000 eingestellt.
- **Self-contained Output.** Ziel: keine Laufzeit-Requests (keine CDNs, keine Google-Fonts) → DSGVO-sauber und offlinefähig.

-----

## D. Anforderungen

**Funktional**

- Scrollbare Einzelseite mit Hero, Kennzahlen, mehreren interaktiven Diagrammen, Fließtext, Methoden-/Quellen-Footer.
- Interaktivität clientseitig: Auswahl/Umschaltung von Kennzahlen und Reihen, ohne Backend.
- Zahlen ausschließlich aus belegten Quellen; keine erfundenen Werte.

**Nicht-funktional**

- **DSGVO/Datenhoheit:** on-prem, EWR; keine Tracker/Cookies; idealerweise null externe Laufzeit-Calls.
- **Marke:** zentrale CD (Farben, Schriften, Logo) über eine Quelle; alle Publikationen erben sie.
- **Barrierearmut:** Tastaturfokus sichtbar, `prefers-reduced-motion` respektiert, responsiv bis Mobil.
- **Wartbarkeit:** ein Befund = ein Ordner; Templates zentral; reproduzierbarer Build.
- **Freigabe:** fachliche Bestätigung durch die Autor:innen vor Veröffentlichung (gegen Verzerrung).

-----

## E. Betriebsmodell, Rollen, Roadmap

**Rollen**

- *Kommunikation:* pflegt CD/Vorlagen, betreibt den Build, führt die Freigabe.
- *Forschende:* liefern Befund (Text + CSV), prüfen und geben frei.
- *IT:* stellt VM und Hosting bereit; prüft DSGVO/Netzwerk.

**VM-Dimensionierung (zu testen).** Reiner Build/Static-Hosting; CPU genügt, keine GPU. Für einen Hausdienst ≥ 8 GB RAM, mehrere vCPU ausreichend; statische Auslieferung ist anspruchslos.

**Phasen**

1. **PoC (sofort):** dieses Referenzbeispiel als Standalone-HTML + 1 CD-Entwurf. *(liegt vor)*
1. **Pilot:** Quarto-Hausdienst mit `_brand.yml`, 2–3 echte Befunde, interner Webspace.
1. **Rollout:** Self-Service-Vorlage + Kurzanleitung; optionaler KI-Entwurfsschritt (extern, mit Freigabe-Gate).

**Risiken / offene Punkte**

- CD-Werte sind Platzhalter → durch offizielles ZEW-CD ersetzen.
- `embed-resources` bündelt Assets; Quarto lädt Google-Fonts zur **Build-Zeit** → für volle DSGVO-Sauberkeit Hausschrift lokal einbinden; nach Build mit Netzwerk-Monitor verifizieren.
- Lizenzcheck Quarto/Engines (alle quelloffen) für institutionelle Nutzung dokumentieren.
- Inhaltliche Korrektheit: Freigabe-Gate verbindlich.

-----

## F. Tech-Stack & Entscheidungen (für Umsetzende)

|Baustein                   |Wahl                                            |Begründung                                                                                      |
|---------------------------|------------------------------------------------|------------------------------------------------------------------------------------------------|
|Skalierbarer Generator     |**Quarto** (CLI, quelloffen)                    |wissenschaftsnah, Markdown+Code→statisches HTML, zentrale CD via `_brand.yml`, Python-Codezellen|
|Interaktive Grafik (Quarto)|**Observable JS / Plot** (gebündelt)            |clientseitig, kein Server; in Quarto integriert                                                 |
|Standalone-Grafik          |**Vanilla-JS + Inline-SVG**                     |null Abhängigkeiten, null externe Calls, voll DSGVO-konform                                     |
|Orchestrierung             |**Python** (subprocess → Quarto-CLI)            |vorhandene Kompetenz, kein Zusatztool                                                           |
|Schriften                  |System-Stack bzw. lokal eingebundene Hausschrift|keine Google-Fonts-Calls                                                                        |
|Scrollytelling (optional)  |Quarto-Extension **closeread**                  |wenn Grafik beim Scrollen „pinnen” soll                                                         |

**Verworfen:** n8n (Zusatzlaufzeit + Lizenzfrage), Datawrapper/Flourish (SaaS), Remotion/Video-Stack (nicht nötig für statisch-interaktiv).

-----

## G. Repository-Struktur (kanonisch)

```
wisskomm-viz/
├── implementation_plan.md      # dieses Dokument
├── README.md
├── config.json                 # Feature- und Build-Konfiguration
├── setup.ps1                   # idempotentes Einrichtungsskript für Windows
├── requirements.txt            # Python-Abhängigkeiten (pandas, etc.)
├── _quarto.yml                 # zentrale Quarto-Projektkonfig (Format, Theme, Brand-Bindung)
├── _brand.yml                  # zentrale ZEW-CD (Farben, Schriften, Logo)
├── theme/
│   ├── zew.scss                # Signature (Signal-Meter), KPI-Karten
│   └── fonts/                  # Lokale WOFF2-Dateien der Hausschriften (DSGVO-Konformität)
├── build.py                    # Orchestrierung: Validierung, Standalone- & Quarto-Build
├── templates/
│   ├── standalone.html         # dependency-freie HTML-Vorlage
│   └── story.qmd               # Quarto-Vorlage
├── publications/
│   └── <slug>/                 # ein Befund = ein Ordner
│       ├── index.qmd  |  index.html
│       └── data/*.csv
└── _site/                      # Build-Output (statisch)
```

`_quarto.yml`, `_brand.yml` und `theme/` liegen **einmal zentral im Wurzelverzeichnis**. Quarto sucht die Projektkonfiguration beim Rendern eines Unterordners aufwärts im Verzeichnisbaum; jede Publikation unter `publications/<slug>/` erbt damit automatisch Format und CD. (Standalone-HTML-Befunde brauchen weder `_quarto.yml` noch `_brand.yml` — sie tragen alles inline.)

-----

## H. Datenvertrag (für Coding-Agenten verbindlich)

Jeder Befund liefert CSVs mit festen Spalten. Beispielschemata aus dem Referenzfall:

- **`scenarios_eu.csv`** — Szenarienkennzahlen.
  `scenario` (string), `global_emissions_pct`, `leakage_pct`, `welfare_bn`, `out_flat_pct`, `out_long_pct`, `out_macro_pct`, `carbon_price` (alle numerisch).
- **`prices_eu.csv`** — Preisänderungen in % ggü. Baseline.
  `scenario`, `import_flat_pct`, `import_long_pct`, `user_flat_pct`, `user_long_pct`, `cpi_pct`.
- **`signal.csv`** — effektiver Signal-Anteil λ (relativ, Mass-based = 1).
  `label`, `setting`, `design`, `lambda`.

**Regeln:** Spaltennamen sind die API zwischen Daten und Vorlage. Dezimaltrennung in CSV mit Punkt; Anzeige-Formatierung (de-DE, Komma) erfolgt im Code. Fehlende Werte = leer (nicht 0). Die CSV-Dateien müssen UTF-8-codiert (ohne BOM) vorliegen.

### Formaler Datenvertrag (`data/README.md`):
Jedes Datenverzeichnis einer Publikation muss eine `README.md` enthalten, die den Datenvertrag formalisiert. Sie dokumentiert:
1. **Pflichtdateien:** `scenarios_eu.csv` und `signal.csv` müssen vorhanden sein.
2. **Optionale Dateien:** `prices_eu.csv` und `scenarios_us.csv` sind optional und steuern das Rendering der erweiterten Explorer-Features.
3. **Format-Vorgaben:** Spaltennamen exakt wie unten angegeben, UTF-8 ohne BOM, Punkt als Dezimaltrenner, keine Tausendertrennzeichen.

CSV-Inhalte des Referenzfalls:

`data/scenarios_eu.csv`

```csv
scenario,global_emissions_pct,leakage_pct,welfare_bn,out_flat_pct,out_long_pct,out_macro_pct,carbon_price
A. Cap,-0.69,56.44,-0.39,-17.65,-6.68,-0.062,69.71
B. M-BCA,-1.34,16.05,-0.89,-16.25,-4.60,-0.126,87.90
C. R-BCA,-1.02,36.18,-1.38,-17.02,-6.19,-0.081,74.94
D. DM-BCA,-1.02,36.18,-0.07,-17.12,-5.79,-0.087,76.91
```

`data/prices_eu.csv`

```csv
scenario,import_flat_pct,import_long_pct,user_flat_pct,user_long_pct,cpi_pct
A. Cap,0.69,-0.26,19.88,8.70,0.02
B. M-BCA,37.10,29.90,34.58,16.36,0.04
C. R-BCA,10.95,5.70,24.18,10.49,0.02
D. DM-BCA,13.80,11.47,25.61,11.85,0.03
```

`data/signal.csv`

```csv
label,setting,design,lambda
EU Mass-based,EU,Mass-based,1.00
EU Rate-based,EU,Rate-based,0.36
US Mass-based,US,Mass-based,1.00
US Rate-based (standalone),US,Rate-based,0.12
```

`data/scenarios_us.csv`

```csv
scenario,global_emissions_pct,reverse_leakage_pct,welfare_bn,out_flat_pct,out_long_pct,out_macro_pct,carbon_price
E. M-BCA,-0.26,23.05,-0.88,1.21,1.11,-0.018,87.90
F. R-BCA,-0.06,14.93,-0.32,0.40,0.86,-0.004,
G. DM-BCA,-0.06,15.72,-0.01,0.11,0.19,-0.003,10.19
```

-----

## I. Referenzbeispiel + vollständige HTML-Umsetzung

**Befund (ZEW DP 26-021):** Park/Rausch/Karplus (05/2026), *Environmental Ambition and Economic Protectionism: The Design of Border Carbon Adjustments.* Kernaussage: Ein **benchmarkbasierter** CO₂-Grenzausgleich überträgt nur **36 %** (EU) bzw. **12 %** (US-Alleingang) des nominalen CO₂-Preises an die Grenze; das erhöht Leakage (16 → 36 %), Wohlfahrtsverluste (+55 %) und vertikale Leakage (Roheisenimporte ×2, Preis −41 %).

**Story-Aufbau (verbindlich für die Vorlage):** Hero mit Signal-Meter (100/36/12 %) → KPI-Karten → „Zwei Bauarten” → interaktiver EU-Szenarien-Explorer → Mechanismus (Reshuffling, vertikale Leakage) → interaktiver Preis-Explorer → US-Alleingang → drei Schlussfolgerungen → Methoden/Quelle.

**Signature:** „Signal-Attenuation” — Farbe kodiert Inhalt (`signal` = übertragenes Preissignal, `diluted` = Verlust/Leakage). Die Boldness liegt allein im Hero; der Rest bleibt ruhig.

Vollständige, eigenständige Umsetzung (`templates/standalone.html`, hier mit Referenzdaten befüllt):

```html
<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wie viel Klimaschutz kommt an der Grenze an? – ZEW DP 26-021</title>
<style>
  /* --- ZEW Haus-CD: PLATZHALTER-Farben, durch offizielles CD ersetzen.
        Farben sind semantisch: signal = übertragenes Preissignal, diluted = Verlust. --- */
  :root{
    --ink:#16223D; --signal:#0F7E8C; --diluted:#C0492F; --mute:#6B7280;
    --paper:#ffffff; --paper2:#F6F8FA; --line:rgba(22,34,61,.12);
    --serif: "Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
    --sans: system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono: ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  @media (prefers-reduced-motion: reduce){ html{scroll-behavior:auto} *{transition:none!important} }
  body{
    margin:0; background:var(--paper); color:var(--ink);
    font-family:var(--sans); font-size:18px; line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }
  .wrap{max-width:760px; margin-inline:auto; padding:0 22px}
  .wide{max-width:920px}

  h1,h2,h3{font-family:var(--serif); font-weight:600; line-height:1.12; color:var(--ink)}
  a{color:var(--signal)}

  /* ---- Hero / Signature ---- */
  header.hero{border-bottom:1px solid var(--line); padding:64px 0 36px}
  .eyebrow{font-family:var(--mono); text-transform:uppercase; letter-spacing:.14em;
    font-size:.72rem; color:var(--mute)}
  h1.title{font-size:clamp(2rem,5.2vw,3.1rem); margin:.5rem 0 1rem; max-width:20ch}
  .lede{font-size:1.18rem; color:rgba(22,34,61,.82); max-width:42rem}
  .lede strong{color:var(--ink)}

  .meter{margin-top:34px; display:grid; gap:12px}
  .meter .row{display:grid; grid-template-columns:13rem 1fr 4rem; align-items:center; gap:14px}
  .meter .name{font-size:.92rem}
  .meter .track{height:26px; border-radius:3px; background:rgba(22,34,61,.08); overflow:hidden}
  .meter .fill{height:100%; border-radius:3px; transform-origin:left;
    animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
  @media (prefers-reduced-motion: reduce){ .meter .fill{animation:none} }
  @keyframes grow{from{transform:scaleX(0)} to{transform:scaleX(1)}}
  .fill.full{background:var(--signal)}
  .fill.dil{background:var(--diluted)}
  .meter .pct{font-variant-numeric:tabular-nums; font-weight:700; text-align:right}
  .note{font-size:.82rem; color:var(--mute); margin-top:.5rem}
  @media (max-width:600px){ .meter .row{grid-template-columns:1fr auto} .meter .track{grid-column:1/-1; order:3} }

  /* ---- KPI ---- */
  .kpis{display:grid; grid-template-columns:repeat(auto-fit,minmax(11rem,1fr)); gap:14px; margin:34px auto}
  .kpi{border:1px solid var(--line); border-radius:6px; padding:16px 18px; background:var(--paper)}
  .kpi .num{font-family:var(--serif); font-size:2.2rem; line-height:1; color:var(--diluted); font-variant-numeric:tabular-nums}
  .kpi .lab{font-size:.86rem; color:rgba(22,34,61,.78); margin-top:.5rem}

  section{padding:30px 0}
  section h2{font-size:1.55rem; margin:.2em 0 .5em}
  ul.clean{padding-left:1.1em}
  ul.clean li{margin:.5em 0}

  /* ---- Charts ---- */
  .panel{border:1px solid var(--line); border-radius:8px; padding:18px; background:var(--paper2); margin-top:14px}
  .controls{display:flex; flex-wrap:wrap; gap:8px; margin-bottom:6px}
  .controls .lbl{font-size:.8rem; color:var(--mute); width:100%; font-family:var(--mono); text-transform:uppercase; letter-spacing:.08em}
  button.seg{font:inherit; font-size:.86rem; cursor:pointer; border:1px solid var(--line);
    background:var(--paper); color:var(--ink); padding:7px 11px; border-radius:999px}
  button.seg[aria-pressed="true"]{background:var(--ink); color:#fff; border-color:var(--ink)}
  button.seg:focus-visible{outline:3px solid color-mix(in srgb,var(--signal) 60%,transparent); outline-offset:2px}
  svg{width:100%; height:auto; display:block}
  .bar{transition:y .35s ease, height .35s ease}
  .blabel{font-size:12px; fill:var(--ink); font-variant-numeric:tabular-nums; font-family:var(--sans)}
  .xlabel{font-size:12px; fill:rgba(22,34,61,.8); font-family:var(--sans)}
  .axis{stroke:rgba(22,34,61,.35)}
  .legend{font-size:.78rem; color:var(--mute); margin-top:10px}
  .legend span{display:inline-flex; align-items:center; gap:6px; margin-right:14px}
  .sw{width:11px; height:11px; border-radius:2px; display:inline-block}

  /* ---- Takeaways ---- */
  .take{counter-reset:t; margin:8px 0}
  .take .it{display:grid; grid-template-columns:2.4rem 1fr; gap:16px; padding:16px 0; border-top:1px solid var(--line)}
  .take .it::before{counter-increment:t; content:counter(t); font-family:var(--serif); font-size:1.5rem; color:var(--signal)}

  footer{border-top:1px solid var(--line); margin-top:24px; padding:26px 0 70px}
  footer .note{max-width:48rem}
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <div class="eyebrow">ZEW Discussion Paper 26-021 · Befund kompakt</div>
    <h1 class="title">Wie viel Klimaschutz kommt an der Grenze an?</h1>
    <p class="lede">
      CO₂-Grenzausgleiche (Border Carbon Adjustments) sollen Klimaschutz und Industrie
      zugleich schützen. Entscheidend ist die <strong>Bauart</strong>: Ein <strong>mengenbasiertes</strong>
      Design bepreist die gesamten eingebetteten Emissionen, ein <strong>benchmarkbasiertes</strong>
      nur die Abweichung von einem Richtwert. Letzteres entlastet die Abnehmer – aber nur ein
      Bruchteil des CO₂-Preises erreicht die ausländischen Produzenten.
    </p>

    <div class="meter" aria-label="Anteil des CO2-Preissignals, der die Grenze erreicht">
      <div class="row"><span class="name">EU · mengenbasiert</span>
        <span class="track"><span class="fill full" style="width:100%"></span></span><span class="pct">100&nbsp;%</span></div>
      <div class="row"><span class="name">EU · benchmarkbasiert</span>
        <span class="track"><span class="fill dil" style="width:36%"></span></span><span class="pct">36&nbsp;%</span></div>
      <div class="row"><span class="name">US · benchmark (allein)</span>
        <span class="track"><span class="fill dil" style="width:12%"></span></span><span class="pct">12&nbsp;%</span></div>
    </div>
    <p class="note">Effektiver Signal-Anteil λ: Anteil des nominalen CO₂-Preises, der als
      Grenzabgabe tatsächlich auf ausländische Produzenten wirkt. Mengenbasiert = 100&nbsp;%.</p>
  </div>
</header>

<div class="wrap wide">
  <div class="kpis">
    <div class="kpi"><div class="num">36&nbsp;%</div><div class="lab">des CO₂-Preises erreichen unter dem EU-Benchmark-Design die ausländischen Produzenten – ein Rabatt von 64&nbsp;%.</div></div>
    <div class="kpi"><div class="num">+55&nbsp;%</div><div class="lab">höhere Wohlfahrtsverluste der EU gegenüber dem mengenbasierten Design (1,38 statt 0,89&nbsp;Mrd.&nbsp;USD).</div></div>
    <div class="kpi"><div class="num">16→36&nbsp;%</div><div class="lab">so stark steigt die Carbon-Leakage-Rate vom mengen- zum benchmarkbasierten Design.</div></div>
    <div class="kpi"><div class="num">×2</div><div class="lab">Verdopplung der EU-Roheisenimporte (1,73→3,50&nbsp;Mt); Importpreis rund 41&nbsp;% niedriger.</div></div>
  </div>
</div>

<div class="wrap">
  <section>
    <h2>Zwei Bauarten, ein Zielkonflikt</h2>
    <p>Stahl steht für rund 7&nbsp;% der globalen Treibhausgasemissionen, ist stark gehandelt
    und technologisch heterogen: Hochofen-Route (BF-BOF) und Elektrolichtbogen (EAF)
    unterscheiden sich massiv in der Emissionsintensität. Genau diese Streuung macht das
    Design des Grenzausgleichs folgenreich.</p>
    <ul class="clean">
      <li><strong>Mengenbasiert (wie EU-CBAM):</strong> bepreist jede Tonne eingebetteter Emissionen. Erhält das Preissignal, schützt die heimische Vorstufe, verteuert aber die Abnehmerprodukte stärker.</li>
      <li><strong>Benchmarkbasiert:</strong> bepreist nur die Abweichung von einem Intensitäts-Richtwert. Wirkt wie eine CO₂-Abgabe plus impliziter Mengensubvention – dämpft Abnehmerpreise, verdünnt aber das Klimasignal.</li>
    </ul>
  </section>
</div>

<div class="wrap wide">
  <section>
    <h2>Befunde im Szenarienvergleich (EU)</h2>
    <p>Alle EU-Szenarien am selben Stringenzpunkt (≈ 30&nbsp;% Reduktion der heimischen
    Stahlemissionen, CO₂-Preis ≈ 88&nbsp;USD/t). Kennzahl wählen:</p>
    <div class="panel">
      <div class="controls" id="euControls"><span class="lbl">Kennzahl</span></div>
      <svg id="euChart" viewBox="0 0 720 340" role="img" aria-label="Szenarienvergleich EU"></svg>
      <div class="legend">
        <span><span class="sw" style="background:#6B7280"></span>A. Cap (ohne Grenzausgleich)</span>
        <span><span class="sw" style="background:#0F7E8C"></span>B. M-BCA (mengenbasiert)</span>
        <span><span class="sw" style="background:#C0492F"></span>C. R-BCA (benchmarkbasiert)</span>
        <span><span class="sw" style="background:#16223D"></span>D. DM-BCA (rabattiert)</span>
      </div>
      <p class="note">Quelle: DP 26-021, Tab. 2 (Panel a). D = mengenbasiert, rabattiert auf dieselbe globale Emissionswirkung wie C.</p>
    </div>
    <p style="margin-top:14px">Das Muster ist konsistent: Das benchmarkbasierte Design (C) senkt
    die globalen Emissionen weniger (−1,02 statt −1,34&nbsp;%), erhöht die Leakage (36 statt
    16&nbsp;%) und kostet mehr Wohlfahrt – bei niedrigerem effektivem CO₂-Preis an der Grenze.</p>
  </section>
</div>

<div class="wrap">
  <section>
    <h2>Der Mechanismus: Reshuffling und vertikale Leakage</h2>
    <ul class="clean">
      <li><strong>Reshuffling:</strong> Exporteure lenken ihre ohnehin saubersten Einheiten (EAF) in den regulierten Markt, ohne global sauberer zu produzieren. Der Reshuffling-Index für Langstahl fällt von 1,08 auf 0,55.</li>
      <li><strong>Vertikale Leakage:</strong> Roheisen ist technologisch homogen; ein Benchmark greift dort kaum. Unter dem benchmarkbasierten Design bleibt der Importpreis für Roheisen rund 41&nbsp;% niedriger, die EU-Importe verdoppeln sich (1,73→3,50&nbsp;Mt). Die CO₂-intensive Vorstufe wandert ins Ausland.</li>
    </ul>
  </section>
</div>

<div class="wrap wide">
  <section>
    <h2>Wer trägt die Kosten? Import- und Nutzerpreise (EU)</h2>
    <p>Der politische Reiz des benchmarkbasierten Designs ist der Schutz der Abnehmerpreise –
    auf Kosten der heimischen Vorstufe und des Klimasignals.</p>
    <div class="panel">
      <div class="controls" id="prControls"><span class="lbl">Preisreihe</span></div>
      <svg id="prChart" viewBox="0 0 720 320" role="img" aria-label="Preisänderungen EU"></svg>
      <p class="note">Quelle: DP 26-021, Tab. 4 (% ggü. Baseline). Beispiel Flachstahl: Nutzerpreis
      steigt benchmarkbasiert um 24,2&nbsp;% statt 34,6&nbsp;% – rund 30&nbsp;% weniger, aber zum
      Preis eines schwächeren Klimasignals.</p>
    </div>
  </section>
</div>

<div class="wrap">
  <section>
    <h2>Im US-Alleingang fast wirkungslos</h2>
    <p>Ohne nationalen CO₂-Preis als Anker wirkt ein benchmarkbasierter Grenzausgleich kaum
    als Klimapolitik: Nur rund ein Achtel des Preissignals (λ ≈ 0,12) erreicht die Grenze;
    das Instrument verschiebt vor allem Renten und verlagert Produktion zurück ins Inland
    („reverse leakage"), statt im Ausland Emissionen zu senken.</p>
  </section>

  <section>
    <h2>Was folgt daraus</h2>
    <div class="take">
      <div class="it"><div>Grenzausgleich und nationaler CO₂-Preis sind <strong>Komplemente, kein Ersatz</strong>. Ein benchmarkbasiertes Standalone-Instrument verschiebt vor allem Renten.</div></div>
      <div class="it"><div>Das <strong>Benchmark-Design entscheidet über die Umweltwirkung</strong> – besonders die Behandlung homogener Vorprodukte wie Roheisen. Gilt über Stahl hinaus für energieintensive, handelsexponierte Sektoren.</div></div>
      <div class="it"><div>Belastbare Bewertung braucht Modelle mit <strong>Technologie-Heterogenität und vertikalen Lieferketten</strong> – sonst bleiben Reshuffling und vertikale Leakage unsichtbar.</div></div>
    </div>
  </section>
</div>

<footer>
  <div class="wrap">
    <p class="note"><strong>Methode:</strong> Plant-level allgemeines Gleichgewichtsmodell der
    globalen Stahl-Lieferkette (~300 Werke, 48 Länder, 15 Regionen; Daten: CRU, Global Steel
    Plant Tracker, worldsteel, UN&nbsp;Comtrade, GTAP&nbsp;11). Vergleichspunkt: 30&nbsp;% EU-Reduktion,
    CO₂-Preis ≈ 88&nbsp;USD/t.<br>
    <strong>Quelle:</strong> Eunseong Park, Sebastian Rausch, Valerie J. Karplus (2026):
    <em>Environmental Ambition and Economic Protectionism: The Design of Border Carbon
    Adjustments.</em> ZEW Discussion Paper No.&nbsp;26-021. Alle Zahlen aus dem Paper; diese
    Seite ist eine nicht-amtliche Aufbereitung für die Wissenschaftskommunikation.</p>
  </div>
</footer>

<script>
const COLORS = {"A. Cap":"#6B7280","B. M-BCA":"#0F7E8C","C. R-BCA":"#C0492F","D. DM-BCA":"#16223D"};

const EU = [
  {scenario:"A. Cap",    global_emissions_pct:-0.69, leakage_pct:56.44, welfare_bn:-0.39, out_long_pct:-6.68, carbon_price:69.71},
  {scenario:"B. M-BCA",  global_emissions_pct:-1.34, leakage_pct:16.05, welfare_bn:-0.89, out_long_pct:-4.60, carbon_price:87.90},
  {scenario:"C. R-BCA",  global_emissions_pct:-1.02, leakage_pct:36.18, welfare_bn:-1.38, out_long_pct:-6.19, carbon_price:74.94},
  {scenario:"D. DM-BCA", global_emissions_pct:-1.02, leakage_pct:36.18, welfare_bn:-0.07, out_long_pct:-5.79, carbon_price:76.91}
];
const EU_METRICS = [
  ["Leakage-Rate (%)","leakage_pct"],
  ["Globale Emissionen (%)","global_emissions_pct"],
  ["EU-Wohlfahrt (Mrd. USD)","welfare_bn"],
  ["CO₂-Preis (USD/t)","carbon_price"],
  ["Output Langstahl (%)","out_long_pct"]
];

const PRICES = [
  {scenario:"A. Cap",    import_flat_pct:0.69,  import_long_pct:-0.26, user_flat_pct:19.88, user_long_pct:8.70},
  {scenario:"B. M-BCA",  import_flat_pct:37.10, import_long_pct:29.90, user_flat_pct:34.58, user_long_pct:16.36},
  {scenario:"C. R-BCA",  import_flat_pct:10.95, import_long_pct:5.70,  user_flat_pct:24.18, user_long_pct:10.49},
  {scenario:"D. DM-BCA", import_flat_pct:13.80, import_long_pct:11.47, user_flat_pct:25.61, user_long_pct:11.85}
];
const PR_SERIES = [
  ["Nutzerpreis Flachstahl","user_flat_pct"],
  ["Importpreis Flachstahl","import_flat_pct"],
  ["Nutzerpreis Langstahl","user_long_pct"],
  ["Importpreis Langstahl","import_long_pct"]
];

const SVGNS="http://www.w3.org/2000/svg";
function el(tag,attrs,txt){const n=document.createElementNS(SVGNS,tag);
  for(const k in attrs)n.setAttribute(k,attrs[k]); if(txt!=null)n.textContent=txt; return n;}

function drawBars(svgId, data, key){
  const svg=document.getElementById(svgId);
  const vb=svg.getAttribute("viewBox").split(" ").map(Number);
  const W=vb[2], H=vb[3], m={t:26,r:16,b:60,l:58};
  const iw=W-m.l-m.r, ih=H-m.t-m.b;
  svg.innerHTML="";
  const vals=data.map(d=>+d[key]);
  let min=Math.min(0,...vals), max=Math.max(0,...vals);
  if(min===max){max=min+1;}
  const span=max-min, pad=span*0.14; max+=pad; if(min<0)min-=pad; else min=0;
  const y=v=> m.t + ih*(max-v)/(max-min);
  const zeroY=y(0);
  const bw=iw/data.length;
  // zero axis
  svg.appendChild(el("line",{x1:m.l,y1:zeroY,x2:m.l+iw,y2:zeroY,class:"axis"}));
  data.forEach((d,i)=>{
    const v=+d[key];
    const cx=m.l+i*bw;
    const barW=bw*0.62, bx=cx+(bw-barW)/2;
    const top=Math.min(y(v),zeroY), h=Math.max(1,Math.abs(y(v)-zeroY));
    const r=el("rect",{x:bx,y:top,width:barW,height:h,rx:2,fill:COLORS[d.scenario],class:"bar"});
    svg.appendChild(r);
    const lbl=Number.isInteger(v*100)?(+v).toLocaleString("de-DE"):(+v).toLocaleString("de-DE");
    svg.appendChild(el("text",{x:bx+barW/2,y:(v>=0?top-7:top+h+15),"text-anchor":"middle",class:"blabel"},
      (+v).toLocaleString("de-DE")));
    svg.appendChild(el("text",{x:cx+bw/2,y:H-38,"text-anchor":"middle",class:"xlabel"},d.scenario));
  });
}

function buildControls(containerId, items, current, onPick){
  const c=document.getElementById(containerId);
  items.forEach(([label,key])=>{
    const b=document.createElement("button");
    b.className="seg"; b.textContent=label; b.setAttribute("aria-pressed", key===current);
    b.onclick=()=>{ c.querySelectorAll("button.seg").forEach(x=>x.setAttribute("aria-pressed","false"));
      b.setAttribute("aria-pressed","true"); onPick(key); };
    c.appendChild(b);
  });
}

buildControls("euControls", EU_METRICS, "leakage_pct", k=>drawBars("euChart",EU,k));
drawBars("euChart", EU, "leakage_pct");

buildControls("prControls", PR_SERIES, "user_flat_pct", k=>drawBars("prChart",PRICES,k));
drawBars("prChart", PRICES, "user_flat_pct");
</script>
</body>
</html>
```

-----

## J. Skalierbare Quarto-Variante (Hausdienst)

Gleicher Inhalt, aber über den zentralen CD-/Build-Pfad. Dateien:

`_quarto.yml`

```yaml
project:
  type: default
  output-dir: _site

brand: _brand.yml

format:
  html:
    theme: [cosmo, theme/zew.scss]
    toc: true
    toc-title: "Inhalt"
    toc-location: right
    smooth-scroll: true
    page-layout: article
    grid:
      body-width: 900px
    fig-responsive: true
    # DSGVO: alles in eine eigenständige Datei bündeln -> keine Laufzeit-Requests
    # an CDNs/Google. (Nach Build mit Netzwerk-Monitor verifizieren.)
    embed-resources: true
    lang: de
    code-tools: false
    execute:
      echo: false
      warning: false

execute:
  freeze: auto
```

`_brand.yml` (zentrale CD — Platzhalter ersetzen)

```yaml
# ---------------------------------------------------------------------------
# ZEW Haus-CD  (Quarto Brand, >= 1.6)
# ACHTUNG: Farb-Hex und Fonts sind PLATZHALTER. Vor Produktiveinsatz durch die
# offiziellen ZEW-Corporate-Design-Werte ersetzen (Farbpalette, Hausschrift).
# Farben sind hier bewusst SEMANTISCH benannt: "signal" = übertragenes Preissignal,
# "diluted" = verlorenes Signal / Leakage. Damit kodiert Farbe Inhalt, nicht Deko.
# ---------------------------------------------------------------------------
color:
  palette:
    zew-navy:    "#16223D"   # Platzhalter: Text/Headings
    zew-signal:  "#0F7E8C"   # Platzhalter: volles CO2-Preissignal (Mass-based)
    zew-diluted: "#C0492F"   # Platzhalter: Signalverlust / Leakage (Rate-based)
    zew-mute:    "#6B7280"   # Captions / Achsen
    zew-paper:   "#FFFFFF"
  primary: zew-signal
  foreground: zew-navy
  background: zew-paper

typography:
  # HINWEIS: Um DSGVO-Konformitaet sicherzustellen, werden Google Fonts nicht online geladen.
  # Schriftarten muessen als lokale WOFF2-Dateien unter theme/fonts/ liegen und 
  # in theme/zew.scss via @font-face referenziert werden.
  fonts:
    - family: Source Sans 3      # Platzhalter Body -> ZEW-Hausschrift
      source: file
      files:
        - theme/fonts/source-sans-3.woff2
    - family: Spectral           # Platzhalter Display -> ZEW-Display-Schrift
      source: file
      files:
        - theme/fonts/spectral.woff2
  base:
    family: Source Sans 3
    size: 1.05rem
  headings:
    family: Spectral
    weight: 600
```

`theme/zew.scss`

```scss
/*-- scss:defaults --*/
// Greift auf _brand.yml-Farben zu; hier nur Feinschliff.
$body-bg: #ffffff;
$content-padding-top: 0;

/*-- scss:rules --*/

// ---- Lesefluss: schmale Spalte für Fließtext, breit für Grafiken ----
.story {
  max-width: 46rem;
  margin-inline: auto;
}

// ---- Hero / Signature: Signal-Attenuation ----
.hero {
  margin: 0 0 2.5rem 0;
  padding: 3rem 0 2rem 0;
  border-bottom: 1px solid color-mix(in srgb, var(--bs-body-color) 12%, transparent);
}
.hero .eyebrow {
  font-family: var(--bs-font-monospace, monospace);
  letter-spacing: .12em;
  text-transform: uppercase;
  font-size: .72rem;
  color: var(--brand-color-zew-mute, #6B7280);
}
.hero h1 {
  font-size: clamp(1.9rem, 4.5vw, 3rem);
  line-height: 1.08;
  margin: .5rem 0 1rem 0;
  max-width: 18ch;
}
.hero .lede {
  font-size: 1.2rem;
  color: color-mix(in srgb, var(--bs-body-color) 80%, transparent);
  max-width: 40rem;
}

// Der eine "memorable" Block: wie stark das Preissignal die Grenze erreicht.
.signal-meter {
  margin: 2rem 0 0 0;
  display: grid;
  gap: .6rem;
}
.signal-row { display: grid; grid-template-columns: 12rem 1fr 4rem; align-items: center; gap: .75rem; }
.signal-row .name { font-size: .9rem; }
.signal-row .track {
  height: 1.5rem; border-radius: 2px;
  background: color-mix(in srgb, var(--bs-body-color) 8%, transparent);
  position: relative; overflow: hidden;
}
.signal-row .fill { height: 100%; border-radius: 2px; }
.signal-row .fill.full    { background: var(--brand-color-zew-signal, #0F7E8C); }
.signal-row .fill.diluted { background: var(--brand-color-zew-diluted, #C0492F); }
.signal-row .pct { font-variant-numeric: tabular-nums; font-weight: 600; text-align: right; }

@media (max-width: 600px) {
  .signal-row { grid-template-columns: 1fr; }
  .signal-row .track { order: 3; }
}

// ---- KPI-Karten ----
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
  gap: 1rem;
  margin: 2rem auto;
  max-width: 60rem;
}
.kpi {
  border: 1px solid color-mix(in srgb, var(--bs-body-color) 12%, transparent);
  border-radius: 4px; padding: 1.1rem 1.2rem;
}
.kpi .num {
  font-family: var(--bs-headings-font-family);
  font-size: 2.1rem; line-height: 1; font-variant-numeric: tabular-nums;
  color: var(--brand-color-zew-diluted, #C0492F);
}
.kpi .lab { font-size: .85rem; color: color-mix(in srgb, var(--bs-body-color) 75%, transparent); margin-top: .4rem; }

// ---- Chart-Rahmen ----
.figure-note { font-size: .8rem; color: var(--brand-color-zew-mute, #6B7280); margin-top: .4rem; }

// ---- Schlussfolgerungen ----
.takeaways { counter-reset: t; max-width: 46rem; margin-inline: auto; }
.takeaways .item { display: grid; grid-template-columns: 2.4rem 1fr; gap: 1rem; padding: 1rem 0; border-top: 1px solid color-mix(in srgb, var(--bs-body-color) 12%, transparent); }
.takeaways .item::before { counter-increment: t; content: counter(t); font-family: var(--bs-headings-font-family); font-size: 1.4rem; color: var(--brand-color-zew-signal, #0F7E8C); }
```

`build.py` (Orchestrierung, Validierung & Ausführung beider Stufen)

```python
#!/usr/bin/env python3
"""
Build-Orchestrierung fuer den ZEW Wisskomm-Visualisierungsdienst.

Führt Datenvalidierung durch (mit Graceful Degradation) und generiert wahlweise 
das Standalone-HTML (mit CSS-Feature-Flags) und/oder das Quarto-Projekt.

Aufruf:
    python build.py --target all
    python build.py --target standalone --data-dir data/ --out dist/standalone
    python build.py --target quarto --data-dir data/ --out dist/quarto
"""
from __future__ import annotations
import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent

@dataclass
class ValidationResult:
    required_ok: bool
    optional_missing: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

def validate_data(data_dir: Path, features: list[str]) -> ValidationResult:
    result = ValidationResult(required_ok=True)
    
    # 1. Pflichtdateien pruefen
    required_files = ["scenarios_eu.csv", "signal.csv"]
    for f in required_files:
        p = data_dir / f
        if not p.is_file():
            result.required_ok = False
            result.errors.append(f"Pflichtdatei fehlt: {f}")
            
    # 2. Optionale Dateien pruefen basierend auf aktivierten Features
    if "us-explorer" in features:
        if not (data_dir / "scenarios_us.csv").is_file():
            result.optional_missing.append("scenarios_us.csv")
            
    if "price-explorer" in features:
        if not (data_dir / "prices_eu.csv").is_file():
            result.optional_missing.append("prices_eu.csv")
            
    return result

def build_standalone(data_dir: Path, output_file: Path, features: list[str]) -> None:
    template_path = ROOT / "templates" / "standalone.html"
    if not template_path.is_file():
        raise FileNotFoundError(f"Template nicht gefunden: {template_path}")
        
    html = template_path.read_text(encoding="utf-8")
    
    # CSS Custom Property (Feature-Flag) im Head injizieren
    has_us = 1 if "us-explorer" in features and (data_dir / "scenarios_us.csv").is_file() else 0
    css_injection = f"<style>:root {{ --has-us-explorer: {has_us}; }}</style>"
    html = html.replace("</head>", f"  {css_injection}\n</head>")
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html, encoding="utf-8")
    print(f"Standalone-HTML erfolgreich generiert: {output_file}")

def build_quarto(data_dir: Path, output_dir: Path) -> None:
    quarto_exe = shutil.which("quarto")
    if not quarto_exe:
        raise RuntimeError("FEHLER: 'quarto' nicht im PATH. Bitte Quarto CLI installieren.")
    
    cmd = [quarto_exe, "render", str(ROOT), "--output-dir", str(output_dir)]
    print("->", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("Quarto-Build erfolgreich abgeschlossen.")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=["standalone", "quarto", "all"], default="all")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out)
    
    # Konfiguration laden
    config_path = ROOT / "config.json"
    features = ["eu-explorer"]
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            features = config.get("features", features)
        except Exception as e:
            print(f"WARNUNG: Fehler beim Lesen der config.json ({e}). Verwende Standard-Features.")
            
    # Validierung durchfuehren
    val = validate_data(data_dir, features)
    if not val.required_ok:
        print("FEHLER bei der Datenvalidierung:")
        for err in val.errors:
            print(f" - {err}")
        sys.exit(1)
        
    if val.optional_missing:
        print("WARNUNG: Folgende optionale Dateien fehlen (Graceful Degradation):")
        for m in val.optional_missing:
            print(f" - {m}")
            
    # Ausfuehrung der Builds
    if args.target in ("standalone", "all"):
        build_standalone(data_dir, out_dir / "standalone" / "index.html", features)
    if args.target in ("quarto", "all"):
        try:
            build_quarto(data_dir, out_dir / "quarto")
        except Exception as e:
            print(f"Quarto-Build fehlgeschlagen: {e}")
            if args.target == "quarto":
                sys.exit(1)

if __name__ == "__main__":
    main()
```

`config.json` (Konfigurationsdatei der Publikation)

```json
{
  "features": ["eu-explorer", "price-explorer"],
  "data_dir": "data/",
  "output_dir": "dist/",
  "publication_id": "zew-dp-26-021"
}
```

`setup.ps1` (Idempotentes Windows-Einrichtungsskript)

```powershell
# Windows-PowerShell Skript zur Vorbereitung der Build-Umgebung
param([switch]$SkipQuartoCheck)

Write-Host "--- Wisskomm-Viz Umgebung wird vorbereitet ---"

# 1. Virtuelles Environment (venv) erstellen
if (-not (Test-Path ".venv")) {
    Write-Host "Erstelle Python .venv..."
    python -m venv .venv
}

# 2. Abhängigkeiten installieren
Write-Host "Installiere Python-Bibliotheken..."
& .venv\Scripts\pip install --quiet -r requirements.txt

# 3. Font-Verzeichnis validieren
if (-not (Test-Path "theme\fonts")) {
    Write-Warning "Ordner 'theme\fonts' nicht gefunden. Bitte WOFF2-Dateien der Hausschriften dort manuell fuer den DSGVO-konformen Offline-Betrieb ablegen."
}

# 4. Quarto CLI pruefen (optional ueberspringbar)
if (-not $SkipQuartoCheck) {
    if (-not (Get-Command quarto -ErrorAction SilentlyContinue)) {
        Write-Warning "Quarto CLI nicht im PATH gefunden. Stufe 2 (Quarto) ist auf dieser Maschine nicht verfuegbar. Setup fuer Stufe 1 (Standalone) beendet."
    } else {
        Write-Host "Quarto CLI $(quarto --version) gefunden. Beide Stufen verfuegbar."
    }
}

Write-Host "--- Setup beendet ---"
```

`templates/story.qmd` (Quarto-Vorlage, mit Referenzdaten)

```qmd
---
title: "Wie viel Klimaschutz kommt an der Grenze an?"
subtitle: "CO₂-Grenzausgleich für Stahl: warum die Bauart über die Wirkung entscheidet"
lang: de
---

```{python}
#| label: data
import pandas as pd

eu     = pd.read_csv("data/scenarios_eu.csv")
us     = pd.read_csv("data/scenarios_us.csv")
prices = pd.read_csv("data/prices_eu.csv")

ojs_define(eu = eu.to_dict("records"))
ojs_define(us = us.to_dict("records"))
ojs_define(prices = prices.to_dict("records"))
```

```{=html}
<section class="hero">
  <div class="eyebrow">ZEW Discussion Paper 26-021 · Befund kompakt</div>
  <h1>Ein Grenzausgleich ist nur so stark wie das Preissignal, das ankommt.</h1>
  <p class="lede">
    Grenzausgleiche (Border Carbon Adjustments) sollen Klimaschutz und Industrie
    zugleich schützen. Entscheidend ist die Bauart: Ein <strong>mengenbasiertes</strong>
    Design bepreist die gesamten eingebetteten Emissionen, ein <strong>benchmark­basiertes</strong>
    nur die Abweichung von einem Richtwert. Letzteres entlastet die Abnehmer &mdash;
    aber nur ein Bruchteil des CO₂-Preises erreicht die ausländischen Produzenten.
  </p>

  <div class="signal-meter" aria-label="Anteil des CO2-Preissignals, der die Grenze erreicht">
    <div class="signal-row">
      <span class="name">EU · mengenbasiert</span>
      <span class="track"><span class="fill full" style="width:100%"></span></span>
      <span class="pct">100&nbsp;%</span>
    </div>
    <div class="signal-row">
      <span class="name">EU · benchmarkbasiert</span>
      <span class="track"><span class="fill diluted" style="width:36%"></span></span>
      <span class="pct">36&nbsp;%</span>
    </div>
    <div class="signal-row">
      <span class="name">US · benchmark (allein)</span>
      <span class="track"><span class="fill diluted" style="width:12%"></span></span>
      <span class="pct">12&nbsp;%</span>
    </div>
  </div>
  <p class="figure-note">Effektiver Signal-Anteil &lambda;: Anteil des nominalen CO₂-Preises,
  der als Grenzabgabe tatsächlich auf ausländische Produzenten wirkt. Mengenbasiert = 100&nbsp;%.</p>
</section>
```

```{=html}
<div class="kpi-grid">
  <div class="kpi"><div class="num">36&nbsp;%</div><div class="lab">des CO₂-Preises erreichen unter dem EU-Benchmark-Design die ausländischen Produzenten – ein Rabatt von 64&nbsp;%.</div></div>
  <div class="kpi"><div class="num">+55&nbsp;%</div><div class="lab">höhere Wohlfahrtsverluste der EU gegenüber dem mengenbasierten Design (1,38 statt 0,89 Mrd. USD).</div></div>
  <div class="kpi"><div class="num">16&nbsp;→&nbsp;36&nbsp;%</div><div class="lab">so stark steigt die Carbon-Leakage-Rate vom mengen- zum benchmarkbasierten Design.</div></div>
  <div class="kpi"><div class="num">&times;2</div><div class="lab">Verdopplung der EU-Roheisenimporte (1,73&nbsp;→&nbsp;3,50&nbsp;Mt); Importpreis rund 41&nbsp;% niedriger.</div></div>
</div>
```

## Zwei Bauarten, ein Zielkonflikt

Stahl steht für rund 7&nbsp;% der globalen Treibhausgasemissionen, ist stark gehandelt und
technologisch heterogen: Hochofen-Route (BF-BOF) und Elektrolichtbogen (EAF) unterscheiden
sich massiv in Emissionsintensität. Genau diese Streuung macht das Design des Grenzausgleichs
folgenreich.

- **Mengenbasiert (Mass-based, wie EU-CBAM):** bepreist jede Tonne eingebetteter Emissionen. Erhält das Preissignal, schützt die heimische Vorstufe, verteuert aber die Abnehmerprodukte stärker.
- **Benchmarkbasiert (Rate-based):** bepreist nur die Abweichung von einem Intensitäts-Richtwert. Wirkt wie eine CO₂-Abgabe plus impliziter Mengensubvention – dämpft Abnehmerpreise, verdünnt aber das Klimasignal.

## Befunde im Vergleich der Szenarien (EU)

Die EU-Szenarien vergleichen denselben Stringenzpunkt (≈ 30&nbsp;% Reduktion der heimischen
Stahlemissionen, CO₂-Preis ≈ 88&nbsp;USD/t). Kennzahl wählen:

```{ojs}
//| label: eu-explorer
colors = ({
  "A. Cap":    "#6B7280",
  "B. M-BCA":  "#0F7E8C",
  "C. R-BCA":  "#C0492F",
  "D. DM-BCA": "#16223D"
})

viewof metric = Inputs.select(
  new Map([
    ["Globale Emissionen (%)",        "global_emissions_pct"],
    ["Leakage-Rate (%)",              "leakage_pct"],
    ["EU-Wohlfahrt (Mrd. USD)",       "welfare_bn"],
    ["CO₂-Preis (USD/t)",             "carbon_price"],
    ["Output Langstahl (%)",          "out_long_pct"]
  ]),
  {label: "Kennzahl", value: "leakage_pct"}
)

Plot.plot({
  marginLeft: 70,
  marginBottom: 64,
  height: 340,
  x: {label: null, domain: eu.map(d => d.scenario)},
  y: {label: null, grid: true, zero: true},
  marks: [
    Plot.barY(eu, {x: "scenario", y: metric, fill: d => colors[d.scenario]}),
    Plot.ruleY([0]),
    Plot.text(eu, {
      x: "scenario", y: metric, text: d => d[metric],
      dy: d => d[metric] >= 0 ? -8 : 14, fontWeight: 600
    })
  ]
})
```

::: figure-note
**A. Cap** = EU-Klimaziel ohne Grenzausgleich · **B. M-BCA** = mengenbasiert ·
**C. R-BCA** = benchmarkbasiert · **D. DM-BCA** = mengenbasiert, rabattiert auf dieselbe
globale Emissionswirkung wie C. — Quelle: DP 26-021, Tab. 2 (Panel a).
:::

Das Muster ist konsistent: Das benchmarkbasierte Design (C) senkt die globalen Emissionen
weniger (−1,02 statt −1,34&nbsp;%), erhöht die Leakage (36 statt 16&nbsp;%) und kostet mehr
Wohlfahrt – bei niedrigerem effektivem CO₂-Preis an der Grenze.

## Der Mechanismus: Reshuffling und vertikale Leakage

Zwei Kanäle treiben das Ergebnis:

- **Reshuffling:** Exporteure lenken ihre ohnehin saubersten Einheiten (EAF) in den regulierten Markt, ohne global sauberer zu produzieren. Der Reshuffling-Index für Langstahl fällt von 1,08 auf 0,55.
- **Vertikale Leakage:** Roheisen ist technologisch homogen; ein Benchmark greift dort kaum. Unter dem benchmarkbasierten Design bleibt der Importpreis für Roheisen rund 41&nbsp;% niedriger, die EU-Importe verdoppeln sich (1,73&nbsp;→&nbsp;3,50&nbsp;Mt). Die CO₂-intensive Vorstufe wandert ins Ausland.

## Wer trägt die Kosten? Import- und Nutzerpreise (EU)

Der politische Reiz des benchmarkbasierten Designs ist der Schutz der Abnehmerpreise –
auf Kosten der heimischen Vorstufe und des Klimasignals.

```{ojs}
//| label: price-explorer
viewof preis = Inputs.radio(
  new Map([
    ["Importpreis Flachstahl", "import_flat_pct"],
    ["Nutzerpreis Flachstahl", "user_flat_pct"],
    ["Importpreis Langstahl",  "import_long_pct"],
    ["Nutzerpreis Langstahl",  "user_long_pct"]
  ]),
  {label: "Preisreihe", value: "user_flat_pct"}
)

Plot.plot({
  marginLeft: 70,
  marginBottom: 64,
  height: 320,
  x: {label: null, domain: prices.map(d => d.scenario)},
  y: {label: "% ggü. Baseline", grid: true, zero: true},
  marks: [
    Plot.barY(prices, {x: "scenario", y: preis, fill: d => colors[d.scenario]}),
    Plot.ruleY([0]),
    Plot.text(prices, {x: "scenario", y: preis, text: d => d[preis], dy: -8, fontWeight: 600})
  ]
})
```

::: figure-note
Quelle: DP 26-021, Tab. 4. Beispiel Flachstahl: Nutzerpreis steigt benchmarkbasiert um
24,2&nbsp;% statt 34,6&nbsp;% (mengenbasiert) – rund 30&nbsp;% weniger, aber zum Preis eines
schwächeren Klimasignals.
:::

## Im US-Alleingang fast wirkungslos

Ohne nationalen CO₂-Preis als Anker wirkt ein benchmarkbasierter Grenzausgleich kaum als
Klimapolitik: Nur rund ein Achtel des Preissignals (λ ≈ 0,12) erreicht die Grenze; das
Instrument verschiebt vor allem Renten und verlagert Produktion zurück ins Inland
(„reverse leakage"), statt im Ausland Emissionen zu senken.

## Was folgt daraus

```{=html}
<div class="takeaways">
  <div class="item"><div>Grenzausgleich und nationaler CO₂-Preis sind <strong>Komplemente, kein Ersatz</strong>. Ein benchmarkbasiertes Standalone-Instrument verschiebt vor allem Renten.</div></div>
  <div class="item"><div>Das <strong>Benchmark-Design entscheidet über die Umweltwirkung</strong> – besonders die Behandlung homogener Vorprodukte wie Roheisen. Gilt über Stahl hinaus für energieintensive, handelsexponierte Sektoren.</div></div>
  <div class="item"><div>Belastbare Bewertung braucht Modelle mit <strong>Technologie-Heterogenität und vertikalen Lieferketten</strong> – sonst bleiben Reshuffling und vertikale Leakage unsichtbar.</div></div>
</div>
```

---

::: figure-note
**Methode:** Plant-level allgemeines Gleichgewichtsmodell der globalen Stahl-Lieferkette
(~300 Werke, 48 Länder, 15 Regionen; Daten: CRU, Global Steel Plant Tracker, worldsteel,
UN Comtrade, GTAP&nbsp;11). Vergleichspunkt: 30&nbsp;% EU-Reduktion, CO₂-Preis ≈ 88&nbsp;USD/t.
**Quelle:** Eunseong Park, Sebastian Rausch, Valerie J. Karplus (2026): *Environmental
Ambition and Economic Protectionism: The Design of Border Carbon Adjustments.*
ZEW Discussion Paper No.&nbsp;26-021. Alle Zahlen aus dem Paper; diese Seite ist eine
nicht-amtliche Aufbereitung für die Wissenschaftskommunikation.
:::
```

**Build:**

```bash
# 1. Einrichtung der Umgebung
powershell -ExecutionPolicy Bypass -File .\setup.ps1

# 2. Ausführung des Builds
python build.py --target all
python build.py --target standalone --data-dir data/ --out dist/standalone
python build.py --target quarto --data-dir data/ --out dist/quarto
```

-----

## K. Konventionen & Akzeptanzkriterien (für Cursor/Codex/Antigravity)

**Konventionen**

- Ausgabesprache **Deutsch**; nüchtern, ohne Floskeln; Fachbegriffe beibehalten.
- **Keine externen Laufzeit-Aufrufe** (keine CDNs, keine Google-Fonts, keine Tracker). Bibliotheken nur, wenn lokal gebündelt.
- **Keine** `localStorage`/`sessionStorage`/Browser-Storage.
- Farben **semantisch** über CSS-Variablen bzw. `_brand.yml`; eine zentrale Farbquelle, Chart-Farb-Map synchron halten.
- Zahlen nur aus dem gelieferten Datensatz; Formatierung de-DE im Code, Punkt-Dezimaltrennung in CSV.
- Spaltennamen des Datenvertrags (Teil H) sind bindend.

**Definition of Done**

1. Seite rendert als **eine** eigenständige Datei (Standalone) bzw. baut fehlerfrei via `build.py` (Quarto).
2. Alle Diagramme reagieren auf ihre Bedienelemente, ohne Backend.
3. Negative Werte werden mit Null-Basislinie korrekt dargestellt.
4. Responsiv bis Mobil; sichtbarer Tastaturfokus; `prefers-reduced-motion` respektiert.
5. Netzwerk-Monitor nach Build: **keine** ausgehenden Requests (Standalone) bzw. dokumentierte Build-Zeit-Fonts (Quarto).
6. CD-Platzhalter und Quellen-/Methoden-Footer vorhanden; Freigabe-Gate vermerkt.
7. **Validierungs- & Fehlerverhalten:** `build.py` bricht bei fehlenden Pflichtdateien (`scenarios_eu.csv`, `signal.csv`) oder falschen Schemata kontrolliert ab. Fehlen optionale Dateien, wird der Build mit Warnungen im Log fortgesetzt (Graceful Degradation).
8. **CSS-Feature-Flags:** Optionale Blöcke im Standalone-HTML werden rein CSS-basiert über die im `<head>` injizierte Variable `--has-us-explorer` gesteuert.
9. **Lokales Font-Hosting:** Google Fonts dürfen nicht über externe URLs nachgeladen werden. Lokale `.woff2` Schriftdateien müssen im Ordner `theme/fonts/` liegen und per `@font-face` im SCSS referenziert sein.

**Aufgabe für einen Agenten (Kurzform):** „Erzeuge aus `data/*.csv` und dem Story-Aufbau (Teil I) eine `index.html` nach `templates/standalone.html`. Halte Datenvertrag, Konventionen und Definition of Done ein. Keine externen Abhängigkeiten.”

-----

## L. Quellen

- Eunseong Park, Sebastian Rausch, Valerie J. Karplus (2026): *Environmental Ambition and Economic Protectionism: The Design of Border Carbon Adjustments.* ZEW Discussion Paper No. 26-021.
- Alle Kennzahlen dieser Spezifikation stammen aus diesem Paper (Tab. 2, Tab. 3, Tab. 4, Abschnitt V.B). Diese Aufbereitung ist nicht-amtlich.