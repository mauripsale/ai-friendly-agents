#!/usr/bin/env python3

# main.py
# The entry point for our Cloud Run Assistant! 🎉

import argparse
import os
import sys
import logging
from dotenv import load_dotenv, dotenv_values
from pathlib import Path  # Ensure Path is imported
from constants import *
from lib.ricc_utils import save_to_file
from constants import GOOGLE_CLOUD_PROJECT as CONSTANTS_GOOGLE_CLOUD_PROJECT

# Riccardo added this for troublshooting
if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']

# --- Removed sys.path manipulation ---
# script_dir = os.path.dirname(os.path.realpath(__file__))
# lib_dir = os.path.join(script_dir, 'lib')
# if lib_dir not in sys.path:
#     sys.path.insert(0, lib_dir)

# Now import using the 'lib' package name directly
try:
    # Import directly from the 'lib' package
    from lib.ricc_genai import GeminiChatSession
    #from lib.ricc_colors import deb
    from lib import ricc_colors as C  # Use colors for output
except ImportError as e:
    print(f"{C.ERROR_ICON if 'C' in locals() else '🚨'} Error importing library modules: {e}", file=sys.stderr)
    # Give a more specific hint if the error persists
    print("Please ensure the 'lib' directory with '__init__.py' exists in the same directory as 'main.py'.", file=sys.stderr)
    print("Also ensure all dependencies in 'requirements.txt' are installed.", file=sys.stderr)
    sys.exit(1)

# Configure the root logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_external_library_log_levels(level):
    """Sets the log level for external libraries."""
    logging.getLogger("google.auth").setLevel(level)
    logging.getLogger("httpcore").setLevel(level)
    logging.getLogger("httpx").setLevel(level)
    logging.getLogger("google.generativeai").setLevel(level)
    logging.getLogger("urllib3").setLevel(level)
    logging.getLogger("google.api_core").setLevel(level)
    logger.debug(f"External library log levels set to {logging.getLevelName(level)}")




def main():
    parser = argparse.ArgumentParser(
        description="Chat with Gemini to manage Google Cloud Run services.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--prompt",
        help="Optional initial prompt to start the conversation.",
        type=str,
        default=None
    )
    parser.add_argument(
        "--promptfile",
        help="Optional file containing the initial prompt.",
        type=str,
        default=None
    )
    parser.add_argument(
        "--verbose",
        help="Show verbose output, including function call details.",
        action="store_true"
    )
    parser.add_argument(
        "--debug",
        help="Show detailed debug information, including function results.",
        action="store_true"
    )
    parser.add_argument(
        "--env", # TODO add -e
        help="Path to the .env file.",
        default=".env"
    )

    args = parser.parse_args()

    # Load environment variables
    dotenv_path = Path(args.env)
    if not dotenv_path.exists():
        print(f"{C.ERROR_ICON} Environment file not found: {dotenv_path}", file=sys.stderr)
        print(f"Please create a '{dotenv_path}' file with GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, and GOOGLE_API_KEY.", file=sys.stderr)
        sys.exit(1)

    load_dotenv(dotenv_path=dotenv_path)
    config = dotenv_values(dotenv_path)
    print(f"[ENV] Config taken from {dotenv_path}: {config}")

    project_id = config['GOOGLE_CLOUD_PROJECT'] # os.getenv("GOOGLE_CLOUD_PROJECT")
    #project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    region = config['GOOGLE_CLOUD_LOCATION'] # os.getenv("GOOGLE_CLOUD_LOCATION")
    #region = os.getenv("GOOGLE_CLOUD_LOCATION")
    api_key = os.getenv("GOOGLE_API_KEY")#
    DOTENV_DESCRIPTION = os.getenv("DOTENV_DESCRIPTION")
    dotenv_desc = config['DOTENV_DESCRIPTION']
    model = os.getenv("GEMINI_MODEL", 'gemini-2.0-flash-001')
    user_location = os.getenv("USER_LOCATION", 'San Francisco, US')
    print(f"Now forcing some values from {C.yellow(dotenv_path)} into the followin 3 vars:")
    print(f"Now project_id (forceful)  = {C.yellow(project_id)}")
    print(f"Now region     (forceful)  = {C.yellow(region)}")
    print(f"DotEnv Desc    (forceful)  = {C.yellow(dotenv_desc)}")

    print(f"Gemini model  (from ENV)      = {C.green(model)}")
    print(f"api_key       (from ENV)      = {C.green(api_key)}")
    print(f"DOTENV_DESCRIPTION (from ENV) = {C.green(DOTENV_DESCRIPTION)}")

    #GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    # GCP_REGION = os.getenv("GOOGLE_CLOUD_LOCATION")
    # GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    # GEMINI_MODEL = os.getenv("GEMINI_MODEL", 'gemini-2.0-flash-001')
    # FAVORITE_CLOUD_RUN_SERVICE = os.getenv("FAVORITE_CLOUD_RUN_SERVICE", None)
    CONSTANTS_DEFINED_IN = 'main.py (redefined)' # redefinable, sweet!

    if 'GOOGLE_CLOUD_PROJECT' not in locals():
        GOOGLE_CLOUD_PROJECT = 'non datur'
    if 'CONSTANTS_GOOGLE_CLOUD_PROJECT' not in locals():
        #print("Yes in globals l")
        #GOOGLE_CLOUD_PROJECT = 'existiert nood in globalitaet'
        GOOGLE_CLOUD_PROJECT = CONSTANTS_GOOGLE_CLOUD_PROJECT
    #else:
    #    print("Not in globals l")

    print(f"GOOGLE_CLOUD_PROJECT (from constants) = {C.yellow(GOOGLE_CLOUD_PROJECT)}")
    #print(f"GOOGLE_CLOUD_PROJECT (from constants) = {C.green(constants.GOOGLE_CLOUD_PROJECT)}")
    GOOGLE_CLOUD_PROJECT = project_id # os.getenv("GOOGLE_CLOUD_PROJECT")
    print(f"GOOGLE_CLOUD_PROJECT (redefined) = {C.green(GOOGLE_CLOUD_PROJECT)}")

    #GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    #GCP_REGION = os.getenv("GOOGLE_CLOUD_LOCATION")
    #GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

    #exit(42)


    if not project_id or not region or not api_key:
        print(f"{C.ERROR_ICON} Missing required environment variables in {dotenv_path}.", file=sys.stderr)
        print("Ensure GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, and GOOGLE_API_KEY are set.", file=sys.stderr)
        sys.exit(1)

    # Set external library log levels based on debug flag
    if args.debug:
        set_external_library_log_levels(logging.DEBUG)
        global DEBUG #  = True
        DEBUG = True
    else:
        set_external_library_log_levels(logging.WARNING)

    # Start the chat session
    #try:
        # Pass C (colors module) if needed by GeminiChatSession, otherwise remove
        chat_session = GeminiChatSession(
            project_id=project_id,
            region=region,
            api_key=api_key,
            model=model,
            verbose=args.verbose,  # Set verbose directly from args.verbose
            debug=args.debug
        )

        print(C.yellow("\n--- Welcome to CRUDO, the Cloud RUn DevOps assistant ---"))
        print(f"Talking to project '{C.bold(project_id)}' in region '{C.bold(region)}' (model={C.bold(model)}). Type 'quit' or 'exit' to end. Type 'hist' to get history")
        sample_prompt = "How are my Cloud Run services doing?"
        print(f"Example prompt: {C.cyan(sample_prompt)}")
        # if DEBUG:
        #     print(f"Debug1 should be enabled: {C.cyan(args.debug)}")
        # deb(f"Debug2 should be enabled: {args.debug}")
        # Handle initial prompt if provided
        initial_prompt = None
        if args.promptfile:
            try:
                with open(args.promptfile, 'r') as f:
                    initial_prompt = f.read().strip()
            except FileNotFoundError:
                print(f"{C.ERROR_ICON} Prompt file not found: {args.promptfile}", file=sys.stderr)
                sys.exit(1)
        elif args.prompt:
            initial_prompt = args.prompt

        if initial_prompt:
            # print("todo ricc once it works remove me..")
            print(f"Got prompt: {C.bold(initial_prompt)}")
            #chat_session.send_simple_message(f"In the following conversation, please remember to use use GCP project id as '{project_id}' and region '{region}'.")
            if FAVORITE_CLOUD_RUN_SERVICE:
               InitialConvoPrompt =  f"In the following conversation, please remember to use use GCP project id as '{project_id}' and region '{region}'. Also assume the Cloud Run Service of interest is always '{FAVORITE_CLOUD_RUN_SERVICE}' (unless the user specifically tells you otherwise)"
            else:
                InitialConvoPrompt = f"In the following conversation, please remember to use use GCP project id as '{project_id}' and region '{region}'."
            # THIS WORKS
            chat_session.send_simple_message(InitialConvoPrompt)
            for line in initial_prompt.splitlines():
                chat_session.send_simple_message(line)
            # THIS WORKS
            #chat_session.test_weather_functionality(initial_prompt)
            #chat_session.test_weather_functionality("Where do i live again?!?")
            #chat_session.test_weather_functionality("Repeat the weather forecast please, I missed it.")
            # End of session
            #print(f"History: ```{chat_session.get_chat_history()}```")
            #print(chat_session.get_chat_history())
            txt_file_content = f"initial_prompt: '''{initial_prompt}'''\n\n\n{chat_session.get_chat_history()}"
            save_to_file('chat_history_from_prompt.latest.txt', txt_file_content)
            #save_to_file('chat_history.latest.txt', chat_session.get_chat_history())
            print(C.yellow("👋 Goodbye!"))
            exit(0)
        else:
            print('[main] No prompt provided => entering infinite chat loop. Type "quit" or "exit" to end, "help" for other.')
            chat_session.send_simple_message(f"Please find the configuration for my project ('{project_id}') and region ('{region}')")
            # Main chat loop
            #print(C.bold("Big Bug: currently the chat doesnt support history. Every message is by itself :/"))
            while True:
                try:
                    user_input = input(f"\n{C.USER_ICON} {C.blue('You:')} ")
                    if user_input.lower() in ["quit", "exit"]:
                        print(C.yellow("👋 Goodbye!"))
                        break
                    if user_input.lower() in ["hist", "history"]:
                        print(C.orange("Let's get to a Chat History lesson!"))
                        print(chat_session.get_chat_history())
                        continue
                    if user_input.lower() in ["info", "information"]:
                        print(C.orange("Let's get some Juicy Info!"))
                        print(chat_session.get_info())
                        continue
                    if user_input.lower() in ["demo"]:
                        print(C.orange("TODO(ricc): do some auto-chat with sample rows which narrates a story and maybe pauses a few dramatic seconds before injecting the next chat."))
                        #print(chat_session.get_info())
                        print("Riccardo, check in justfile, there are some great demo stories in test/etc/*.prompt")
                        continue
                    if user_input.lower() in ["help", "aiuto"]:
                        print(C.orange("Supported Carlessian Keywords: help, info, hist, demo, quit/exit."))
                        #print(chat_session.get_info())
                        continue
                    if not user_input:
                        continue

                    # chat_session.send_message(user_input)
                    chat_session.send_simple_message(user_input)

                except KeyboardInterrupt:
                    print(C.yellow("\n👋 Exiting due to keyboard interrupt."))
                    break
                except EOFError:  # Handle Ctrl+D
                    print(C.yellow("\n👋 Exiting due to EOF."))
                    break


    # except Exception as e:
    #     print(f"\n{C.ERROR_ICON} [main] A critical error occurred: {e}", file=sys.stderr)
    #     import traceback
    #     traceback.print_exc()
    #     sys.exit(1)


if __name__ == "__main__":
    # No need for Path import here anymore unless used elsewhere in main directly
    main()
