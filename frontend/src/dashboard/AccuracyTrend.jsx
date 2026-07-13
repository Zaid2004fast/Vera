import { useEffect, useState } from "react";
import axios from "axios";
import API_BASE from "../api";
import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

export default function AccuracyTrend() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get(`${API_BASE}/metrics/accuracy`).then(r => setData(r.data));
  }, []);

  return (
    <div style={{
      background: "#fff", borderRadius: 12,
      border: "1px solid #e8e8e8", padding: "1.5rem", marginBottom: 16
    }}>
      <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 3 }}>Accuracy over time</div>
      <div style={{ fontSize: 13, color: "#aaa", marginBottom: 20 }}>
        Populated nightly by the Auditor. After your first audit run this chart will show VERA improving.
      </div>

      {data.length === 0 ? (
        <div style={{
          height: 200, display: "flex", alignItems: "center",
          justifyContent: "center", background: "#f8f9fb",
          borderRadius: 10, border: "1px dashed #e4e4e4",
          flexDirection: "column", gap: 8, color: "#ccc"
        }}>
          <div style={{ fontSize: 32 }}>📈</div>
          <div style={{ fontSize: 14 }}>No audit data yet</div>
          <div style={{ fontSize: 12 }}>Run the Auditor once and this chart populates automatically</div>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} />
            <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v, name) => [
              `${v}%`,
              name === "accuracy" ? "Benchmark accuracy" : "Avg confidence"
            ]} />
            <Legend />
            <Line type="monotone" dataKey="accuracy"       name="accuracy"
                  stroke="#5B6EFF" strokeWidth={2.5} dot={{ r: 5 }} activeDot={{ r: 7 }} />
            <Line type="monotone" dataKey="avg_confidence" name="avg_confidence"
                  stroke="#1DB8A2" strokeWidth={2} strokeDasharray="5 4" dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}