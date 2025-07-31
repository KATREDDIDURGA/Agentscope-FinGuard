# app/agents/compliance_agent.py
import json
import os
from datetime import datetime
from app.scope.step_logger import StepLogger
# Import the new threshold
from app.core.app_config import DEFAULT_POLICY_DOC, CONFIDENCE_THRESHOLD, HIGH_VALUE_TRANSACTION_THRESHOLD, VIRTUAL_CARD_LIMIT, EXTREMELY_HIGH_VALUE_DEBIT_THRESHOLD

# Initialize the logger for this agent
logger = StepLogger()

# Load policy rules from file
def load_policy_rules(policy_doc_path: str = DEFAULT_POLICY_DOC) -> dict:
    """Loads policy rules from a JSON file."""
    if not os.path.exists(policy_doc_path):
        print(f"Warning: Policy document not found at {policy_doc_path}. Using empty rules.")
        return {}
    try:
        with open(policy_doc_path, 'r') as f:
            rules = json.load(f)
        return rules
    except json.JSONDecodeError as e:
        print(f"Error decoding policy JSON from {policy_doc_path}: {e}. Using empty rules.")
        return {}
    except Exception as e:
        print(f"Error loading policy rules from {policy_doc_path}: {e}. Using empty rules.")
        return {}

# Load rules once when the module is imported
POLICY_RULES = load_policy_rules()

def check_policy_violation(transaction: dict, amount_flag: bool, location_flag: bool, merchant_flag: bool) -> dict:
    """
    Checks the transaction against predefined policy rules.
    """
    transaction_id = transaction.get("transaction_id", "unknown")
    amount = float(transaction.get("amount", 0))
    card_type = transaction.get("card_type", "unknown").lower()
    user_location = transaction.get("user_location", "unknown").lower()
    merchant_location = transaction.get("merchant_location", "unknown").lower()
    merchant = transaction.get("merchant", "unknown").lower()

    violated = False
    policy_id = None
    reason = "No policy violation detected."
    confidence = 0.0
    rule_action = "none"

    # Log the input to the compliance agent
    logger.log_step(
        transaction_id=transaction_id,
        step=6,
        component="ComplianceGuard",
        input_data={"transaction_data": transaction, "flags": {"amount": amount_flag, "location": location_flag, "merchant": merchant_flag}},
        description="Checking transaction against policy rules.",
        confidence=0.8
    )

    for rule_id, rule_details in POLICY_RULES.items():
        rule_condition = rule_details.get("condition", "")
        rule_action_from_rule = rule_details.get("action", "flag")
        rule_reason = rule_details.get("reason", "Policy violation.")
        rule_confidence = rule_details.get("confidence", 0.9)

        try:
            eval_context = {
                "amount": amount,
                "card_type": card_type,
                "user_location": user_location,
                "merchant_location": merchant_location,
                "merchant": merchant,
                "amount_flag": amount_flag,
                "location_flag": location_flag,
                "merchant_flag": merchant_flag,
                "HIGH_VALUE_TRANSACTION_THRESHOLD": HIGH_VALUE_TRANSACTION_THRESHOLD,
                "VIRTUAL_CARD_LIMIT": VIRTUAL_CARD_LIMIT,
                "EXTREMELY_HIGH_VALUE_DEBIT_THRESHOLD": EXTREMELY_HIGH_VALUE_DEBIT_THRESHOLD # Pass new threshold
            }
            
            if eval(rule_condition, {"__builtins__": None}, eval_context):
                violated = True
                policy_id = rule_id
                reason = rule_reason
                confidence = rule_confidence
                rule_action = rule_action_from_rule
                
                logger.log_step(
                    transaction_id=transaction_id,
                    step=6,
                    component="ComplianceGuard",
                    input_data={"rule_id": rule_id, "condition": rule_condition, "action": rule_action},
                    description=f"Policy {rule_id} violated: {rule_reason}",
                    confidence=confidence,
                    policy_violation=True,
                    policy_id=rule_id
                )
                break
        except Exception as e:
            print(f"Error evaluating policy rule {rule_id}: {e} - Condition: {rule_condition}")

    return {
        "violated": violated,
        "policy_id": policy_id,
        "reason": reason,
        "confidence": confidence,
        "action": rule_action
    }
