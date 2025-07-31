from app.scope.step_logger import StepLogger
from app.core.app_config import CONFIDENCE_THRESHOLD

# Define required fields for the pipeline to run
REQUIRED_FIELDS = ["transaction_id", "amount", "card_type", "user_location", "merchant", "merchant_location"]

# Confidence threshold is loaded from app_config
fallback_logger = StepLogger()

def check_fallback(transaction: dict, current_confidence: float) -> dict:
    """
    Checks if fallback is needed due to missing fields or low model confidence.
    Returns a dict with 'triggered' flag and reason.
    Logs decision to AgentScope.
    """
    missing_fields = [field for field in REQUIRED_FIELDS if field not in transaction or transaction[field] in [None, "", "N/A"]]
    fallback_triggered = False
    fallback_reason = ""

    if missing_fields:
        fallback_triggered = True
        fallback_reason = f"Missing required fields: {', '.join(missing_fields)}"
    elif current_confidence < CONFIDENCE_THRESHOLD:
        fallback_triggered = True
        fallback_reason = f"Model confidence too low: {current_confidence:.2f} < threshold {CONFIDENCE_THRESHOLD}"

    if fallback_triggered:
        fallback_logger.log_step(
            transaction_id=transaction.get("transaction_id", "unknown"),
            step=5,
            component="FallbackAgent",
            input_data={"fields_checked": REQUIRED_FIELDS, "confidence": current_confidence},
            description=fallback_reason,
            confidence=current_confidence,
            policy_violation=False  # Fallback is not a policy violation
        )

    return {
        "triggered": fallback_triggered,
        "reason": fallback_reason if fallback_triggered else "All checks passed"
    }