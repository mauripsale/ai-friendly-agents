import streamlit as st
from .state import (
    update_config, set_selected_project, set_selected_service,
    set_current_investigation, add_chat_message
)
from .gcp_helpers import (
    fetch_projects, fetch_services, fetch_service_details, fetch_monitoring_charts
)
from .db import (
    create_investigation, get_investigations_for_service, load_messages, save_message
)
from lib.ricc_genai import GeminiChatSession # Assuming this exists
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from .config import STREAMLIT_UI_VER

logger = logging.getLogger(__name__)


# Add on from prompt 2


# --- Cached Resource for Chat Session ---
# Use cache_resource to keep the chat object alive per investigation
# The key arguments (investigation_id, project, etc.) determine uniqueness
@st.cache_resource(ttl=3600) # Cache for 1 hour, adjust as needed
def get_chat_session(
    _investigation_id: int, # Underscore prevents hashing the mutable object if passed directly
    project_id: str,
    region: str,
    api_key: str,
    model: str,
    cloud_run_service: str | None # Add cloud_run_service here
    ) -> GeminiChatSession:
    """
    Gets or creates a cached GeminiChatSession for a specific investigation.
    The actual history is managed internally by the Gemini library's chat object.
    """
    logger.info(f"Cache miss or creating new chat session for Investigation ID: {_investigation_id}")
    # Pass cloud_run_service to the constructor
    return GeminiChatSession(
        project_id=project_id,
        region=region,
        api_key=api_key, # Ensure your class uses this if needed, or relies on global config
        model=model,
        cloud_run_service=cloud_run_service, # Pass it here
        verbose=True, # Or get from config/state
        debug=True    # Or get from config/state
    )


# --- UI Building Blocks ---

def display_configuration_editor():
    """Displays the configuration section in the sidebar."""
    with st.sidebar.expander("⚙️ Configuration", expanded=False):
        st.caption("Current Settings:")
        st.write(f"👤 User: `{st.session_state.user_id}`")
        st.write(f"♊ Model: `{st.session_state.gemini_model}`")
        #st.write(f"🌍 ProjectId: `{st.session_state.project_id}`") # better not to
        st.write(f"🌍 Region: `{st.session_state.cloud_region}`")
        st.write(f"🔑 API Key Set: `{'Yes' if st.session_state.api_key else 'No 🚨'}`")

        st.divider()
        st.caption("Edit Settings:")

        # Use a form for editing to update all at once
        with st.form("config_form"):
            new_user_id = st.text_input("User Email", value=st.session_state.user_id)
            new_model = st.selectbox(
                "Gemini Model",
                options=st.session_state.available_models,
                index=st.session_state.available_models.index(st.session_state.gemini_model)
                     if st.session_state.gemini_model in st.session_state.available_models else 0
            )
            new_region = st.text_input("Cloud Region", value=st.session_state.cloud_region)
            # API key editing is generally discouraged in UI for security
            # Consider instructing users to set the ENV VAR instead.
            # new_api_key = st.text_input("API Key (optional)", value=st.session_state.api_key or "", type="password")

            submitted = st.form_submit_button("💾 Save Configuration")
            if submitted:
                if not new_user_id or not new_region:
                     st.warning("User ID and Region cannot be empty.")
                else:
                    update_config(new_user_id, new_model, new_region)
                    st.success("Configuration updated!")
                    st.rerun() # Rerun to reflect changes immediately


def display_investigation_list():
    """Displays the list of investigations in the sidebar."""
    with st.sidebar.expander("📜 Investigations", expanded=True):
        if not st.session_state.selected_project_id or not st.session_state.selected_service_id:
            st.caption("Select a Project and Service first.")
            return

        st.caption(f"For: `{st.session_state.selected_project_id} / {st.session_state.selected_service_id}`")

        # Fetch investigation titles if not already loaded for this service
        # This avoids redundant DB queries on every rerun unless the service changes
        # Note: If titles can change, this caching needs invalidation logic
        if not st.session_state.investigation_titles:
            investigations_data = get_investigations_for_service(
                st.session_state.selected_project_id,
                st.session_state.selected_service_id,
                st.session_state.cloud_region
            )
            # Store titles keyed by ID
            st.session_state.investigation_titles = {inv['id']: inv['title'] for inv in investigations_data}

        if not st.session_state.investigation_titles:
            st.caption("No investigations yet for this service.")
            return

        # Display investigations, highlight the active one
        for inv_id, inv_title in st.session_state.investigation_titles.items():
            button_type = "primary" if inv_id == st.session_state.current_investigation_id else "secondary"
            if st.button(f"📄 {inv_title or f'Investigation {inv_id}'}", key=f"inv_btn_{inv_id}", use_container_width=True, type=button_type):
                if st.session_state.current_investigation_id != inv_id:
                    set_current_investigation(inv_id)
                    # Force rerun ONLY if selection changed to load messages and switch view
                    st.rerun()
                # If already selected, clicking again does nothing here.


def build_sidebar():
    """Builds the sidebar UI elements."""
    st.sidebar.title(f"Cloud Run Investigator v{STREAMLIT_UI_VER} 🕵️‍♀️")
    st.sidebar.divider()

    display_configuration_editor()
    st.sidebar.divider()
    display_investigation_list()


def display_project_service_selector():
    """Displays dropdowns for selecting project and service."""
    st.subheader("🎯 Select Project and Service", help='Choose Project, and then a Service within it')

    # --- Project Selector ---
    # Fetch projects only if the list is empty or user changed
    # (Simple check - could be more robust based on user/config changes)
    if not st.session_state.projects_list:
        st.session_state.projects_list = fetch_projects(st.session_state.user_id)

    # Prepare options, adding a placeholder if needed
#    project_options = ["<Select a Project>"] + st.session_state.projects_list
    project_options = st.session_state.projects_list
    current_project_index = 0
    if st.session_state.selected_project_id and st.session_state.selected_project_id in st.session_state.projects_list:
        current_project_index = project_options.index(st.session_state.selected_project_id)

    selected_project = st.selectbox(
        "Google Cloud Project",
        options=project_options,
        index=current_project_index,
        key="project_selector",
        # on_change=lambda: set_selected_project(st.session_state.project_selector if st.session_state.project_selector != "<Select a Project>" else None)
    )
    # Handle selection change manually to reset dependencies
    if selected_project != "<Select a Project>" and selected_project != st.session_state.selected_project_id:
         set_selected_project(selected_project)
         st.rerun() # Rerun to fetch services for the new project
    elif selected_project == "<Select a Project>" and st.session_state.selected_project_id is not None:
         set_selected_project(None)
         st.rerun() # Rerun to clear service selector


    # --- Service Selector (dependent on Project) ---
    if st.session_state.selected_project_id:
        # Fetch services only if project is selected and list is empty or project changed
        # This logic is implicitly handled by set_selected_project resetting services_list
        if not st.session_state.services_list:
             st.session_state.services_list = fetch_services(
                 st.session_state.selected_project_id,
                 st.session_state.cloud_region
             )

#        service_options = ["<Select a Service>"] + st.session_state.services_list
        service_options = st.session_state.services_list
        current_service_index = 0
        if st.session_state.selected_service_id and st.session_state.selected_service_id in st.session_state.services_list:
            current_service_index = service_options.index(st.session_state.selected_service_id)

        selected_service = st.selectbox(
            f"Cloud Run Service (in {st.session_state.cloud_region})",
            options=service_options,
            index=current_service_index,
            key="service_selector",
            # on_change=lambda: set_selected_service(st.session_state.service_selector if st.session_state.service_selector != "<Select a Service>" else None)
        )
        # Handle selection change manually
        if selected_service != "<Select a Service>" and selected_service != st.session_state.selected_service_id:
            set_selected_service(selected_service)
            st.rerun() # Rerun to fetch details for the new service
        elif selected_service == "<Select a Service>" and st.session_state.selected_service_id is not None:
            set_selected_service(None)
            st.rerun() # Rerun to clear details view

    else:
        st.caption("Select a project to see available Cloud Run services.")


def display_synoptic_view():
    """Displays the detailed synoptic view for the selected service."""
    project = st.session_state.selected_project_id
    service = st.session_state.selected_service_id
    region = st.session_state.cloud_region

    st.header(f"🔎 Synoptic View: '{service}'")
    st.caption(f"Project: `{project}` | Region: `{region}`")


    # Fetch details if not already loaded for this service
    if st.session_state.current_service_details is None:
        st.session_state.current_service_details = fetch_service_details(project, service, region)

    service_details = st.session_state.current_service_details

    if not service_details:
        st.warning("Could not load service details. Cannot display synoptic view.", icon="⚠️")
        # Maybe add a button to retry fetching?
    else:
        st.caption(f"LastModified: `{service_details['updateTime']}` by: `{service_details['lastModifier']}`")
        st.caption(f"Created: `{service_details['createTime']}` by `{service_details['creator']}`")
        st.subheader("Configuration Summary")
        try:
            # Safely extract data using .get() with defaults
            container = service_details.get('template', {}).get('containers', [{}])[0]
            limits = container.get('resources', {}).get('limits', {})
            cpu_limit = limits.get('cpu', 'N/A')
            memory_limit = limits.get('memory', 'N/A')
            env_vars = container.get('env', [])
            image_uri = container.get('image', 'N/A') # Corrected key based on gcloud output 'image'
            #service_urls = service_details.get('status', {}).get('url', 'N/A') # Primary URL
            service_urls = service_details.get('urls', ['N/A']) # Primary URL
            scaling_max = service_details.get('template', {}).get('scaling', {}).get('maxInstanceCount', {})
            labels = service_details.get('labels', {})
            create_time = service_details.get('createTime', {})
            update_time = service_details.get('updateTime', {})
            #st.caption(f"Created at: `{service_details['creator']}` | LastModifier: `{service_details['lastModifier']}`")


            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="CPU Limit ⚙️", value=cpu_limit)
            with col2:
                st.metric(label="Memory Limit 💾", value=memory_limit)
            with col3:
                st.metric(label="Max Instances 🖥️", value=scaling_max)
            for service_url in service_urls:
                st.link_button(f"🔗 {service_url}", service_url)


            linked_image = f"[{image_uri}]({image_uri})"
            st.write(f"**Base Image:** {linked_image}")
            # link_to

            with st.expander("Environment Variables"):
                if env_vars:
                    # Filter out variables with valueFrom (like secrets) for cleaner display
                    display_vars = {var['name']: var.get('value', '******') for var in env_vars if 'value' in var}
                    if display_vars:
                         st.dataframe(display_vars)
                    else:
                         st.caption("No simple key-value environment variables defined.")
                else:
                    st.caption("No environment variables defined.")

            #st.area_chart(labels)
            #label_columns =  st.columns(len(labels))
            # for col_i in label_columns:
            #     with col_i:
            #         st.metric(label=f"🖥️ Label {}", value=scaling_max)
            label_blurb = []
            for key in labels:
                val = labels[key]
                #st.metric(label=f"🖥️ Label {key}", value=val)
                #st.caption(f"{key}: `{project}` | Region: `{region}`")
                #st.caption(f"{key}: `{val}` | ")
                label_blurb += [f"🏷️ {key}: `{val}` "]
            st.caption(" | ".join(label_blurb))



        except Exception as e:
            st.error(f"🚨 Error parsing service details: {e}")
            logger.error(f"Error parsing service details dict for {service}: {e}", exc_info=True)

    #st.subheader("Ricc Debug: service_details [deleteme]")
    #st.dataframe(service_details)

    # --- Monitoring Charts ---
    st.subheader("📊 Monitoring Charts")
    # Fetch chart paths if not already loaded
    if not st.session_state.current_monitoring_charts:
        st.session_state.current_monitoring_charts = fetch_monitoring_charts(project, service)

    chart_paths = st.session_state.current_monitoring_charts

    if not chart_paths:
        st.caption("No monitoring charts found in the cache.")
    else:
        # Display charts, potentially in columns
        num_cols = 3 # Adjust as needed
        cols = st.columns(num_cols)
        for i, chart_path in enumerate(chart_paths):
            try:
                with cols[i % num_cols]:
                    st.image(str(chart_path), caption=chart_path.name, use_column_width=True)
            except Exception as e:
                 st.warning(f"Could not load chart: {chart_path.name} ({e})")
                 logger.warning(f"Failed to load image {chart_path}: {e}", exc_info=True)


    st.divider()

    # --- Investigation Buttons ---
    st.subheader("Investigations")

    # Button to start a new investigation
    if st.button("➕ Start New Investigation", type="primary"):
        try:
            new_inv_id = create_investigation(project, service, region)
            set_current_investigation(new_inv_id)
             # Add new investigation to the sidebar list immediately
            st.session_state.investigation_titles[new_inv_id] = f"Investigation {new_inv_id}"
            st.rerun() # Switch to chat view
        except Exception as e:
            st.error(f"🚨 Failed to create new investigation: {e}")
            logger.error(f"Failed to create investigation via button: {e}", exc_info=True)

    # Buttons for existing investigations (fetched in sidebar logic, use titles from state)
    if st.session_state.investigation_titles:
        st.write("Continue existing investigation:")
        cols = st.columns(3) # Adjust layout as needed
        i = 0
        for inv_id, inv_title in st.session_state.investigation_titles.items():
             # Skip the currently active one if already in chat view (though we aren't here)
            # if inv_id == st.session_state.current_investigation_id: continue

            # Place button in columns
            with cols[i % len(cols)]:
                if st.button(f"▶️ {inv_title or f'Investigation {inv_id}'}", key=f"cont_inv_{inv_id}", use_container_width=True):
                    set_current_investigation(inv_id)
                    st.rerun() # Switch to chat view
            i += 1




def display_chat_interface(debug=False):
    """Displays the chat interface for the current investigation."""
    investigation_id = st.session_state.current_investigation_id
    project = st.session_state.selected_project_id
    service = st.session_state.selected_service_id # Get selected service
    region = st.session_state.cloud_region
    model = st.session_state.gemini_model
    api_key = st.session_state.api_key

    if not investigation_id:
        st.error("No investigation selected.")
        return
    if not project or not service or not region or not model or not api_key:
        st.error("Missing required configuration (Project, Service, Region, Model, API Key) to start chat.", icon="🚨")
        return


    # Try to get title from sidebar cache, fallback to ID
    title = st.session_state.investigation_titles.get(investigation_id, f"Investigation {investigation_id}")
    st.header(f"💬 Investigation: {title}")
    st.caption(f"Service: `{project} / {service}` | Model: `{model}`")

    # --- Load messages from DB for display ---
    # We still load from DB to display the history reliably on first load or if cache expires
    if not st.session_state.current_chat_messages:
        logger.debug(f"Loading messages from DB for Invest ID: {investigation_id}")
        st.session_state.current_chat_messages = load_messages(investigation_id)
        # If the DB has messages, but the cached session is new, its internal history might be empty.
        # The Gemini library *should* handle this if we re-instantiate, but caching aims to avoid that.

    # Display chat messages from history stored in session state (which mirrors DB)
    for msg in st.session_state.current_chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("chart"):
                try:
                    chart_path = Path(msg["chart"])
                    if chart_path.is_file():
                        st.image(str(chart_path), caption="Generated Chart")
                    else:
                        st.caption(f"[Chart not found: {msg['chart']}]")
                        logger.warning(f"Chart file not found during display: {chart_path}")
                except Exception as e:
                    st.caption(f"[Error loading chart: {e}]")
                    logger.warning(f"Error loading chart image {msg['chart']}: {e}", exc_info=True)

    chat_message_pseudo_history = st.session_state.current_chat_messages # [-1]["content"]
    st.caption(f"📜 History size: **{len(chat_message_pseudo_history)}**")
    if debug:
        st.caption(chat_message_pseudo_history)
    if len(chat_message_pseudo_history) == 0:
        # st.caption("TODO(ricc): since this is size=0, let me inject a message with knowledge of PrId, region and Service. ")
        # st.caption(f"project: {project}")
        # st.caption(f"service: {service}")
        # st.caption(f"region: {region}")
        # st.caption(f"model: {model}")
        # st.caption(f"investigation_id: {investigation_id}")
        # Also api_key but its secret
        # TODO - move to file.
        prompt = f"""[Note for LLM: AutoGenerated by Streamlit App2] Let me set the context for you:
* project id: **{project}**
* service: **{service}**
* region: {region}
* revision: use LATEST

Now tell the user what can you do - enumerate your Tool Calling capabilities. Also, do you see anything fishy?
"""
        # * investigation_id: {investigation_id}
        st.caption(f"prompt: ```markdown\n{prompt}\n```")

        logger.info(f"[Invest. {investigation_id}] User: {prompt}")
        save_message(investigation_id, "user", prompt)
        add_chat_message("user", prompt) # Add to session state for immediate display
        # Rerun needed here to show the user message immediately before waiting for Gemini
        st.rerun()



    # --- Chat Input ---
    if prompt := st.chat_input("Ask Gemini about this service..."):
        # 1. Save and display user message immediately
        logger.info(f"[Invest. {investigation_id}] User: {prompt}")
        save_message(investigation_id, "user", prompt)
        add_chat_message("user", prompt) # Add to session state for immediate display
        # Rerun needed here to show the user message immediately before waiting for Gemini
        st.rerun()


    # --- Process Gemini Response (Only if there's a last user prompt) ---
    # Check if the last message added was from the user, implying we need Gemini's reply
    # This logic runs *after* the potential st.rerun() above
    last_message_role = st.session_state.current_chat_messages[-1]["role"] if st.session_state.current_chat_messages else None

    if last_message_role == "user":
        # Ensure API key is available
        if not api_key:
            st.error("🚨 GOOGLE_API_KEY is not configured. Cannot contact Gemini.")
            st.stop()

        # 2. Prepare for and call Gemini using the cached session
        try:
            # Get the cached chat session instance for this specific investigation
            # Pass the selected service name here
            chat_session = get_chat_session(
                investigation_id, project, region, api_key, model, service
            )

            # The prompt is the content of the last message in our state list
            user_prompt = st.session_state.current_chat_messages[-1]["content"]

            # Display thinking indicator
            with st.chat_message("assistant"):
                with st.spinner("🤔 Gemini is thinking..."):
                    # --- Call Gemini using the cached session object ---
                    # send_simple_message uses the internal history of the cached chat_session.chat object
                    response = chat_session.send_simple_message(user_prompt)

                    # --- Process Gemini Response ---
                    # TODO: Adapt this based on how your send_simple_message/function calling returns data
                    # Assuming response object has .text and potentially .function_calls or similar
                    assistant_text = getattr(response, 'text', "Sorry, I couldn't process that.")
                    chart_info = None # Placeholder - Extract chart info if function calling worked

                    # --- Placeholder for Function Call Handling ---
                    # if response.function_calls:
                    #    fc = response.function_calls[0]
                    #    logger.info(f"Function call requested: {fc.name}({fc.args})")
                    #    # --> Add logic here to execute the function based on fc.name
                    #    # --> Get the result
                    #    # --> Send result back using chat_session.send_function_response(...)
                    #    # --> Get the *final* text response from Gemini after function execution
                    #    # --> Potentially update assistant_text and chart_info here
                    #    pass # Replace with actual function call handling

                    logger.info(f"[Invest. {investigation_id}] Assistant: {assistant_text[:100]}...")
                    if chart_info:
                        logger.info(f"[Invest. {investigation_id}] Assistant generated chart: {chart_info}")


            # 3. Save and display assistant message(s)
            save_message(investigation_id, "assistant", assistant_text, chart_filename=chart_info)
            add_chat_message("assistant", assistant_text, chart_path=chart_info)

            # 4. Rerun to display the new assistant message
            # Important: Clear memo/cache if necessary? Maybe not needed if Streamlit handles resource mutation. Test first.
            # get_chat_session.clear() # This clears the *entire* cache, not ideal.
            # If history isn't persisting correctly, we might need a more complex cache invalidation strategy.
            st.rerun()

        except Exception as e:
            error_msg = f"🚨 An error occurred while interacting with Gemini: {e}"
            st.error(error_msg)
            logger.error(f"Gemini interaction failed for Invest {investigation_id}: {e}", exc_info=True)



def display_chat_interface_REMOVEME():
    """Displays the chat interface for the current investigation."""
    investigation_id = st.session_state.current_investigation_id
    project = st.session_state.selected_project_id
    service = st.session_state.selected_service_id
    region = st.session_state.cloud_region
    model = st.session_state.gemini_model
    api_key = st.session_state.api_key

    if not investigation_id:
        st.error("No investigation selected.")
        return

    # Try to get title from sidebar cache, fallback to ID
    title = st.session_state.investigation_titles.get(investigation_id, f"Investigation {investigation_id}")
    st.header(f"💬 Investigation: {title}")
    st.caption(f"Service: `{project} / {service}` | Model: `{model}`")

    # Load messages if not already loaded or if investigation changed
    if not st.session_state.current_chat_messages:
        st.session_state.current_chat_messages = load_messages(investigation_id)

    # Display chat messages from history
    for msg in st.session_state.current_chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("chart"):
                try:
                    # Ensure chart path is valid before displaying
                    chart_path = Path(msg["chart"])
                    if chart_path.is_file():
                        st.image(str(chart_path), caption="Generated Chart")
                    else:
                        st.caption(f"[Chart not found: {msg['chart']}]")
                        logger.warning(f"Chart file not found during display: {chart_path}")
                except Exception as e:
                    st.caption(f"[Error loading chart: {e}]")
                    logger.warning(f"Error loading chart image {msg['chart']}: {e}", exc_info=True)


    # --- Chat Input ---
    if prompt := st.chat_input("Ask Gemini about this service..."):
        # 1. Save and display user message immediately
        logger.info(f"[Invest. {investigation_id}] User: {prompt}")
        save_message(investigation_id, "user", prompt)
        add_chat_message("user", prompt) # Add to session state for immediate display

        # Ensure API key is available
        if not api_key:
            st.error("🚨 GOOGLE_API_KEY is not configured. Cannot contact Gemini.")
            st.stop()

        # 2. Prepare for and call Gemini
        try:
            # Instantiate Gemini Chat Session (consider caching/reusing?)
            # This might need adjustment based on your GeminiChatSession implementation
            # especially regarding how history is passed and function calling is handled.
            chat_session = GeminiChatSession(
                project_id=project,
                region=region,
                api_key=api_key, # Assuming the class handles the key internally if needed
                model=model, # Ensure correct parameter name
                cloud_run_service='onramp', # TODO find where it is
                # Pass previous messages if required by your class
                # history=st.session_state.current_chat_messages # Adjust format as needed
                verbose=True,
                debug=True, # Or link to a debug flag
            )
            # retrieve historty, if empty inject an initial message
            history = chat_session.get_chat_history_array()
            # chat_session.send_simple_message(f"Please find the configuration for my project ('{project_id}') and region ('{region}')")

            # Display thinking indicator
            with st.chat_message("assistant"):
                with st.spinner("🤔 Gemini is thinking..."):
                    # --- This is the core Gemini interaction ---
                    # Replace with your actual function call method
                    # This needs to handle potential function calls and streaming.

                    # Example: Simple text generation (replace with your actual call)
                    # response_stream = chat_session.send_simple_message_stream(prompt)
                    # full_response = st.write_stream(response_stream)

                    # Example: Function calling (conceptual)
                    # Assume send_message returns text and potentially structured data
                    # for function calls/charts. You'll need to adapt this precisely.
#                    response_data = chat_session.send_message_with_function_calling(
                    response_data = chat_session.send_simple_message(
                        prompt=prompt,
                        # Potentially pass available tools/functions here
                    )
                    #
                    # chat_history_so_far = chat.get_chat_history_array()
                    # print(f"[DEB] ChatHistory: {chat_history_so_far}" )

                    # print("[DEB] Gemini responded: '''{response_data}'''")

                    # --- Process Gemini Response ---
                    assistant_text = response_data.text # response_data.get("text", "Sorry, I couldn't process that.")
                    if response_data.function_calls:
                        print("FUN_CALL is TRUE v2. 1. TODO ricc manage charts.")
                        print(response_data.function_calls)
                        assistant_text += " [FunCall Check Logs]"
                    try:
                        # TODO fix this
                        chart_info = response_data.get("chart_filename") # Assuming this structure
                        print(f"chart info found!!! chart_info = {chart_info} TODO lets visualize it")
                    except:
                        print("no chart info found")
                        chart_info = None

                    logger.info(f"[Invest. {investigation_id}] Assistant: {assistant_text[:100]}...")
                    if chart_info:
                        logger.info(f"[Invest. {investigation_id}] Assistant generated chart: {chart_info}")


            # 3. Save and display assistant message(s)
            save_message(investigation_id, "assistant", assistant_text, chart_filename=chart_info)
            add_chat_message("assistant", assistant_text, chart_path=chart_info)

            # 4. Rerun to display the new messages from session state
            st.rerun()

        except Exception as e:
            error_msg = f"🚨 An error occurred while interacting with Gemini: {e}"
            st.error(error_msg)
            logger.error(f"Gemini interaction failed for Invest {investigation_id}: {e}", exc_info=True)
            # Optionally save an error message to the chat history?
            # save_message(investigation_id, "assistant", f"Error: {e}")
            # add_chat_message("assistant", f"Error: {e}")
            # st.rerun()


def build_main_area():
    """Builds the main content area based on the current state."""

    # 1. Always display selectors at the top
    display_project_service_selector()
    st.divider()

    # 2. Conditional display: Synoptic View or Chat Interface
    if st.session_state.current_investigation_id and st.session_state.show_chat_interface:
        # If an investigation is selected, show the chat
        display_chat_interface()
    elif st.session_state.selected_project_id and st.session_state.selected_service_id:
        # If project/service selected but no active chat, show synoptic view
        display_synoptic_view()
    else:
        # Initial state or after deselecting project/service
        st.info("👋 Select a Google Cloud Project and Cloud Run Service to begin.", icon="☁️")


def build_ui():
    """Constructs the entire Streamlit UI."""
    build_sidebar()
    build_main_area()

