import { useEffect, useState } from "react";
import { apiRequest, clearAccessToken } from "../lib/api";
import KnowledgeTreeMap from "../components/KnowledgeTreeMap";
import WeaknessAnalysisCard from "../components/WeaknessAnalysisCard";
import QuizPlayer from "../components/QuizPlayer";
import ModulesView from "../components/ModulesView";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [matrix, setMatrix] = useState(null);
  const [activeTab, setActiveTab] = useState("weakness"); // 'weakness' | 'modules' | 'questions'
  const [questionsList, setQuestionsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Quiz Launcher State
  const [quizConfigModal, setQuizConfigModal] = useState(null); // { type: 'general' | 'topic' | 'remediation' | 'document', topic, documentId, docName }
  const [selectedQuestionCount, setSelectedQuestionCount] = useState(10);
  const [activeQuizSession, setActiveQuizSession] = useState(null); // { session_id, questions, is_adaptive }
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizError, setQuizError] = useState("");

  useEffect(() => {
    loadDashboardData();
  }, []);

  async function loadDashboardData() {
    setLoading(true);
    setError("");
    try {
      const [currentUser, diagnosticMatrix] = await Promise.all([
        apiRequest("/api/auth/me"),
        apiRequest("/api/diagnostics/matrix"),
      ]);
      setUser(currentUser);
      setMatrix(diagnosticMatrix);
    } catch (requestError) {
      clearAccessToken();
      setError(requestError.message || "Please log in to continue.");
    } finally {
      setLoading(false);
    }
  }

  async function loadQuestions() {
    try {
      const data = await apiRequest("/api/questions");
      setQuestionsList(data || []);
    } catch (err) {
      console.error("Failed to load question bank:", err);
    }
  }

  useEffect(() => {
    if (activeTab === "questions" && questionsList.length === 0) {
      loadQuestions();
    }
  }, [activeTab]);

  function logOut() {
    clearAccessToken();
    window.location.href = "/login";
  }

  // Quiz Opener Helpers with Count Selection Modal
  function openQuizConfig(type, options = {}) {
    setSelectedQuestionCount(options.defaultCount || 10);
    setQuizConfigModal({
      type,
      topic: options.topic || null,
      documentId: options.documentId || null,
      docName: options.docName || null,
    });
  }

  async function launchConfiguredQuiz() {
    if (!quizConfigModal) return;
    const { type, topic, documentId } = quizConfigModal;
    const count = Math.min(Math.max(Number(selectedQuestionCount) || 10, 1), 20);

    setQuizLoading(true);
    setQuizError("");

    try {
      if (type === "remediation") {
        const data = await apiRequest(`/api/diagnostics/adaptive-quiz?count=${count}`, { method: "POST" });
        setActiveQuizSession({
          session_id: data.session_id,
          questions: data.questions,
          is_adaptive: true,
        });
      } else if (type === "document") {
        const data = await apiRequest(`/api/quiz/start?document_id=${documentId}&count=${count}`, { method: "POST" });
        setActiveQuizSession({
          session_id: data.session_id,
          questions: data.questions,
          is_adaptive: false,
        });
      } else {
        // general diagnostic or topic-filtered quiz
        const url = topic
          ? `/api/quiz/start?topic=${encodeURIComponent(topic)}&count=${count}`
          : `/api/quiz/start?count=${count}`;
        const data = await apiRequest(url, { method: "POST" });
        setActiveQuizSession({
          session_id: data.session_id,
          questions: data.questions,
          is_adaptive: false,
        });
      }
      setQuizConfigModal(null);
    } catch (err) {
      setQuizError(err.message || "Could not launch quiz. Please try again.");
    } finally {
      setQuizLoading(false);
    }
  }

  if (loading) {
    return (
      <main
        className="flex min-h-screen items-center justify-center font-body text-sm"
        style={{ background: "#F7F8F4", color: "#14231C" }}
      >
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-3 border-[#2F6B4F] border-t-transparent"></div>
          <span className="font-mono text-xs text-[#8B9A8C]">Loading your placement profile...</span>
        </div>
      </main>
    );
  }

  if (error || !user) {
    return (
      <main
        className="flex min-h-screen items-center justify-center px-6 font-body"
        style={{ background: "#F7F8F4", color: "#14231C" }}
      >
        <div className="w-full max-w-sm text-center">
          <h1 className="font-display text-3xl font-semibold">Your session has ended</h1>
          <p className="mt-3 text-sm text-[#8B9A8C]">{error}</p>
          <a
            href="/login"
            className="mt-8 inline-block rounded-full px-6 py-3 text-sm font-semibold text-white shadow-xs"
            style={{ background: "#2F6B4F" }}
          >
            Log in again
          </a>
        </div>
      </main>
    );
  }

  const cells = matrix?.cells || [];
  const gaps = cells.filter((cell) => cell.is_gap);
  const totalAttempted = cells.reduce((sum, c) => sum + (c.attempted || 0), 0);
  const totalCorrect = cells.reduce((sum, c) => sum + (c.correct || 0), 0);
  const overallAccuracy = totalAttempted > 0 ? Math.round((totalCorrect / totalAttempted) * 100) : 0;
  const masteredCount = cells.filter((c) => !c.is_gap).length;

  return (
    <div className="min-h-screen font-body flex flex-col" style={{ background: "#F7F8F4", color: "#14231C" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
        .font-display { font-family: 'Fraunces', serif; font-optical-sizing: auto; }
        .font-body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'IBM Plex Mono', monospace; }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fadeIn 0.25s ease-out forwards; }
      `}</style>

      {/* Top Header */}
      <header
        className="sticky top-0 z-30 border-b backdrop-blur-md"
        style={{ borderColor: "#D8DED4", background: "rgba(247, 248, 244, 0.88)" }}
      >
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <a href="/" className="flex items-center gap-2.5">
            <div
              className="flex h-8 w-8 items-center justify-center rounded-xl"
              style={{ background: "#14231C" }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="6" r="3" fill="#2F6B4F" />
                <circle cx="6" cy="18" r="2.5" fill="#E2A73E" />
                <circle cx="18" cy="18" r="2.5" fill="#2F6B4F" />
                <path
                  d="M12 9V13M12 13L6 15.5M12 13L18 15.5"
                  stroke="#8B9A8C"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                />
              </svg>
            </div>
            <span className="font-display text-lg font-semibold tracking-tight">CogniTree</span>
          </a>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 rounded-full border border-[#D8DED4] bg-white px-3 py-1 text-xs">
              <span className="h-2 w-2 rounded-full bg-[#2F6B4F]"></span>
              <span className="font-medium text-[#14231C]">
                {user.full_name || user.email.split("@")[0]}
              </span>
              <span className="font-mono text-[10px] text-[#8B9A8C] uppercase">
                {user.is_teacher ? "Teacher" : "Student"}
              </span>
            </div>

            <button
              type="button"
              onClick={logOut}
              className="text-xs font-semibold text-[#8B9A8C] hover:text-[#14231C] transition"
            >
              Log out
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="mx-auto max-w-6xl w-full px-6 py-8 flex-1">
        {/* Error notification if quiz fails to launch */}
        {quizError && (
          <div className="mb-6 rounded-xl border border-[#FECACA] bg-[#FEF2F2] p-4 text-xs font-medium text-[#991B1B] flex items-center justify-between">
            <span>⚠️ {quizError}</span>
            <button
              type="button"
              onClick={() => setQuizError("")}
              className="text-xs font-bold"
            >
              ✕
            </button>
          </div>
        )}

        {/* Hero Section & Quick Actions */}
        <section className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b pb-8" style={{ borderColor: "#D8DED4" }}>
          <div>
            <span className="font-mono text-xs uppercase tracking-wider text-[#8B9A8C]">
              Placement Preparation & Concept Tracker
            </span>
            <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight text-[#14231C] mt-1">
              Welcome, {user.full_name || "Student"}.
            </h1>
            <p className="mt-2 max-w-xl text-xs sm:text-sm text-[#3D4A40] leading-relaxed">
              Track mastery across core placement subjects (DSA, Computer Networks, DBMS, OS, OOPs). Take tests to diagnose exact gaps, then launch adaptive remediation.
            </p>
          </div>

          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3">
            {gaps.length > 0 && (
              <button
                type="button"
                disabled={quizLoading}
                onClick={() => openQuizConfig("remediation", { defaultCount: 10 })}
                className="flex items-center gap-2 rounded-full px-5 py-3 text-xs font-semibold text-white shadow-sm transition hover:opacity-95 disabled:opacity-60"
                style={{ background: "#B45309" }}
              >
                <span>⚡ Remediation Quiz ({gaps.length} Gaps)</span>
              </button>
            )}

            <button
              type="button"
              disabled={quizLoading}
              onClick={() => openQuizConfig("general", { defaultCount: 10 })}
              className="flex items-center gap-2 rounded-full px-5 py-3 text-xs font-semibold text-white shadow-sm transition hover:opacity-95 disabled:opacity-60"
              style={{ background: "#2F6B4F" }}
            >
              <span>{quizLoading ? "Loading..." : "🎯 Start Diagnostic Quiz"}</span>
            </button>
          </div>
        </section>

        {/* Top Summary Metrics */}
        <section className="mt-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="rounded-2xl border bg-white p-5 shadow-xs" style={{ borderColor: "#D8DED4" }}>
            <span className="font-mono text-[11px] uppercase tracking-wider text-[#8B9A8C]">
              Overall Accuracy
            </span>
            <p className="font-display text-3xl font-semibold text-[#14231C] mt-2">
              {totalAttempted > 0 ? `${overallAccuracy}%` : "—"}
            </p>
            <span className="font-mono text-[10px] text-[#8B9A8C] mt-1 block">
              {totalCorrect}/{totalAttempted} correct
            </span>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-xs" style={{ borderColor: "#D8DED4" }}>
            <span className="font-mono text-[11px] uppercase tracking-wider text-[#B45309] font-bold">
              Diagnosed Weaknesses
            </span>
            <p className="font-display text-3xl font-semibold text-[#B45309] mt-2">
              {gaps.length}
            </p>
            <span className="font-mono text-[10px] text-[#8B9A8C] mt-1 block">
              Below 70% threshold
            </span>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-xs" style={{ borderColor: "#D8DED4" }}>
            <span className="font-mono text-[11px] uppercase tracking-wider text-[#2F6B4F] font-bold">
              Mastered Concepts
            </span>
            <p className="font-display text-3xl font-semibold text-[#2F6B4F] mt-2">
              {masteredCount}
            </p>
            <span className="font-mono text-[10px] text-[#8B9A8C] mt-1 block">
              &ge; 70% accuracy
            </span>
          </div>

          <div className="rounded-2xl border bg-white p-5 shadow-xs" style={{ borderColor: "#D8DED4" }}>
            <span className="font-mono text-[11px] uppercase tracking-wider text-[#8B9A8C]">
              Branches Mapped
            </span>
            <p className="font-display text-3xl font-semibold text-[#14231C] mt-2">
              {cells.length}
            </p>
            <span className="font-mono text-[10px] text-[#8B9A8C] mt-1 block">
              Placement skill pairs
            </span>
          </div>
        </section>

        {/* Tab Navigation */}
        <section className="mt-8 border-b" style={{ borderColor: "#D8DED4" }}>
          <div className="flex gap-8">
            <button
              type="button"
              onClick={() => setActiveTab("weakness")}
              className={`pb-3 text-sm font-semibold transition border-b-2 ${
                activeTab === "weakness"
                  ? "border-[#2F6B4F] text-[#2F6B4F]"
                  : "border-transparent text-[#8B9A8C] hover:text-[#14231C]"
              }`}
            >
              🌿 Concept Weakness & Tree Map
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("modules")}
              className={`pb-3 text-sm font-semibold transition border-b-2 ${
                activeTab === "modules"
                  ? "border-[#2F6B4F] text-[#2F6B4F]"
                  : "border-transparent text-[#8B9A8C] hover:text-[#14231C]"
              }`}
            >
              📚 Learning Modules & Document Ingestion
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("questions")}
              className={`pb-3 text-sm font-semibold transition border-b-2 ${
                activeTab === "questions"
                  ? "border-[#2F6B4F] text-[#2F6B4F]"
                  : "border-transparent text-[#8B9A8C] hover:text-[#14231C]"
              }`}
            >
              ❓ Placement Question Bank ({questionsList.length})
            </button>
          </div>
        </section>

        {/* Tab 1: Weakness & Concept Diagnostics */}
        {activeTab === "weakness" && (
          <div className="mt-8 space-y-8 animate-fade-in">
            {/* Visual Concept Tree */}
            <KnowledgeTreeMap
              cells={cells}
              onSelectTopic={(topic) => openQuizConfig("topic", { topic, defaultCount: 8 })}
            />

            {/* Weakness Breakdown Cards */}
            <WeaknessAnalysisCard
              gaps={gaps}
              onStartRemediation={(topic) =>
                topic
                  ? openQuizConfig("topic", { topic, defaultCount: 8 })
                  : openQuizConfig("remediation", { defaultCount: 10 })
              }
            />

            {/* 2D Topic x Skill Performance Grid */}
            <div className="rounded-2xl border bg-white p-6 shadow-xs" style={{ borderColor: "#D8DED4" }}>
              <div className="flex items-center justify-between border-b pb-4" style={{ borderColor: "#D8DED4" }}>
                <div>
                  <h3 className="font-display text-xl font-semibold text-[#14231C]">
                    Placement Topic &times; Cognitive Skill Matrix
                  </h3>
                  <p className="font-body text-xs text-[#8B9A8C] mt-1">
                    Live breakdown of student accuracy on definitions (memorization) vs problem solving (application).
                  </p>
                </div>
              </div>

              {cells.length === 0 ? (
                <div className="py-12 text-center text-sm text-[#8B9A8C]">
                  <p>No diagnostic test completed yet.</p>
                  <button
                    type="button"
                    onClick={() => openQuizConfig("general", { defaultCount: 10 })}
                    className="mt-4 rounded-full px-5 py-2.5 text-xs font-semibold text-white"
                    style={{ background: "#2F6B4F" }}
                  >
                    Take Your First Diagnostic Test →
                  </button>
                </div>
              ) : (
                <div className="mt-4 overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b text-[#8B9A8C] font-mono" style={{ borderColor: "#D8DED4" }}>
                        <th className="py-3 px-4">Subject Branch</th>
                        <th className="py-3 px-4">Cognitive Skill</th>
                        <th className="py-3 px-4">Attempts</th>
                        <th className="py-3 px-4">Accuracy</th>
                        <th className="py-3 px-4">Diagnostic Status</th>
                        <th className="py-3 px-4 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cells.map((cell) => (
                        <tr
                          key={`${cell.topic}-${cell.skill_type}`}
                          className="border-b transition hover:bg-[#F7F8F4]"
                          style={{ borderColor: "#D8DED4" }}
                        >
                          <td className="py-3.5 px-4 font-semibold text-[#14231C]">
                            {cell.topic}
                          </td>
                          <td className="py-3.5 px-4 capitalize font-mono text-[#3D4A40]">
                            {cell.skill_type}
                          </td>
                          <td className="py-3.5 px-4 font-mono text-[#8B9A8C]">
                            {cell.correct} / {cell.attempted}
                          </td>
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold">
                                {Math.round(cell.accuracy * 100)}%
                              </span>
                              <div className="h-1.5 w-16 rounded-full bg-[#E5E7EB] overflow-hidden">
                                <div
                                  className="h-full rounded-full"
                                  style={{
                                    width: `${Math.round(cell.accuracy * 100)}%`,
                                    background: cell.is_gap ? "#E2A73E" : "#2F6B4F",
                                  }}
                                />
                              </div>
                            </div>
                          </td>
                          <td className="py-3.5 px-4">
                            <span
                              className="rounded-full px-2.5 py-0.5 text-[10px] font-semibold"
                              style={{
                                background: cell.is_gap ? "#FEF3C7" : "#E8F5E9",
                                color: cell.is_gap ? "#B45309" : "#2F6B4F",
                              }}
                            >
                              {cell.is_gap ? "Weakness (Gap)" : "Mastered"}
                            </span>
                          </td>
                          <td className="py-3.5 px-4 text-right">
                            <button
                              type="button"
                              onClick={() => openQuizConfig("topic", { topic: cell.topic, defaultCount: 8 })}
                              className="text-xs font-semibold text-[#2F6B4F] hover:underline"
                            >
                              Practice →
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: Modules & Document Ingestion */}
        {activeTab === "modules" && (
          <div className="mt-8 animate-fade-in">
            <ModulesView
              onStartTopicQuiz={(topic) => openQuizConfig("topic", { topic, defaultCount: 8 })}
              onStartDocumentQuiz={(docId, docName) =>
                openQuizConfig("document", { documentId: docId, docName, defaultCount: 10 })
              }
              onUploadSuccess={() => loadDashboardData()}
            />
          </div>
        )}

        {/* Tab 3: Question Bank Explorer */}
        {activeTab === "questions" && (
          <div className="mt-8 rounded-2xl border bg-white p-6 shadow-xs animate-fade-in" style={{ borderColor: "#D8DED4" }}>
            <div className="flex items-center justify-between border-b pb-4" style={{ borderColor: "#D8DED4" }}>
              <div>
                <h3 className="font-display text-xl font-semibold text-[#14231C]">
                  Placement Question Bank ({questionsList.length})
                </h3>
                <p className="font-body text-xs text-[#8B9A8C] mt-1">
                  Validated schema placement questions mapped to standard reference books and cognitive skills.
                </p>
              </div>
            </div>

            {questionsList.length === 0 ? (
              <p className="py-8 text-center text-xs text-[#8B9A8C]">Loading question bank...</p>
            ) : (
              <div className="mt-6 space-y-4">
                {questionsList.map((q) => (
                  <div
                    key={q.id}
                    className="rounded-xl border p-4 bg-[#F7F8F4]"
                    style={{ borderColor: "#D8DED4" }}
                  >
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="rounded-md bg-white border border-[#D8DED4] px-2 py-0.5 text-xs font-semibold text-[#14231C]">
                          {q.topic}
                        </span>
                        <span className="text-xs text-[#8B9A8C]">{q.subtopic}</span>
                      </div>
                      <span className="font-mono text-[10px] uppercase tracking-wider rounded-full px-2 py-0.5 border border-[#D8DED4] text-[#8B9A8C]">
                        {q.skill_type}
                      </span>
                    </div>
                    <p className="font-display text-sm font-medium text-[#14231C]">
                      {q.question_text}
                    </p>
                    <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs text-[#3D4A40]">
                      {q.options.map((opt, i) => (
                        <div key={i} className="rounded-lg bg-white p-2 border border-[#E5E7EB]">
                          <span className="font-mono font-bold text-[#8B9A8C] mr-1.5">
                            {["A", "B", "C", "D"][i]}:
                          </span>
                          {opt}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Customizable Quiz Length & Configuration Modal (Max 20 questions) */}
      {quizConfigModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs font-body animate-fade-in">
          <div
            className="w-full max-w-md rounded-2xl bg-white shadow-2xl border p-6 overflow-hidden"
            style={{ borderColor: "#D8DED4" }}
          >
            <div className="flex items-center justify-between pb-3 border-b" style={{ borderColor: "#D8DED4" }}>
              <div className="flex items-center gap-2">
                <span className="text-xl">🎯</span>
                <h3 className="font-display text-lg font-semibold text-[#14231C]">
                  Configure Quiz Session
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setQuizConfigModal(null)}
                className="text-[#8B9A8C] hover:text-[#14231C] p-1"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-4">
              <div>
                <span className="text-xs font-mono text-[#8B9A8C] uppercase tracking-wider">Assessment Focus</span>
                <p className="font-semibold text-sm text-[#14231C] mt-0.5">
                  {quizConfigModal.type === "remediation" && "⚡ Adaptive Weakness Remediation"}
                  {quizConfigModal.type === "topic" && `📖 Subject Practice: ${quizConfigModal.topic}`}
                  {quizConfigModal.type === "document" && `📄 Document Assessment: ${quizConfigModal.docName || "Custom PDF"}`}
                  {quizConfigModal.type === "general" && "🎯 Full Placement Diagnostic Assessment"}
                </p>
              </div>

              {/* Question Count Selector (Max 20) */}
              <div className="pt-2">
                <div className="flex items-center justify-between mb-2">
                  <label htmlFor="q-count-input" className="text-xs font-semibold text-[#14231C]">
                    Select Number of Questions:
                  </label>
                  <span className="font-mono text-sm font-bold text-[#2F6B4F] bg-[#E8F5E9] px-2.5 py-0.5 rounded-full border border-[#86EFAC]">
                    {selectedQuestionCount} Questions
                  </span>
                </div>

                {/* Preset Chips */}
                <div className="grid grid-cols-4 gap-2 mb-3">
                  {[5, 10, 15, 20].map((num) => (
                    <button
                      key={num}
                      type="button"
                      onClick={() => setSelectedQuestionCount(num)}
                      className={`py-2 text-xs font-mono font-semibold rounded-xl border transition ${
                        selectedQuestionCount === num
                          ? "bg-[#2F6B4F] text-white border-[#2F6B4F] shadow-xs"
                          : "bg-[#F7F8F4] text-[#14231C] border-[#D8DED4] hover:border-[#2F6B4F]"
                      }`}
                    >
                      {num} Qs
                    </button>
                  ))}
                </div>

                {/* Slider (1 to 20) */}
                <input
                  id="q-count-input"
                  type="range"
                  min="1"
                  max="20"
                  value={selectedQuestionCount}
                  onChange={(e) => setSelectedQuestionCount(Number(e.target.value))}
                  className="w-full h-2 bg-[#E5E7EB] rounded-lg appearance-none cursor-pointer accent-[#2F6B4F]"
                />
                <div className="flex justify-between text-[10px] font-mono text-[#8B9A8C] mt-1">
                  <span>1 min</span>
                  <span>10 standard</span>
                  <span>20 max</span>
                </div>
              </div>

              <div className="rounded-xl bg-[#F7F8F4] p-3 text-xs text-[#3D4A40] border" style={{ borderColor: "#D8DED4" }}>
                💡 <span className="font-semibold">Exam Mode:</span> Correct answers and concept explanations will be detailed at the final completion review for wrong choices.
              </div>
            </div>

            <div className="mt-6 pt-3 border-t flex items-center justify-end gap-3" style={{ borderColor: "#D8DED4" }}>
              <button
                type="button"
                onClick={() => setQuizConfigModal(null)}
                className="px-4 py-2 text-xs font-semibold text-[#8B9A8C] hover:text-[#14231C]"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={quizLoading}
                onClick={launchConfiguredQuiz}
                className="rounded-full px-6 py-2.5 text-xs font-semibold text-white transition hover:opacity-90 shadow-xs"
                style={{ background: "#2F6B4F" }}
              >
                {quizLoading ? "Launching..." : `Start Quiz (${selectedQuestionCount} Questions) →`}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Quiz Player Modal */}
      {activeQuizSession && (
        <QuizPlayer
          sessionData={activeQuizSession}
          onClose={() => {
            setActiveQuizSession(null);
            loadDashboardData();
          }}
          onComplete={() => {
            loadDashboardData();
          }}
        />
      )}
    </div>
  );
}

