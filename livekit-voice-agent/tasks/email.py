"""
Email collection task.

Used by CheckoutAgent's TaskGroup to gather the user's email address.
"""

from dataclasses import dataclass
from livekit.agents import AgentTask, function_tool, RunContext


@dataclass
class EmailResult:
    email_address: str


class GetEmailTask(AgentTask[EmailResult]):
    def __init__(self) -> None:
        super().__init__(
            instructions="Collect the user's email address."
        )

    @function_tool()
    async def record_email(self, context: RunContext, email: str) -> None:
        """Record the user's email address."""
        self.complete(EmailResult(email_address=email))
