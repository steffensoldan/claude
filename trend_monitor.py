"""
trend_monitor.py — GitHub Trend Monitor Collector (CLI-Entry-Point)

Aufruf:
  python trend_monitor.py
  python trend_monitor.py --config config.json --base-dir C:\\AI-Tools\\claude\\github-trend-monitor

Voraussetzungen:
  - GITHUB_TOKEN in .env oder Umgebungsvariable (sonst 10 Req/h Limit)
  - config.json im Basis-Verzeichnis
"""
import argparse
import json
import os
import sys
from pathlib import Path


def load_dotenv(env_path: Path) -> None:
    """Lädt .env in os.environ (überschreibt keine bereits gesetzten Variablen)."""
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub Trend Monitor — Collector")
    parser.add_argument("--config",   default="config.json",
                        help="Pfad zur config.json (default: config.json im Basis-Verzeichnis)")
    parser.add_argument("--base-dir", default=None,
                        help="Basis-Verzeichnis (default: Verzeichnis dieser Datei)")
    args = parser.parse_args()

    base_dir = Path(args.base_dir) if args.base_dir else Path(__file__).parent.resolve()

    # .env laden
    load_dotenv(base_dir / ".env")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("[Collector] ⚠️  GITHUB_TOKEN nicht gesetzt — Rate-Limit: 10 Req/h (Search unauthentifiziert).")
        print("[Collector]    Token erstellen: https://github.com/settings/tokens (Classic PAT, kein Scope)")

    # config.json laden
    config_path = base_dir / args.config
    if not config_path.exists():
        print(f"[Collector] ❌ config.json nicht gefunden: {config_path}")
        return 1
    config = json.loads(config_path.read_text(encoding="utf-8"))
    print(f"[Collector] Config: {config_path}")

    # core.py aus gleichem Verzeichnis importieren
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))

    try:
        import core
    except ImportError as e:
        print(f"[Collector] ❌ core.py nicht gefunden: {e}")
        return 1

    report_file = core.run(base_dir=base_dir, config=config, token=token)
    print(f"[Collector] ✅ Fertig. Report: {report_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
