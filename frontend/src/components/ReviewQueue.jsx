import { useEffect, useState } from "react";
import axios from "axios";
import API_BASE from "../api";

export default function ReviewQueue() {
  const [items, setItems]     = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    axios.get(`${API_BASE}/review-queue`)
      .then(r => { setItems(r.data); setLoading(false); });
  };

  useEffect(() => { load(); }, []);

  async function verify(id) {
    await axios.post(`${API_BASE}/review-queue/${id}/verify`);
    setItems(p => p.filter(i => i.id !== id));
  }

  if (loading) return <div style={{ color: "#ccc", fontSize: 14 }}>Loading...</div>;

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>Human review queue</div>
        <div style={{ fontSize: 13, color: "#aaa" }}>
          Responses where VERA scored below 60% confidence. Review them and mark as verified.
        </div>
      </div>

      {items.length === 0 ? (
        <div style={{
          background: "#fff", borderRadius: 12,
          border: "1px solid #e8e8e8",
          padding: "3.5rem", textAlign: "center"
        }}>
          <div style={{ fontSize: 40, marginBottom: 10 }}>✅</div>
          <div style={{ fontSize: 15, fontWeight: 500, color: "#555" }}>Queue is empty</div>
          <div style={{ fontSize: 13, color: "#aaa", marginTop: 4 }}>
            All responses have been high confidence
          </div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {items.map(item => (
            <div key={item.id} style={{
              background: "#fff", borderRadius: 12,
              border: "1px solid #ffd4d4", padding: "1.25rem"
            }}>
              <div style={{
                display: "flex", justifyContent: "space-between",
                alignItems: "flex-start", marginBottom: 10, gap: 12
              }}>
                <div style={{ fontSize: 15, fontWeight: 500, flex: 1 }}>{item.query}</div>
                <span style={{
                  fontSize: 12, fontWeight: 700, color: "#E24B4A",
                  background: "#E24B4A15", border: "1px solid #E24B4A30",
                  borderRadius: 20, padding: "3px 10px", whiteSpace: "nowrap"
                }}>{item.confidence}% confident</span>
              </div>

              <div style={{
                fontSize: 13, color: "#555", lineHeight: 1.65,
                background: "#f8f9fb", borderRadius: 8,
                padding: "10px 14px", marginBottom: 12
              }}>{item.answer}</div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 12, color: "#ccc" }}>{item.timestamp}</span>
                <button onClick={() => verify(item.id)} style={{
                  padding: "7px 18px", borderRadius: 8,
                  border: "none", background: "#1DB8A2",
                  color: "#fff", cursor: "pointer",
                  fontSize: 13, fontWeight: 600
                }}>Mark verified ✓</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}