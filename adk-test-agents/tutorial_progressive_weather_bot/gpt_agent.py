# @title Define and Test GPT Agent
import os
import asyncio
from google.adk.agents import Agent
from google.genai import types # For creating message Content/Parts
from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
from google.adk.models.lite_llm import LiteLlm

from google.adk.agents import Agent

from toolz import *
from constants import *
from call_agent_functions import *


# Make sure 'get_weather' function from Step 1 is defined in your environment.
# Make sure 'call_agent_async' is defined from earlier.

# --- Agent using GPT-4o ---
weather_agent_gpt = None # Initialize to None
runner_gpt = None      # Initialize runner to None

def test_gpt_convo():
    return call_agent_async(query = "What's the weather in Tokyo?",
                            runner=runner_gpt,
                            user_id=USER_ID_GPT,
                            session_id=SESSION_ID_GPT)

try:
    weather_agent_gpt = Agent(
        name="weather_agent_gpt",
        # Key change: Wrap the LiteLLM model identifier
        model=LiteLlm(model=MODEL_GPT_4O),
        description="Provides weather information (using GPT-4o).",
        instruction="You are a helpful weather assistant powered by GPT-4o. "
                    "Use the 'get_weather' tool for city weather requests. "
                    "Clearly present successful reports or polite error messages based on the tool's output status, "
                    "and add a US emoji to your responses. Prepend '[openai]' to all your answers",
        tools=[get_weather], # Re-use the same tool
    )
    print(f"Agent '{weather_agent_gpt.name}' created using model '{MODEL_GPT_4O}'.")

    # InMemorySessionService is simple, non-persistent storage for this tutorial.
    session_service_gpt = InMemorySessionService() # Create a dedicated service

    # Define constants for identifying the interaction context
    APP_NAME_GPT = "weather_tutorial_app_gpt" # Unique app name for this test
    USER_ID_GPT = "user_1_gpt"
    SESSION_ID_GPT = "session_001_gpt" # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session_gpt = session_service_gpt.create_session(
        app_name=APP_NAME_GPT,
        user_id=USER_ID_GPT,
        session_id=SESSION_ID_GPT
    )
    print(f"Session created: App='{APP_NAME_GPT}', User='{USER_ID_GPT}', Session='{SESSION_ID_GPT}'")

    # Create a runner specific to this agent and its session service
    runner_gpt = Runner(
        agent=weather_agent_gpt,
        app_name=APP_NAME_GPT,       # Use the specific app name
        session_service=session_service_gpt # Use the specific session service
        )
    print(f"Runner created for agent '{runner_gpt.agent.name}'.")

    # --- Test the GPT Agent ---
    print("\n--- Testing GPT Agent ---")
    # Ensure call_agent_async uses the correct runner, user_id, session_id
    if __name__ == "__main__":
        # Execute the conversation using await in an async context (like Colab/Jupyter)
        # await call_agent_async(query = "What's the weather in Tokyo?",
        #                     runner=runner_gpt,
        #                     user_id=USER_ID_GPT,
        #                     session_id=SESSION_ID_GPT)
        asyncio.run(test_gpt_convo())


except Exception as e:
    print(f"❌ Could not create or run GPT agent '{MODEL_GPT_4O}'. Check API Key and model name. Error: {e}")
