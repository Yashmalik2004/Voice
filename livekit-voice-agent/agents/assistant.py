"""
Main customer-service assistant.

Handles general inquiries. Greets the user, mentions recording policy,
then immediately offers assistance. No blocking consent gate.
"""

from livekit.agents import Agent

from tools.weather import lookup_weather
from tools.escalation import escalate_to_manager


class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a friendly, helpful frontline customer service representative (Tier 1 Support).
            You help customers with general questions, information, and basic inquiries.

            ORGANIZATION & HIERARCHY RULES:
            - You are a frontline representative and report to the Customer Service Manager.
            - You do NOT have managerial authority. You cannot approve refunds, policy exceptions, or managerial escalations yourself.
            - When a customer asks to speak with a manager, supervisor, or someone in charge, or if an issue is beyond your authority, you MUST IMMEDIATELY use the `escalate_to_manager` tool.
            - Never claim that you are the manager, that you are the final authority, or that there is no one above you.
            """,
            tools=[lookup_weather, escalate_to_manager],
        )

    async def on_enter(self) -> None:
        await self.session.say(
            "Hello! I'm your customer service assistant. This call may be recorded for quality assurance. How can I help you today?"
        )
