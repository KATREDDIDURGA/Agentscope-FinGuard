from pydantic import BaseModel
from typing import Optional, List, Dict, Union

# --- Transaction Input ---
class TransactionInput(BaseModel):
    transaction_id: str
    amount: float
    card_type: str
    merchant: str
    merchant_location: str
    user_location: str

# --- Policy Upload + Query ---
class PolicyDoc(BaseModel):
    name: str
    content: str

class PolicyQuery(BaseModel):
    query: str

# --- AgentScope Trace Step Model ---
class TraceStep(BaseModel):
    step: int
    agent: str
    reason: str
    confidence: float
    input: Optional[Union[Dict, str]] = None
    output: Optional[Union[Dict, str]] = None
    violation: Optional[bool] = False
    policy_id: Optional[str] = None
    timestamp: Optional[str] = None

# --- Full Trace View Response ---
class VerboseTrace(BaseModel):
    transaction_id: str
    steps: List[TraceStep]

# --- Summary Trace Response (Optional) ---
class SummaryTrace(BaseModel):
    transaction_id: str
    agents_triggered: List[str]
    final_confidence: float
    final_decision: str

# --- Final Fraud Response (to UI) ---
class FraudResponse(BaseModel):
    status: str  # "fraud" or "safe" or "escalated"
    confidence: float
    trace_id: str
    narrative: str
