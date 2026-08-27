"""
Consent collection task.

Runs at the start of every Assistant session. Asks the user for recording
consent and resolves to True (consented) or False (declined).
"""

from livekit.agents import AgentTask, function_tool, RunContext


class CollectConsent(AgentTask[bool]):
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions="""
            Your ONLY job is to obtain recording consent from the user and call the appropriate tool.

            RULES:
            - When the user gives consent (e.g. 'yes', 'sure', 'okay', 'go ahead', 'fine', 'yeah', 'i consent'), you MUST IMMEDIATELY call the `consent_given` tool.
            - When the user denies consent (e.g. 'no', 'i decline', 'do not record', 'nope', 'negative'), you MUST IMMEDIATELY call the `consent_denied` tool.
            - Do not engage in general conversation until you have called either `consent_given` or `consent_denied`.
            """,
            chat_ctx=chat_ctx,
        )

    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions="""
            Briefly introduce yourself as the voice assistant, then ask the user for permission to record 
            the conversation for quality and training purposes. Make it clear they can decline.
            """
        )

    @function_tool()
    async def consent_given(self) -> None:
        """Use this immediately when the user agrees or gives consent to record."""
        self.complete(True)

    @function_tool()
    async def consent_denied(self) -> None:
        """Use this immediately when the user denies, refuses, or declines consent to record."""
        self.complete(False)
