from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime
)

from datetime import datetime

from app.database import Base


class Agent(Base):

    __tablename__ = "agents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    agent_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    owner_id = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        default="ACTIVE"
    )

    transaction_limit = Column(
        Float,
        nullable=False
    )

    daily_limit = Column(
        Float,
        nullable=False
    )

    trust_score = Column(
        Float,
        default=100.0
    )

    is_frozen = Column(
        Boolean,
        default=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    transaction_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    agent_id = Column(
        String,
        nullable=False,
        index=True
    )

    amount = Column(
        Float,
        nullable=False
    )

    merchant_id = Column(
        String,
        nullable=False
    )

    category = Column(
        String,
        nullable=False
    )

    purpose = Column(
        String,
        nullable=False
    )

    decision = Column(
        String,
        nullable=False
    )

    risk_score = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )