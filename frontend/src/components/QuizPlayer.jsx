import React, { useState, useEffect } from "react";
import { apiRequest } from "../lib/api";

export default function QuizPlayer({ sessionData, onClose, onComplete }) {
  const { session_id, questions = [], is_adaptive = false } = sessionData;

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({}); // { [question_id]: selected_index }
  const [questionStartTimes, setQuestionStartTimes] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [quizFinished, setQuizFinished] = useState(false);
  const [completionData, setCompletionData] = useState(null);
  const [reviewFilter, setReviewFilter] = useState("wrong"); // 'wrong' | 'all'
  const [error, setError] = useState("");

  const currentQuestion = questions[currentIndex];
  const selectedIndex = currentQuestion ? selectedAnswers[currentQuestion.id] ?? null : null;

  useEffect(() => {
    if (currentQuestion && !questionStartTimes[currentQuestion.id]) {
      setQuestionStartTimes((prev) => ({
        ...prev,
        [currentQuestion.id]: Date.now(),
      }));
    }
    setError("");
  }, [currentIndex, currentQuestion]);

  function handleSelectOption(index) {
    if (!currentQuestion || submitting) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: index,
    }));
    setError("");
  }

  async function handleNextOrFinish() {
    if (selectedIndex === null) {
      setError("Please select an answer to proceed.");
      return;
    }

    setSubmitting(true);
    setError("");

    const startTime = questionStartTimes[currentQuestion.id] || Date.now();
    const responseTimeMs = Date.now() - startTime;

    try {
      // Record answer on server
      await apiRequest(`/api/quiz/${session_id}/answer`, {
        method: "POST",
        body: JSON.stringify({
          question_id: currentQuestion.id,
          selected_index: selectedIndex,
          response_time_ms: responseTimeMs,
        }),
      });

      if (currentIndex + 1 < questions.length) {
        // Move to next question without revealing answer
        setCurrentIndex((prev) => prev + 1);
      } else {
        // Complete the quiz session and fetch final review data
        const summary = await apiRequest(`/api/quiz/${session_id}/complete`, {
          method: "POST",
        });
        setCompletionData(summary);
        setQuizFinished(true);
        if (onComplete) {
          onComplete();
        }
      }
    } catch (err) {
      setError(err.message || "Failed to submit answer. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  function handlePrevious() {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
      setError("");
    }
  }

  if (!currentQuestion && !quizFinished) {
    return null;
  }

  const reviews = completionData?.reviews || [];
  const wrongReviews = reviews.filter((r) => !r.is_correct);
  const displayReviews = reviewFilter === "wrong" ? wrongReviews : reviews;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/60 backdrop-blur-xs font-body animate-fade-in overflow-y-auto">
      <div
        className="w-full max-w-3xl rounded-2xl bg-white shadow-2xl border overflow-hidden my-auto max-h-[92vh] flex flex-col"
        style={{ borderColor: "#D8DED4" }}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b bg-[#F7F8F4] shrink-0" style={{ borderColor: "#D8DED4" }}>
          <div className="flex items-center gap-3">
            <span
              className="rounded-full px-3 py-1 text-xs font-mono font-semibold uppercase tracking-wider"
              style={{
                background: is_adaptive ? "#FEF3C7" : "#E8F5E9",
                color: is_adaptive ? "#B45309" : "#2F6B4F",
              }}
            >
              {is_adaptive ? "⚡ Adaptive Remediation" : "🎯 Diagnostic Assessment"}
            </span>
            {!quizFinished && (
              <span className="font-mono text-xs text-[#8B9A8C]">
                Question {currentIndex + 1} of {questions.length}
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-[#8B9A8C] hover:bg-white hover:text-[#14231C] transition"
            title="Close Quiz"
          >
            ✕
          </button>
        </div>

        {/* Progress Bar */}
        {!quizFinished && (
          <div className="h-1.5 w-full bg-[#EEF1EB] shrink-0">
            <div
              className="h-full transition-all duration-300"
              style={{
                width: `${((currentIndex + 1) / questions.length) * 100}%`,
                background: "#2F6B4F",
              }}
            />
          </div>
        )}

        {/* Main Body */}
        <div className="p-6 sm:p-8 overflow-y-auto flex-1">
          {quizFinished ? (
            /* =======================================================
               FINAL COMPLETION & WRONG ANSWER REVIEW SCREEN
               ======================================================= */
            <div className="space-y-6">
              <div className="text-center py-2 space-y-3">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[#E8F5E9] text-3xl">
                  📊
                </div>

                <div>
                  <h3 className="font-display text-2xl sm:text-3xl font-semibold text-[#14231C]">
                    Quiz Complete & Evaluated!
                  </h3>
                  <p className="font-body text-xs sm:text-sm text-[#8B9A8C] mt-1">
                    Your cognitive profile has been updated. Review incorrect answers below to close knowledge gaps.
                  </p>
                </div>

                {/* Score Summary Metrics */}
                <div className="grid grid-cols-3 gap-3 max-w-lg mx-auto p-4 rounded-xl bg-[#F7F8F4] border" style={{ borderColor: "#D8DED4" }}>
                  <div>
                    <p className="text-[10px] font-mono uppercase text-[#8B9A8C]">Score</p>
                    <p className="font-display text-2xl font-bold text-[#14231C] mt-0.5">
                      {completionData?.correct_count ?? 0} / {completionData?.total_questions ?? questions.length}
                    </p>
                  </div>
                  <div>
                    <p className="text-[10px] font-mono uppercase text-[#8B9A8C]">Accuracy</p>
                    <p className="font-display text-2xl font-bold text-[#2F6B4F] mt-0.5">
                      {completionData?.accuracy_percentage ?? 0}%
                    </p>
                  </div>
                  <div>
                    <p className="text-[10px] font-mono uppercase text-[#B45309]">Wrong Choices</p>
                    <p className="font-display text-2xl font-bold text-[#B45309] mt-0.5">
                      {wrongReviews.length}
                    </p>
                  </div>
                </div>
              </div>

              {/* Review Filter Tabs */}
              <div className="border-t pt-5" style={{ borderColor: "#D8DED4" }}>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                  <h4 className="font-display text-lg font-semibold text-[#14231C] flex items-center gap-2">
                    <span>🔍</span> Diagnostic Answer Review
                  </h4>

                  <div className="flex items-center gap-2 bg-[#F7F8F4] p-1 rounded-xl border" style={{ borderColor: "#D8DED4" }}>
                    <button
                      type="button"
                      onClick={() => setReviewFilter("wrong")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                        reviewFilter === "wrong"
                          ? "bg-white text-[#B45309] shadow-xs"
                          : "text-[#8B9A8C] hover:text-[#14231C]"
                      }`}
                    >
                      ❌ Wrong Answers ({wrongReviews.length})
                    </button>
                    <button
                      type="button"
                      onClick={() => setReviewFilter("all")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                        reviewFilter === "all"
                          ? "bg-white text-[#2F6B4F] shadow-xs"
                          : "text-[#8B9A8C] hover:text-[#14231C]"
                      }`}
                    >
                      📑 All Questions ({reviews.length})
                    </button>
                  </div>
                </div>

                {/* Question Review Cards List */}
                {displayReviews.length === 0 ? (
                  <div className="rounded-xl border border-[#BBF7D0] bg-[#F0FDF4] p-6 text-center text-sm text-[#166534]">
                    🎉 Outstanding! You had zero wrong answers in this quiz. All tested concepts scored 100%!
                  </div>
                ) : (
                  <div className="space-y-4 max-h-[420px] overflow-y-auto pr-1">
                    {displayReviews.map((rev, idx) => {
                      const isWrong = !rev.is_correct;
                      return (
                        <div
                          key={rev.question_id || idx}
                          className="rounded-xl border p-5 transition-all"
                          style={{
                            background: isWrong ? "#FFFDF9" : "#FFFFFF",
                            borderColor: isWrong ? "#F3D6B5" : "#D8DED4",
                          }}
                        >
                          {/* Card Header metadata */}
                          <div className="flex items-center justify-between gap-2 mb-2.5">
                            <div className="flex flex-wrap items-center gap-2">
                              <span
                                className="rounded-md px-2 py-0.5 text-[10px] font-mono font-bold uppercase"
                                style={{
                                  background: isWrong ? "#FEE2E2" : "#DCFCE7",
                                  color: isWrong ? "#991B1B" : "#166534",
                                }}
                              >
                                {isWrong ? "❌ Incorrect" : "✅ Correct"}
                              </span>
                              <span className="font-mono text-xs font-semibold text-[#14231C]">
                                {rev.topic}
                              </span>
                              <span className="text-xs text-[#8B9A8C]">• {rev.subtopic}</span>
                            </div>

                            <span className="font-mono text-[10px] uppercase tracking-wider text-[#8B9A8C]">
                              {rev.skill_type}
                            </span>
                          </div>

                          {/* Question Text */}
                          <p className="font-display text-sm font-medium text-[#14231C] leading-snug">
                            {rev.question_text}
                          </p>

                          {/* Options Grid */}
                          <div className="mt-3.5 space-y-2 text-xs">
                            {rev.options.map((opt, optIdx) => {
                              const isStudentChoice = rev.selected_index === optIdx;
                              const isCorrectOpt = rev.correct_index === optIdx;

                              let optStyle = "bg-white border-[#E5E7EB] text-[#3D4A40]";
                              let badge = null;

                              if (isCorrectOpt) {
                                optStyle = "bg-[#F0FDF4] border-[#86EFAC] text-[#166534] font-semibold";
                                badge = (
                                  <span className="ml-auto font-mono text-[10px] bg-[#22C55E] text-white px-2 py-0.5 rounded-md">
                                    Correct Answer
                                  </span>
                                );
                              } else if (isStudentChoice && isWrong) {
                                optStyle = "bg-[#FEF2F2] border-[#FCA5A5] text-[#991B1B] font-semibold";
                                badge = (
                                  <span className="ml-auto font-mono text-[10px] bg-[#EF4444] text-white px-2 py-0.5 rounded-md">
                                    Your Choice (Wrong)
                                  </span>
                                );
                              }

                              return (
                                <div
                                  key={optIdx}
                                  className={`flex items-center gap-3 rounded-lg border p-2.5 transition ${optStyle}`}
                                >
                                  <span className="font-mono font-bold shrink-0 w-5">
                                    {["A", "B", "C", "D"][optIdx] || optIdx + 1}:
                                  </span>
                                  <span className="flex-1">{opt}</span>
                                  {badge}
                                </div>
                              );
                            })}
                          </div>

                          {/* Detailed Concept Explanation */}
                          {rev.explanation && (
                            <div className="mt-3 rounded-lg bg-[#F7F8F4] p-3 border border-[#D8DED4] text-xs leading-relaxed text-[#3D4A40]">
                              <span className="font-semibold text-[#14231C] block mb-0.5">
                                💡 Concept Explanation & Key Takeaway:
                              </span>
                              {rev.explanation}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Bottom Action */}
              <div className="pt-4 border-t flex justify-end" style={{ borderColor: "#D8DED4" }}>
                <button
                  type="button"
                  onClick={onClose}
                  className="rounded-full px-7 py-3 text-xs font-semibold text-white shadow-xs transition hover:opacity-90"
                  style={{ background: "#2F6B4F" }}
                >
                  Return to Dashboard & Weakness Map →
                </button>
              </div>
            </div>
          ) : (
            /* =======================================================
               ACTIVE EXAM / QUIZ TAKING FORM (NO MID-QUIZ REVEALS)
               ======================================================= */
            <div className="space-y-6">
              {/* Question metadata badge */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs font-semibold px-2.5 py-1 rounded-md bg-[#EEF1EB] text-[#14231C]">
                  {currentQuestion.topic}
                </span>
                {currentQuestion.subtopic && (
                  <span className="font-body text-xs text-[#8B9A8C]">
                    • {currentQuestion.subtopic}
                  </span>
                )}
                <span className="ml-auto font-mono text-[11px] uppercase tracking-wider px-2 py-0.5 rounded-full border border-[#D8DED4] text-[#8B9A8C]">
                  {currentQuestion.skill_type}
                </span>
              </div>

              {/* Question Text */}
              <h2 className="font-display text-xl sm:text-2xl font-medium text-[#14231C] leading-snug">
                {currentQuestion.question_text}
              </h2>

              {/* Options List */}
              <div className="space-y-2.5 pt-2">
                {currentQuestion.options.map((option, index) => {
                  const isSelected = selectedIndex === index;

                  let borderClass = "border-[#D8DED4] hover:border-[#2F6B4F] bg-white text-[#14231C]";
                  let badgeBg = "bg-[#F7F8F4] text-[#14231C]";

                  if (isSelected) {
                    borderClass = "border-[#2F6B4F] bg-[#F4F9F6] ring-1.5 ring-[#2F6B4F]";
                    badgeBg = "bg-[#2F6B4F] text-white";
                  }

                  const optionLabels = ["A", "B", "C", "D"];

                  return (
                    <button
                      key={index}
                      type="button"
                      disabled={submitting}
                      onClick={() => handleSelectOption(index)}
                      className={`w-full text-left flex items-start gap-3 rounded-xl border p-4 transition-all duration-150 ${borderClass} cursor-pointer`}
                    >
                      <span
                        className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full font-mono text-xs font-semibold ${badgeBg}`}
                      >
                        {optionLabels[index] || index + 1}
                      </span>
                      <span className="font-body text-sm text-[#14231C] pt-0.5 leading-relaxed">
                        {option}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Error state */}
              {error && (
                <p role="alert" className="text-xs font-medium text-[#991B1B]">
                  ⚠️ {error}
                </p>
              )}

              {/* Action Buttons */}
              <div className="pt-4 border-t flex items-center justify-between" style={{ borderColor: "#D8DED4" }}>
                <div>
                  {currentIndex > 0 && (
                    <button
                      type="button"
                      disabled={submitting}
                      onClick={handlePrevious}
                      className="text-xs font-semibold text-[#8B9A8C] hover:text-[#14231C] transition px-3 py-2"
                    >
                      ← Previous
                    </button>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-[11px] text-[#8B9A8C] font-mono hidden sm:inline">
                    {selectedIndex !== null ? "Answer chosen" : "Select an option"}
                  </span>

                  <button
                    type="button"
                    disabled={selectedIndex === null || submitting}
                    onClick={handleNextOrFinish}
                    className="flex items-center gap-2 rounded-full px-6 py-2.5 text-xs font-semibold text-white transition hover:opacity-90 disabled:opacity-40 shadow-xs"
                    style={{ background: "#2F6B4F" }}
                  >
                    <span>
                      {submitting
                        ? "Saving..."
                        : currentIndex + 1 < questions.length
                        ? "Next Question →"
                        : "Finish Quiz & See Results →"}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

