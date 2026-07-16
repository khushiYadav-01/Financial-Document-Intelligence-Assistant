import React, { useState, useEffect, useCallback } from "react";
import { api } from "./api";
import UploadPanel from "./components/UploadPanel";
import SummaryCards from "./components/SummaryCards";
import AnomalyChart from "./components/AnomalyChart";
import TransactionsTable from "./components/TransactionsTable";

export default function App() {
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const [txns, summ] = await Promise.all([
        api.getTransactions(false),
        api.getSummary(),
      ]);
      setTransactions(txns);
      setSummary(summ);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <span className="eyebrow">Audit &amp; Advisory / Document Review</span>
          <h1>Financial Document Intelligence</h1>
        </div>
        <span className="tagline">OCR extraction · duplicate &amp; outlier detection · policy checks</span>
      </header>

      <UploadPanel onUploaded={refresh} />

      {loading ? (
        <div className="empty-state">Loading...</div>
      ) : (
        <>
          <SummaryCards summary={summary} />
          <div className="dashboard-body">
            <TransactionsTable transactions={transactions} onChange={refresh} />
            <AnomalyChart summary={summary} transactions={transactions} />
          </div>
        </>
      )}
    </div>
  );
}
