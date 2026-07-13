import { useEffect, useState } from "react";
import axios from "axios";
import API_BASE from "../api";

function Card({ label, value, sub, color }) {
  return (
    <div style={{
      background: "#fff", borderRadius: 12,
      border: "1px solid #e8e8e8",
      padding: "1.25rem 1.5rem", flex: 1, minWidth: 155
    }}>
      <div style={{ fontSize: 11, fontWeight: 600, color: "#aaa", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>
        {label}
      </div>
      <div style={{ fontSize: 30, fontWeight: 700, color, lineHeight: 1, marginBottom: 4 }}>
        {value}
      </div>
      <div style={{ fontSize: 12, color: "#bbb" }}>{sub}</div>
    </div>
  );
}

export default function SummaryStats() {
  const [s, setS] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE}/metrics/summary`).then(r => setS(r.data));
  }, []);

  if (!s) return <div style={{ color: "#ccc", fontSize: 14, marginBottom: 16 }}>Loading stats...</div>;

  return (
    <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
      <Card label="Total queries"      value={s.total_queries}   sub="questions answered"       color="#5B6EFF" />
      <Card label="Avg confidence"     value={`${s.avg_confidence}%`} sub="across all responses"
            color={s.avg_confidence >= 80 ? "#1DB8A2" : "#F5A623"} />
      <Card label="Review queue"       value={s.review_queue_size} sub="need human review"
            color={s.review_queue_size > 0 ? "#E24B4A" : "#1DB8A2"} />
      <Card label="Benchmark accuracy" value={s.latest_accuracy > 0 ? `${s.latest_accuracy}%` : "—"}
            sub={s.latest_accuracy > 0 ? "latest audit run" : "run auditor to populate"}
            color={s.latest_accuracy >= 80 ? "#1DB8A2" : "#ccc"} />
    </div>
  );
}