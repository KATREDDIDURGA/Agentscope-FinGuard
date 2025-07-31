# app/api/routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.agents.fraud_agent import run_fraud_pipeline
from app.scope.trace_reader import get_trace_summary, get_trace_verbose

router = APIRouter()

# Pydantic model for incoming transaction data
class TransactionInput(BaseModel):
    transaction_id: str = None
    amount: float
    card_type: str
    merchant: str
    merchant_location: str
    user_location: str

# Pydantic model for the simulation response
class SimulationResponse(BaseModel):
    status: str
    confidence: float
    trace_id: str
    narrative: str

# Pydantic model for a single trace step (for verbose output)
class TraceStep(BaseModel):
    step: int
    component: str
    input_data: Dict[str, Any]
    description: str
    confidence: float
    timestamp: str
    policy_violation: Optional[bool] = False
    policy_id: Optional[str] = None
    # Add these new fields, making them Optional as they only appear in FinalDecisionAgent step
    final_decision_status: Optional[str] = None
    final_decision_confidence: Optional[float] = None

# Pydantic model for verbose trace output
class VerboseTraceOutput(BaseModel):
    transaction_id: str
    steps: List[TraceStep]

# Pydantic model for summary trace output
class SummaryTraceOutput(BaseModel):
    transaction_id: str
    agents_triggered: List[str]
    final_confidence: float
    final_decision: str
    violations_count: int


@router.post("/simulate_transaction", response_model=SimulationResponse)
def simulate_transaction_endpoint(transaction: TransactionInput):
    """
    Receives transaction input, runs the fraud detection pipeline,
    and returns the result.
    """
    transaction_dict = transaction.dict()
    
    result = run_fraud_pipeline(transaction_dict)
    
    return SimulationResponse(
        status=result["status"],
        confidence=result["confidence"],
        trace_id=result["trace_id"],
        narrative=result["narrative"]
    )

@router.get("/trace/summary/{transaction_id}", response_model=SummaryTraceOutput)
def get_summary_trace(transaction_id: str):
    """
    Retrieves a summary of the agent trace for a given transaction ID.
    """
    summary = get_trace_summary(transaction_id)
    if not summary or summary.get("final_decision") == "No trace data":
        raise HTTPException(status_code=404, detail="Trace summary not found for this transaction ID.")
    return SummaryTraceOutput(**summary)

@router.get("/trace/verbose/{transaction_id}", response_model=VerboseTraceOutput)
def get_verbose_trace(transaction_id: str):
    """
    Retrieves the detailed verbose agent trace for a given transaction ID.
    """
    verbose_data = get_trace_verbose(transaction_id)
    if not verbose_data or not verbose_data.get("steps"):
        raise HTTPException(status_code=404, detail="Verbose trace not found for this transaction ID.")
    
    validated_steps = []
    for step_dict in verbose_data.get("steps", []):
        try:
            validated_steps.append(TraceStep(**step_dict))
        except Exception as e:
            print(f"Pydantic validation error for trace step: {e} - Problematic data: {step_dict}")
            raise HTTPException(status_code=500, detail=f"Invalid trace step data encountered: {e}")

    return VerboseTraceOutput(transaction_id=transaction_id, steps=validated_steps)
