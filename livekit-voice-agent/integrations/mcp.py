"""
MCP server configuration.

Returns the list of MCP servers to mount on every AgentSession.
Add or remove servers here without touching agent.py.
"""

from livekit.agents import mcp


def get_mcp_servers() -> list:
    """Return the configured MCP server list."""
    # MCP disabled — enable when needed:
    # mcp.MCPServerHTTP(url="https://docs.livekit.io/mcp")
    return []
