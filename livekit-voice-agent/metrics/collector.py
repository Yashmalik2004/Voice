"""
Metrics collection and reporting.

Wires up all metric event handlers on an AgentSession and registers a
shutdown callback for the per-session usage summary.

Tracks:
  - All metric types via UsageCollector (tokens, audio duration, costs)
  - EOU (End-of-Utterance) timing for TTFA (Time-to-First-Audio) computation
"""

import logging
import time

from livekit.agents import AgentSession, JobContext
from livekit.agents import AgentStateChangedEvent, MetricsCollectedEvent, metrics

logger = logging.getLogger(__name__)


def setup_metrics(session: AgentSession, ctx: JobContext) -> None:
    """
    Attach metric event handlers to *session* and register a shutdown
    callback on *ctx* that logs the per-session usage summary.
    """
    usage_collector = metrics.UsageCollector()
    # Holds the most recent EOU metrics so TTFA can be derived when the
    # agent begins speaking.
    last_eou_metrics: metrics.EOUMetrics | None = None

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        nonlocal last_eou_metrics

        if ev.metrics.type == "eou_metrics":
            last_eou_metrics = ev.metrics

        # Stream each metric to the logger and roll it into the session total.
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    @session.on("agent_state_changed")
    def _on_agent_state_changed(ev: AgentStateChangedEvent):
        if ev.new_state == "speaking" and last_eou_metrics:
            elapsed = time.time() - last_eou_metrics.timestamp
            logger.info("Time to first audio: %.3fs", elapsed)

    async def _log_usage():
        summary = usage_collector.get_summary()
        logger.info("Usage summary: %s", summary)

    ctx.add_shutdown_callback(_log_usage)
