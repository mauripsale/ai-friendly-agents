'''This Marchesa (inspired by the 9th Osteria) is the summa of Cloud Run knowledge.
'''

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import FunctionTool

# Import functions from constants.py and lib
from .constants import (
    default_project_and_region_instructions,
    current_time,
    current_place,
    check_url_endpoint,
    get_cloud_run_endpoints,
    get_cloud_run_revisions,
    get_cloud_run_logs,
    gfc_generate_cloud_run_requests_vs_latency_chart,
    gfc_generate_cloud_run_instance_chart,
    gfc_generate_cloud_run_network_chart,
    gfc_generate_cloud_run_cpu_memory_chart,
    execute_gcloud_command,
)

# Create FunctionTool instances for each function
crudo_tools = [
    FunctionTool(default_project_and_region_instructions),
    FunctionTool(current_time),
    FunctionTool(current_place),
    FunctionTool(check_url_endpoint),
    FunctionTool(get_cloud_run_endpoints),
    FunctionTool(get_cloud_run_revisions),
    FunctionTool(get_cloud_run_logs),
    FunctionTool(gfc_generate_cloud_run_requests_vs_latency_chart),
    FunctionTool(gfc_generate_cloud_run_instance_chart),
    FunctionTool(gfc_generate_cloud_run_network_chart),
    FunctionTool(gfc_generate_cloud_run_cpu_memory_chart),
    FunctionTool(execute_gcloud_command),
]

sample_questions = [
   'What can you do?',
   'What is my Project id?',
   'Show me the Cloud Run apps running in this project',
]


root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='CloudRunAgent',
    instruction="""
    You're the Marchesa Sofia Crudo (or Mrs Crudo), a knowledgeable agent who know everything about Cloud Run.
    """,
    tools=crudo_tools,
)