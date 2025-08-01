# app/core/app_config.py
import os
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file for local development.
# This should be the very first executable line after imports.
load_dotenv()

# --- Directory Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
LOG_DIR = os.path.join(PROJECT_ROOT, "agent_logs")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
POLICY_DIR = os.path.join(PROJECT_ROOT, "policies")

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(POLICY_DIR, exist_ok=True)

# --- Model Files ---
FRAUD_MODEL_PATH = os.path.join(MODEL_DIR, "fraud_model.pkl")

# --- Policy Files ---
DEFAULT_POLICY_DOC = os.path.join(POLICY_DIR, "fraud_rules.txt")

# --- Logging ---
LOG_FILE_EXTENSION = ".jsonl"

# --- Suggested Confidence Thresholds (from your rules) ---
CONFIDENCE_THRESHOLD = 0.85 # Transactions > 0.85 are "Approve" (Safe) or "Fraud"
FALLBACK_THRESHOLD = 0.60  # Transactions 0.60 - 0.85 are "Manual Review" (Escalate)

# --- Rule-based Data ---
VIRTUAL_CARD_LIMIT = 3000.0 # Example value for virtual card limit (for F2.1)
HIGH_VALUE_TRANSACTION_THRESHOLD = 5000.0 # For E1.1: Amount > $5000
EXTREMELY_HIGH_VALUE_DEBIT_THRESHOLD = 100000.0 # New: For extremely high value debit transactions
RISKY_MERCHANTS = {"fraud_kirlin", "shady_importsng", "unverified_gadgetx"} # For F1.1

# --- LLM API Configuration (for Groq) ---
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# IMPORTANT: Read API key from environment variable for security
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY environment variable not set. Narrative generation may fail.")
GROQ_MODEL_NAME = "llama3-8b-8192"

# --- Backend API URL Configuration ---
# This is crucial for your Streamlit frontend to connect to the FastAPI backend.
# It defaults to localhost for local development, but will be overridden by
# the environment variable set in Render/Streamlit Cloud for deployment.
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
