import React from "react";

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

export default function SummaryCards({ summary }) {
  if (!summary) return null;

  const flagRate =
    summary.total_transactions > 0
      ? Math.round((summary.flagged_transactions / summary.total_transactions) * 100)
      : 0;

  return (
    <div className="summary-grid">
      <div className="summary-card">
        <div className="label">Total documents</div>
        <div className="value">{summary.total_transactions}</div>
      </div>
      <div className="summary-card">
        <div className="label">Total value processed</div>
        <div className="value">{formatCurrency(summary.total_amount)}</div>
      </div>
      <div className="summary-card flagged">
        <div className="label">Flagged for review ({flagRate}%)</div>
        <div className="value">{summary.flagged_transactions}</div>
      </div>
      <div className="summary-card flagged">
        <div className="label">Value at risk</div>
        <div className="value">{formatCurrency(summary.flagged_amount)}</div>
      </div>
    </div>
  );
}
