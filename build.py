import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "output"

def build_html(slug: str, data: dict) -> Path:
    """Rendert die JSON-Daten in templates/standalone.html und speichert sie in output/<slug>/index.html."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("standalone.html")
    
    # Sicherstellen, dass optionale Arrays existieren
    if "signal" not in data:
        data["signal"] = []
    if "kpis" not in data:
        data["kpis"] = []
    if "scenarios_eu" not in data:
        data["scenarios_eu"] = []
    if "prices_eu" not in data:
        data["prices_eu"] = []
    if "scenarios_us" not in data:
        data["scenarios_us"] = []
    if "takeaways" not in data:
        data["takeaways"] = []
        
    html_content = template.render(**data)
    
    # Ausgabeort vorbereiten
    pub_dir = OUTPUT_DIR / slug
    pub_dir.mkdir(parents=True, exist_ok=True)
    
    index_file = pub_dir / "index.html"
    index_file.write_text(html_content, encoding="utf-8")
    
    print(f"Standalone HTML für {slug} kompiliert nach {index_file}")
    return index_file
