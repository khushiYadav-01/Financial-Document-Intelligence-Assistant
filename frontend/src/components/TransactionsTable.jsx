import React, { useState, useMemo } from "react";
import { api } from "../api";

function formatCurrency(value) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

const FILTERS = ["All", "Flagged", "Duplicates", "Outliers", "Policy"];

export default function TransactionsTable({ transactions, onChange }) {
  const [filter, setFilter] = useState("All");
  const [expandedId, setExpandedId] = useState(null);

  const filtered = useMemo(() => {
    switch (filter) {
      case "Flagged":
        return transactions.filter(
          (t) => t.is_duplicate || t.is_statistical_outlier || t.is_policy_violation
        );
      case "Duplicates":
        return transactions.filter((t) => t.is_duplicate);
      case "Outliers":
        return transactions.filter((t) => t.is_statistical_outlier);
      case "Policy":
        return transactions.filter((t) => t.is_policy_violation);
      default:
        return transactions;
    }
  }, [transactions, filter]);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    await api.deleteTransaction(id);
    onChange();
  };

  return (
    <div className="table-panel">
      <div className="section-title">Transactions</div>
      <div className="filter-tabs">
        {FILTERS.map((f) => (
          <button
            key={f}
            className={filter === f ? "active" : ""}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="empty-state">
          No documents here yet. Upload an invoice or expense claim to get started.
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Vendor</th>
              <th>Invoice #</th>
              <th>Date</th>
              <th>Category</th>
              <th style={{ textAlign: "right" }}>Amount</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((t) => {
              const isFlagged = t.is_duplicate || t.is_statistical_outlier || t.is_policy_violation;
              const isExpanded = expandedId === t.id;
              return (
                <React.Fragment key={t.id}>
                  <tr
                    className={isFlagged ? "flagged" : ""}
                    onClick={() => setExpandedId(isExpanded ? null : t.id)}
                    style={{ cursor: "pointer" }}
                  >
                    <td>{t.vendor || "Unknown"}</td>
                    <td>{t.invoice_number || "—"}</td>
                    <td>{t.invoice_date || "—"}</td>
                    <td>{t.category}</td>
                    <td className="amount-cell">{formatCurrency(t.amount)}</td>
                    <td>
                      {t.is_duplicate && <span className="tag duplicate">Duplicate</span>}
                      {t.is_statistical_outlier && <span className="tag outlier">Outlier</span>}
                      {t.is_policy_violation && <span className="tag policy">Policy</span>}
                      {!isFlagged && <span className="tag clean">Clean</span>}
                    </td>
                    <td>
                      <button className="delete-btn" onClick={(e) => handleDelete(t.id, e)}>
                        ✕
                      </button>
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr>
                      <td colSpan={7} style={{ background: "#faf8f2" }}>
                        <div className="flags-list">
                          <strong>Source file:</strong> {t.filename}
                          <br />
                          <strong>Anomaly score:</strong> {t.anomaly_score}
                          {t.flags.length > 0 && (
                            <>
                              <br />
                              <strong>Reasons flagged:</strong>
                              <ul style={{ margin: "4px 0 0 18px" }}>
                                {t.flags.map((f, i) => (
                                  <li key={i}>{f}</li>
                                ))}
                              </ul>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
