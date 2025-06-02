
# CRuDO 1.0 Agent (Work in Progress)

This directory contains a work-in-progress migration of the Cloud Run DevOps (CRuDO) agent to ADK v1.0.

The original CRuDO agent is designed to help with Cloud Run operations, monitoring, and logging via chat.

**Purpose of the original CRuDO agent:**

*   **Ops**: Investigate a Cloud Run service via chat.
*   **Monitoring**: Generate charts on demand.
*   **Logging**: Get/analyze logs, and get them by day.

This `crudo10/` version is being updated to be compatible with ADK v1.0, using `LlmAgent` and other v1.0 features.

Further migration and development are required to fully implement the original CRuDO agent's functionality with ADK v1.0.

## Running the CRuDO 1.0 Agent

This agent is configured to run using `uvicorn` within a `uv` virtual environment, with the necessary `PYTHONPATH` set to include the `lib/` directory.

The `adk-prod-agents/justfile` contains targets to simplify running this agent:

*   **Using `adk run .`:**
    From the `adk-prod-agents/` directory, run:
    ```bash
    just run-crudo10
    ```
    *(Note: Running `adk run .` directly from the `crudo10/` directory might fail due to import issues with the `lib` directory, as the standard `adk run` command might not set the `PYTHONPATH` correctly. The `just` target handles this.)*

*   **Using `adk web` (for the development UI):**
    From the `adk-prod-agents/` directory, run:
    ```bash
    just web-crudo10
    ```

These `just` targets activate the `uv` environment and run the agent using `uvicorn` with the correct configuration.
