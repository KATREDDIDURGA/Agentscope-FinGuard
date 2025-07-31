# app/agents/fraud_agent.py
import pandas as pd
import pickle
import os
import uuid

from app.scope.step_logger import StepLogger
from app.core.app_config import CONFIDENCE_THRESHOLD, FALLBACK_THRESHOLD, RISKY_MERCHANTS, VIRTUAL_CARD_LIMIT, HIGH_VALUE_TRANSACTION_THRESHOLD
from app.agents.fallback_agent import check_fallback
from app.agents.compliance_agent import check_policy_violation
from app.agents.narrative_agent import generate_narrative

# --- ML Model Loading ---
current_file_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_FROM_AGENT = os.path.abspath(os.path.join(current_file_dir, "..", ".."))
FRAUD_MODEL_PATH = os.path.join(PROJECT_ROOT_FROM_AGENT, "models", "fraud_model.pkl")

model = None
if os.path.exists(FRAUD_MODEL_PATH):
    try:
        with open(FRAUD_MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print(f"Fraud model loaded successfully from {FRAUD_MODEL_PATH}")
    except Exception as e:
        print(f"Warning: Could not load fraud model from {FRAUD_MODEL_PATH}: {e}. Running without ML scoring.")
        model = None
else:
    print(f"Warning: Fraud model not found at {FRAUD_MODEL_PATH}. Please run 'python create_dummy_model.py'. Running without ML scoring.")

logger = StepLogger()

def run_fraud_pipeline(transaction: dict) -> dict:
    """
    Runs the fraud detection pipeline, orchestrating various agents
    to determine the transaction's status, confidence, and narrative.
    """
    transaction_id = transaction.get("transaction_id")
    if not transaction_id:
        transaction_id = str(uuid.uuid4())
        transaction["transaction_id"] = transaction_id
        print(f"Generated new transaction ID: {transaction_id}")

    amount = float(transaction.get("amount", 0))
    card_type = transaction.get("card_type", "unknown").lower()
    user_location = transaction.get("user_location", "unknown").lower()
    merchant = transaction.get("merchant", "").lower()
    merchant_location = transaction.get("merchant_location", "unknown").lower()

    is_escalated_by_initial_fallback = False
    amount_flag = False
    location_flag = False
    merchant_flag = False
    
    policy_result = {"violated": False, "policy_id": None, "reason": "No policy violation detected.", "confidence": 0.0, "action": "safe"} 
    model_score = 0.5

    initial_fallback_result = check_fallback(transaction, 1.0)
    if initial_fallback_result["triggered"]:
        is_escalated_by_initial_fallback = True
        transaction["initial_fallback_reason"] = initial_fallback_result["reason"]
        logger.log_step(transaction_id, 1, "InitialFallbackCheck", transaction,
                        f"Initial fallback triggered: {initial_fallback_result['reason']}", 0.0)
        pass

    if not is_escalated_by_initial_fallback:
        if card_type == "virtual" and amount > VIRTUAL_CARD_LIMIT:
            amount_flag = True
            logger.log_step(transaction_id, 2, "AmountChecker", {"amount": amount, "card_type": card_type},
                            f"Amount (${amount:,.2f}) exceeds limit ({VIRTUAL_CARD_LIMIT:,.2f}) for virtual card.", 0.75)
        elif amount > HIGH_VALUE_TRANSACTION_THRESHOLD:
            amount_flag = True 
            logger.log_step(transaction_id, 2, "AmountChecker", {"amount": amount},
                            f"High-value transaction (${amount:,.2f}) detected.", 0.80)

        if user_location != merchant_location:
            location_flag = True
            logger.log_step(transaction_id, 3, "LocationValidator", {"user_loc": user_location, "merchant_loc": merchant_location},
                            "Cross-border transaction detected.", 0.88)

        if merchant in RISKY_MERCHANTS:
            merchant_flag = True
            logger.log_step(transaction_id, 4, "MerchantRiskChecker", {"merchant": merchant},
                            "Merchant identified as high-risk.", 0.91)

    model_score = 0.5
    if model and not is_escalated_by_initial_fallback:
        try:
            features = pd.DataFrame([{
                "amount": amount,
                "card_type_virtual": int(card_type == "virtual"),
                "merchant_is_risky": int(merchant_flag),
                "location_mismatch": int(location_flag)
            }])
            model_score = model.predict_proba(features)[0][1]
            logger.log_step(transaction_id, 5, "MLScorer", {"features": features.to_dict('records')[0]},
                            f"Model fraud score: {model_score:.2f}", model_score)
        except Exception as e:
            print(f"Model prediction error for transaction {transaction_id}: {e}. Using default score (0.5).")
            model_score = 0.5
            logger.log_step(transaction_id, 5, "MLScorer", {"error": str(e)},
                            "Model prediction failed, using default score.", 0.0)
    elif not model:
        logger.log_step(transaction_id, 5, "MLScorer", {}, "ML model not loaded, using default score (0.5).", 0.0)

    if not is_escalated_by_initial_fallback:
        policy_result = check_policy_violation(transaction, amount_flag, location_flag, merchant_flag)
        if policy_result["violated"]:
            logger.log_step(transaction_id, 6, "ComplianceGuardSummary", transaction,
                            f"Policy {policy_result['policy_id']} violated: {policy_result['reason']}",
                            policy_result["confidence"], True, policy_result["policy_id"])

    final_status = "safe"
    final_confidence = 0.0

    if is_escalated_by_initial_fallback:
        final_status = "escalated"
        final_confidence = 0.1
    elif policy_result["violated"]:
        final_status = policy_result["action"]
        final_confidence = policy_result["confidence"]
    elif merchant_flag: # F1.1 - Blacklisted Merchant
        final_status = "fraud"
        final_confidence = max(model_score, 0.95)
    elif location_flag and card_type == "virtual" and amount > VIRTUAL_CARD_LIMIT: # F2.1 - Foreign IP + Virtual Card + High Value
        final_status = "fraud"
        final_confidence = max(model_score, 0.98)
    elif merchant == "" or merchant_location == "": # F6.1 - Invalid Metadata
        final_status = "fraud"
        final_confidence = max(model_score, 0.90)
    elif amount > HIGH_VALUE_TRANSACTION_THRESHOLD: # E1.1 - Amount > $5000
        final_status = "escalated"
        final_confidence = max(model_score, 0.80)
    # NEW RULE: If cross-border is detected, and not caught by stronger fraud rules, escalate.
    elif location_flag: # E6.1 - Cross-Border Without Metadata (or just general cross-border for escalation)
        final_status = "escalated"
        final_confidence = max(model_score, 0.65) # A confidence that pushes it to manual review range
    else:
        # If no specific rule or policy triggers, rely on ML model score and suggested thresholds
        if model_score > CONFIDENCE_THRESHOLD: # > 0.85
            final_status = "fraud" # ML is highly confident in fraud
            final_confidence = model_score
        elif model_score >= FALLBACK_THRESHOLD: # 0.60 - 0.85
            final_status = "escalated" # ML uncertainty (E5)
            final_confidence = model_score
        else: # model_score < 0.60
            final_status = "safe" # If ML score is low, AND no other flags, it should be SAFE.
            final_confidence = model_score

    narrative = generate_narrative(
        transaction=transaction,
        amount_flag=amount_flag,
        location_flag=location_flag,
        merchant_flag=merchant_flag,
        policy_result=policy_result
    )

    logger.log_step(
        transaction_id=transaction_id,
        step=8,
        component="FinalDecisionAgent",
        input_data={"final_status": final_status, "final_confidence": final_confidence},
        description=f"Final decision: {final_status} with confidence {final_confidence:.2f}",
        confidence=final_confidence,
        final_decision_status=final_status,
        final_decision_confidence=final_confidence
    )

    return {
        "status": final_status,
        "confidence": round(final_confidence, 2),
        "trace_id": transaction_id,
        "narrative": narrative,
    }
