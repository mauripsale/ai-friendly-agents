## todo Ricc when home clean this up.

from pathlib import Path
#from typing import List, Optional
#from typing_extensions import Annotated  # For Typer >0.9 for Optional flags
#import typer
from ricclib.utils import enumerate_data_sources, find_files
#from agent import enumerate_data_sources
#from google.adk.agents import Agent
#from google.adk.agents import LlmAgent

#import agent
print('testing agent.py')

sources = enumerate_data_sources()
print(enumerate_data_sources())
#print(find_files(sources[0], [".pdf"] )) # , ".md", ".txt"
