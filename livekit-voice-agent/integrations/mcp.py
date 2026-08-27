"""
MCP server configuration.

Returns the list of MCP servers to mount on every AgentSession.
Add or remove servers here without touching agent.py.
"""

from livekit.agents import mcp


def get_mcp_servers() -> list:
    """Return the configured MCP server list."""
    return [
        # LiveKit documentation MCP — lets the agent answer questions about
        # LiveKit APIs and features by querying the official docs at runtime.
        mcp.MCPServerHTTP(url="https://docs.livekit.io/mcp"),
    ]
