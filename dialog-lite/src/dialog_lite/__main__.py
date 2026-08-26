"""Start ueber stdio:

    python -m dialog_lite --as claude --dir /pfad/zu/dialogen
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .server import build_server
from .thread import ID_RE


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dialog-lite", description="Kleiner MCP-Server fuer Agent-Dialoge (stdio)"
    )
    parser.add_argument("--as", dest="me", required=True, help="Deine Kennung im Dialog, z. B. claude")
    parser.add_argument("--dir", dest="directory", required=True, help="Ordner fuer die Dialog-Dateien")
    args = parser.parse_args(argv)

    if not ID_RE.match(args.me):
        print("--as: Buchstaben, Ziffern, Punkt, Bindestrich, Unterstrich.", file=sys.stderr)
        return 2

    directory = Path(args.directory).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)

    build_server(str(directory), args.me).run(transport="stdio")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
