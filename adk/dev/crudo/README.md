# Cloud Run DevOps (CRuDO) 🍖 Tool

This project provides tools to investigate and troubleshoot Google Cloud Run services using the Gemini API.
It includes a command-line interface (CLI) agent for direct interaction and a Streamlit web application for a more visual experience.

## Features

### CLI Agent

*   Interact with a Gemini-powered agent via your terminal.
*   Utilize function calling to retrieve information about your Cloud Run services.
*   Get details on endpoints, revisions, logs, and configurations.

### Streamlit UI

*   Web-based interface for a user-friendly experience.
*   Select GCP projects and Cloud Run services via dropdowns.
*   View a synoptic overview of a selected service, including key metrics and configuration.
*   Engage in persistent chat investigations with a Gemini model, visualizing generated charts directly in the conversation.

## Getting Started

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Set up your environment variables:**

    Create a `.env` file in the `python-code/` directory with the following variables:

    ```dotenv
    GOOGLE_CLOUD_PROJECT=your-gcp-project-id
    GOOGLE_CLOUD_LOCATION=your-gcp-region
    GOOGLE_API_KEY=your-gemini-api-key
    # Optional: Set a favorite service for the CLI
    # FAVORITE_CLOUD_RUN_SERVICE=your-default-service-name
    ```

    Replace the placeholder values with your actual GCP project ID, region, and Gemini API key.

3.  **Install dependencies:**

    Navigate to the `python-code/` directory and install the required Python packages:

    ```bash
    cd 01-prova-python/
    pip install -r requirements.txt
    ```

4.  **Provision Service Account (Recommended for Production):**

    For production environments, it's recommended to run the provisioning script to create a dedicated service account with limited permissions. This script is located in the `bin/` directory at the project root.

    ```bash
    # From the project root directory
    ./bin/provision-agent-sa.sh [YOUR_GCP_PROJECT_ID]
    ```

    Follow the prompts to create the service account and grant necessary read-only permissions for Cloud Run, Logging, Monitoring, and BigQuery.

## Usage

### CLI Agent

Navigate to the `python-code/` directory and run the `main.py` script:

```bash
python main.py
```

You can also provide an initial prompt or a prompt file:

```bash
python main.py --prompt "How are my Cloud Run services doing?"
python main.py --promptfile etc/prompts/generic-app-test.prompt
```

Type `quit` or `exit` to end the chat. Type `hist` to see chat history. Type `info` for more information.

### Streamlit UI

Navigate to the `01-prova-python/` directory and run the `app2.py` script:

```bash
streamlit run app2.py
```

The application will open in your web browser.

## Project Structure

```
crudo/
├── python-code/
│   ├── app.py             # Older Streamlit app (can be removed)
│   ├── app2.py            # Main Streamlit application
│   ├── constants.py       # Project constants
│   ├── main.py            # Main CLI entry point
│   ├── requirements.txt   # Python dependencies
│   ├── .env.dist          # Example environment file
│   ├── ...                # Other environment files
│   ├── lib/
│   │   ├── ricc_cloud_monitoring.py # Cloud Monitoring interactions
│   │   ├── ricc_cloud_run.py        # Cloud Run API interactions
│   │   ├── ricc_genai.py            # Gemini API interactions
│   │   ├── ricc_gcp.py              # Basic GCP interactions
│   │   ├── ricc_gcp_projects.py     # GCP Projects listing
│   │   ├── ricc_net.py              # Network utilities
│   │   ├── ricc_protobuf_converter.py # Protobuf to Dict conversion
│   │   ├── ricc_system.py           # System utilities
│   │   ├── ricc_utils.py            # General utilities
│   │   ├── streamlit/             # Older Streamlit components
│   │   └── streamlit2/            # New Streamlit components
│   │       ├── __init__.py
│   │       ├── config.py
│   │       ├── db.py              # SQLite Database interactions
│   │       ├── gcp_helpers.py     # Streamlit GCP data fetching
│   │       └── ui.py              # Streamlit UI rendering
│   ├── etc/
│   │   └── prompts/           # Example prompts
│   └── ...                # Other files and directories
├── bin/
│   ├── process-cloudrun-json.sh # Script to process inventory JSON
│   ├── provision-agent-sa.sh    # Script to provision Service Account
│   └── ...                # Other scripts
├── cloud_run_services_inventory.json # Generated inventory (can be ignored)
├── cloud_run_services_inventory4user.json # Generated inventory (can be ignored)
└── README.md
```

## Future Enhancements

*   Refactor and distill the codebase into more focused modules.
*   Improve error handling and user feedback.
*   Add more comprehensive testing.
*   Explore additional Cloud Run and GCP APIs for more capabilities.
