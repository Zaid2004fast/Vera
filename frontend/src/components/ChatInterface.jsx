import { useState, useRef, useEffect } from "react";
import axios from "axios";
import API_BASE from "../api";

function Badge({ children, color }) {
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, color,
      background: color + "18",
      border: `1px solid ${color}35`,
      borderRadius: 20, padding: "2px 9px",
      marginLeft: 7, whiteSpace: "nowrap"
    }}>{children}</span>
  );
}

function Message({ m }) {
  const isUser = m.role === "user";

  if (isUser) {
    return (
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <div style={{
          background: "#5B6EFF", color: "#fff",
          borderRadius: "14px 14px 3px 14px",
          padding: "10px 15px", maxWidth: "78%",
          fontSize: 14, lineHeight: 1.65
        }}>{m.text}</div>
      </div>
    );
  }

  const confColor = m.confidence >= 80
    ? "#1DB8A2" : m.confidence >= 60 ? "#F5A623" : "#E24B4A";

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start" }}>
      {/* Meta row */}
      <div style={{ display: "flex", alignItems: "center", marginBottom: 5 }}>
        <span style={{ fontSize: 12, fontWeight: 700, color: "#5B6EFF" }}>VERA</span>

        {m.blocked ? (
          <Badge color="#999">off-topic</Badge>
        ) : (
          <>
            <Badge color={confColor}>{m.confidence}% confident</Badge>
            {m.flagged && <Badge color="#E24B4A">⚑ review queue</Badge>}
            {m.criticFixed && <Badge color="#F5A623">critic fixed issues</Badge>}
          </>
        )}
      </div>

      {/* Answer bubble */}
      <div style={{
        background: "#fff",
        border: "1px solid #ebebeb",
        borderRadius: "3px 14px 14px 14px",
        padding: "11px 15px", maxWidth: "82%",
        fontSize: 14, lineHeight: 1.7, color: "#1a1a1a"
      }}>{m.text}</div>

      {/* Improvements row */}
      {!m.blocked && m.improvements?.length > 0 && (
        <div style={{
          marginTop: 5, fontSize: 12, color: "#999",
          background: "#fafafa", border: "1px solid #f0f0f0",
          borderRadius: 8, padding: "4px 10px", maxWidth: "82%"
        }}>
          <span style={{ color: "#F5A623", fontWeight: 600 }}>Critic improved: </span>
          {m.improvements.join(" · ")}
        </div>
      )}
    </div>
  );
}

export default function ChatInterface() {
  const [query, setQuery]     = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const q = query.trim();
    if (!q || loading) return;
    setQuery("");
    setMessages(p => [...p, { role: "user", text: q }]);
    setLoading(true);

    try {
      const { data } = await axios.post(`${API_BASE}/chat`, { query: q });
      setMessages(p => [...p, {
        role:        "vera",
        text:        data.answer,
        confidence:  data.confidence,
        flagged:     data.in_review_queue,
        blocked:     !data.is_cs_question,
        criticFixed: data.critic_found_issues,
        improvements: data.improvements_made,
      }]);
    } catch {
      setMessages(p => [...p, {
        role: "vera", text: "Cannot reach the VERA backend. Is the server running on port 8000?",
        confidence: 0, flagged: false, blocked: false, criticFixed: false, improvements: []
      }]);
    }
    setLoading(false);
  }

  const suggestions = [
    "What is a binary search tree?",
    "Explain deadlocks in OS",
    "What is database normalization?",
    "BFS vs DFS — when to use each?",
  ];

  return (
    <div>
      {/* Subtitle */}
      <p style={{ fontSize: 14, color: "#777", marginBottom: 16, lineHeight: 1.6 }}>
        Ask any CS interview question. VERA runs{" "}
        <strong style={{ color: "#5B6EFF" }}>Guard → Response → Critic → Synthesis</strong>{" "}
        and scores its own confidence on every answer.
      </p>

      {/* Message window */}
      <div style={{
        background: "#f9f9fb",
        border: "1px solid #e8e8e8",
        borderRadius: 14,
        minHeight: 400, maxHeight: 500,
        overflowY: "auto",
        padding: "1.25rem",
        marginBottom: 12,
        display: "flex", flexDirection: "column", gap: 14
      }}>
        {messages.length === 0 && (
          <div style={{ margin: "auto", textAlign: "center", color: "#ccc" }}>
            <div style={{ fontSize: 40, marginBottom: 10 }}>🧠</div>
            <div style={{ fontSize: 14 }}>Ask a CS interview question to get started</div>
            <div style={{
              display: "flex", flexWrap: "wrap", gap: 6,
              justifyContent: "center", marginTop: 16
            }}>
              {suggestions.map(s => (
                <button key={s} onClick={() => setQuery(s)} style={{
                  fontSize: 12, padding: "5px 12px",
                  borderRadius: 20, border: "1px solid #e0e0e0",
                  background: "#fff", color: "#555", cursor: "pointer"
                }}>{s}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => <Message key={i} m={m} />)}

        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: "#5B6EFF" }}>VERA</span>
            <div style={{
              background: "#fff", border: "1px solid #ebebeb",
              borderRadius: "3px 14px 14px 14px",
              padding: "10px 15px", fontSize: 13, color: "#aaa"
            }}>
              Running Guard → Response → Critic → Synthesis...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
          disabled={loading}
          placeholder="e.g. What is the difference between TCP and UDP?"
          style={{
            flex: 1, padding: "11px 15px",
            borderRadius: 10, fontSize: 14,
            border: "1px solid #e0e0e0",
            background: "#fff", outline: "none"
          }}
        />
        <button
          onClick={send}
          disabled={loading || !query.trim()}
          style={{
            padding: "11px 26px", borderRadius: 10,
            border: "none", fontSize: 14, fontWeight: 600,
            cursor: loading || !query.trim() ? "not-allowed" : "pointer",
            background: loading || !query.trim() ? "#c5caff" : "#5B6EFF",
            color: "#fff", transition: "background 0.15s"
          }}
        >
          {loading ? "..." : "Ask"}
        </button>
      </div>
    </div>
  );
}