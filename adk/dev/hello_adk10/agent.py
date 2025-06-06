from google.genai import types
from google.adk.agents import LlmAgent

# Define a simple tool function to retrieve the capital city of a country
def get_capital_city(country: str) -> str:
  """Retrieves the capital city for a given country."""
  # Replace with actual logic (e.g., API call, database lookup)
  capitals = {"france": "Paris", "japan": "Tokyo", "canada": "Ottawa"}
  return capitals.get(country.lower(), f"Sorry, I don't know the capital of {country}.")

# Add the tool to the agent
# capital_agent
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="capital_agent",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2, # More deterministic output
        max_output_tokens=250
    ),
    description="Answers user questions about the capital city of a given country.",
    instruction="""You are an agent that provides the capital city of a country... (previous instruction text)""",
    tools=[get_capital_city] # Provide the function directly
)
