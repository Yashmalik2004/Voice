"""
Main customer-service assistant.

Handles general inquiries. Runs the consent workflow on entry, then
exposes weather lookup and manager escalation as LLM-callable tools.
"""

from livekit.agents import Agent

from tasks.consent import CollectConsent
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
        # Run consent workflow before the main conversation begins.
        # Passing chat_ctx preserves any prior context across the handoff.
        consented = await CollectConsent(chat_ctx=self.chat_ctx)

        if consented:
            await self.session.generate_reply(
                instructions="Thank the user cheerfully for granting consent. Let them know you're ready to help and ask how you can assist them today."
            )
        else:
            await self.session.generate_reply(
                instructions="Politely acknowledge that you will proceed without recording. Let them know you're ready to help and ask how you can assist them today."
            )
