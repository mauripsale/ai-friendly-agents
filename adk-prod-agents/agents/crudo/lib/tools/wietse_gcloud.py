'''From Wietse idea, lets see if Gemini is smart enough to calculate generic gcloud commands.
'''

import subprocess
import time
from typing import Dict, Union

def execute_generic_shell_command(cmd: str) -> Dict[str, Union[int, str]]:
    """
    Executes a generic Linux command and returns its output, error,
    return code, and execution time.

    This is DANGEROUS - Gemini should NEVER use it by itself.

    Args:
        cmd: The command string to execute.

    Returns:
        A dictionary containing:
            ret (int): The command's return code.
            stdout (str): The command's standard output.
            stderr (str): The command's standard error.
            execution_time (str): The execution time formatted like '0.488s'.
    """
    print(f"🚀 Attempting to run command: {cmd}")
    start_time = time.monotonic()
    result = {'ret': -1, 'stdout': '', 'stderr': '', 'execution_time': '0.0s'} # Default/error state

    try:
        # Using shell=True allows passing the command as a single string,
        # but be cautious about unsanitized input!  Mwahahaha 😈
        process = subprocess.run(
            cmd,
            shell=True,
            check=False,  # Don't raise exception on non-zero exit code
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, # Automatically decode stdout/stderr as text
            timeout=300 # Added a 5-minute timeout, just in case things get wild!
        )
        end_time = time.monotonic()

        result['ret'] = process.returncode
        result['stdout'] = process.stdout.strip() # Strip trailing newline often added
        result['stderr'] = process.stderr.strip()
        result['execution_time'] = f"{end_time - start_time:.3f}s"
        result['status'] = 'success' if process.returncode == 0 else f"some_error (exit {process.returncode})"

        if process.returncode == 0:
            print(f"✅ Command executed successfully in {result['execution_time']}!")
        else:
            print(f"⚠️ Command finished with non-zero exit code ({process.returncode}) in {result['execution_time']}.")
            print(f"   Stderr: {result['stderr'][:200]}...") # Print first 200 chars of stderr

    except FileNotFoundError:
        end_time = time.monotonic()
        result['stderr'] = f"Error: Command not found: '{cmd.split()[0]}'. Is it installed and in PATH?"
        result['execution_time'] = f"{end_time - start_time:.3f}s"
        print(f"❌ {result['stderr']}")
    except subprocess.TimeoutExpired:
        end_time = time.monotonic()
        result['stderr'] = f"Error: Command timed out after {end_time - start_time:.3f}s."
        result['ret'] = 124 # Standard exit code for timeout
        result['execution_time'] = f"{end_time - start_time:.3f}s"
        print(f"⏳ {result['stderr']}")
    except Exception as e:
        end_time = time.monotonic()
        result['stderr'] = f"An unexpected error occurred: {e}"
        result['execution_time'] = f"{end_time - start_time:.3f}s"
        print(f"💥 Oh no! An unexpected error: {e}")


    return result


def execute_gcloud_command(command: str, project_id: str, gcloud_format: str = 'json') -> Dict[str, Union[int, str]]:
    '''Adds the --project unless its already there.

    Arguments:

        command: the gcloud command to give, excluded the initial 'gcloud' (eg "run services list")
        project_id: the project id to use
        gcloud_format: the output format for gcloud. Optimal for machine parsing is 'json'.

    Example:

    gcloud_command('my-project', 'run services list')

    => executes 'gcloud --project my-project run services list --format json'

    '''
    return execute_generic_shell_command(f"gcloud --project {project_id} {command} --format {gcloud_format}")


# gcloud --project ric-cccwiki run services list

# --- Example Usage or Unit Test ---
if __name__ == "__main__":
    # Example 1: Successful command (like your gcloud example)
    # Assuming gcloud is configured and you have a project named 'your-gcp-project-id'
    # Replace 'your-gcp-project-id' with an actual project ID or remove --project if default is set
    # gcloud_command = "gcloud --project your-gcp-project-id run services list --format json"
    # Or a simpler one that always works:
    ls_command = "ls -la"
    print(f"\n--- Running: {ls_command} ---")
    output = execute_generic_shell_command(ls_command)
    print("--- Result ---")
    # Use json.dumps for pretty printing the dict if needed
    import json
    print(json.dumps(output, indent=2))
    # print(f"Return Code: {output['ret']}")
    # print(f"Stdout: {output['stdout'][:200]}...") # Print first 200 chars
    # print(f"Stderr: {output['stderr']}")
    # print(f"Time: {output['execution_time']}")

    # Example 2: Command that produces stderr and non-zero exit code
    error_command = "ls /non/existent/path"
    print(f"\n--- Running: {error_command} ---")
    output_err = execute_generic_shell_command(error_command)
    print("--- Result ---")
    print(json.dumps(output_err, indent=2))
    # print(f"Return Code: {output_err['ret']}")
    # print(f"Stdout: {output_err['stdout']}")
    # print(f"Stderr: {output_err['stderr']}")
    # print(f"Time: {output_err['execution_time']}")

    # Example 3: Command not found
    notfound_command = "nonexistentcommand_foo_bar"
    print(f"\n--- Running: {notfound_command} ---")
    output_nf = execute_generic_shell_command(notfound_command)
    print("--- Result ---")
    print(json.dumps(output_nf, indent=2))


    # Example 4: gcloud config list
    notfound_command = "gcloud config list"
    print(f"\n--- Running: {notfound_command} ---")
    output_nf = execute_generic_shell_command(notfound_command)
    print("--- Result ---")
    print(json.dumps(output_nf, indent=2))
