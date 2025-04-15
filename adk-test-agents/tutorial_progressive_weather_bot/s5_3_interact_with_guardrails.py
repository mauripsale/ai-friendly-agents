# @title 3. Interact to Test the Model Input Guardrail

from s5_2_block_guardrail import *


# Ensure the runner for the guardrail agent is available
if runner_root_model_guardrail:
  async def run_guardrail_test_conversation():
      print("\n--- Testing Model Input Guardrail ---")

      # Use the runner for the agent with the callback and the existing stateful session ID
      interaction_func = lambda query: call_agent_async(query,
      runner_root_model_guardrail, USER_ID_STATEFUL, SESSION_ID_STATEFUL # <-- Pass correct IDs
  )
      # 1. Normal request (Callback allows, should use Fahrenheit from Step 4 state change)
      await interaction_func("What is the weather in London?")

      # 2. Request containing the blocked keyword
      await interaction_func("BLOCK the request for weather in Tokyo")

      # 2. Request containing the blocked keyword
      await interaction_func("What about Paris?")

      # 3. Normal greeting (Callback allows root agent, delegation happens)
      await interaction_func("Hello again")

  if __name__ == "__main__":
    # Execute the conversation
    #await run_guardrail_test_conversation()
    asyncio.run(run_guardrail_test_conversation())
    print("\n--- Conversation Complete ---")


  # Optional: Check state for the trigger flag set by the callback
  final_session = session_service_stateful.get_session(app_name=APP_NAME,
                                                       user_id=USER_ID_STATEFUL,
                                                       session_id=SESSION_ID_STATEFUL)
  if final_session:
      print("\n--- Final Session State (After Guardrail Test) ---")
      print(f"Guardrail Triggered Flag: {final_session.state.get('guardrail_block_keyword_triggered')}")
      print(f"Last Weather Report: {final_session.state.get('last_weather_report')}") # Should be London weather
      print(f"Temperature Unit: {final_session.state.get('user_preference_temperature_unit')}") # Should be Fahrenheit
  else:
      print("\n❌ Error: Could not retrieve final session state.")

else:
  print("\n⚠️ Skipping model guardrail test. Runner ('runner_root_model_guardrail') is not available.")

