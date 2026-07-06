import os
import json

SYSTEM_PROMPT = """Du bist ein Experte für Wissenschaftskommunikation am ZEW und Datenjournalist.
Deine Aufgabe ist es, aus dem Rohtext eines wissenschaftlichen Discussion Papers (Stahl-Grenzausgleich / Border Carbon Adjustments) die wesentlichen Kernaussagen, Kennzahlen und Datenreihen zu extrahieren.

Du MUSST das Ergebnis als ein einziges, valides JSON-Objekt zurückgeben. Gib KEINEN Freitext, keine Erklärungen und kein Markdown (wie ```json ... ```) aus, sondern NUR das reine JSON-Objekt.

Das JSON-Objekt muss EXAKT folgende Struktur aufweisen:
{
  "title": "Prägnanter, spannender Titel (deutsch)",
  "subtitle": "Kernaussage als Untertitel (deutsch)",
  "eyebrow": "Z.B. ZEW Discussion Paper 26-021 · Befund kompakt",
  "lede": "Einleitender Text (Lede-Absatz, deutsch) - erklärt kurz das Problem und den Zielkonflikt (Bauart des BCA). Nutze HTML-Tags wie <strong> zur Betonung wichtiger Begriffe.",
  "signal": [
    {"label": "EU · mengenbasiert", "setting": "EU", "design": "mengenbasiert", "lambda": 1.00, "pct": 100},
    {"label": "EU · benchmarkbasiert", "setting": "EU", "design": "benchmarkbasiert", "lambda": 0.36, "pct": 36},
    {"label": "US · benchmark (allein)", "setting": "US", "design": "benchmarkbasiert", "lambda": 0.12, "pct": 12}
  ],
  "kpis": [
    {"num": "36 %", "lab": "Beschreibung der Kennzahl (z.B. des effektiven CO2-Preissignals an der Grenze)."},
    {"num": "+55 %", "lab": "Beschreibung der Wohlfahrtsverluste."},
    {"num": "16→36 %", "lab": "Anstieg der Carbon-Leakage-Rate."},
    {"num": "x2", "lab": "Verdopplung der Importe von Roheisen."}
  ],
  "section1_title": "Zwei Bauarten, ein Zielkonflikt",
  "section1_text": "<p>Erläuterung des Unterschieds zwischen mengenbasiertem (Mass-based, CBAM) und benchmarkbasiertem (Rate-based) Grenzausgleich. Nutze Absätze und starke Betonungen.</p>",
  "section2_title": "Befunde im Szenarienvergleich (EU)",
  "section2_text": "Kurze Einleitung zum EU-Szenarien-Explorer. Erwähne den Vergleichspunkt (z.B. 30% Reduktion, CO2-Preis von ~88 USD/t).",
  "scenarios_eu": [
    {"scenario": "A. Cap", "global_emissions_pct": -0.69, "leakage_pct": 56.44, "welfare_bn": -0.39, "out_long_pct": -6.68, "carbon_price": 69.71},
    {"scenario": "B. M-BCA", "global_emissions_pct": -1.34, "leakage_pct": 16.05, "welfare_bn": -0.89, "out_long_pct": -4.60, "carbon_price": 87.90},
    {"scenario": "C. R-BCA", "global_emissions_pct": -1.02, "leakage_pct": 36.18, "welfare_bn": -1.38, "out_long_pct": -6.19, "carbon_price": 74.94},
    {"scenario": "D. DM-BCA", "global_emissions_pct": -1.02, "leakage_pct": 36.18, "welfare_bn": -0.07, "out_long_pct": -5.79, "carbon_price": 76.91}
  ],
  "section3_title": "Der Mechanismus: Reshuffling und vertikale Leakage",
  "section3_text": "Erklärung der Mechanismen (Reshuffling sauberer Exporte, Verlagerung homogener Vorprodukte wie Roheisen). Nutze HTML-Listen <ul><li>...</li></ul>.",
  "section4_title": "Wer trägt die Kosten? Import- und Nutzerpreise (EU)",
  "section4_text": "Erklärung der Auswirkungen auf die Preise für Importeure und heimische Abnehmer (z.B. Flachstahl, Langstahl).",
  "prices_eu": [
    {"scenario": "A. Cap", "import_flat_pct": 0.69, "import_long_pct": -0.26, "user_flat_pct": 19.88, "user_long_pct": 8.70},
    {"scenario": "B. M-BCA", "import_flat_pct": 37.10, "import_long_pct": 29.90, "user_flat_pct": 34.58, "user_long_pct": 16.36},
    {"scenario": "C. R-BCA", "import_flat_pct": 10.95, "import_long_pct": 5.70, "user_flat_pct": 24.18, "user_long_pct": 10.49},
    {"scenario": "D. DM-BCA", "import_flat_pct": 13.80, "import_long_pct": 11.47, "user_flat_pct": 25.61, "user_long_pct": 11.85}
  ],
  "section5_title": "Im US-Alleingang fast wirkungslos",
  "section5_text": "Analyse eines US-Alleingangs ohne nationalen CO2-Preis (λ ≈ 12% an der Grenze).",
  "scenarios_us": [
    {"scenario": "E. M-BCA", "global_emissions_pct": -0.26, "reverse_leakage_pct": 23.05, "welfare_bn": -0.88, "out_flat_pct": 1.21, "out_long_pct": 1.11, "carbon_price": 87.90},
    {"scenario": "F. R-BCA", "global_emissions_pct": -0.06, "reverse_leakage_pct": 14.93, "welfare_bn": -0.32, "out_flat_pct": 0.40, "out_long_pct": 0.86, "carbon_price": 0.0},
    {"scenario": "G. DM-BCA", "global_emissions_pct": -0.06, "reverse_leakage_pct": 15.72, "welfare_bn": -0.01, "out_flat_pct": 0.11, "out_long_pct": 0.19, "carbon_price": 10.19}
  ],
  "takeaways": [
    "Erste Schlussfolgerung (Komplementarität von CO2-Preis und Grenzausgleich)",
    "Zweite Schlussfolgerung (Bedeutung homogener Vorprodukte wie Roheisen)",
    "Dritte Schlussfolgerung (Modellierung von Technologie-Heterogenität)"
  ],
  "methodology": "Kurzer Absatz zur Methodik (Modelltyp, Datenquellen wie CRU, worldsteel, etc.) und offizieller Quellenangabe der Autoren."
}

WICHTIG: 
- Alle Zahlen in den Daten-Arrays müssen numerisch sein (Dezimalpunkt verwenden).
- Fehlen Daten im Paper, schätze sie plausibel anhand der Kernaussagen oder setze sie konsistent ein.
- Übersetze Fachausdrücke sinnvoll ins Deutsche, behalte etablierte Begriffe (z. B. Carbon Leakage, Reshuffling, Flachstahl, Langstahl) bei.
- Richte dich nach den initialen Wünschen und Korrekturhinweisen des Nutzers.
"""

async def query_claude(prompt_history: list[dict], api_key: str = None) -> dict:
    """Sendet den Verlauf an den gewählten Provider (Anthropic Claude oder Scaleway GLM).

    Die Auswahl erfolgt über WISSKOMM_LLM_PROVIDER ('anthropic' oder 'scaleway') in .env.
    """
    provider = os.environ.get("WISSKOMM_LLM_PROVIDER", "").lower()
    
    # Auto-Erkennung, falls nicht explizit gesetzt
    if not provider:
        if os.environ.get("SCW_SECRET_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
            provider = "scaleway"
        else:
            provider = "anthropic"

    if provider == "scaleway":
        # Lazy Import, um Fehler zu vermeiden falls openai-Bibliothek nicht installiert ist
        from openai import AsyncOpenAI
        
        scw_key = api_key or os.environ.get("SCW_SECRET_KEY")
        if not scw_key:
            raise ValueError("Scaleway API Key (SCW_SECRET_KEY) nicht konfiguriert.")
            
        base_url = os.environ.get("SCW_BASE_URL", "https://api.scaleway.ai/v1")
        client = AsyncOpenAI(
            base_url=base_url,
            api_key=scw_key
        )
        
        # System-Prompt bei OpenAI-kompatiblen Schnittstellen als System-Nachricht einhängen
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + prompt_history
        model_name = os.environ.get("WISSKOMM_LLM_MODEL", "glm-5.2")
        
        response = await client.chat.completions.create(
            model=model_name,
            max_tokens=8000,
            messages=messages,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError(
                "Das LLM hat eine leere Antwort (None) zurückgegeben. Bitte prüfen Sie Ihre "
                "API-Konfiguration, Kontingente oder die Projekt-ID (SCW_BASE_URL) bei Scaleway."
            )
        content = content.strip()
        
    else:  # anthropic
        # Lazy Import, um Fehler zu vermeiden falls anthropic-Bibliothek nicht installiert ist
        import anthropic
        
        ant_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not ant_key:
            raise ValueError("Anthropic API Key (ANTHROPIC_API_KEY) nicht konfiguriert.")
            
        client = anthropic.AsyncAnthropic(api_key=ant_key)
        model_name = os.environ.get("WISSKOMM_LLM_MODEL", "claude-opus-4-8")
        
        response = await client.messages.create(
            model=model_name,
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            messages=prompt_history
        )
        content = response.content[0].text
        if content is None:
            raise RuntimeError("Das Anthropic-Modell hat eine leere Antwort (None) zurückgegeben.")
        content = content.strip()

    # JSON-Extraktion aus der Antwort (falls das Modell Markdown drumherum gepackt hat)
    json_start = content.find("{")
    json_end = content.rfind("}") + 1
    if json_start != -1 and json_end != -1:
        content = content[json_start:json_end]
        
    try:
        data = json.loads(content, strict=False)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON Fehler ({provider}):", content)
        raise RuntimeError(f"Ungültige JSON-Antwort von der LLM-API ({provider}): {e}")
