import os
import sys
from lib.ricc_gcp import default_project_and_region_instructions
from dotenv import load_dotenv

# Add the lib directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

load_dotenv()

print(default_project_and_region_instructions())
