"""
LiveKit access-token and Web UI HTTP server.

Provides:
  - GET /token?room=<room_name>&identity=<participant_identity> -> Returns short-lived JWT
  - GET / -> Serves compiled React frontend if frontend/dist exists
  - GET /assets/... -> Serves frontend static assets
  - CORS support for local development

Can be run:
  1. Embedded automatically by agent.py (start_token_server_in_background())
  2. Standalone via `python token_server.py`
"""

import asyncio
import datetime
import json
import logging
import os
import threading
from pathlib import Path

from aiohttp import web
from dotenv import load_dotenv
from livekit.api import AccessToken, VideoGrants

load_dotenv()

logger = logging.getLogger(__name__)

LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET", "")
LIVEKIT_URL = os.environ.get("LIVEKIT_URL", "")

TOKEN_TTL = datetime.timedelta(hours=1)

# Frontend build directory
DIST_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

_server_thread: threading.Thread | None = None
_server_started = False
_server_lock = threading.Lock()


async def handle_token(request: web.Request) -> web.Response:
    room = request.rel_url.query.get("room", "voice-room")
    identity = request.rel_url.query.get("identity", "browser-user")

    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET or not LIVEKIT_URL:
        return web.Response(
            status=500,
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"},
            text=json.dumps({"error": "LiveKit credentials not configured in .env"}),
        )

    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .with_ttl(TOKEN_TTL)
        .to_jwt()
    )

    logger.info("Issued token for identity=%s room=%s", identity, room)

    return web.Response(
        content_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
        text=json.dumps({"token": token, "url": LIVEKIT_URL}),
    )


async def handle_options(request: web.Request) -> web.Response:
    """CORS preflight."""
    return web.Response(
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({"status": "healthy", "service": "livekit-voice-agent"})


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/token", handle_token)
    app.router.add_route("OPTIONS", "/token", handle_options)
    app.router.add_get("/api/token", handle_token)
    app.router.add_route("OPTIONS", "/api/token", handle_options)
    app.router.add_get("/health", handle_health)

    # If compiled frontend exists in frontend/dist, serve it directly
    if DIST_DIR.exists() and (DIST_DIR / "index.html").exists():
        logger.info("Serving static frontend UI from %s", DIST_DIR)

        async def serve_index(request: web.Request) -> web.FileResponse:
            return web.FileResponse(DIST_DIR / "index.html")

        app.router.add_get("/", serve_index)
        app.router.add_static("/", path=str(DIST_DIR), name="static")

    return app


def start_token_server_in_background(host: str | None = None, port: int | None = None) -> None:
    """
    Starts the HTTP token server on a background daemon thread.
    Called automatically by agent.py on startup.
    """
    global _server_thread, _server_started

    with _server_lock:
        if _server_started:
            return

        srv_host = host or os.environ.get("TOKEN_SERVER_HOST", "0.0.0.0")
        srv_port = port or int(os.environ.get("PORT", os.environ.get("TOKEN_SERVER_PORT", "7880")))

        def _run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            app = create_app()
            runner = web.AppRunner(app)
            try:
                loop.run_until_complete(runner.setup())
                site = web.TCPSite(runner, srv_host, srv_port)
                loop.run_until_complete(site.start())
                logger.info("Token & Web server listening on http://%s:%s", srv_host, srv_port)
                loop.run_forever()
            except Exception as e:
                logger.warning("Could not start background HTTP server on %s:%s (%s)", srv_host, srv_port, e)

        _server_thread = threading.Thread(target=_run_server, daemon=True, name="TokenHTTPServer")
        _server_thread.start()
        _server_started = True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    host = os.environ.get("TOKEN_SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", os.environ.get("TOKEN_SERVER_PORT", "7880")))
    logger.info("Starting standalone Token & Web server on %s:%s", host, port)
    web.run_app(create_app(), host=host, port=port)
