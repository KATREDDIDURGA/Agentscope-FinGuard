# app/scope/trace_reader.py
import json
import os
from datetime import datetime
# Import LOG_DIR and LOG_FILE_EXTENSION from app_config
from app.core.app_config import LOG_DIR, LOG_FILE_EXTENSION, CONFIDENCE_THRESHOLD, FALLBACK_THRESHOLD

def _get_transaction_log_path(transaction_id: str) -> str:
    """Constructs the full path for a specific transaction's log file."""
    file_name = f"{transaction_id}{LOG_FILE_EXTENSION}"
    return os.path.join(LOG_DIR, file_name)

def get_trace_verbose(transaction_id: str) -> dict:
    """
    Retrieves the verbose log entries for a given transaction ID from its dedicated file.
    """
    verbose_steps = []
    log_file_path = _get_transaction_log_path(transaction_id)

    if not os.path.exists(log_file_path):
        print(f"Warning: Log file not found for transaction ID: {transaction_id} at {log_file_path}")
        return {"transaction_id": transaction_id, "steps": []}

    with open(log_file_path, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                # No need to filter by transaction_id here, as the file itself is for that ID
                # Ensure all fields expected by TraceStep Pydantic model are present,
                # or provide sensible defaults if they might be missing.
                log_entry.setdefault('timestamp', datetime.now().isoformat())
                log_entry.setdefault('input_data', {})
                log_entry.setdefault('policy_violation', False)
                log_entry.setdefault('policy_id', None)
                log_entry.setdefault('component', "Unknown")
                log_entry.setdefault('description', "No description provided.")
                log_entry.setdefault('confidence', 0.0)
                log_entry.setdefault('step', 0)
                log_entry.setdefault('final_decision_status', None)
                log_entry.setdefault('final_decision_confidence', None)

                verbose_steps.append(log_entry)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from log file {log_file_path}: {e} - Line: '{line.strip()}'")
            except Exception as e:
                print(f"Unexpected error processing log line from {log_file_path}: {e} - Line: '{line.strip()}'")

    verbose_steps.sort(key=lambda x: x.get('step', 0))
    
    return {"transaction_id": transaction_id, "steps": verbose_steps}

def get_trace_summary(transaction_id: str) -> dict:
    """
    Retrieves a summary of the log entries for a given transaction ID.
    Explicitly looks for the FinalDecisionAgent step for the authoritative decision.
    """
    verbose_trace = get_trace_verbose(transaction_id)
    steps = verbose_trace.get("steps", [])

    agents_triggered = set()
    final_decision = "unknown"
    final_confidence = 0.0
    violations_count = 0
    
    if not steps:
        return {
            "transaction_id": transaction_id,
            "agents_triggered": [],
            "final_confidence": 0.0,
            "final_decision": "No trace data",
            "violations_count": 0
        }

    # Iterate through steps to collect information for the summary
    for step_data in steps:
        agents_triggered.add(step_data.get("component", "Unknown Agent"))
        
        if step_data.get("policy_violation"):
            violations_count += 1
        
        # Explicitly look for the 'FinalDecisionAgent' step for the authoritative decision
        if step_data.get("component") == "FinalDecisionAgent":
            final_decision = step_data.get("final_decision_status", "unknown")
            final_confidence = step_data.get("final_decision_confidence", 0.0)
            # If found, this is the authoritative decision. We continue iterating to collect all agents_triggered and violations_count.

    # If FinalDecisionAgent was not found (e.g., old logs or error), infer decision
    # This inference logic should mirror fraud_agent.py's decision logic
    if final_decision == "unknown" and steps:
        last_step_confidence = steps[-1].get("confidence", 0.0)
        
        if last_step_confidence > CONFIDENCE_THRESHOLD:
            final_decision = "fraud"
        elif last_step_confidence >= FALLBACK_THRESHOLD:
            final_decision = "escalated"
        else:
            final_decision = "safe"
        final_confidence = last_step_confidence


    return {
        "transaction_id": transaction_id,
        "agents_triggered": sorted(list(agents_triggered)),
        "final_confidence": round(final_confidence, 2),
        "final_decision": final_decision,
        "violations_count": violations_count
    }
