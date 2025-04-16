# @title 1. Define the before_model_callback Guardrail


# Ensure necessary imports are available
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
#from google.adk.tools.tool_response import ToolResponse

# Ensure necessary imports are available
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types # For creating response content
#from typing import Optional
from typing import Optional, Dict, Any # For type hints

#from ..lib_colors import * # keeping it simple.
def green(str):
    """Formats the input string with green color using ANSI escape codes."""
    return f"\033[92m{str}\033[0m"
def red(str):
    """Formats the input string with red color using ANSI escape codes."""
    return f"\033[91m{str}\033[0m"


def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name # Get the name of the agent whose model call is being intercepted
    print(f"--- [before_model_callback] Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break # Found the last user message text

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---") # Log first 100 chars

    # --- Guardrail Logic ---
    keywords_to_block = ["block", "Zurich"]
    for keyword in keywords_to_block:
        #if keyword in last_user_message_text.upper():
        keyword_to_block = keyword.upper()
        #keyword_to_block = "BLOCK"
        if keyword_to_block in last_user_message_text.upper(): # Case-insensitive check
            print(f"--- Callback: 🚧 Found '{red(keyword_to_block)}'. Blocking LLM call! ---")
            # Optionally, set a flag in state to record the block event
            callback_context.state["guardrail_block_keyword_triggered"] = True
            print(f"--- Callback: 🚧 Set state 'guardrail_block_keyword_triggered': True ---")

            # Construct and return an LlmResponse to stop the flow and send this back instead
            return LlmResponse(
                content=types.Content(
                    role="model", # Mimic a response from the agent's perspective
                    parts=[types.Part(text=f"🚧 I cannot process this request because it contains the blocked keyword '{keyword_to_block}'. Note to ricc: This LlmResponse is a 1/1 artefact - guardrail-generated.")],
                )
                # Note: You could also set an error_message field here if needed
            )
        else:
            # Keyword not found, allow the request to proceed to the LLM
            # too verbose
            #print(f"--- Callback: 🚧 Keyword '{keyword_to_block}' not found. Allowing LLM call for {(agent_name)}. ---")
            pass
    return None # Returning None signals ADK to continue normally

print("✅ block_keyword_guardrail function defined.")


def riccardo_messing_around_after_agent_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    print(f"--- Callback == 💛 Carlessian AfterAgentCallback (tool '{tool}') ---")
    return "Mi nombre es Inigo Montoya."

def riccardo_messing_around_after_tool_callback(
    tool: BaseTool,
    args: Dict[str, Any],
    tool_context: ToolContext,
    tool_response,
) -> Optional[Dict]:
    print(f"--- AfterToolCallback == 💛 Carlessian after_tool_callback (tool '{tool.__class__.__name__}') ---")
    print(f"--- AfterToolCallback == 💛 Carlessian after_tool_callback (args= '{args}') ---")
    print(f"--- AfterToolCallback == 💛 Carlessian after_tool_callback (tool_response='{tool_response}') ---")


    #return {"riccardo_fake_response": "Mi nombre es Inigo Montoya."}
    return {"riccardo_favorite_color": "yellow", 'original_tool_response': tool_response}


def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Checks if 'get_weather_stateful' is called for 'Paris'.
    If so, blocks the tool execution and returns a specific error dictionary.
    Otherwise, allows the tool call to proceed by returning None.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name # Agent attempting the tool call
    print(f"--- Callback: [before_tool_callback] block_paris_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")
    print(f"--- Callback: Inspecting args: {args} ---")

    # --- Guardrail Logic ---
    target_tool_name = "get_weather_stateful" # Match the function name used by FunctionTool
    blocked_city = "paris"

    # Check if it's the correct tool and the city argument matches the blocked city
    if tool_name == target_tool_name:
        city_argument = args.get("city", "") # Safely get the 'city' argument
        if city_argument and city_argument.lower() == blocked_city:
            print(f"--- Callback: Detected blocked city '{city_argument}'. Blocking tool execution! ---")
            # Optionally update state
            tool_context.state["guardrail_tool_block_triggered"] = True
            print(f"--- Callback: Set state 'guardrail_tool_block_triggered': True ---")

            # Return a dictionary matching the tool's expected output format for errors
            # This dictionary becomes the tool's result, skipping the actual tool run.
            return {
                "status": "error",
                "error_message": f"Policy restriction: Weather checks for '{city_argument.capitalize()}' are currently disabled by a tool guardrail."
            }
        else:
             print(f"--- Callback: City '{city_argument}' is allowed for tool '{tool_name}'. ---")
    else:
        print(f"--- Callback: Tool '{tool_name}' is not the target tool. Allowing. ---")


    # If the checks above didn't return a dictionary, allow the tool to execute
    print(f"--- Callback: Allowing tool '{tool_name}' to proceed. ---")
    return None # Returning None allows the actual tool function to run

print("✅ block_paris_tool_guardrail function defined.")
