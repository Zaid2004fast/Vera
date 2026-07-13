import { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import SummaryStats from "./dashboard/SummaryStats";
import AccuracyTrend from "./dashboard/AccuracyTrend";
import ReviewQueue from "./components/ReviewQueue";

const TABS = ["Chat", "Dashboard", "Review Queue"];

export default function App() {
  const [tab, setTab] = useState("Chat");

  return (
    <div style={{ minHeight: "100vh" }}>

      {/* ── Top nav ── */}
      <div style={{
        background: "#fff",
        borderBottom: "1px solid #e8e8e8",
        padding: "0 2rem",
        position: "sticky", top: 0, zIndex: 10
      }}>
        <div style={{
          maxWidth: 860, margin: "0 auto",
          display: "flex", alignItems: "center",
          justifyContent: "space-between", height: 58
        }}>
          {/* Logo */}
          <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
            <span style={{ fontSize: 20, fontWeight: 700, color: "#5B6EFF" }}>VERA</span>
            <span style={{ fontSize: 12, color: "#999", letterSpacing: "0.01em" }}>
              Verified and Reliable AI
            </span>
          </div>

          {/* Tabs */}
          <div style={{ display: "flex", gap: 2 }}>
            {TABS.map(t => (
              <button key={t} onClick={() => setTab(t)} style={{
                padding: "6px 18px", borderRadius: 8, border: "none",
                cursor: "pointer", fontSize: 13, fontWeight: 500,
                background: tab === t ? "#5B6EFF" : "transparent",
                color: tab === t ? "#fff" : "#666",
                transition: "all 0.15s ease"
              }}>{t}</button>
            ))}
          </div>
        </div>
      </div>

      {/* ── Page content ── */}
      <div style={{ maxWidth: 860, margin: "0 auto", padding: "2rem 1.5rem" }}>
        {tab === "Chat"         && <ChatInterface />}
        {tab === "Dashboard"    && <><SummaryStats /><AccuracyTrend /></>}
        {tab === "Review Queue" && <ReviewQueue />}
      </div>
    </div>
  );
}