"""
Address collection task.

Used by CheckoutAgent's TaskGroup to gather the user's shipping address.
"""

from dataclasses import dataclass
from livekit.agents import AgentTask, function_tool, RunContext


@dataclass
class AddressResult:
    address: str


class GetAddressTask(AgentTask[AddressResult]):
    def __init__(self) -> None:
        super().__init__(
            instructions="Collect the user's shipping address."
        )

    @function_tool()
    async def record_address(self, context: RunContext, address: str) -> None:
        """Record the user's shipping address."""
        self.complete(AddressResult(address=address))
