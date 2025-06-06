def get_current_temperature(location: str) -> dict:
    """Gets the current temperature for a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA

    Returns:
        A dictionary containing the temperature and unit.
    """
    # ... (implementation) ...
    return {"temperature": 25, "unit": "Celsius"}



from constants import *
from google import genai
from google.genai import types

CHAT_GEMINI_MODEL = "gemini-2.0-flash"
print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")
print(f"CHAT_GEMINI_MODEL: {CHAT_GEMINI_MODEL}")

config = types.GenerateContentConfig(
    tools=[get_current_temperature]
)  # Pass the function itself


#client = genai.Client(api_key=GEMINI_API_KEY, vertexai=False)
client = genai.Client(vertexai=True)
chat = client.chats.create(model=CHAT_GEMINI_MODEL)

response = chat.send_message("I have 2 dogs in my house, called Ricky and Nardy.",    config=config,)
print(response.text)

response = chat.send_message("How many paws are in my house? Whats my dogs name?",    config=config, )
print(response.text)

for message in chat.get_history():
    print(f'role - {message.role}',end=": ")
    print(message.parts[0].text)
