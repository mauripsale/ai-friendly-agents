import streamlit as st
from pathlib import Path
import time # For simulating streaming
import yaml # For parsing service.yaml in synoptic view

# Use relative imports for modules within the streamlit package
from . import state, helpers, database

# Import specific functions needed for UI (selectors, etc.)
# Ensure these exist and have correct signatures in your core libs!
#try:
    #from lib.ricc_gcp import get_projects_by_user
from lib.ricc_utils import get_projects_by_user_faker
# except ImportError:
#     st.error("Failed to import get_projects_by_user from lib.ricc_gcp")
#     # Define a dummy function to avoid crashing the app immediately
#     def get_projects_by_user_faker(user_id): return []
try:
    from lib.ricc_cloud_run import get_cloud_run_endpoints
except ImportError:
    st.error("Failed to import get_cloud_run_endpoints from lib.ricc_cloud_run")
    def get_cloud_run_endpoints(project_id, region): return []
try:
    from lib.ricc_genai import generate_content_with_function_calling # Placeholder!
    # Define a dummy if needed for testing UI without full backend
    # def generate_content_with_function_calling(**kwargs):
    #     yield "Simulated response chunk 1..."
    #     time.sleep(0.5)
    #     yield "Simulated response chunk 2."

except ImportError:
     st.error("Failed to import generate_content_with_function_calling from lib.ricc_genai")
     # Define dummy generator
     def generate_content_with_function_calling(**kwargs):
         yield "ERROR: Gemini function not imported."


# --- Constants ---
USER_AVATAR = "🧑‍💻"
MODEL_AVATAR = "🤖"
DELETE_ICON = "🗑️" # Or "💥" or "❌"

# --- Sidebar Rendering ---
def render_sidebar(cache_dir: Path, service_select_callback):
    """Renders the sidebar content."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"User: {st.session_state.user_id}")
        st.caption(f"Model: {st.session_state.gemini_model}")
        st.caption(f"Region: {st.session_state.cloud_region}") # Default region for lookups

        st.markdown("---")

        # --- Project & Service Selection ---
        st.header("🎯 Select Service")

        # Project Selector
        if not st.session_state.get('available_projects'):
             with st.spinner("Fetching projects..."):
                  try:
                       st.session_state.available_projects = get_projects_by_user_faker(st.session_state.user_id)
                       # Assuming returns list of strings (Project IDs) based on previous fix
                  except Exception as e:
                       st.error(f"Failed to get projects: {e}")
                       st.session_state.available_projects = []

        # Use a temporary variable to hold selection before committing to state if needed,
        # but binding with 'key' and using 'on_change' is standard.
        st.selectbox(
            "Select GCP Project:",
            options=st.session_state.available_projects,
            index=None if not st.session_state.project_id else st.session_state.available_projects.index(st.session_state.project_id),
            key="project_id", # Binds to session state automatically
            placeholder="Choose a project...",
            # No on_change needed here, service selector depends on it
        )

        # Service Selector (only if project is selected)
        selected_service_name = None
        if st.session_state.project_id:
             # Fetch services if project changes or services aren't loaded for this project
             # This could be more efficient by caching per project_id
             current_services = st.session_state.get(f"services_{st.session_state.project_id}", [])
             if not current_services:
                 with st.spinner(f"Fetching Cloud Run services for {st.session_state.project_id}..."):
                    try:
                        endpoints_answer = get_cloud_run_endpoints(
                            project_id=st.session_state.project_id,
                            region=st.session_state.cloud_region # Use default region for discovery
                        )

#                        print(f"DEB endpoints_answer: {endpoints_answer}")
                        if endpoints_answer['status'] in ['success_api', 'success_cache']:
                            pass # All good
                        else:
                            raise Exception(f"Exception in get_cloud_run_endpoints(): status not ok: '{endpoints_answer['status']}'")
                        service_names = [ srv_dict['name'] for srv_dict in endpoints_answer['services'] ]
                        if service_names == []:
                            service_names = [ "😞 Empty! (Change project please)"]
                        endpoints_answer = sorted(service_names)
                        st.session_state.available_services = endpoints_answer
                        print(f"DEB service_names (sorted): {endpoints_answer}")

                        #st.session_state[f"services_{st.session_state.project_id}"] = current_services
                        st.session_state[f"services_{st.session_state.project_id}"] = sorted(service_names)
                    except Exception as e:
                        st.error(f"Failed to get services for {st.session_state.project_id}: {e}")
                        current_services = []


             # Get current index for the selectbox if a service is already selected
             try:
                 current_service_index = current_services.index(st.session_state.service_name)  if (st.session_state.service_name and st.session_state.service_name in current_services) else None
             except ValueError:
                 current_service_index = None # Service name in state not found in list

             st.selectbox(
                  f"Select Cloud Run Service ({st.session_state.cloud_region}):",
                  options=current_services,
                  index=current_service_index,
                  key="service_name", # Binds to session state
                  placeholder="Choose a service...",
                  on_change=service_select_callback # Call state function to change view mode
             )

        st.markdown("---")

        # --- Investigation Management ---
        st.header("📜 Investigations")

        # Button to create a new, generic investigation
        if st.button("➕ New Blank Investigation", use_container_width=True):
             state.create_new_investigation(activate=True) # Will switch view to chat

        # List existing investigations with delete buttons
        if st.session_state.investigations:
            # Sort investigations, e.g., by creation date descending
            sorted_investigations = sorted(
                st.session_state.investigations.items(),
                key=lambda item: item[1].get('created_at', '0'),
                reverse=True
            )

            active_inv_id = st.session_state.get("current_investigation_id")
            view_mode = st.session_state.get("view_mode")

            for inv_id, inv_data in sorted_investigations:
                inv_name = inv_data.get('name', 'Untitled Investigation')
                # Use columns for name button and delete button
                col1, col2 = st.columns([0.85, 0.15]) # Adjust ratio as needed

                with col1:
                     # Highlight if active chat, otherwise secondary
                     button_type = "primary" if view_mode == "chat" and inv_id == active_inv_id else "secondary"
                     if st.button(inv_name, key=f"inv_btn_{inv_id}", type=button_type, use_container_width=True):
                         state.switch_investigation(inv_id) # Switches view to chat

                with col2:
                     if st.button(DELETE_ICON, key=f"del_btn_{inv_id}", help=f"Delete '{inv_name}'", use_container_width=True):
                         # Confirmation could be added here using a modal or expander if desired
                         state.delete_investigation(inv_id)
                         # state.delete_investigation handles rerun

        else:
            st.caption("No investigations yet.")

# --- Synoptic View Rendering ---
def render_synoptic_view(project_id: str, service_name: str, region: str, cache_dir: Path):
    """Renders the informational view for a selected Cloud Run service."""

    st.markdown(f"**Project:**  | **Region:** ")

    with st.spinner(f"Loading details for ..."):
        # Use the existing helper, but we need the parsed dict now
        service_yaml_content, service_urls, monitor_charts = helpers.load_service_data_from_cache(
            cache_dir, project_id, service_name
        )

    if not service_yaml_content:
        st.error(f"Could not load  from cache for {service_name}. Cannot display details.")
        return # Stop rendering if core info is missing

    # Parse the YAML content
    service_dict = None
    try:
        service_dict = yaml.safe_load(service_yaml_content)
    except yaml.YAMLError as e:
        st.error(f"Error parsing service.yaml: {e}")
        st.text(service_yaml_content) # Show raw content on error

    # --- Display Key Information ---
    st.subheader("📊 Key Metrics & Config")
    col1, col2, col3 = st.columns(3)

    cpu_limit = "N/A"
    memory_limit = "N/A"
    base_image = "N/A"
    env_vars = []

    if service_dict: # Safely extract data if parsing succeeded
        try:
            # Safe navigation using .get() with defaults
            container = service_dict.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [{}])[0] # Get first container
            resources = container.get('resources', {})
            limits = resources.get('limits', {})
            cpu_limit = limits.get('cpu', 'N/A')
            memory_limit = limits.get('memory', 'N/A') # Corrected key from user request (was cpu)
            base_image = container.get('image', 'N/A') # Corrected key from user request (was baseImageUri)

            # Extract Env Vars
            raw_env_vars = container.get('env', [])
            env_vars = [{"Name": env.get('name'), "Value": env.get('value', env.get('valueFrom'))} # Handle value/valueFrom
                        for env in raw_env_vars if env.get('name')]

        except (AttributeError, IndexError, TypeError) as e:
            st.warning(f"Could not extract all details from service.yaml structure: {e}")

    with col1:
        st.metric(label="💻 CPU Limit", value=cpu_limit)
    with col2:
        st.metric(label="💾 Memory Limit", value=memory_limit) # Corrected label/icon
    with col3:
         if base_image != "N/A":
             st.metric(label="📦 Base Image", value=base_image.split('/')[-1].split(':')[0], help=base_image) # Show image name, full on hover
         else:
             st.metric(label="📦 Base Image", value="N/A")


    # --- Display URLs ---
    if service_urls:
        st.subheader("🔗 URLs")
        for url in service_urls:
            st.code(url, language=None)
    else:
        st.caption("No public URLs found in service status.") # Clarified source


    # --- Display Environment Variables ---
    if env_vars:
        st.subheader("🔑 Environment Variables")
        # Improve display compared to raw dict list
        st.dataframe(env_vars, use_container_width=True)
    else:
        st.caption("No environment variables found in container spec.")


    # --- Display Monitoring Charts ---
    if monitor_charts:
        st.subheader("📈 Monitoring Charts")
        # Use columns for better layout
        num_cols = min(len(monitor_charts), 3) # Max 3 cols
        cols = st.columns(num_cols)
        col_idx = 0
        for chart_path in monitor_charts:
            with cols[col_idx % num_cols]:
                try:
                    st.image(str(chart_path), caption=chart_path.name, use_column_width=True)
                except Exception as e:
                    st.error(f"Error loading {chart_path.name}: {e}")
            col_idx += 1
    else:
        st.caption("No monitoring charts found in cache.")

    st.markdown("---")

    # --- Investigation Buttons ---
    st.subheader("🚀 Investigations for this Service")

    # Button to start a NEW investigation specific to this service
    if st.button(f"➕ Start New Investigation for {service_name}", type="primary"):
        state.create_new_investigation(
            context_project=project_id,
            context_service=service_name,
            context_region=region, # Pass the region associated with this service
            activate=True # This will switch view to chat
        )

    # Find existing investigations related to this service
    related_investigations = []
    for inv_id, inv_data in st.session_state.investigations.items():
        # Check if context matches the currently selected service
        if (inv_data.get('project_id') == project_id and
            inv_data.get('service_name') == service_name and
            inv_data.get('region') == region):
             related_investigations.append((inv_id, inv_data))

    if related_investigations:
        st.markdown("**Continue existing investigation:**")
        # Sort related investigations maybe?
        related_investigations.sort(key=lambda item: item[1].get('created_at', '0'), reverse=True)
        for inv_id, inv_data in related_investigations:
            if st.button(f"▶️ Continue: {inv_data.get('name', 'Untitled')}", key=f"continue_{inv_id}"):
                state.switch_investigation(inv_id) # Switches view to chat
    else:
        st.caption("No previous investigations found specifically for this service.")


# --- Chat Interface Rendering ---
def render_chat_interface(db_file):
    """Renders the main chat area and handles user input."""
    # Title is now handled in app.py based on view mode

    current_id = st.session_state.get("current_investigation_id")
    if not current_id or current_id not in st.session_state.investigations:
        st.info("No active investigation selected.") # Should generally not be reached if logic in app.py is correct
        return

    investigation = st.session_state.investigations[current_id]

    # Display chat messages from history
    for message in investigation.get("history", []):
        role = message.get("role")
        avatar = USER_AVATAR if role == "user" else MODEL_AVATAR
        with st.chat_message(role, avatar=avatar):
            # Display text content (handle potential structures)
            content = message.get("content") # Expects dict like {"parts": [{"text": ...}]}
            full_text = ""
            if isinstance(content, dict) and "parts" in content:
                 full_text = "\n".join([part.get("text", "") for part in content.get("parts", []) if "text" in part])

            if full_text:
                st.markdown(full_text) # Render markdown

            # Display charts if available (check for key outside 'content')
            chart_filename = message.get("chart_filename")
            if chart_filename:
                chart_path = Path(chart_filename)
                if chart_path.is_file():
                    try:
                        st.image(str(chart_path), caption=f"📊 Chart: {chart_path.name}")
                    except Exception as e:
                        st.error(f"Failed to display chart {chart_path.name}: {e}")
                else:
                    st.warning(f"Chart file not found: {chart_filename}")

    # Chat input - Capture user prompt
    if prompt := st.chat_input(f"Ask Gemini about '{investigation.get('name', 'this investigation')}'..."):
        # 1. Add user message to state and display it immediately
        # Use the standardized message structure
        state.add_message_to_current_investigation(role="user", text=prompt) # Persists here
        # Rerun happens naturally after state update, or explicitly if needed

        # Display the user message that was just added to history
        with st.chat_message("user", avatar=USER_AVATAR):
             st.markdown(prompt)

        # 2. Prepare history for Gemini (check what your function expects)
        # Send the full history up to the user's latest message
        gemini_history = investigation["history"]

        # 3. Call Gemini (handle streaming and function calling)
        try:
            with st.chat_message("assistant", avatar=MODEL_AVATAR):
                message_placeholder = st.empty()
                full_response_text = ""
                final_chart_filename = None

                # --- Streaming Call ---
                # Replace with your actual function call using the prepared history
                response_stream = generate_content_with_function_calling(
                    model_name=st.session_state.gemini_model,
                    # Pass the full prompt or just the latest message? Depends on your function
                    prompt=prompt, # Or maybe construct a prompt object if needed
                    history=gemini_history, # Pass the conversation history
                    # Pass tools definition for function calling here!
                    # tools=YOUR_FUNCTION_DEFINITIONS
                )

                # Process the stream from Gemini
                stream_content_parts = []
                for chunk in response_stream:
                     # Assuming chunk is an object with text or function call parts
                     # This part depends heavily on your Gemini library's streaming response format!
                     # Example: adapt based on actual chunk structure
                     if hasattr(chunk, 'text'):
                          text_chunk = chunk.text
                          full_response_text += text_chunk
                          message_placeholder.markdown(full_response_text + "▌") # Simulate cursor
                          stream_content_parts.append({"text": text_chunk})
                     elif hasattr(chunk, 'function_call'):
                          # Handle function call received mid-stream or at the end
                          # TODO: Implement function call execution logic here
                          st.warning(f"Function call received: {chunk.function_call}")
                          # result = execute_my_tool(chunk.function_call)
                          # Need to send result back to model... complex flow.
                          pass
                     # Check for chart filename if returned specially
                     if hasattr(chunk, 'chart_filename'): # Or however your function returns it
                          final_chart_filename = chunk.chart_filename


                message_placeholder.markdown(full_response_text) # Final text

                # TODO: If function calling requires a second turn, handle it here.
                # This usually involves sending the function result back to the model.

                # Display chart if generated during the response processing
                if final_chart_filename:
                    chart_path = Path(final_chart_filename)
                    if chart_path.is_file():
                         try:
                              st.image(str(chart_path), caption=f"📊 Generated Chart: {chart_path.name}")
                         except Exception as e:
                              st.error(f"Failed display generated chart {chart_path.name}: {e}")
                    else:
                         st.warning(f"Generated chart file not found: {final_chart_filename}")


            # 4. Add final assistant response (potentially just text if chart displayed above)
            # Use the collected stream parts for accurate history
            state.add_message_to_current_investigation(
                 role="assistant",
                 parts=stream_content_parts, # Save the structured parts
                 chart_filename=final_chart_filename # Store chart path with message
            )
            # Rerun not strictly needed here, but might help refresh state cleanly. Consider if issues arise.
            # st.rerun()

        except Exception as e:
            st.error(f"🤖 Oops! Error calling Gemini: {e}")
            # Optionally add error message to chat history
            state.add_message_to_current_investigation(role="assistant", text=f"Error during generation: {e}")
            st.rerun() # Rerun after error to show the error message in chat history

