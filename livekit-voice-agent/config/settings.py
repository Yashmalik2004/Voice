"""
Application configuration loaded from environment variables.
Secrets are never hardcoded here; they come from .env via python-dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central access point for all environment-driven configuration."""

    # LiveKit cloud credentials
    livekit_url: str = os.environ.get("LIVEKIT_URL", "")
    livekit_api_key: str = os.environ.get("LIVEKIT_API_KEY", "")
    livekit_api_secret: str = os.environ.get("LIVEKIT_API_SECRET", "")

    # Token server
    token_server_host: str = os.environ.get("TOKEN_SERVER_HOST", "0.0.0.0")
    token_server_port: int = int(os.environ.get("TOKEN_SERVER_PORT", "7880"))

    # Logging level
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")


settings = Settings()
