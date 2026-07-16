from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from .database import Base


class Transaction(Base):
    """
    Represents a single extracted financial transaction/document
    (invoice, expense claim, or ledger line item).
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # File / source info
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    raw_text = Column(Text, nullable=True)  # full OCR/parsed text, for audit trail

    # Extracted structured fields
    vendor = Column(String, nullable=True, index=True)
    invoice_number = Column(String, nullable=True, index=True)
    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True, default="INR")
    invoice_date = Column(String, nullable=True)  # kept as string (raw parsed date)
    category = Column(String, nullable=True)

    # Anomaly detection results
    is_duplicate = Column(Boolean, default=False)
    is_statistical_outlier = Column(Boolean, default=False)
    is_policy_violation = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)  # higher = more anomalous
    flags = Column(Text, nullable=True)  # JSON-encoded list of human-readable reasons

    @property
    def is_flagged(self) -> bool:
        return self.is_duplicate or self.is_statistical_outlier or self.is_policy_violation
