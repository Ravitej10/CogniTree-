import React from "react";

export default function KnowledgeTreeMap({ cells, onSelectTopic }) {
  // Group cells by topic
  const topicMap = {};
  cells.forEach((cell) => {
    if (!topicMap[cell.topic]) {
      topicMap[cell.topic] = { memorization: null, application: null };
    }
    topicMap[cell.topic][cell.skill_type] = cell;
  });

  const allTopics = [
    { name: "Data Structures & Algorithms", icon: "💻", category: "Core CS (CLRS)" },
    { name: "Computer Networks", icon: "🌐", category: "Systems (Kurose & Ross)" },
    { name: "Database Management Systems", icon: "🗄️", category: "Databases (Korth)" },
    { name: "Operating Systems", icon: "⚙️", category: "Systems (Galvin)" },
    { name: "Object-Oriented Programming", icon: "🧩", category: "Design (GoF)" },
  ];


  return (
    <div className="rounded-2xl border bg-white p-6 shadow-xs" style={{ borderColor: "#D8DED4" }}>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b pb-4" style={{ borderColor: "#D8DED4" }}>
        <div>
          <h3 className="font-display text-xl font-semibold text-[#14231C] flex items-center gap-2">
            <span>🌿</span> Cognitive Concept Tree
          </h3>
          <p className="font-body text-xs text-[#8B9A8C] mt-1">
            Visual tree map separating memorization recall from practical problem-solving.
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs font-mono">
          <span className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full" style={{ background: "#2F6B4F" }}></span>
            Mastered (&ge;70%)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full" style={{ background: "#E2A73E" }}></span>
            Diagnosed Weakness
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-3 w-3 rounded-full" style={{ background: "#D8DED4" }}></span>
            Unmapped
          </span>
        </div>
      </div>

      {/* Tree Grid Cards */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {allTopics.map((topic) => {
          const data = topicMap[topic.name] || {};
          const mem = data.memorization;
          const app = data.application;

          const hasAnyData = mem || app;
          const hasGap = (mem && mem.is_gap) || (app && app.is_gap);
          const isAllMastered = hasAnyData && !hasGap && ((mem && !mem.is_gap) || (app && !app.is_gap));

          let statusBadgeColor = "#D8DED4";
          let statusText = "Not yet tested";
          if (hasGap) {
            statusBadgeColor = "#E2A73E";
            statusText = "Weakness Found";
          } else if (isAllMastered) {
            statusBadgeColor = "#2F6B4F";
            statusText = "Mastered";
          }

          return (
            <div
              key={topic.name}
              onClick={() => onSelectTopic && onSelectTopic(topic.name)}
              className="group cursor-pointer rounded-xl border p-4 transition-all duration-200 hover:shadow-md hover:border-[#2F6B4F] bg-[#F7F8F4]"
              style={{ borderColor: "#D8DED4" }}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="text-2xl">{topic.icon}</span>
                  <div>
                    <h4 className="font-display font-semibold text-sm text-[#14231C] group-hover:text-[#2F6B4F]">
                      {topic.name}
                    </h4>
                    <span className="font-body text-[11px] text-[#8B9A8C]">{topic.category}</span>
                  </div>
                </div>
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-mono font-semibold"
                  style={{
                    background: hasGap ? "#FEF3C7" : isAllMastered ? "#E8F5E9" : "#ECEFF1",
                    color: hasGap ? "#B45309" : isAllMastered ? "#2F6B4F" : "#546E7A",
                  }}
                >
                  {statusText}
                </span>
              </div>

              {/* Sub-branch status: Memorization vs Application */}
              <div className="mt-4 space-y-2 border-t pt-3" style={{ borderColor: "#D8DED4" }}>
                {/* Memorization */}
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-[#3D4A40] font-medium">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{
                        background: mem ? (mem.is_gap ? "#E2A73E" : "#2F6B4F") : "#D8DED4",
                      }}
                    ></span>
                    Memorization:
                  </span>
                  <span className="font-mono text-xs font-semibold">
                    {mem ? `${Math.round(mem.accuracy * 100)}% (${mem.correct}/${mem.attempted})` : "—"}
                  </span>
                </div>

                {/* Application */}
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-[#3D4A40] font-medium">
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{
                        background: app ? (app.is_gap ? "#E2A73E" : "#2F6B4F") : "#D8DED4",
                      }}
                    ></span>
                    Application:
                  </span>
                  <span className="font-mono text-xs font-semibold">
                    {app ? `${Math.round(app.accuracy * 100)}% (${app.correct}/${app.attempted})` : "—"}
                  </span>
                </div>
              </div>

              {/* Action */}
              <div className="mt-3 flex justify-end">
                <span className="text-[11px] font-semibold text-[#2F6B4F] group-hover:underline flex items-center gap-1">
                  Practice Topic →
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
