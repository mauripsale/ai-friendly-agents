from google.adk.tools.tool_context import ToolContext
from lib_colors import *

# @title Define the get_weather Tool
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: {cyan('get_weather')} called for city: {yellow(city)} ---") # Log tool execution
    city_normalized = city.lower().replace(" ", "") # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy and miserable in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
        "paris": {"status": "success", "report": "Paris is sunny with a temperature of 22°C."},
        "berlin": {"status": "success", "report": "It's cloudy and a temperature of 18°C."},
        "zurich": {"status": "success", "report": "Zurich is sunny with a temperature of 21°C; the lake temperature is 18°C."},
        "new delhi": {"status": "success", "report": "New Delhi is sunny with a temperature of 25°C."},
        "istanbul": {"status": "success", "report": "Istanbul is sunny with a temperature of 25°C."},
        "rome": {"status": "success", "report": "Rome is sunny with a temperature of 25°C."},
        "madrid": {"status": "success", "report": "Madrid is sunny with a temperature of 25°C."},
        "moscow": {"status": "success", "report": "Moscow is sunny with a temperature of 25°C."},
        "singapore": {"status": "success", "report": "Singapore is sunny with a temperature of 25°C."},
        "dubai": {"status": "success", "report": "experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        ret = mock_weather_db[city_normalized]
    else:
        ret = {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}
    ret['colorful_status'] = green(ret['status']) if ret['status'] == 'success' else red(ret['status'])
    return ret

print("✅ Simple 'get_weather' tool defined.")




def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: {cyan('get_weather_stateful')} called for {yellow(city)} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
    print(f"--- Tool: Reading state '{cyan('user_preference_temperature_unit')}': {yellow(preferred_unit)} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
        "zurich": {"temp_c": 23, "condition": "miserable rain"},
        "paris": {"temp_c": 19, "condition": "miserable rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
            temp_unit = "°F"
        else: # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")



# @title Define Tools for Greeting and Farewell Agents

# Ensure 'get_weather' from Step 1 is available if running this step independently.
# def get_weather(city: str) -> dict: ... (from Step 1)

def say_hello(name: str = "there") -> str:
    """Provides a simple greeting, optionally addressing the user by name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to "there".

    Returns:
        str: A friendly greeting message.
    """
#    print(f"--- Tool: say_hello called with name: {name} ---")
    print(f"--- Tool: {cyan('say_hello')} called  with name: {yellow(name)} ---")

    return f"Hello, {name}!"

def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    print(f"--- Tool: {cyan('say_goodbye')} called ---")
    return "Goodbye! Have a great day."

print("Greeting and Farewell tools defined.")




def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converts temp unit based on session state."""
    print(f"--- Tool: {cyan('get_weather_stateful')} called for {yellow(city)} ---")

    # --- Read preference from state ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius") # Default to Celsius
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    # Mock weather data (always stored in Celsius internally)
    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
            temp_unit = "°F"
        else: # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Example of writing back to state (optional for this tool)
        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state '{gray('last_city_checked_stateful')}': {yellow(city)} ---")

        return result
    else:
        # Handle city not found
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}

print("✅ State-aware 'get_weather_stateful' tool defined.")


def print_fancy_weather(weather_data: dict):
    """Prints weather information in a fancy format.

    Args:
        weather_data (dict): A dictionary containing weather information.
    """
    #print(f"--- [{weather_data['colorful_status']}] Weather Report: {weather_data['report']} ---")
    if weather_data["status"] == "success":
        print(f"--- [{weather_data['colorful_status']}] Weather Report: {weather_data['report']} ---")
    else:
        print(f"--- [{weather_data['colorful_status']}] ErrMsg: {red(weather_data['error_message'])} ---")
        #print(f"--- Error: {weather_data['error_message']} ---")
        #print(f"--- Status: {weather_data['status']} ---")
        #print(f"--- Colorful Status: {weather_data['colorful_status']} ---")
        #print(f"--- Error Message: {weather_data['error_message']} ---")
        #print(f"--- Colorful Error Message: {weather_data['colorful_error_message']} ---")


# Test functionality
if __name__ == "__main__":
    print("Testing TOOLS functionality..")
    # Example tool usage (optional test)
    print_fancy_weather(get_weather("New York"))
    print_fancy_weather(get_weather("Zurich"))
    print_fancy_weather(get_weather("London"))
    print_fancy_weather(get_weather("Paris"))
    print_fancy_weather(get_weather("Argenta"))
    # Optional self-test
    print(say_hello("Alice"))
    print(say_goodbye())

