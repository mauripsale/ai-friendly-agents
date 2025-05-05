import os

# UNUSED FOR NOW.
# def execute(cmd: str, cwd: str = None):
#     '''Executes a generic command.'''
#     if cwd:
#         os.chdir(cwd)
#     #if cmd.startswith("gcloud"):
#        #print(f"Executing gcloud command: {cmd}")
#        # TODO: Implement actual gcloud execution here
#     result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
#     return { "ret": "success", "result": result.stdout }
#     # else:
#     #    print(f"Executing generic command: {cmd}")
#     #    # TODO: Implement generic command execution here
