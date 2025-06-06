import os
import dotenv
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

# --- IMPORTANT: Replace placeholders with your real API keys ---

# --- Verify Keys (Optional Check) ---
print("API Keys Set:")

print(f"* Google API Key set: {'Yes' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'YOUR_GOOGLE_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"* OpenAI API Key set: {'Yes' if os.environ.get('OPENAI_API_KEY') and os.environ['OPENAI_API_KEY'] != 'YOUR_OPENAI_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")
print(f"* Anthropic API Key set: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') and os.environ['ANTHROPIC_API_KEY'] != 'YOUR_ANTHROPIC_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}")

# Configure ADK to use API keys directly (not Vertex AI for this multi-model setup)
#os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash"
# Note: Specific model names might change. Refer to LiteLLM/Provider documentation.
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_SONNET = "anthropic/claude-3-sonnet-20240229"


print("\nEnvironment configured.")
# @title Setup Session Service and Runner

############################
# MAIN Session info:
############################

# Define constants for identifying the interaction context
APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001" # Using a fixed ID for simplicity

############################
# STEP4 Session info:
############################
# Define a NEW session ID for this part of the tutorial
SESSION_ID_STATEFUL = "session_state_demo_001"
USER_ID_STATEFUL = "user_state_demo"
