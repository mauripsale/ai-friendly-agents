import datetime
import os
import logging
from . import ricc_colors as C # Assuming ricc_colors.py is in the same dir
logger = logging.getLogger(__name__)

def current_time() -> dict:
    """Gets the current time and weekday.

    This function is useful for providing the current time and weekday to the user or for logging purposes.
    It returns the current time in ISO 8601 format and the current weekday.

    Returns:
        A dictionary containing the current time in ISO 8601 format and the weekday.
        Example:
        {
            "current_time_iso": "2023-10-27T10:30:00Z",
            "current_weekday": "Friday"
        }
    """
    log_function_called("current_time()")
    now = datetime.datetime.now(datetime.timezone.utc)
    current_time_iso = now.isoformat()
    current_weekday = now.strftime("%A")  # %A gives the full weekday name
    return {
        "current_time_iso": current_time_iso,
        "current_weekday": current_weekday,
    }

def current_place() -> dict:
    """Gets the current location, provided by user in ENV"""
    user_location = os.getenv("USER_LOCATION", 'San Francisco, US')
    return {
        "user_location": user_location,
    }



# from lib.ricc_system import function_called, log_function_called

def log_function_called(str):
    print(f"{C.FUN_CALL} Function called: {C.darkgray(str)}", flush=True)
    logger.warn(f"AFC Function called: {str}")

def log_function_call_output(name: str, result: str):
    print(f"{C.FUN_CALL} Function {C.orange(name)} returned: {C.darkgray(result)}", flush=True)

    result_size = result.__sizeof__()
    max_response_length = 500
    if len(result) > max_response_length:
                    result = result[:max_response_length] + "... ✂️"

    logger.info(f"AFC Function {name} returned: {result_size} bytes")
