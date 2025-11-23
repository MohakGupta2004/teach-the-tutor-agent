import logging
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
import json
import os
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""   
You are a mental wellness assistant. 
Identify if the user is new or returning. 
If new, create their profile. 
If returning, continue based on their latest session. 
Store each new session entry. 
Keep responses simple, supportive, and non-medical.
""",
        )

    @function_tool
    async def identify_user(self, user_name: str):
        """
        Check if a user already exists and return their latest wellness entry (if any).
        This function should never modify or save data.

        args:
        user_name: The person's identifier as given by the user.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "wellness_log.json")

        if not os.path.exists(file_path):
            return {
                "exists": False,
                "last_entry": None,
                "message": "No data file found. Treat user as new."
            }

        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {
                        "exists": False,
                        "last_entry": None,
                        "message": "Empty data file. Treat user as new."
                    }
                data = json.loads(content)
        except Exception as e:
            logger.error(f"Error reading wellness file: {e}")
            return {
                "exists": False,
                "last_entry": None,
                "message": "Error reading file. Treat user as new."
            }

        # If user is not found or has no history
        if user_name not in data or len(data[user_name]) == 0:
            return {
                "exists": False,
                "last_entry": None,
                "message": "User not found in data. Treat as new."
            }

        # Otherwise return their most recent entry
        latest = data[user_name][-1]
        return {
            "exists": True,
            "last_entry": latest,
            "message": "User found. Returning latest session."
        }
    
    @function_tool
    async def save_wellness_entry(self, user_name: str, mood: str, energy: str, goals: list[str], summary: str, timestamp: str):
        """
        Save a new wellness check-in for a specific user.
        This function assumes all check-in questions have been completed.

        args:
        user_name: the person doing the check-in
        mood: user-described mood (their own wording)
        energy: self-described energy level
        goals: up to 3 intentions for today
        summary: short, neutral recap sentence created by the agent
        timestamp: ISO 8601 date-time string
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "wellness_log.json")

        # Load or initialize file
        data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
            except Exception as e:
                logger.error(f"Error reading wellness log file: {e}")

        # Make sure user key exists
        if user_name not in data:
            data[user_name] = []

        # Append new entry
        new_data = {
            "timestamp": timestamp,
            "mood": mood,
            "energy": energy,
            "goals": goals,
            "summary": summary
        }
        data[user_name].append(new_data)

        # Save updated file
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error writing to wellness file: {e}")
            return "Failed to save wellness entry"

        return "Wellness entry saved successfully"



        


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()    


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-UK-hazel", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
