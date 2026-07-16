import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
  Legend,
} from "recharts";

const COLORS = {
  Duplicates: "#b5751b",
  "Statistical outliers": "#9c3b2e",
  "Policy violations": "#5a3b9c",
};

export default function AnomalyChart({ summary, transactions }) {
  if (!summary) return null;

  const breakdown = [
    { name: "Duplicates", value: summary.duplicates },
    { name: "Statistical outliers", value: summary.statistical_outliers },
    { name: "Policy violations", value: summary.policy_violations },
  ];

  const categoryTotals = {};
  transactions.forEach((t) => {
    const cat = t.category || "uncategorized";
    categoryTotals[cat] = (categoryTotals[cat] || 0) + (t.amount || 0);
  });
  const categoryData = Object.entries(categoryTotals).map(([name, value]) => ({
    name,
    value: Math.round(value),
  }));

  const hasFlags = breakdown.some((b) => b.value > 0);

  return (
    <div className="chart-panel">
      <div className="section-title">Anomaly breakdown</div>
      {hasFlags ? (
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={breakdown.filter((b) => b.value > 0)}
              dataKey="value"
              nameKey="name"
              innerRadius={45}
              outerRadius={75}
              paddingAngle={3}
            >
              {breakdown
                .filter((b) => b.value > 0)
                .map((entry) => (
                  <Cell key={entry.name} fill={COLORS[entry.name]} />
                ))}
            </Pie>
            <Tooltip />
            <Legend
              layout="vertical"
              align="right"
              verticalAlign="middle"
              wrapperStyle={{ fontSize: 11, fontFamily: "IBM Plex Mono, monospace" }}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <div className="empty-state">No anomalies detected yet.</div>
      )}

      <div className="section-title" style={{ marginTop: 22 }}>
        Spend by category
      </div>
      {categoryData.length > 0 ? (
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={categoryData} layout="vertical" margin={{ left: 10 }}>
            <XAxis type="number" hide />
            <YAxis
              dataKey="name"
              type="category"
              width={100}
              tick={{ fontSize: 11, fontFamily: "IBM Plex Mono, monospace" }}
            />
            <Tooltip formatter={(v) => `₹${v.toLocaleString("en-IN")}`} />
            <Bar dataKey="value" fill="#1f2d3d" radius={[0, 3, 3, 0]} />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="empty-state">Upload documents to see category spend.</div>
      )}
    </div>
  );
}
