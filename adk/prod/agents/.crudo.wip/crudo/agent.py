'''This Marchesa (inspired by the 9th Osteria) is the summa of Cloud Run knowledge.
'''

from google.adk.tools import agent_tool
from google.adk.agents import Agent

from google.adk.tools import google_search


sample_questions = [
   'What can you do?',
   'What is my Project id?',
   'Show me the Cloud Run apps running in this project',
]


#coding_agent = Agent(
root_agent = Agent(
    model='gemini-2.0-flash',
    name='CloudRunAgent',
    instruction="""
    You're the Marchesa Sofia Crudo (or Mrs Crudo), a knowledgeable agent who know everything about Cloud Run.
    """,
    tools=[google_search],
)
