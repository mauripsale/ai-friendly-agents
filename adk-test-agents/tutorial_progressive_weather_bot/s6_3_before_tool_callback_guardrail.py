# @title 2. Update Root Agent with BOTH Callbacks (Self-Contained)

# @title 2. Update Root Agent with before_model_callback
import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# Riccardo improts
from constants import *
from toolz import *
from call_agent_functions import *
from sub_agents_v2 import *
from lib.guardrails import *


# --- Ensure Prerequisites are Defined ---
# (Include or ensure execution of definitions for: Agent, LiteLlm, Runner, ToolContext,
#  MODEL constants, say_hello, say_goodbye, greeting_agent, farewell_agent,
#  get_weather_stateful, block_keyword_guardrail, block_paris_tool_guardrail)

# --- Redefine Sub-Agents (Ensures they exist in this context) ---
greeting_agent = None
try:
    # Use a defined model constant like MODEL_GPT_4O
    greeting_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="greeting_agent", # Keep original name for consistency
        instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
        description="Handles simple greetings and hellos using the 'say_hello' tool.",
        tools=[say_hello],
    )
    print(f"✅ Sub-Agent '{greeting_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Greeting agent. Check Model/API Key ({MODEL_GPT_4O}). Error: {e}")

farewell_agent = None
try:
    # Use a defined model constant like MODEL_GPT_4O
    farewell_agent = Agent(
        model=MODEL_GEMINI_2_0_FLASH,
        name="farewell_agent", # Keep original name
        instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
        description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
        tools=[say_goodbye],
    )
    print(f"✅ Sub-Agent '{farewell_agent.name}' redefined.")
except Exception as e:
    print(f"❌ Could not redefine Farewell agent. Check Model/API Key ({MODEL_GPT_4O}). Error: {e}")

# --- Define the Root Agent with Both Callbacks ---
root_agent_tool_guardrail = None
runner_root_tool_guardrail = None

if ('greeting_agent' in globals() and greeting_agent and
    'farewell_agent' in globals() and farewell_agent and
    'get_weather_stateful' in globals() and
    'block_keyword_guardrail' in globals() and
    'block_paris_tool_guardrail' in globals()):

    root_agent_model = MODEL_GEMINI_2_0_FLASH

    root_agent_tool_guardrail = Agent(
        name="weather_agent_v6_tool_guardrail", # New version name
        model=root_agent_model,
        description="Main agent: Handles weather, delegates, includes input AND tool guardrails.",
        instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                    "Delegate greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                    "Handle only weather, greetings, and farewells.",
        tools=[get_weather_stateful],
        sub_agents=[greeting_agent, farewell_agent],
        output_key="last_weather_report",
        before_model_callback=block_keyword_guardrail, # Keep model guardrail
        before_tool_callback=block_paris_tool_guardrail, # <<< Add tool guardrail
        after_agent_callback=riccardo_messing_around_after_agent_callback,
        after_tool_callback=riccardo_messing_around_after_tool_callback,
    )
    print(f"✅ Root Agent '{root_agent_tool_guardrail.name}' created with BOTH callbacks.")

    # --- Create Runner, Using SAME Stateful Session Service ---
    if 'session_service_stateful' in globals():
        runner_root_tool_guardrail = Runner(
            agent=root_agent_tool_guardrail,
            app_name=APP_NAME,
            session_service=session_service_stateful # <<< Use the service from Step 4/5
        )
        print(f"✅ Runner created for tool guardrail agent '{runner_root_tool_guardrail.agent.name}', using stateful session service.")
    else:
        print("❌ Cannot create runner. 'session_service_stateful' from Step 4/5 is missing.")

else:
    print("❌ Cannot create root agent with tool guardrail. Prerequisites missing.")








#######################
# RICC: 6.3 here
#######################



# @title 3. Interact to Test the Tool Argument Guardrail

# Ensure the runner for the tool guardrail agent is available
if runner_root_tool_guardrail:
  async def run_tool_guardrail_test():
      print("\n--- Testing Tool Argument Guardrail ('Paris' blocked) ---")

        # Use the runner for the agent with both callbacks and the existing stateful session
      interaction_func = lambda query: call_agent_async(query,
      runner_root_tool_guardrail, USER_ID_STATEFUL, SESSION_ID_STATEFUL
  )
      # 1. Allowed city (Should pass both callbacks, use Fahrenheit state)
      await interaction_func("What's the weather in New York?")

      # 2. Blocked city (Should pass model callback, but be blocked by tool callback)
      await interaction_func("How about Paris?")

      # 3. Another allowed city (Should work normally again)
      await interaction_func("Tell me the weather in London.")

      # 2. Blocked city (Should pass model callback, but be blocked by tool callback)
      await interaction_func("How about Zurich, Switzerland?")

  if __name__ == "__main__":
    # Execute the conversation
    #await run_tool_guardrail_test()
    asyncio.run(run_tool_guardrail_test())
    print("\n--- Conversation Complete ---")



  # Optional: Check state for the tool block trigger flag
  final_session = session_service_stateful.get_session(app_name=APP_NAME,
                                                       user_id=USER_ID_STATEFUL,
                                                       session_id= SESSION_ID_STATEFUL)
  if final_session:
      print("\n--- Final Session State (After Tool Guardrail Test) ---")
      print(f"Tool Guardrail Triggered Flag: {final_session.state.get('guardrail_tool_block_triggered')}")
      print(f"Last Weather Report: {final_session.state.get('last_weather_report')}") # Should be London weather
      print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit')}") # Should be Fahrenheit
  else:
      print("\n❌ Error: Could not retrieve final session state.")

else:
  print("\n⚠️ Skipping tool guardrail test. Runner ('runner_root_tool_guardrail') is not available.")
