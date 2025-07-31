# app/agents/narrative_agent.py
import requests
import json
import time # For exponential backoff

from app.scope.step_logger import StepLogger
# Import Groq specific configuration
from app.core.app_config import GROQ_API_URL, GROQ_API_KEY, GROQ_MODEL_NAME

logger = StepLogger()

# Function to call the Groq API with exponential backoff
def call_groq_api(prompt: str, max_retries: int = 5, initial_delay: int = 1) -> str:
    """
    Calls the Groq API (OpenAI-compatible) to generate text based on a prompt,
    with exponential backoff for retries.
    """
    # Groq's API expects an OpenAI-like chat completions payload
    payload = {
        "model": GROQ_MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a concise and professional financial assistant who explains fraud detection results."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7, # Controls creativity (0.0-1.0)
        "max_tokens": 200, # Limits the length of the generated response
        "stream": False # We want a single, complete response
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROQ_API_KEY}' # Your Groq API Key
    }
    api_url = GROQ_API_URL

    for i in range(max_retries):
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            result = response.json()

            # Parse the OpenAI-compatible response structure
            if result.get("choices") and result["choices"][0].get("message") and \
               result["choices"][0]["message"].get("content"):
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Groq API response structure unexpected: {result}")
                return "Could not generate narrative due to unexpected API response from Groq."

        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                delay = initial_delay * (2 ** i) # Exponential backoff
                print(f"Groq API request failed: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Groq API request failed after {max_retries} retries: {e}")
                return "Could not generate narrative due to Groq API error after multiple retries."
        except json.JSONDecodeError as e:
            print(f"Groq API response not valid JSON: {e}. Response: {response.text}")
            return "Could not generate narrative due to invalid JSON response from Groq API."
        except Exception as e:
            print(f"An unexpected error occurred during Groq API call: {e}")
            return "Could not generate narrative due to an unexpected error."
    return "Could not generate narrative." # Should not be reached if max_retries is hit

def generate_narrative(transaction: dict, amount_flag: bool, location_flag: bool, merchant_flag: bool, policy_result: dict) -> str:
    """
    Generates a natural-language narrative for a transaction using an LLM,
    based on the various flags and analysis results.
    """
    transaction_id = transaction.get("transaction_id", "unknown")
    amount = float(transaction.get("amount", 0))
    card_type = transaction.get("card_type", "unknown")
    user_location = transaction.get("user_location", "unknown")
    merchant_location = transaction.get("merchant_location", "unknown")
    merchant = transaction.get("merchant", "unknown")

    # Collect the specific reasons/flags for the prompt
    reasons_list_for_llm = []

    if amount_flag:
        reasons_list_for_llm.append(f"- High-value payment: ${amount:,.2f} using a {card_type.lower()} card.")
    if location_flag:
        reasons_list_for_llm.append(f"- Cross-border transaction: from {user_location} to {merchant_location}.")
    if merchant_flag:
        reasons_list_for_llm.append(f"- High-risk merchant detected: {merchant}.")
    if policy_result.get("violated"):
        reasons_list_for_llm.append(f"- Policy Violation: Policy {policy_result['policy_id']} was violated. Reason: '{policy_result['reason']}'.")
    
    # If the transaction was escalated by initial fallback (e.g., missing data)
    if transaction.get("initial_fallback_reason"):
        reasons_list_for_llm.append(f"- Initial data missing/invalid: {transaction['initial_fallback_reason']}.")


    # Construct the prompt for the LLM
    if not reasons_list_for_llm:
        # Prompt for a safe transaction
        llm_prompt = (
            "The following financial transaction passed all fraud checks and no unusual patterns were detected. "
            "Please generate a concise (2-3 sentences) and reassuring narrative explaining this. "
            "Do not include a conversational opening or closing. Focus on clarity and professionalism.\n\n"
            f"Transaction details: ID {transaction_id}, Amount ${amount:,.2f}, Card Type {card_type}, "
            f"User Location {user_location}, Merchant {merchant}, Merchant Location {merchant_location}."
        )
    else:
        # Prompt for a flagged/escalated transaction
        reasons_text = "\n".join(reasons_list_for_llm)
        llm_prompt = (
            "A financial transaction has been processed and requires an explainable narrative. "
            "Based on the following flags and details, generate a concise (2-3 sentences), professional, "
            "and clear explanation of why this transaction was flagged or what unusual patterns were detected. "
            "Focus on the 'why' and provide actionable insights if possible. "
            "Do not include a conversational opening or closing.\n\n"
            f"Transaction ID: {transaction_id}\n"
            f"Amount: ${amount:,.2f}\n"
            f"Card Type: {card_type}\n"
            f"User Location: {user_location}\n"
            f"Merchant: {merchant}\n"
            f"Merchant Location: {merchant_location}\n\n"
            f"Triggered Reasons/Flags:\n{reasons_text}\n\n"
            "Narrative:"
        )

    # Call the Groq LLM to generate the narrative
    narrative = call_groq_api(llm_prompt) # <--- Changed to call_groq_api

    # Log the LLM's input and output for traceability
    logger.log_step(
        transaction_id=transaction_id,
        step=7, # Consistent step number for NarrativeAgent
        component="NarrativeAgent",
        input_data={"prompt_to_llm": llm_prompt, "transaction_details": transaction, "flags_for_llm": reasons_list_for_llm},
        description=narrative,
        confidence=0.95 # Confidence in the narrative generation itself
    )

    return narrative
