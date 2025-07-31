from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from app.db.base import Base
from datetime import datetime


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    card_type = Column(String)
    merchant = Column(String)
    merchant_location = Column(String)
    user_location = Column(String)
    fraud_score = Column(Float)
    is_fraud = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentScopeLog(Base):
    __tablename__ = "agent_scope_logs"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, index=True)
    step = Column(Integer)
    component = Column(String)
    input_data = Column(JSON)
    description = Column(String)
    confidence = Column(Float)
    policy_violation = Column(Boolean, default=False)
    policy_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
