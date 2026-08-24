from sqlalchemy.orm import Session

from app.schemas import PaymentRequest
from app.models import Agent, Transaction

from uuid import uuid4
from datetime import datetime, timedelta


def evaluate_payment(
    request: PaymentRequest,
    db: Session
):

    # --------------------------------
    # 1. FIND AGENT
    # --------------------------------

    agent = (
        db.query(Agent)
        .filter(Agent.agent_id == request.agent_id)
        .first()
    )

    if not agent:

        return {
            "decision": "BLOCK",
            "risk_score": 1.0,
            "violations": ["UNKNOWN_AGENT"],
            "reason": "Agent is not registered with PayGuard."
        }

    # --------------------------------
    # 2. CHECK AGENT STATUS
    # --------------------------------

    if agent.is_frozen:

        return {
            "decision": "BLOCK",
            "risk_score": 1.0,
            "violations": ["AGENT_FROZEN"],
            "reason": "Agent has been frozen by PayGuard."
        }

    if agent.status != "ACTIVE":

        return {
            "decision": "BLOCK",
            "risk_score": 0.9,
            "violations": ["AGENT_INACTIVE"],
            "reason": "Agent is not currently active."
        }

    violations = []

    # --------------------------------
    # 3. TRANSACTION LIMIT
    # --------------------------------

    if request.amount > agent.transaction_limit:

        violations.append(
            "TRANSACTION_LIMIT_EXCEEDED"
        )

    # --------------------------------
    # 4. DAILY SPENDING
    # --------------------------------

    start_of_day = datetime.utcnow().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    daily_spending = (
        db.query(Transaction)
        .filter(
            Transaction.agent_id == request.agent_id,
            Transaction.decision == "APPROVE",
            Transaction.created_at >= start_of_day
        )
        .all()
    )

    total_today = sum(
        transaction.amount
        for transaction in daily_spending
    )

    if (
        total_today + request.amount
        > agent.daily_limit
    ):

        violations.append(
            "DAILY_LIMIT_EXCEEDED"
        )

    # --------------------------------
    # 5. BASIC POLICY
    # --------------------------------

    allowed_categories = [
        "electronics",
        "office_supplies"
    ]

    if request.category not in allowed_categories:

        violations.append(
            "CATEGORY_NOT_ALLOWED"
        )

    allowed_merchants = [
        "office_mart",
        "tech_world"
    ]

    if request.merchant_id not in allowed_merchants:

        violations.append(
            "MERCHANT_NOT_ALLOWED"
        )

    # --------------------------------
    # 6. DECISION
    # --------------------------------

    if violations:

        risk_score = min(
            0.4 + (0.15 * len(violations)),
            1.0
        )

        decision = "BLOCK"

        reason = (
            "Payment violates one or more "
            "financial security policies."
        )

    else:

        risk_score = 0.05

        decision = "APPROVE"

        reason = (
            "Payment satisfies the agent's "
            "current authorization policies."
        )

    # --------------------------------
    # 7. RECORD TRANSACTION
    # --------------------------------

    transaction = Transaction(
        transaction_id=str(uuid4()),
        agent_id=request.agent_id,
        amount=request.amount,
        merchant_id=request.merchant_id,
        category=request.category,
        purpose=request.purpose,
        decision=decision,
        risk_score=risk_score
    )

    db.add(transaction)
    db.commit()

    return {
        "decision": decision,
        "risk_score": risk_score,
        "violations": violations,
        "reason": reason
    }