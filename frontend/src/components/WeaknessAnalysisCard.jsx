import React from "react";

const REMEDIAL_GUIDES = {
  "Data Structures & Algorithms": {
    memorization: "Review asymptotic time complexities (Big-O) in CLRS Chapter 3 and BST balance invariants (AVL/Red-Black).",
    application: "Practice memoization state transitions in Dynamic Programming (0/1 Knapsack, LCS) and Dijkstra edge relaxation steps.",
  },
  "Computer Networks": {
    memorization: "Memorize OSI/TCP-IP 5-layer header formats, standard port numbers, and CIDR subnet masking rules (Kurose & Ross).",
    application: "Solve TCP Tahoe/Reno congestion window calculations (ssthresh adjustments upon packet loss) and subnet host range problems.",
  },
  "Database Management Systems": {
    memorization: "Study ACID property definitions, transaction isolation anomalies (dirty/fuzzy/phantom reads), and 1NF to BCNF rules (Korth).",
    application: "Trace functional dependencies for 3NF/BCNF decomposition, B+ Tree split/merge traversals, and complex SQL joins.",
  },
  "Operating Systems": {
    memorization: "Review PCB state lifecycle, Coffman deadlock conditions, and page replacement policy definitions (Galvin & Gagne).",
    application: "Calculate SJF/Round Robin average turnaround & wait times, execute Banker's algorithm safety checks, and compute FIFO page faults (Belady's Anomaly).",
  },
  "Object-Oriented Programming": {
    memorization: "Review the 4 OOP pillars (Encapsulation, Abstraction, Inheritance, Polymorphism) and all 5 SOLID design principles (GoF).",
    application: "Trace dynamic method dispatch via vtables/vptrs, virtual destructor memory cleanup, and implement Observer/Factory patterns.",
  },
};


export default function WeaknessAnalysisCard({ gaps, onStartRemediation }) {
  if (!gaps || gaps.length === 0) {
    return (
      <div className="rounded-2xl border bg-white p-6 shadow-xs" style={{ borderColor: "#D8DED4" }}>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#E8F5E9] text-xl">
            🎉
          </div>
          <div>
            <h3 className="font-display text-lg font-semibold text-[#14231C]">
              No Critical Gaps Detected!
            </h3>
            <p className="font-body text-xs text-[#8B9A8C] mt-0.5">
              All tested concepts are above your 70% mastery threshold. Take a full diagnostic quiz to discover new areas to sharpen.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border bg-white p-6 shadow-xs" style={{ borderColor: "#D8DED4" }}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b pb-4" style={{ borderColor: "#D8DED4" }}>
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2.5 w-2.5 rounded-full bg-[#E2A73E]"></span>
            <h3 className="font-display text-xl font-semibold text-[#14231C]">
              Diagnosed Concept Weaknesses ({gaps.length})
            </h3>
          </div>
          <p className="font-body text-xs text-[#8B9A8C] mt-1">
            Specific branches where accuracy is below the 70% mastery benchmark.
          </p>
        </div>

        <button
          type="button"
          onClick={onStartRemediation}
          className="inline-flex items-center justify-center gap-2 rounded-full px-5 py-2.5 text-xs font-semibold text-white shadow-xs transition hover:opacity-90"
          style={{ background: "#2F6B4F" }}
        >
          <span>⚡ Launch Adaptive Remediation</span>
        </button>
      </div>

      {/* Weakness Cards Grid */}
      <div className="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {gaps.map((gap, index) => {
          const guide =
            (REMEDIAL_GUIDES[gap.topic] && REMEDIAL_GUIDES[gap.topic][gap.skill_type]) ||
            "Review course lecture notes and complete focused practice questions.";

          const isCritical = gap.accuracy < 0.4;

          return (
            <div
              key={`${gap.topic}-${gap.subtopic}-${gap.skill_type}-${index}`}
              className="flex flex-col justify-between rounded-xl border p-4.5 bg-[#FFFDF9] transition-all hover:shadow-xs"
              style={{ borderColor: "#F3D6B5" }}
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="font-mono text-[10px] uppercase tracking-wider text-[#B45309] font-bold">
                      {gap.topic}
                    </span>
                    <h4 className="font-display text-base font-semibold text-[#14231C] mt-0.5">
                      {gap.subtopic}
                    </h4>
                    <p className="text-xs text-[#8B9A8C] mt-0.5 capitalize">{gap.skill_type}</p>
                  </div>
                  <span
                    className="rounded-full px-2 py-0.5 text-[10px] font-mono font-semibold"
                    style={{
                      background: isCritical ? "#FEE2E2" : "#FEF3C7",
                      color: isCritical ? "#B91C1C" : "#B45309",
                    }}
                  >
                    {isCritical ? "Critical Gap" : "Needs Review"}
                  </span>
                </div>

                {/* Accuracy progress bar */}
                <div className="mt-3">
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="text-[#8B9A8C]">Accuracy:</span>
                    <span className="font-bold text-[#B45309]">
                      {Math.round(gap.accuracy * 100)}% ({gap.correct}/{gap.attempted} correct)
                    </span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-[#E5E7EB] overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.max(gap.accuracy * 100, 8)}%`,
                        background: isCritical ? "#EF4444" : "#E2A73E",
                      }}
                    />
                  </div>
                </div>

                {/* AI Prescription Note */}
                <div className="mt-3.5 rounded-lg bg-white p-3 border border-[#F3D6B5] text-xs font-body text-[#3D4A40] leading-relaxed">
                  <span className="font-semibold text-[#14231C] block mb-1">💡 Remedial Suggestion:</span>
                  {guide}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-[#F3D6B5] flex justify-end">
                <button
                  type="button"
                  onClick={() => onStartRemediation(gap.topic, gap.tag_id)}
                  className="text-xs font-semibold text-[#2F6B4F] hover:underline flex items-center gap-1"
                >
                  Practice this tag →
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
