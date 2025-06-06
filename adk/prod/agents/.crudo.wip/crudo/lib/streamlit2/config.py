import os
from dotenv import load_dotenv
from typing import List

# Load .env file if it exists (useful for local development)
load_dotenv()

# --- Environment Variable Loading ---

DEFAULT_USER_ID = "ricc@google.com"
#DEFAULT_REGION = "europe-west1"
DEFAULT_REGION = "us-central1"
#DEFAULT_MODEL = "gemini-1.5-flash" # Using latest alias
AVAILABLE_MODELS: List[str] = ["gemini-2.0-flash-001", "gemini-1.5-flash", ]
DEFAULT_MODEL = AVAILABLE_MODELS[0] # first by default

# 👤 User ID Configuration
def get_user_id() -> str:
    """Gets user ID from environment or defaults."""
    user = os.getenv("USER", None)
    email_domain = "@google.com" # Assuming google.com domain
    if user:
        return f"{user}{email_domain}"
    # Fallback if USER env var is not set
    try:
        # Attempt to get login name, handle potential errors
        login_name = os.getlogin()
        return f"{login_name}{email_domain}"
    except OSError:
        # If getlogin fails (e.g., in certain environments), use the hardcoded default
        return DEFAULT_USER_ID

# ♊ Gemini Model Configuration
def get_gemini_model() -> str:
    """Gets Gemini model from environment or defaults."""
    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    if model not in AVAILABLE_MODELS:
        print(f"⚠️ Warning: Env Var GEMINI_MODEL ('{model}') is not in AVAILABLE_MODELS. Using default: {DEFAULT_MODEL}")
        return DEFAULT_MODEL
    return model

# 🌍 Cloud Region Configuration
def get_GOOGLE_CLOUD_LOCATION() -> str:
    """Gets Google Cloud region from environment or defaults."""
    return os.getenv("GOOGLE_CLOUD_LOCATION", DEFAULT_REGION)

# Ricc - get project id
def get_project_id() -> str:
    """Gets Google Cloud Project from environment or defaults."""
    return os.getenv("GOOGLE_CLOUD_PROJECT", '')

# 🔑 API Key Configuration
def get_google_api_key() -> str | None:
    """Gets Google API Key from environment. No default."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️ Warning: GOOGLE_API_KEY environment variable not set.")
    return api_key

# --- Application Configuration ---
# You could also define a dataclass here to hold these values
USER_ID: str = get_user_id()
GEMINI_MODEL: str = get_gemini_model()
GOOGLE_CLOUD_LOCATION: str = get_GOOGLE_CLOUD_LOCATION()
GOOGLE_API_KEY: str | None = get_google_api_key()
AVAILABLE_MODELS_LIST: List[str] = AVAILABLE_MODELS
#GOOGLE_CLOUD_PROJECTUD_PROJECT: str | None = get_project_id()
GOOGLE_CLOUD_PROJECT: str | None = get_project_id()
#STREAMLIT_UI_VER: str = "1.0a_9apr25"
STREAMLIT_UI_VER: str = "1.0a"

# --- Database ---
DB_FILE = "convos.sqlite3"

# --- Cache Dirs ---
# Define base cache dir relative to app root for consistency
CACHE_BASE_DIR = ".cache"

