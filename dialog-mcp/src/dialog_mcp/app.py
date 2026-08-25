"""Setzt MCP-Endpunkt und Weboberflaeche zu einer ASGI-Anwendung zusammen.

Ein Prozess, ein Port, eine systemd-Unit. Beide Haelften greifen auf dieselbe
`Service`-Instanz zu - es gibt keine zweite Regelquelle.
"""

from __future__ import annotations

from starlette.applications import Starlette
from starlette.routing import Mount

from .auth import Config, StaticTokenVerifier, token_hash
from .server import build_server
from .service import Service
from .store import Store
from .web import build_web

MCP_PATH = "/mcp"


def sync_participants(store: Store, config: Config) -> None:
    """Konfiguration ist die Wahrheit ueber Teilnehmer, nicht die Datenbank."""
    for p in config.participants:
        store.upsert_participant(p.id, p.display_name, p.role, token_hash(p.token), p.human)


def build_app(config: Config) -> Starlette:
    store = Store(config.database)
    sync_participants(store, config)
    service = Service(store, config.export_dir)

    mcp = build_server(config, service)
    mcp_app = mcp.streamable_http_app(streamable_http_path=MCP_PATH, host=config.host)
    verifier = StaticTokenVerifier(config.participants)

    routes = [*build_web(service, verifier), Mount("", app=mcp_app)]
    app = Starlette(routes=routes, lifespan=mcp_app.router.lifespan_context)
    app.state.service = service
    app.state.store = store
    app.state.config = config
    return app
