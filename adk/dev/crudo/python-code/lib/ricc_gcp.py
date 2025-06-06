import os
import logging
from lib.ricc_system import log_function_called

# Configure the logger
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def default_project_and_region_instructions():
    '''Retrieves my default Project and Region.

    Args:
        none.

    Returns:
        An array of two strings containing GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION. Example: 'foo-bar' and 'us-central1'
    '''
    log_function_called("default_project_and_region_instructions()")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    region = os.getenv("GOOGLE_CLOUD_LOCATION")
    ret =  {"project_id": project_id, "region": region }
    logger.debug(f"[func_call] default_project_and_region_instructions: {ret}")
    return ret


