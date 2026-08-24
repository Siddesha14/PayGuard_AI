from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import models
from app.schemas import (
    PaymentRequest,
    PaymentDecision,
    AgentCreate
)
from app.policy_engine import evaluate_payment
from app.database import Base, engine, get_db


# Create database tables after models have been imported
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="PayGuard AI",
    description="Runtime security layer for autonomous financial agents",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "name": "PayGuard AI",
        "status": "operational",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post(
    "/api/v1/authorize-payment",
    response_model=PaymentDecision
)
def authorize_payment(request: PaymentRequest, db: Session = Depends(get_db)):
    return evaluate_payment(request, db)


@app.post("/api/v1/agents")
def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db)
):

    existing = (
        db.query(models.Agent)
        .filter(models.Agent.agent_id == agent.agent_id)
        .first()
    )

    if existing:
        return {
            "error": "Agent already exists"
        }

    new_agent = models.Agent(
        agent_id=agent.agent_id,
        name=agent.name,
        owner_id=agent.owner_id,
        transaction_limit=agent.transaction_limit,
        daily_limit=agent.daily_limit
    )

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    return {
        "agent_id": new_agent.agent_id,
        "name": new_agent.name,
        "status": new_agent.status,
        "trust_score": new_agent.trust_score
    }