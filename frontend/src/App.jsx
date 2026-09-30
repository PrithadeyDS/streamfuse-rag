import { useState } from "react";
import {
  Send,
  Zap,
  Search,
  GitBranch,
  Database,
  Activity,
  LoaderCircle,
} from "lucide-react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userText = message.trim();

    setLoading(true);
    setError("");

    setMessages((prev) => [
      ...prev,
      {
        type: "user",
        text: userText,
      },
    ]);

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/stream",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            session_id: "demo123",
            text: userText,
          }),
        }
      );

      if (!res.ok) {
        throw new Error(
          `Backend returned ${res.status}`
        );
      }

      const data = await res.json();

      console.log(
        "StreamFuse backend response:",
        data
      );

      /*
       * Safely normalize backend arrays.
       * This prevents the UI from breaking if
       * the backend omits one of these fields.
       */

      const normalizedSubqueries =
        Array.isArray(data.subqueries)
          ? data.subqueries
          : [];

      const normalizedCitations =
        Array.isArray(data.citations)
          ? data.citations
          : [];

      const normalizedEvidence =
        Array.isArray(data.evidence)
          ? data.evidence
          : [];

      const normalizedResponse = {
        ...data,
        subqueries: normalizedSubqueries,
        citations: normalizedCitations,
        evidence: normalizedEvidence,
      };

      setResponse(normalizedResponse);

      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          text:
            data.answer ||
            "No answer returned.",
          refinement:
            Boolean(data.refinement),
          version: data.version || 1,
        },
      ]);

      setMessage("");
    } catch (err) {
      console.error(
        "StreamFuse error:",
        err
      );

      setError(
        "Could not connect to the StreamFuse backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  const getStatus = () => {
    if (loading) {
      return "PROCESSING";
    }

    if (error) {
      return "ERROR";
    }

    if (response) {
      return "LIVE";
    }

    return "IDLE";
  };

  const getEvidenceLabel = (item, index) => {
    if (typeof item === "string") {
      return item;
    }

    if (item && typeof item === "object") {
      return (
        item.title ||
        item.source ||
        item.name ||
        item.id ||
        `Evidence ${index + 1}`
      );
    }

    return `Evidence ${index + 1}`;
  };

  return (
    <div className="app">

      {/* ================= HEADER ================= */}

      <header className="header">

        <div>
          <div className="logo">
            <Zap size={22} />
            StreamFuse
          </div>

          <div className="subtitle">
            Streaming Live RAG
          </div>
        </div>

        <div className="session">

          <span
            className={`status-dot ${
              loading
                ? "processing-dot"
                : error
                ? "error-dot"
                : ""
            }`}
          />

          SESSION: demo123

        </div>

      </header>

      {/* ================= STATUS BAR ================= */}

      <div className="status-bar">

        <div className="status-label">

          {loading ? (
            <LoaderCircle
              size={15}
              className="spin"
            />
          ) : (
            <Activity size={15} />
          )}

          <span>
            SYSTEM STATUS
          </span>

        </div>

        <strong
          className={`system-status ${
            loading
              ? "processing"
              : error
              ? "failed"
              : response
              ? "live"
              : "idle"
          }`}
        >
          {getStatus()}
        </strong>

      </div>

      {/* ================= MAIN ================= */}

      <main className="main-layout">

        {/* ================= LEFT — CONVERSATION ================= */}

        <section className="chat-panel">

          <div className="panel-title">

            <div>
              <h2>
                Conversation
              </h2>

              <span>
                Live session
              </span>
            </div>

          </div>

          <div className="messages">

            {/* EMPTY STATE */}

            {messages.length === 0 &&
              !error && (
                <div className="empty-state">

                  <Zap size={40} />

                  <h3>
                    Ready for a live RAG query
                  </h3>

                  <p>
                    Ask something and watch
                    StreamFuse decide whether
                    to wait, retrieve, or
                    suppress retrieval.
                  </p>

                </div>
              )}

            {/* CONVERSATION */}

            {messages.length > 0 && (
              <div className="conversation">

                {messages.map(
                  (item, index) => (
                    <div
                      className={`message ${
                        item.type === "user"
                          ? "user-message"
                          : "assistant-message"
                      }`}
                      key={index}
                    >

                      <div className="message-label">

                        {item.type === "user"
                          ? "YOU"
                          : "STREAMFUSE"}

                      </div>

                      <p>
                        {item.text}
                      </p>

                      {item.refinement && (
                        <div className="refinement">

                          <GitBranch
                            size={15}
                          />

                          Refined answer · v
                          {item.version}

                        </div>
                      )}

                    </div>
                  )
                )}

                {/* PROCESSING */}

                {loading && (
                  <div className="message assistant-message">

                    <div className="message-label">
                      STREAMFUSE
                    </div>

                    <div className="thinking-row">

                      <LoaderCircle
                        size={16}
                        className="spin"
                      />

                      <p className="thinking">
                        Processing retrieval...
                      </p>

                    </div>

                  </div>
                )}

              </div>
            )}

            {/* ERROR */}

            {error && (
              <div className="error-message">

                <strong>
                  Connection error
                </strong>

                <p>
                  {error}
                </p>

                <small>
                  Make sure the backend is
                  running at{" "}
                  http://127.0.0.1:8000
                </small>

              </div>
            )}

          </div>

          {/* ================= INPUT ================= */}

          <div className="input-area">

            <input
              type="text"
              placeholder="Ask StreamFuse something..."
              value={message}
              onChange={(e) =>
                setMessage(e.target.value)
              }
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            <button
              onClick={sendMessage}
              disabled={
                loading ||
                !message.trim()
              }
            >

              {loading ? (
                <LoaderCircle
                  size={18}
                  className="spin"
                />
              ) : (
                <Send size={18} />
              )}

              {loading
                ? "Processing..."
                : "Send"}

            </button>

          </div>

        </section>

        {/* ================= RIGHT — ENGINEERING TRACE ================= */}

        <aside className="trace-panel">

          {/* RETRIEVAL DECISION */}

          <div className="trace-card decision-card">

            <div className="card-heading">

              <span>
                RETRIEVAL DECISION
              </span>

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
                  response?.decision === "WAIT"
                    ? "active"
                    : ""
                }
              >
                WAIT
              </span>

              <span>→</span>

              <span
                className={
                  response?.decision ===
                  "RETRIEVE"
                    ? "active"
                    : ""
                }
              >
                RETRIEVE
              </span>

              <span>→</span>

              <span
                className={
                  response?.subqueries
                    ?.length > 0
                    ? "active"
                    : ""
                }
              >
                DECOMPOSE
              </span>

              <span>→</span>

              <span
                className={
                  response?.evidence
                    ?.length > 0
                    ? "active"
                    : ""
                }
              >
                FUSE
              </span>

              <span>→</span>

              <span
                className={
                  response?.answer
                    ? "active"
                    : ""
                }
              >
                ANSWER
              </span>

            </div>

          </div>

          {/* SUBQUERIES */}

          <div className="trace-card">

            <div className="card-heading">

              <span>
                SUBQUERIES
              </span>

              <GitBranch size={17} />

            </div>

            {response?.subqueries
              ?.length > 0 ? (

              <div className="subqueries">

                {response.subqueries.map(
                  (subquery, index) => (

                    <div
                      className="subquery"
                      key={index}
                    >

                      <span>
                        {index + 1}
                      </span>

                      <p>
                        {typeof subquery ===
                        "string"
                          ? subquery
                          : getEvidenceLabel(
                              subquery,
                              index
                            )}
                      </p>

                    </div>

                  )
                )}

              </div>

            ) : (

              <div className="placeholder">

                <Search size={18} />

                <span>
                  Waiting for retrieval...
                </span>

              </div>

            )}

          </div>

          {/* SOURCES */}

          <div className="trace-card">

            <div className="card-heading">

              <span>
                SOURCES
              </span>

              <Database size={17} />

            </div>

            {response?.citations
              ?.length > 0 ? (

              <div className="sources">

                {response.citations.map(
                  (citation, index) => (

                    <div
                      className="source"
                      key={index}
                    >

                      <Database
                        size={15}
                      />

                      <span>
                        {getEvidenceLabel(
                          citation,
                          index
                        )}
                      </span>

                    </div>

                  )
                )}

              </div>

            ) : response?.evidence
                ?.length > 0 ? (

              <div className="sources">

                {response.evidence.map(
                  (item, index) => (

                    <div
                      className="source"
                      key={index}
                    >

                      <Database
                        size={15}
                      />

                      <span>
                        {getEvidenceLabel(
                          item,
                          index
                        )}
                      </span>

                    </div>

                  )
                )}

              </div>

            ) : (

              <div className="placeholder">

                <Database size={18} />

                <span>
                  No evidence retrieved yet
                </span>

              </div>

            )}

          </div>

          {/* TELEMETRY */}

          <div className="trace-card">

            <div className="card-heading">

              <span>
                TELEMETRY
              </span>

              <Activity size={17} />

            </div>

            <div className="metrics">

              <div>

                <span>
                  Retrieval latency
                </span>

                <strong>
                  {response?.metrics
                    ?.retrieval_ms != null
                    ? `${response.metrics.retrieval_ms} ms`
                    : "—"}
                </strong>

              </div>

              <div>

                <span>
                  Total latency
                </span>

                <strong>
                  {response?.metrics
                    ?.total_ms != null
                    ? `${response.metrics.total_ms} ms`
                    : "—"}
                </strong>

              </div>

              <div>

                <span>
                  Answer version
                </span>

                <strong>
                  {response?.version != null
                    ? `v${response.version}`
                    : "v—"}
                </strong>

              </div>

            </div>

            {/* REFINEMENT */}

            {response?.refinement ? (

              <div className="refinement-panel">

                <div className="refinement-header">

                  <GitBranch
                    size={15}
                  />

                  <span>
                    ANSWER REFINED
                  </span>

                </div>

                <div className="version-flow">

                  <span>
                    v
                    {Math.max(
                      (response.version ||
                        2) - 1,
                      1
                    )}
                  </span>

                  <span>
                    →
                  </span>

                  <strong>
                    v{response.version}
                  </strong>

                </div>

                <p>
                  Previous answer refined
                  using the latest user
                  detail.
                </p>

              </div>

            ) : (

              response && (
                <div className="version-flow">

                  <span>
                    Initial answer
                  </span>

                  <strong>
                    v
                    {response.version || 1}
                  </strong>

                </div>
              )

            )}

          </div>

        </aside>

      </main>

    </div>
  );
}

export default App;