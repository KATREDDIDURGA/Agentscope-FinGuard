import streamlit as st
import requests
import json
import uuid

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"

# --- Session State Initialization ---
if 'amount' not in st.session_state:
    st.session_state.amount = 0.0
if 'card_type' not in st.session_state:
    st.session_state.card_type = ""
if 'merchant' not in st.session_state:
    st.session_state.merchant = ""
if 'merchant_location' not in st.session_state:
    st.session_state.merchant_location = ""
if 'user_location' not in st.session_state:
    st.session_state.user_location = ""
if 'transaction_id' not in st.session_state:
    st.session_state.transaction_id = ""

if 'status' not in st.session_state:
    st.session_state.status = ""
if 'confidence' not in st.session_state:
    st.session_state.confidence = 0.0
if 'narrative' not in st.session_state:
    st.session_state.narrative = ""
if 'trace_summary_data' not in st.session_state:
    st.session_state.trace_summary_data = {}
if 'trace_verbose_data' not in st.session_state:
    st.session_state.trace_verbose_data = []
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""
if 'trace_mode' not in st.session_state:
    st.session_state.trace_mode = "summary"

# --- Helper Functions ---

def generate_new_transaction_id():
    st.session_state.transaction_id = str(uuid.uuid4())
    reset_results()

def reset_results():
    st.session_state.status = ""
    st.session_state.confidence = 0.0
    st.session_state.narrative = ""
    st.session_state.trace_summary_data = {}
    st.session_state.trace_verbose_data = []
    st.session_state.error_message = ""

def fetch_trace():
    if not st.session_state.transaction_id:
        st.session_state.error_message = "No transaction ID available to fetch trace."
        return

    try:
        if st.session_state.trace_mode == "summary":
            response = requests.get(f"{API_BASE_URL}/trace/summary/{st.session_state.transaction_id}")
            response.raise_for_status()
            st.session_state.trace_summary_data = response.json()
            st.session_state.trace_verbose_data = []
        else:
            response = requests.get(f"{API_BASE_URL}/trace/verbose/{st.session_state.transaction_id}")
            response.raise_for_status()
            data = response.json()
            
            # FIXED: Properly handle the trace data structure
            if isinstance(data, dict) and 'steps' in data:
                st.session_state.trace_verbose_data = data['steps']
            elif isinstance(data, list):
                st.session_state.trace_verbose_data = data
            else:
                st.session_state.trace_verbose_data = []
                st.session_state.error_message = f"Unexpected trace data format: {type(data)}"
            
            st.session_state.trace_summary_data = {}

    except requests.exceptions.ConnectionError:
        st.session_state.error_message = f"Cannot connect to backend at {API_BASE_URL}. Make sure FastAPI server is running."
    except requests.exceptions.RequestException as e:
        st.session_state.error_message = f"API request failed: {e}"
    except json.JSONDecodeError as e:
        st.session_state.error_message = f"Invalid JSON response: {e}"
    except Exception as e:
        st.session_state.error_message = f"Unexpected error during trace fetch: {e}"

def submit_transaction():
    reset_results()

    if not st.session_state.transaction_id:
        generate_new_transaction_id()

    txn_payload = {
        "transaction_id": st.session_state.transaction_id,
        "amount": st.session_state.amount,
        "card_type": st.session_state.card_type,
        "merchant": st.session_state.merchant,
        "merchant_location": st.session_state.merchant_location,
        "user_location": st.session_state.user_location
    }

    try:
        response = requests.post(f"{API_BASE_URL}/simulate_transaction", json=txn_payload)
        response.raise_for_status()
        data = response.json()

        st.session_state.status = data.get("status", "Unknown")
        st.session_state.confidence = data.get("confidence", 0.0)
        st.session_state.narrative = data.get("narrative", "No explanation generated.")
        st.session_state.transaction_id = data.get("trace_id", st.session_state.transaction_id)

        fetch_trace()

    except requests.exceptions.ConnectionError:
        st.session_state.error_message = f"Cannot connect to backend at {API_BASE_URL}. Start the server with: uvicorn app.main:app --reload"
    except requests.exceptions.RequestException as e:
        st.session_state.error_message = f"API request failed: {e}"
    except json.JSONDecodeError as e:
        st.session_state.error_message = f"Invalid JSON response: {e}"
    except Exception as e:
        st.session_state.error_message = f"Unexpected error: {e}"

def toggle_trace_mode():
    st.session_state.trace_mode = "verbose" if st.session_state.trace_mode == "summary" else "summary"
    fetch_trace()

# --- Analyst Actions ---
def escalate_transaction():
    st.session_state.status = "Escalated to human analyst."
    st.session_state.narrative = "The transaction has been manually escalated for further review by a human analyst."
    st.session_state.error_message = ""

def mark_safe():
    st.session_state.status = "Marked as Safe (Manual Override)."
    st.session_state.narrative = "The transaction has been manually marked as safe by an analyst, overriding system decision."
    st.session_state.error_message = ""

def override_decision():
    st.session_state.status = "Decision Overridden Manually."
    st.session_state.narrative = "The system's decision has been manually overridden by an analyst."
    st.session_state.error_message = ""

# --- Streamlit UI Layout ---

st.set_page_config(layout="wide", page_title="FinGuard Agents UI")

st.title("FinGuard Agents UI")
st.markdown("Real-time Fraud Detection with Explainable AI & AgentScope Traceability")

# Create two columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Transaction Input")

    # Transaction ID input
    new_transaction_id = st.text_input("Transaction ID (optional)", value=st.session_state.transaction_id)
    if new_transaction_id != st.session_state.transaction_id:
        st.session_state.transaction_id = new_transaction_id

    st.button("Generate New ID", on_click=generate_new_transaction_id)

    st.markdown("---")

    # Transaction details
    new_amount = st.number_input("Amount", value=st.session_state.amount, min_value=0.0)
    if new_amount != st.session_state.amount:
        st.session_state.amount = new_amount

    new_card_type = st.text_input("Card Type (e.g., credit, virtual)", value=st.session_state.card_type)
    if new_card_type != st.session_state.card_type:
        st.session_state.card_type = new_card_type

    new_merchant = st.text_input("Merchant", value=st.session_state.merchant)
    if new_merchant != st.session_state.merchant:
        st.session_state.merchant = new_merchant

    new_merchant_location = st.text_input("Merchant Location", value=st.session_state.merchant_location)
    if new_merchant_location != st.session_state.merchant_location:
        st.session_state.merchant_location = new_merchant_location

    new_user_location = st.text_input("User Location", value=st.session_state.user_location)
    if new_user_location != st.session_state.user_location:
        st.session_state.user_location = new_user_location

    st.button("Simulate Transaction", on_click=submit_transaction, type="primary")

with col2:
    st.header("Fraud Detection Result")

    # Error message display
    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    if st.session_state.status:
        # Status and Confidence
        status_color = "red" if "fraud" in st.session_state.status.lower() or "escalated" in st.session_state.status.lower() else "green"
        st.markdown(f"**Status:** <span style='color:{status_color}; font-weight:bold;'>{st.session_state.status}</span>", unsafe_allow_html=True)
        st.markdown(f"**Confidence:** `{st.session_state.confidence:.2f}`")

        # Narrative Explanation
        st.subheader("Narrative Explanation")
        st.markdown(f"*{st.session_state.narrative}*")

        # Analyst Actions
        st.subheader("Analyst Actions")
        action_cols = st.columns(3)
        with action_cols[0]:
            st.button("Escalate", on_click=escalate_transaction, help="Escalate to a human analyst")
        with action_cols[1]:
            st.button("Mark as Safe", on_click=mark_safe, help="Manually mark as safe")
        with action_cols[2]:
            st.button("Override Decision", on_click=override_decision, help="Manually override the system decision")

        st.markdown("---")

        # AgentScope Trace
        st.subheader("AgentScope Trace")
        st.button(f"Toggle to {'Verbose' if st.session_state.trace_mode == 'summary' else 'Summary'} Trace", on_click=toggle_trace_mode)

        if st.session_state.trace_mode == "summary":
            if st.session_state.trace_summary_data:
                st.json(st.session_state.trace_summary_data)
            else:
                st.info("No summary trace data available yet. Submit a transaction.")
        else:
            if st.session_state.trace_verbose_data and len(st.session_state.trace_verbose_data) > 0:
                for i, step in enumerate(st.session_state.trace_verbose_data):
                    # FIXED: Better error handling for trace steps
                    if isinstance(step, dict):
                        step_num = step.get('step', i+1)
                        component = step.get('component', step.get('agent', 'Unknown'))
                        reason = step.get('reason', step.get('description', 'No description'))
                        confidence = step.get('confidence', 0.0)
                        
                        st.markdown(f"**Step {step_num}: {component}**")
                        st.write(f"Description: {reason}")
                        st.write(f"Confidence: {confidence:.2f}")
                        
                        if step.get('policy_violation') or step.get('violation'):
                            policy_id = step.get('policy_id', 'Unknown')
                            st.warning(f"Policy Violation: {policy_id}")
                        
                        # Show input data if available
                        input_data = step.get('input_data', step.get('input', {}))
                        if input_data:
                            with st.expander(f"Input Data for Step {step_num}"):
                                st.json(input_data)
                        
                        st.markdown("---")
                    else:
                        st.warning(f"Invalid trace step format at index {i}: {step}")
            else:
                st.info("No verbose trace data available yet. Submit a transaction.")

# Add some example data buttons for testing
st.sidebar.header("Quick Test Examples")

if st.sidebar.button("Load Safe Transaction Example"):
    st.session_state.amount = 150.0
    st.session_state.card_type = "credit"
    st.session_state.merchant = "Amazon"
    st.session_state.merchant_location = "USA"
    st.session_state.user_location = "USA"
    st.rerun()

if st.sidebar.button("Load Fraud Transaction Example"):
    st.session_state.amount = 4500.0
    st.session_state.card_type = "virtual"
    st.session_state.merchant = "fraud_Kirlin"
    st.session_state.merchant_location = "Nigeria"
    st.session_state.user_location = "USA"
    st.rerun()

if st.sidebar.button("Load Cross-Border Example"):
    st.session_state.amount = 2000.0
    st.session_state.card_type = "credit"
    st.session_state.merchant = "Electronics_Store"
    st.session_state.merchant_location = "China"
    st.session_state.user_location = "USA"
    st.rerun()