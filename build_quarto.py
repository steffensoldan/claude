"""Prototyp: Konvertiert das KI-JSON (gleiches Schema wie der Fixed-HTML-Pfad) in eine
Quarto-Publikation und rendert sie in mehrere Formate (HTML/PDF/RevealJS/PPTX) mit
zentraler ZEW-CD.

Ablauf: JSON-Datenreihen -> CSV (Datenvertrag) + gefüllte .qmd-Vorlage -> `quarto render`
-> Ausgaben nach <publish_dir>/<slug>/ (bedient unter /wisskomm/pub/<slug>/).

Konfiguration über Umgebungsvariablen (siehe .env.example):
  WISSKOMM_QUARTO_DIR  – Wurzel des Quarto-Projekts (mit _quarto.yml/_brand.yml/.venv)
  WISSKOMM_QUARTO_BIN  – Pfad zur quarto-CLI
"""
import os
import csv
import shutil
import subprocess
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / "templates"

# Spalten je CSV gemäß Datenvertrag (implementation_plan.md Teil H).
CSV_SPEC = {
    "scenarios_eu": None,   # None -> Spalten aus den vorhandenen Schlüsseln übernehmen
    "prices_eu": None,
    "scenarios_us": None,
    "signal": ["label", "setting", "design", "lambda"],
}


def _jinja_env() -> Environment:
    # Eigene Delimiter, damit der Python-/{ }-Code in der .qmd-Vorlage nicht mit Jinja kollidiert.
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        variable_start_string="[[", variable_end_string="]]",
        block_start_string="[%", block_end_string="%]",
        comment_start_string="[#", comment_end_string="#]",
        trim_blocks=True, lstrip_blocks=True,
    )


def _write_csv(path: Path, rows: list, fieldnames=None) -> None:
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def prepare_sources(slug: str, data: dict, quarto_dir: Path) -> Path:
    """Schreibt CSVs + index.qmd in <quarto_dir>/publications/<slug>/ und gibt den Ordner zurück."""
    pub_src = quarto_dir / "publications" / slug
    (pub_src / "data").mkdir(parents=True, exist_ok=True)

    for key, fields in CSV_SPEC.items():
        rows = data.get(key) or []
        _write_csv(pub_src / "data" / f"{key}.csv", rows, fields)

    qmd = _jinja_env().get_template("publication.qmd.j2").render(**data)
    (pub_src / "index.qmd").write_text(qmd, encoding="utf-8")
    return pub_src


def build_quarto_publication(slug: str, data: dict, publish_dir: Path) -> Path:
    """Konvertiert, rendert und veröffentlicht eine Publikation. Gibt den Ausgabeordner zurück."""
    quarto_dir = Path(os.environ.get("WISSKOMM_QUARTO_DIR", "/home/sts/wisskomm-quarto-pilot"))
    quarto_bin = os.environ.get("WISSKOMM_QUARTO_BIN", "/home/sts/opt/quarto-1.9.38/bin/quarto")
    venv_python = quarto_dir / ".venv" / "bin" / "python"

    pub_src = prepare_sources(slug, data, quarto_dir)

    run_env = os.environ.copy()
    run_env["QUARTO_PYTHON"] = str(venv_python)
    run_env["PATH"] = os.path.dirname(quarto_bin) + os.pathsep + run_env.get("PATH", "")

    result = subprocess.run(
        [quarto_bin, "render", str(pub_src / "index.qmd")],
        cwd=str(quarto_dir), env=run_env,
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Quarto-Render fehlgeschlagen:\n{result.stdout[-1500:]}\n{result.stderr[-1500:]}")

    rendered = quarto_dir / "_site" / "publications" / slug
    if not (rendered / "index.html").exists():
        raise RuntimeError(f"Render lieferte keine index.html unter {rendered}")

    target = Path(publish_dir) / slug
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(rendered, target, dirs_exist_ok=True)
    return target
