# @title 4. Interact to Test State Flow and output_key

from sub_agents_v2 import *


# Ensure the stateful runner (runner_root_stateful) is available from the previous cell
# Ensure call_agent_async, USER_ID_STATEFUL, SESSION_ID_STATEFUL, APP_NAME are defined

if 'runner_root_stateful' in globals() and runner_root_stateful:
  async def run_stateful_conversation():
      print("\n--- Testing State: Temp Unit Conversion & output_key ---")

      # 1. Check weather (Uses initial state: Celsius)
      print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
      await call_agent_async(query= "What's the weather in London?",
                             runner=runner_root_stateful,
                             user_id=USER_ID_STATEFUL,
                             session_id=SESSION_ID_STATEFUL
                            )

      # 2. Manually update state preference to Fahrenheit - DIRECTLY MODIFY STORAGE
      print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
      try:
          # Access the internal storage directly - THIS IS SPECIFIC TO InMemorySessionService for testing
          stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
          stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
          # Optional: You might want to update the timestamp as well if any logic depends on it
          # import time
          # stored_session.last_update_time = time.time()
          print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state['user_preference_temperature_unit']} ---")
      except KeyError:
          print(f"--- Error: Could not retrieve session '{SESSION_ID_STATEFUL}' from internal storage for user '{USER_ID_STATEFUL}' in app '{APP_NAME}' to update state. Check IDs and if session was created. ---")
      except Exception as e:
           print(f"--- Error updating internal session state: {e} ---")

      # 3. Check weather again (Tool should now use Fahrenheit)
      # This will also update 'last_weather_report' via output_key
      print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
      await call_agent_async(query= "Tell me the weather in New York.",
                             runner=runner_root_stateful,
                             user_id=USER_ID_STATEFUL,
                             session_id=SESSION_ID_STATEFUL
                            )

      # 4. Test basic delegation (should still work)
      # This will update 'last_weather_report' again, overwriting the NY weather report
      print("\n--- Turn 3: Sending a greeting ---")
      await call_agent_async(query= "Hi!",
                             runner=runner_root_stateful,
                             user_id=USER_ID_STATEFUL,
                             session_id=SESSION_ID_STATEFUL
                            )

  if __name__ == "__main__":
    # Execute the conversation
    #await run_stateful_conversation()
    asyncio.run(run_stateful_conversation())
    print("\n--- Conversation Complete ---")


    # Inspect final session state after the conversation
    print("\n--- Inspecting Final Session State ---")
    final_session = session_service_stateful.get_session(app_name=APP_NAME,
                                                        user_id= USER_ID_STATEFUL,
                                                        session_id=SESSION_ID_STATEFUL)
  if final_session:
      print(f"Final Preference: {yellow(final_session.state.get('user_preference_temperature_unit'))}")
      print(f"Final Last Weather Report (from output_key): {yellow(final_session.state.get('last_weather_report'))}")
      print(f"Final Last City Checked (by tool): {yellow(final_session.state.get('last_city_checked_stateful'))}")
      print(f"Final Session (by Ricc): {yellow(final_session.state)}")
      # Print full state for detailed view
      # print(f"Full State: {final_session.state}")
  else:
      print("\n❌ Error: Could not retrieve final session state.")

else:
  print("\n⚠️ Skipping state test conversation. Stateful root agent runner ('runner_root_stateful') is not available.")
