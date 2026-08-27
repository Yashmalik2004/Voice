"""
Manager escalation tool.

Transfers the conversation to ManagerAgent, preserving full chat context
so the manager can see the prior conversation history.
"""

from livekit.agents import function_tool, RunContext


@function_tool()
async def escalate_to_manager(context: RunContext):
    """Transfer the customer to a manager when requested or when you cannot resolve their issue."""
    # Import here to avoid circular: agents → tools → agents
    from agents.manager import ManagerAgent

    agent = context.session.current_agent
    chat_ctx = agent.chat_ctx if agent else None
    return ManagerAgent(chat_ctx=chat_ctx)
