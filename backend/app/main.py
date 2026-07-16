import json
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import models, ocr_extract, anomaly_detection
from .database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Financial Document Intelligence API",
    description="Upload invoices/expenses, extract structured data, and flag anomalies.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TransactionOut(BaseModel):
    id: int
    filename: str
    vendor: Optional[str]
    invoice_number: Optional[str]
    amount: Optional[float]
    currency: Optional[str]
    invoice_date: Optional[str]
    category: Optional[str]
    is_duplicate: bool
    is_statistical_outlier: bool
    is_policy_violation: bool
    anomaly_score: float
    flags: List[str] = []

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_flags(cls, t: models.Transaction):
        data = {
            "id": t.id,
            "filename": t.filename,
            "vendor": t.vendor,
            "invoice_number": t.invoice_number,
            "amount": t.amount,
            "currency": t.currency,
            "invoice_date": t.invoice_date,
            "category": t.category,
            "is_duplicate": t.is_duplicate,
            "is_statistical_outlier": t.is_statistical_outlier,
            "is_policy_violation": t.is_policy_violation,
            "anomaly_score": t.anomaly_score,
            "flags": json.loads(t.flags) if t.flags else [],
        }
        return cls(**data)


class SummaryOut(BaseModel):
    total_transactions: int
    flagged_transactions: int
    total_amount: float
    flagged_amount: float
    duplicates: int
    statistical_outliers: int
    policy_violations: int


@app.get("/")
def root():
    return {"status": "ok", "message": "Financial Document Intelligence API is running"}


@app.post("/api/upload", response_model=TransactionOut)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts an invoice/expense file (image, PDF, or txt), runs OCR + field
    extraction, stores it, then re-runs anomaly detection across all
    transactions so cross-document patterns (like duplicates) are caught.
    """
    file_bytes = await file.read()

    try:
        raw_text = ocr_extract.extract_text(file_bytes, file.filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not extract text: {exc}")

    fields = ocr_extract.parse_fields(raw_text)

    transaction = models.Transaction(
        filename=file.filename,
        raw_text=raw_text,
        vendor=fields["vendor"],
        invoice_number=fields["invoice_number"],
        amount=fields["amount"],
        invoice_date=fields["invoice_date"],
        category=fields["category"],
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Re-run detection across the whole dataset so duplicates/outliers
    # relative to this new record are caught immediately.
    anomaly_detection.run_full_analysis(db)
    db.refresh(transaction)

    return TransactionOut.from_orm_with_flags(transaction)


@app.get("/api/transactions", response_model=List[TransactionOut])
def list_transactions(
    flagged_only: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(models.Transaction).order_by(models.Transaction.id.desc())
    transactions = query.all()

    results = [TransactionOut.from_orm_with_flags(t) for t in transactions]
    if flagged_only:
        results = [
            r for r in results
            if r.is_duplicate or r.is_statistical_outlier or r.is_policy_violation
        ]
    return results


@app.get("/api/transactions/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionOut.from_orm_with_flags(t)


@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    t = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(t)
    db.commit()
    anomaly_detection.run_full_analysis(db)
    return {"status": "deleted", "id": transaction_id}


@app.get("/api/summary", response_model=SummaryOut)
def get_summary(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction).all()
    flagged = [t for t in transactions if t.is_duplicate or t.is_statistical_outlier or t.is_policy_violation]

    return SummaryOut(
        total_transactions=len(transactions),
        flagged_transactions=len(flagged),
        total_amount=sum(t.amount or 0 for t in transactions),
        flagged_amount=sum(t.amount or 0 for t in flagged),
        duplicates=sum(1 for t in transactions if t.is_duplicate),
        statistical_outliers=sum(1 for t in transactions if t.is_statistical_outlier),
        policy_violations=sum(1 for t in transactions if t.is_policy_violation),
    )
