"""
Checkout workflow.

Orchestrates a TaskGroup that collects email and shipping address in sequence,
then confirms the order details to the customer.
"""

from livekit.agents import Agent
from livekit.agents.beta.workflows import TaskGroup

from tasks.email import GetEmailTask
from tasks.address import GetAddressTask


class CheckoutAgent(Agent):
    async def on_enter(self) -> None:
        task_group = TaskGroup()

        # Each task wrapped in a lambda so it can be re-instantiated if the
        # user navigates back through the workflow.
        task_group.add(
            lambda: GetEmailTask(),
            id="email",
            description="Collect email address",
        )
        task_group.add(
            lambda: GetAddressTask(),
            id="address",
            description="Collect shipping address",
        )

        results = await task_group

        email = results.task_results["email"].email_address
        address = results.task_results["address"].address

        await self.session.generate_reply(
            instructions=f"Confirm the order will be sent to {email} at {address}."
        )
