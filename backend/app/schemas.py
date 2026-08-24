from pydantic import BaseModel, Field
from typing import List


class PaymentRequest(BaseModel):
    agent_id: str
    amount: float = Field(gt=0)
    merchant_id: str
    category: str
    purpose: str


class PaymentDecision(BaseModel):
    decision: str
    risk_score: float
    violations: List[str]
    reason: str

class AgentCreate(BaseModel):
    agent_id: str
    name: str
    owner_id: str
    transaction_limit: float
    daily_limit: float