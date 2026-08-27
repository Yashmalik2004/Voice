"""
Manager (escalation) agent.

Handles issues that the frontline Assistant couldn't resolve.
Has authority to offer refunds, credits, or other accommodations.
Uses a distinct TTS voice to signal the handoff to the user.
"""

from dotenv import load_dotenv
from livekit.agents import Agent
from tools.weather import lookup_weather

load_dotenv()


class ManagerAgent(Agent):
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions="""
            You are the Customer Service Manager (Senior Management).
            You handle escalated cases that frontline representatives could not resolve.

            ROLE & AUTHORITY:
            - You hold senior management authority.
            - You have full authority to offer refunds, account credits, discounts, and custom resolutions.
            - Maintain an empathetic, professional, and solution-oriented tone.
            - You have access to the customer's prior conversation with the frontline representative.
            """,
            chat_ctx=chat_ctx,
            tools=[lookup_weather],
            # Distinct voice makes the handoff audibly clear to the customer.
            tts="cartesia/sonic-3:6f84f4b8-58a2-430c-8c79-688dad597532",
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="""
            Introduce yourself as the Customer Service Manager. Acknowledge that the frontline
            representative transferred the call to you. State that you're here to help resolve
            their issue, and ask how you can assist them.
            """
        )
