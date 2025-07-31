# app/scope/step_logger.py
import json
import os
from datetime import datetime
# Import LOG_DIR and LOG_FILE_EXTENSION from app_config
from app.core.app_config import LOG_DIR, LOG_FILE_EXTENSION

class StepLogger:
    """
    A utility class for logging steps of the fraud detection pipeline
    to separate JSONL files for each transaction ID, ensuring clear traceability.
    """
    def __init__(self, log_directory: str = LOG_DIR, log_file_extension: str = LOG_FILE_EXTENSION):
        self.log_directory = log_directory
        self.log_file_extension = log_file_extension
        # Ensure the log directory exists
        os.makedirs(self.log_directory, exist_ok=True)

    def _get_transaction_log_path(self, transaction_id: str) -> str:
        """Constructs the full path for a specific transaction's log file."""
        file_name = f"{transaction_id}{self.log_file_extension}"
        return os.path.join(self.log_directory, file_name)

    def log_step(self, transaction_id: str, step: int, component: str,
                 input_data: dict, description: str, confidence: float,
                 policy_violation: bool = False, policy_id: str = None,
                 final_decision_status: str = None, final_decision_confidence: float = None):
        """
        Logs a single step of the fraud detection process to its dedicated transaction log file.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "step": step,
            "component": component,
            "input_data": input_data,
            "description": description,
            "confidence": round(confidence, 2),
            "policy_violation": policy_violation,
            "policy_id": policy_id
        }
        if final_decision_status is not None:
            log_entry["final_decision_status"] = final_decision_status
        if final_decision_confidence is not None:
            log_entry["final_decision_confidence"] = round(final_decision_confidence, 2)

        # Write to the specific transaction's log file (append mode)
        log_file_path = self._get_transaction_log_path(transaction_id)
        try:
            with open(log_file_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            # print(f"Logged step {step} for {transaction_id} to {file_name}") # Optional: for debugging
        except Exception as e:
            print(f"ERROR: Failed to write log for transaction {transaction_id} to {log_file_path}: {e}")

