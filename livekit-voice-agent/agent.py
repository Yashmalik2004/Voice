"""
Voice AI Agent — entry point.

Assembles the LiveKit voice pipeline and registers the RTC session handler.
All business logic lives in the submodules:

  agents/       — Agent personalities and system prompts
  tools/        — LLM-callable function tools
  tasks/        — Focused conversational tasks (consent, email, address)
  workflows/    — Multi-step TaskGroup workflows (checkout)
  integrations/ — MCP server configuration
  metrics/      — Usage collection and TTFA measurement
  config/       — Environment and settings

Voice pipeline:
  LiveKit/WebRTC → Noise Cancellation → VAD → STT → Turn Detection
  → LLM → Tools/MCP → TTS → LiveKit/WebRTC

STT  fallback: AssemblyAI  → Deepgram
LLM  fallback: OpenAI      → Gemini
TTS  fallback: Cartesia     → Inworld
"""

import logging

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, room_io
from livekit.agents import llm, stt, tts, inference
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from agents import Assistant
from integrations import get_mcp_servers
from metrics import setup_metrics

load_dotenv()

logger = logging.getLogger(__name__)

server = AgentServer()


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    """
    Configure and start an AgentSession for each incoming LiveKit room connection.
    """
    session = AgentSession(
        # ── LLM: OpenAI primary, Gemini fallback ───────────────────────────
        llm=llm.FallbackAdapter(
            [
                inference.LLM(model="openai/gpt-4.1-mini"),
                inference.LLM(model="google/gemini-2.5-flash"),
            ]
        ),
        # ── STT: AssemblyAI primary, Deepgram fallback ─────────────────────
        stt=stt.FallbackAdapter(
            [
                inference.STT.from_model_string("assemblyai/universal-streaming:en"),
                inference.STT.from_model_string("deepgram/nova-3"),
            ]
        ),
        # ── TTS: Cartesia primary, Inworld fallback ─────────────────────────
        tts=tts.FallbackAdapter(
            [
                inference.TTS.from_model_string("cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"),
                inference.TTS.from_model_string("inworld/inworld-tts-1"),
            ]
        ),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        preemptive_generation=True,
        mcp_servers=get_mcp_servers(),
    )

    # Wire up usage collection, EOU metrics, and TTFA logging.
    setup_metrics(session, ctx)

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        ),
        record=False,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Import and start HTTP token+web server only in the main process.
    # IMPORTANT: do NOT import this at the top level — job subprocesses
    # re-import agent.py and aiohttp causes event-loop conflicts that
    # crash the subprocess (DuplexClosed).
    from token_server import start_token_server_in_background
    start_token_server_in_background()
    # Start the LiveKit RTC agent worker
    agents.cli.run_app(server)
