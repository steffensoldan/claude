"""Start: `python -m dialog_mcp --config /etc/dialog-mcp/config.toml`"""

from __future__ import annotations

import argparse
import sys

import uvicorn

from .app import MCP_PATH, build_app
from .auth import Config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dialog-mcp", description="MCP-Server fuer Agent-zu-Agent-Debatten")
    parser.add_argument("--config", default="config.toml", help="Pfad zur TOML-Konfiguration")
    parser.add_argument("--host", default=None, help="ueberschreibt server.host")
    parser.add_argument("--port", type=int, default=None, help="ueberschreibt server.port")
    args = parser.parse_args(argv)

    try:
        config = Config.load(args.config)
    except (OSError, ValueError) as exc:
        print(f"Konfiguration nicht nutzbar: {exc}", file=sys.stderr)
        return 2

    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port

    placeholder = [p.id for p in config.participants if p.token.startswith("BITTE-ERSETZEN")]
    if placeholder:
        print(f"Beispiel-Token noch nicht ersetzt fuer: {', '.join(placeholder)}", file=sys.stderr)
        return 2

    print(f"MCP-Endpunkt : http://{config.host}:{config.port}{MCP_PATH}")
    print(f"Weboberflaeche: http://{config.host}:{config.port}/")
    uvicorn.run(build_app(config), host=config.host, port=config.port, log_level="info")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
