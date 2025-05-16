# Cloud Run Investigator - Python Application

This directory contains the core Python application for the Cloud Run Investigator, providing both a command-line interface (CLI) and a Streamlit web UI.

## Setup

1.  **Navigate to the application directory:**

    ```bash
    cd python-code/
    ```

2.  **Set up your environment variables:**

    Ensure you have a `.env` file in this directory with the necessary credentials and configuration. See the main `../README.md` for details on the required variables.

3.  **Install dependencies:**

    Install the Python packages listed in `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Before you run either agent, make sure to do this:

```bash
# Make sure all info is correctly set into .env
bin/create-gcloud-config-by-env .env # or whichever the name of your dot env.
```

### Run the CLI Agent

```bash
python main.py
```

Use `--prompt` or `--promptfile` for initial input. Type `quit` or `exit` to end.

### Run the Streamlit UI

```bash
# or: just app
streamlit run app2.py
```

This will open the web application in your browser.

## Structure

*   `main.py`: Entry point for the CLI agent.
*   `app2.py`: Entry point for the Streamlit web application.
*   `constants.py`: Application-wide constants.
*   `requirements.txt`: Lists Python dependencies.
*   `.env*`: Environment variable files (should be ignored by git).
*   `lib/`: Contains the core logic modules.
    *   `ricc_cloud_monitoring.py`: Interactions with Cloud Monitoring API.
    *   `ricc_cloud_run.py`: Interactions with Cloud Run Admin and Logging APIs.
    *   `ricc_genai.py`: Handles interactions with the Gemini API.
    *   `ricc_gcp.py`: General GCP utility functions.
    *   `ricc_gcp_projects.py`: Functions for listing GCP projects.
    *   `ricc_net.py`: Network utility functions (e.g., checking URLs).
    *   `ricc_protobuf_converter.py`: Helper for converting Protobuf messages.
    *   `ricc_system.py`: System-related utilities.
    *   `ricc_utils.py`: General helper functions.
    *   `streamlit2/`: Modules specific to the Streamlit UI.
        *   `config.py`: Streamlit application configuration.
        *   `db.py`: SQLite database interactions for investigations.
        *   `gcp_helpers.py`: Helpers for fetching GCP data for the UI.
        *   `state.py`: Manages Streamlit session state.
        *   `ui.py`: Renders the Streamlit user interface.
*   `etc/`: Configuration files and prompts.
*   `test_*.py`: Unit tests.
```
