import { useState } from "react";
import {
  Send,
  Zap,
  Search,
  GitBranch,
  Database,
  Activity,
} from "lucide-react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    setLoading(true);
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8000/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: "demo123",
          text: message.trim(),
        }),
      });

      if (!res.ok) {
        throw new Error(`Backend returned ${res.status}`);
      }

      const data = await res.json();

      console.log("Backend response:", data);

      setResponse(data);
      setMessage("");
    } catch (err) {
      console.error("StreamFuse error:", err);
      setError("Could not connect to the StreamFuse backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      {/* HEADER */}
      <header className="header">
        <div>
          <div className="logo">
            <Zap size={22} />
            StreamFuse
          </div>

          <div className="subtitle">Streaming Live RAG</div>
        </div>

        <div className="session">
          <span className="status-dot"></span>
          SESSION: demo123
        </div>
      </header>

      <main className="main-layout">
        {/* LEFT — CONVERSATION */}
        <section className="chat-panel">
          <div className="panel-title">
            <div>
              <h2>Conversation</h2>
              <span>Live session</span>
            </div>
          </div>

          <div className="messages">
            {!response && !error && (
              <div className="empty-state">
                <Zap size={40} />

                <h3>Ready for a live RAG query</h3>

                <p>
                  Ask something and watch StreamFuse decide whether to
                  wait, retrieve, or suppress retrieval.
                </p>
              </div>
            )}

            {response && (
              <div className="response-box">
                <div className="user-message">
                  <span className="message-label">YOU</span>
                  <p>{response.query || "Query submitted"}</p>
                </div>

                <div className="answer-message">
                  <span className="message-label">STREAMFUSE</span>
                  <p>
                    {response.answer || "No answer returned."}
                  </p>
                </div>

                {response.refinement && (
                  <div className="refinement">
                    <GitBranch size={16} />
                    Answer refined from a previous version
                  </div>
                )}
              </div>
            )}

            {error && (
              <div className="error-message">
                <strong>Connection error</strong>
                <p>{error}</p>
                <small>
                  Make sure the backend is running at
                  {" "}
                  http://127.0.0.1:8000
                </small>
              </div>
            )}
          </div>

          {/* INPUT */}
          <div className="input-area">
            <input
              type="text"
              placeholder="Ask StreamFuse something..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            <button
              onClick={sendMessage}
              disabled={loading || !message.trim()}
            >
              <Send size={18} />

              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </section>

        {/* RIGHT — ENGINEERING TRACE */}
        <aside className="trace-panel">
          {/* DECISION */}
          <div className="trace-card decision-card">
            <div className="card-heading">
              <span>RETRIEVAL DECISION</span>
              <Activity size={17} />
            </div>

            <div
              className={`decision ${
                response?.decision
                  ? response.decision.toLowerCase()
                  : "wait"
              }`}
            >
              {response?.decision || "WAIT"}
            </div>

            <div className="pipeline">
              <span
                className={
                  response?.decision === "WAIT" ? "active" : ""
                }
              >
                WAIT
              </span>

              <span>→</span>

              <span
                className={
                  response?.decision === "RETRIEVE" ? "active" : ""
                }
              >
                RETRIEVE
              </span>

              <span>→</span>

              <span>DECOMPOSE</span>

              <span>→</span>

              <span>FUSE</span>

              <span>→</span>

              <span>ANSWER</span>
            </div>
          </div>

          {/* SUBQUERIES */}
          <div className="trace-card">
            <div className="card-heading">
              <span>SUBQUERIES</span>
              <GitBranch size={17} />
            </div>

            {response?.subqueries?.length > 0 ? (
              <div className="subqueries">
                {response.subqueries.map((subquery, index) => (
                  <div className="subquery" key={index}>
                    <span>{index + 1}</span>
                    <p>{subquery}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="placeholder">
                <Search size={18} />
                <span>Waiting for retrieval...</span>
              </div>
            )}
          </div>

          {/* SOURCES */}
          <div className="trace-card">
            <div className="card-heading">
              <span>SOURCES</span>
              <Database size={17} />
            </div>

            {response?.citations?.length > 0 ? (
              <div className="sources">
                {response.citations.map((citation, index) => (
                  <div className="source" key={index}>
                    <Database size={15} />
                    <span>{citation}</span>
                  </div>
                ))}
              </div>
            ) : response?.evidence?.length > 0 ? (
              <div className="sources">
                {response.evidence.map((item, index) => (
                  <div className="source" key={index}>
                    <Database size={15} />
                    <span>
                      {typeof item === "string"
                        ? item
                        : item.title ||
                          item.source ||
                          `Evidence ${index + 1}`}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="placeholder">
                <Database size={18} />
                <span>No evidence retrieved yet</span>
              </div>
            )}
          </div>

          {/* TELEMETRY */}
          <div className="trace-card">
            <div className="card-heading">
              <span>TELEMETRY</span>
              <Activity size={17} />
            </div>

            <div className="metrics">
              <div>
                <span>Retrieval latency</span>

                <strong>
                  {response?.metrics?.retrieval_ms != null
                    ? `${response.metrics.retrieval_ms} ms`
                    : "—"}
                </strong>
              </div>

              <div>
                <span>Total latency</span>

                <strong>
                  {response?.metrics?.total_ms != null
                    ? `${response.metrics.total_ms} ms`
                    : "—"}
                </strong>
              </div>

              <div>
                <span>Answer version</span>

                <strong>
                  {response?.version != null
                    ? `v${response.version}`
                    : "v—"}
                </strong>
              </div>
            </div>

            {/* REFINEMENT */}
            {response?.refinement && (
              <div className="version-flow">
                <span>v{Math.max((response.version || 2) - 1, 1)}</span>

                <span>→</span>

                <strong>v{response.version}</strong>
              </div>
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;