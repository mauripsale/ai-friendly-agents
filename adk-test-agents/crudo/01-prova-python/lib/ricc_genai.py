# lib/ricc_genai.py
# Handles the chat logic and talking to Gemini! 🤖


import os
#import google.generativeai as genai
#from google.generativeai.types import GenerationConfig, FunctionDeclaration, Tool
from google.protobuf.json_format import MessageToDict

from google import genai
from google.genai import types
from google.genai.types import GenerationConfig, FunctionDeclaration, Tool
from google.protobuf.json_format import MessageToDict

from . import ricc_colors as C
#from .ricc_cloud_run import AVAILABLE_FUNCTIONS # Import the function map

# Functions..
from .ricc_cloud_run import * # get_cloud_run_endpoints, get_cloud_run_logs
#from .ricc_cloud_run import PROTOBUF_CONVERTER # Import the converter
from .ricc_gcp import default_project_and_region_instructions
from .ricc_system import current_time
from .ricc_net import check_url_endpoint
from constants import RICC_SIMPLIFIED_FUNCTIONS

from typing import List, Dict, Any
from google.genai.types import Content, Part
from google.genai.types import FunctionCall, FunctionResponse
from lib import ricc_colors as C



# --- Gemini Configuration ---

def configure_gemini_express_mode(api_key: str):
    """Configures the Gemini client."""
    #    genai.configure(api_key=api_key)
    print("Using API KEY mode: configuring client...")
    client = genai.Client(api_key=api_key)
    # client = genai.Client(
    #     vertexai=True, project='your-project-id', location='us-central1'
    # )
    return client


# --- Chat Session Class ---

def get_current_weather(location: str) -> str:
    """Returns the current weather. Used to test Gemini.

    Args:
      location: The city and state/nation, e.g. 'San Francisco, CA', or 'Rome, Italy'
    """
    return 'always super-duper sunny'


def load_model_instructions(filepath: str, project_id: str, region: str, cloud_run_service: str = None) -> str:
    """Loads model instructions from a file and substitutes placeholders."""
    try:
        with open(filepath, 'r') as file:
            instructions = file.read()
        # if project_id:
        #     instructions = instructions.replace('{project_id}', project_id)
        instructions = instructions.replace('{project_id}', project_id or 'UNKNOWN_PROJECT_ID')
        instructions = instructions.replace('{region}', region or 'UNKNOWN_REGION')
        # if region:
        #     instructions = instructions.replace('{region}', region)
        if cloud_run_service:
            instructions = instructions.replace('{cloud_run_service_optional_bullet_point}', '')
        else:
            print("cloud_run_service GIVEN! Probably calling from Streamlit..")
            sentence_to_inject = "- Cloud Run service: '{cloud_run_service}'\n".replace('{cloud_run_service}', cloud_run_service)
            instructions = instructions.replace('{cloud_run_service_optional_bullet_point}', sentence_to_inject)
        print(f"[DEB] Instructions: '''{instructions}'''")
        return instructions
    except FileNotFoundError:
        print(f"{C.ERROR_ICON} load_model_instructions Error: Instructions file not found at {filepath}")
        return "Empty instructions"
    except Exception as e:
        print(f"{C.ERROR_ICON} load_model_instructions Error: reading instructions file: {e}")
        return "No instructions"



def format_chat_history(history: List[Content]) -> str:
    """Formats the chat history for a more user-friendly display."""
    formatted_history = "============== Chat history ==============\n"
    max_response_length = 500  # Maximum length for function responses, chomp()

    for message in history:
        role = message.role
        for part in message.parts:
            if part.text:
                text = part.text.strip()
                if role == "user":
                    formatted_history += f"{C.USER_ICON} {C.blue('You:')} {C.bold(text)}\n"
                elif role == "model":
                    formatted_history += f"{C.GEMINI_ICON} {C.green('Gemini:')} {C.bold(text)}\n"
            elif part.function_call:
                formatted_history += f"{C.TOOL_ICON} {C.magenta('Function Call:')} {part.function_call.name}({C.darkgray(part.function_call.args)})\n"
            elif part.function_response:
                response_str = str(part.function_response.response)
                if len(response_str) > max_response_length:
                    response_str = response_str[:max_response_length] + "... ✂️"  # Truncate and add emoji
                formatted_history += f"{C.TOOL_ICON} {C.cyan('Function Response:')} {part.function_response.name}: {C.darkgray(response_str)}\n"
    return formatted_history


class GeminiChatSession:
    def __init__(self, project_id: str, region: str, api_key: str, model: str, verbose: bool = False, debug: bool = False, cloud_run_service: str = None):
        self.project_id = project_id
        self.region = region
        self.verbose = verbose
        self.debug = debug
        self.model = model
        self.api_key = api_key
        # Load instructions from file
        instructions_file = "etc/strict_project_region_instructions.prompt"
        self.model_instructions = load_model_instructions(instructions_file, project_id, region, cloud_run_service)

        if debug:
            print("GeminiChatSession: DEBUG ENABLED!")
        if verbose:
            print("GeminiChatSession: VERSBOSE ENABLED!")

        print("Ricc, siccome non va una cippa inizializzo solo il costruttore..")
        # copiato da https://ai.google.dev/gemini-api/docs/function-calling?example=meeting
        #tools = Tool(function_declarations=[get_cloud_run_endpoints])
        #tools = Tool(function_declarations=RICC_SIMPLIFIED_FUNCTIONS)
        self.tools = RICC_SIMPLIFIED_FUNCTIONS
        print("TODO - do the big Tool Mgmt stuff here.")
        self.client = genai.Client()
        self.chat = self.client.chats.create(model=model)
        print("[DEB] CHAT object created: {self.chat.__class__() }")
        #print(self.chat._curated_history())
        #print(self.chat.get_history())
        # if debug:
        #     print("DEBUG: empty history maybe bug ahead")
        #     print(self.get_chat_history_array())

        # local - dies after initialization
        serialized_tools = []
        for tool in self.tools:
            if isinstance(tool, FunctionDeclaration):
                serialized_tools.append(MessageToDict(tool._pb))
            else:
                serialized_tools.append(tool)

        # Convert the tools to a list of dictionaries
        config_tools = []
        for tool in serialized_tools: # self.tools:
            if isinstance(tool, FunctionDeclaration):
                # Convert FunctionDeclaration to a dictionary using our converter
                converted_tool = PROTOBUF_CONVERTER.convert(tool)
                if converted_tool:
                    config_tools.append(converted_tool)
                else:
                    print(f"{C.ERROR_ICON} Error: Could not convert FunctionDeclaration {tool.name} to dictionary.")
                    # Handle the error appropriately, e.g., skip this tool or raise an exception
            else:
                # If it's not a FunctionDeclaration, it's a function, so we don't need to convert it
                config_tools.append(tool)
        self.config_tools = config_tools

        print(f"{C.INFO_ICON} Gemini chat session initialized for project '{C.bold(project_id)}' in region '{C.bold(region)}'. Model: {self.model}", flush=True)

    # def get_chat_history_array(self):
    #     """prints GenAI chat history for self, in array.

    #     Made safe now, returns empty if history gives error."""
    #     # len(this) gives you history size
    #     try:
    #         return self.chat.get_history()
    #     except e:
    #         print(f"Some error: {e}")
    #         return []
    def get_chat_history_array(self):
        """Returns GenAI chat history for self as an array.

        Made safe now, returns empty list if history retrieval gives an error."""
        try:
            return self.chat.get_history()
        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            return []

    # more idiomatic, but what can non-rubyists understand? :)
    def chat_history(self):
        return self.get_chat_history_array()
    def get_chat_history(self):
        return self.get_chat_history_array()

    def get_chat_history_formatted(self):
        """Returns the formatted chat history."""

        #return format_chat_history(self.chat.get_history())
        format_chat_history(self.get_chat_history_array())


    def test_weather_functionality(self, prompt: str):
        """Sends a test prompt to Gemini with function calling.
        Just for cheap easy tests.

        Chat doesnt seem to support Tool Calling.
        """
        print(f"test_weather_functionality(prompt='{prompt}'): start")
        client = self.client
        tools = [get_current_weather]
        config = types.GenerateContentConfig(
                system_instruction='You are a helpful, European weather forecast service. You always use Centigrads and a funny French accent.',
                tools=tools,
                #automatic_function_calling=True
                )

        response = self.chat.send_message(prompt, config=config)
        print(f"test_weather_functionality: {C.yellow(response.text)}")
        if response.function_calls:
            print("FUN_CALL is TRUE. Prnting them..")
            print(response.function_calls)


    def send_simple_message(self, prompt: str):
        """Riccardo simplified function using chat for history persistence.

        Utilization:
            returns a Gemini Response. Use return.text to get the text and
            use the object to do more compplex stuff (like parse function calls)
            if needed.
        """
        print(f"\n{C.USER_ICON} SSM {C.blue('You:')} {C.cyan(prompt)}", flush=True)
        client = self.client
        #print(f"[DEB] send_simple_message: prompt = {prompt}")
        print(f"[DEB] [model={C.cyan(self.model)}] prompt size: {len(prompt)}")

        response = self.chat.send_message(  # Use self.chat here
            prompt,
            config=types.GenerateContentConfig(
                system_instruction=self.model_instructions,
                tools=self.config_tools,  # Use the converted tools
            ),
        )
        self.latest_response = response # why not being more stateful?
        if self.verbose:
            print(f"[VERBOSE] send_simple_message: {C.yellow(response.text)}")
        print(f"{C.GEMINI_ICON} [{C.purple(self.model)}]: {C.yellow(response.text)}")
        if response.function_calls:
            print("FUN_CALL is TRUE. 1. Printing them..")
            print(response.function_calls)
        else:
            logger.debug("FUN_CALL is FALSE. Not sure if maybe an exception was triggered and i cant see it. I smell some issue here.")
            #print(response.candidates[0])
        return response



    def get_info(self):
        '''Returns useful informsation in form of a dict'''
        ret = {}
        ret['my_tools'] = self.tools
        return ret

    def list_models(self):
        '''Ricc copied this from SO.

        https://stackoverflow.com/questions/78772795/what-is-the-python-code-to-check-all-the-generativeai-models-supported-by-google
        '''
        import google.generativeai as genai_ciofeco
        import os

        genai_ciofeco.configure(api_key=api_key)
        genai_ciofeco.configure(transport='grpc')

        for i, m in zip(range(5), genai_ciofeco.list_models()):
            print(f"Name: {m.name} Description: {m.description} support: {m.supported_generation_methods}")
        return genai_ciofeco.list_models()


# def generate_content_with_function_calling(prompt: str):
#     '''TODO created by Gemini'''
#     print("TODO implement me")
#     pass
