"""
Three complementary anomaly detection layers, run over ALL transactions
currently in the database every time a new one is added:

1. Duplicate detection      -> same vendor + same amount within N days
2. Statistical outliers     -> Isolation Forest over numeric/behavioral features
3. Policy violations        -> simple configurable business rules

Each layer is independent and explainable, which matters a lot for an
audit/advisory use case: a flagged transaction should always come with a
human-readable reason, not just a black-box score.
"""
import json
from datetime import datetime
from typing import List

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sqlalchemy.orm import Session

from . import models

# --- Configurable policy thresholds ------------------------------------
POLICY_MAX_AMOUNT = {
    "travel": 25000.0,
    "meals": 3000.0,
    "office_supplies": 15000.0,
    "software": 100000.0,
    "consulting": 500000.0,
    "uncategorized": 50000.0,
}
DUPLICATE_WINDOW_DAYS = 7


def _safe_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None


def detect_duplicates(transactions: List[models.Transaction]) -> None:
    """Flag transactions that share vendor + amount within a short window."""
    seen = {}
    for t in sorted(transactions, key=lambda x: x.id):
        if t.amount is None or not t.vendor:
            continue
        key = (t.vendor.strip().lower(), round(t.amount, 2))
        t_date = _safe_date(t.invoice_date)

        if key in seen:
            prev = seen[key]
            prev_date = _safe_date(prev.invoice_date)
            within_window = True
            if t_date and prev_date:
                within_window = abs((t_date - prev_date).days) <= DUPLICATE_WINDOW_DAYS

            if within_window:
                t.is_duplicate = True
                _add_flag(t, f"Possible duplicate of transaction #{prev.id} "
                              f"({prev.vendor}, {prev.amount})")
        seen[key] = t


def detect_policy_violations(transactions: List[models.Transaction]) -> None:
    """Flag transactions exceeding category-specific spend limits."""
    for t in transactions:
        if t.amount is None:
            continue
        category = t.category or "uncategorized"
        limit = POLICY_MAX_AMOUNT.get(category, POLICY_MAX_AMOUNT["uncategorized"])
        if t.amount > limit:
            t.is_policy_violation = True
            _add_flag(t, f"Exceeds policy limit for '{category}' "
                          f"(limit: {limit:,.2f}, actual: {t.amount:,.2f})")


def detect_statistical_outliers(transactions: List[models.Transaction]) -> None:
    """
    Use Isolation Forest over engineered features to catch transactions
    that are statistically unusual even if no hard rule was broken
    (e.g. an amount that's a huge outlier for that specific vendor).
    """
    valid = [t for t in transactions if t.amount is not None]
    if len(valid) < 5:
        # Not enough data for a meaningful model yet.
        return

    df = pd.DataFrame({
        "id": [t.id for t in valid],
        "amount": [t.amount for t in valid],
        "vendor": [t.vendor or "unknown" for t in valid],
    })

    # Feature engineering: raw amount, log amount (handles skew), and
    # deviation from that vendor's own average spend.
    df["log_amount"] = np.log1p(df["amount"])
    vendor_avg = df.groupby("vendor")["amount"].transform("mean")
    df["vendor_deviation"] = (df["amount"] - vendor_avg) / (vendor_avg + 1e-6)

    features = df[["amount", "log_amount", "vendor_deviation"]].fillna(0)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.1,  # assume ~10% of transactions may be anomalous
        random_state=42,
    )
    model.fit(features)

    # decision_function: lower (more negative) = more anomalous
    raw_scores = model.decision_function(features)
    predictions = model.predict(features)  # -1 = outlier, 1 = normal

    # Normalize scores to a 0-1 "anomaly score" where higher = more anomalous
    normalized = (raw_scores.max() - raw_scores) / (raw_scores.max() - raw_scores.min() + 1e-9)

    id_to_transaction = {t.id: t for t in valid}
    for i, row in df.iterrows():
        t = id_to_transaction[row["id"]]
        t.anomaly_score = round(float(normalized[i]), 4)
        if predictions[i] == -1:
            t.is_statistical_outlier = True
            _add_flag(
                t,
                f"Statistically unusual amount for vendor '{t.vendor}' "
                f"(anomaly score: {t.anomaly_score})"
            )


def _add_flag(t: models.Transaction, reason: str) -> None:
    existing = json.loads(t.flags) if t.flags else []
    if reason not in existing:
        existing.append(reason)
    t.flags = json.dumps(existing)


def run_full_analysis(db: Session) -> None:
    """
    Re-runs all three detection layers over every transaction in the DB.
    Called after every upload so flags stay consistent as new data arrives.
    """
    transactions = db.query(models.Transaction).all()

    # Reset flags before recomputing, so removed anomalies don't linger.
    for t in transactions:
        t.is_duplicate = False
        t.is_statistical_outlier = False
        t.is_policy_violation = False
        t.anomaly_score = 0.0
        t.flags = None

    detect_duplicates(transactions)
    detect_policy_violations(transactions)
    detect_statistical_outliers(transactions)

    db.commit()
