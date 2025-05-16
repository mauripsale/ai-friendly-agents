import subprocess
import sys
from google.cloud import resourcemanager_v3
from google.auth.exceptions import DefaultCredentialsError
from google.api_core import exceptions as api_exceptions

def get_projects_by_user(user_email):
    """
    Finds projects accessible by the currently authenticated credentials.

    Note: This function uses the Application Default Credentials (ADC)
          to query the Resource Manager API. The 'user_email' parameter
          is included to match the requested structure but isn't strictly
          used for the API call itself. The API call reflects the identity
          that ADC resolves to (which might be the same as user_email,
          or could be a service account if ADC is configured that way).

    Note 2: This could return MANY projects. Ricc@ has >11000
    """
    print(f"INFO: Searching for projects accessible by the identity associated with ADC (requested for user: {user_email})...")
    project_ids = []
    try:
        client = resourcemanager_v3.ProjectsClient()
        # Search_projects() finds projects the credential has permission to view.
        request = resourcemanager_v3.SearchProjectsRequest()
        projects_iterator = client.search_projects(request=request)
        project_ids = [project.project_id for project in projects_iterator]
        print(f"INFO: Found {len(project_ids)} accessible projects via API.")

    except DefaultCredentialsError:
        print("ERROR: Could not find Application Default Credentials.", file=sys.stderr)
        print("       Please run 'gcloud auth application-default login'.", file=sys.stderr)
    except api_exceptions.PermissionDenied:
        print("ERROR: Permission denied when trying to list projects.", file=sys.stderr)
        print("       Ensure the authenticated identity has 'resourcemanager.projects.list' permission.", file=sys.stderr)
    except Exception as e:
        # Catch other potential API errors (e.g., API not enabled)
        print(f"ERROR: An API error occurred while listing projects: {e}", file=sys.stderr)

    return project_ids

def my_projects_using_gcloud_email():
    """
    Gets the email from the active gcloud config using subprocess,
    then calls get_projects_by_user.

    """
    my_email = ""
    try:
        # Use get-value for cleaner output, check=True raises error on failure
        gcloud_command = ["gcloud", "config", "get-value", "account"]
        result = subprocess.run(
            gcloud_command,
            capture_output=True,
            text=True, # Decode stdout/stderr as text
            check=True, # Raise CalledProcessError if command fails
            encoding='utf-8' # Be explicit about encoding
        )
        my_email = result.stdout.strip()
        if not my_email:
            print("ERROR: gcloud config returned an empty email.", file=sys.stderr)
            return [] # Return empty list if email is empty

        print(f"INFO: Email obtained via `gcloud config get-value account`: {my_email}")
        return get_projects_by_user(my_email)

    except FileNotFoundError:
        print("ERROR: 'gcloud' command not found.", file=sys.stderr)
        print("       Please ensure the Google Cloud SDK is installed and in your PATH.", file=sys.stderr)
        return [] # Return empty list on error
    except subprocess.CalledProcessError as e:
        print(f"ERROR: '{' '.join(gcloud_command)}' failed:", file=sys.stderr)
        # Avoid printing potentially sensitive stderr unless debugging
        # print(f"  Stderr: {e.stderr.strip()}", file=sys.stderr)
        print(f"       Is gcloud authenticated? Try 'gcloud auth login' or 'gcloud auth list'.", file=sys.stderr)

        return [] # Return empty list on error
    except Exception as e:
        print(f"ERROR: An unexpected error occurred in my_projects_using_gcloud_email: {e}", file=sys.stderr)
        return []


# # --- Example Usage ---
# if __name__ == "__main__":
#     print("--- Running my_projects_using_gcloud_email() ---")
#     projects = my_projects_using_gcloud_email()
#     if projects:
#         print(f"\nAccessible Projects Found: {len(projects)}")
#         for proj in projects:
#             print(f"- {proj}")
#     else:
#         print("\nNo projects found or an error occurred.")
