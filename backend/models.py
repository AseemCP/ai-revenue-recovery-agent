from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base

class FailedPayment(Base):
    __tablename__ = "failed_payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String, unique=True,index=True)
    order_id = Column(String)
    amount = Column(Integer)
    currency = Column(String)
    email = Column(String)
    contact = Column(String)
    error_code = Column(String)
    error_description = Column(String)
    error_reason = Column(String)
    status = Column(String, default="failed")


class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempt_payments"

    id = Column(Integer, primary_key=True, index=True)
    original_payment_id = Column(String, index=True)
    retry_payment_link_id = Column(String, nullable=True)
    retry_link_url = Column(String, nullable=True)
    retry_reference_id = Column(String, nullable=True)
    retry_payment_id = Column(String, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    amount = Column(Integer)
    status = Column(String)

class RecoveryDecision(Base):
    __tablename__ = "recovery_decisions"

    id = Column(Integer, primary_key=True, index=True)
    original_payment_id = Column(String, nullable=False, index=True)
    recovery_attempt_id = Column(Integer, nullable=True)

    action = Column(String, nullable=False)
    priority = Column(String, nullable=True)
    reason = Column(Text, nullable=True)

    ai_message = Column(Text)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))