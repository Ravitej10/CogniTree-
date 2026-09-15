import React, { useState, useEffect } from "react";
import { apiRequest } from "../lib/api";

const MODULES_CATALOG = [
  {
    topic: "Data Structures & Algorithms",
    icon: "💻",
    book: "Introduction to Algorithms (CLRS) / Sedgewick",
    subtopics: [
      "Binary Search Trees & AVL Balance",
      "Dynamic Programming & Optimization",
      "Graph Algorithms & Shortest Path",
      "Heaps & Sorting Complexity",
    ],
    description: "Core algorithms, asymptotic complexity, balanced search trees, memoization patterns, and graph relaxations.",
    color: "#2F6B4F",
  },
  {
    topic: "Computer Networks",
    icon: "🌐",
    book: "Computer Networking: A Top-Down Approach (Kurose & Ross)",
    subtopics: [
      "OSI & TCP/IP Architecture",
      "TCP Handshake & Congestion Control",
      "IP Addressing & Subnetting",
      "Application Protocols: DNS & HTTP",
    ],
    description: "Network layer hierarchy, socket communication, flow control, TCP congestion algorithms, CIDR prefixes, and DNS resolution.",
    color: "#3B82F6",
  },
  {
    topic: "Database Management Systems",
    icon: "🗄️",
    book: "Database System Concepts (Silberschatz, Korth & Sudarshan)",
    subtopics: [
      "ACID Properties & Transactions",
      "Relational Normalization (1NF to BCNF)",
      "Indexing & B+ Trees",
      "SQL & Complex Joins",
    ],
    description: "Relational algebra, transactional isolation levels, write-ahead logging, B+ Tree fanout, and multi-table join optimization.",
    color: "#E2A73E",
  },
  {
    topic: "Operating Systems",
    icon: "⚙️",
    book: "Operating System Concepts (Silberschatz, Galvin & Gagne)",
    subtopics: [
      "Process Management & CPU Scheduling",
      "Synchronization & Concurrency",
      "Deadlock Characterization & Avoidance",
      "Virtual Memory & Page Replacement",
    ],
    description: "Kernel architecture, context switching, semaphores, critical section bounded waiting, Banker's algorithm, and TLB caching.",
    color: "#8B5CF6",
  },
  {
    topic: "Object-Oriented Programming",
    icon: "🧩",
    book: "Design Patterns (GoF) / Head First OOPS",
    subtopics: [
      "Core Pillars & Abstraction",
      "Polymorphism: Static vs Dynamic",
      "SOLID Principles",
      "GoF Design Patterns",
    ],
    description: "Object modeling, virtual method dispatch tables (vtables), single responsibility invariants, and creational/behavioral patterns.",
    color: "#10B981",
  },
];

export default function ModulesView({ onStartTopicQuiz, onStartDocumentQuiz, onUploadSuccess }) {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccessMsg, setUploadSuccessMsg] = useState("");
  const [generatingDocId, setGeneratingDocId] = useState(null);

  useEffect(() => {
    loadDocuments();
    // Poll for pending document updates every 3 seconds
    const interval = setInterval(() => {
      loadDocuments();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  async function loadDocuments() {
    try {
      const data = await apiRequest("/api/documents");
      setDocuments(data || []);
    } catch (err) {
      console.error("Failed to load documents:", err);
    }
  }

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadError("");
    setUploadSuccessMsg("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await apiRequest("/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      setUploadSuccessMsg(`"${file.name}" uploaded successfully! Chunking and indexing in background.`);
      loadDocuments();
      if (onUploadSuccess) onUploadSuccess(res);
    } catch (err) {
      setUploadError(err.message || "Failed to upload document.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleGenerateFromDoc(doc) {
    setGeneratingDocId(doc.id);
    setUploadError("");
    setUploadSuccessMsg("");
    try {
      const generated = await apiRequest(`/api/documents/${doc.id}/generate-questions?count=12`, {
        method: "POST",
      });
      setUploadSuccessMsg(
        `Generated ${generated.length} balanced questions across multiple concept tags from "${doc.filename}".`
      );
      if (onStartDocumentQuiz) {
        onStartDocumentQuiz(doc.id, doc.filename);
      }
    } catch (err) {
      setUploadError(err.message || "Failed to generate questions from document.");
    } finally {
      setGeneratingDocId(null);
    }
  }

  async function handleReingest(docId) {
    try {
      await apiRequest(`/api/documents/${docId}/reingest`, { method: "POST" });
      setUploadSuccessMsg("Re-ingestion triggered in background.");
      loadDocuments();
    } catch (err) {
      setUploadError(err.message || "Re-ingestion failed.");
    }
  }

  return (
    <div className="space-y-8 font-body">
      {/* Placement Catalog Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-display text-xl font-semibold text-[#14231C] flex items-center gap-2">
              <span>🎯</span> Placement Core Curriculum & Standard Books
            </h3>
            <p className="text-xs text-[#8B9A8C] mt-0.5">
              Targeted placement topics aligned with standard textbooks (CLRS, Kurose & Ross, Korth, Galvin, GoF).
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {MODULES_CATALOG.map((mod) => (
            <div
              key={mod.topic}
              className="flex flex-col justify-between rounded-2xl border bg-white p-5 shadow-xs transition hover:shadow-md hover:border-[#2F6B4F]"
              style={{ borderColor: "#D8DED4" }}
            >
              <div>
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#F7F8F4] text-2xl border border-[#D8DED4]">
                    {mod.icon}
                  </div>
                  <div>
                    <h4 className="font-display text-base font-semibold text-[#14231C]">
                      {mod.topic}
                    </h4>
                    <span className="font-mono text-[11px] text-[#2F6B4F] font-medium">
                      📖 {mod.book}
                    </span>
                  </div>
                </div>

                <p className="mt-3 text-xs text-[#3D4A40] leading-relaxed">
                  {mod.description}
                </p>

                {/* Subtopic tags */}
                <div className="mt-3.5 flex flex-wrap gap-1.5">
                  {mod.subtopics.map((sub) => (
                    <span
                      key={sub}
                      className="rounded-md bg-[#F7F8F4] px-2 py-0.5 text-[10px] font-medium text-[#3D4A40] border border-[#D8DED4]"
                    >
                      {sub}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-5 pt-3 border-t flex items-center justify-between" style={{ borderColor: "#D8DED4" }}>
                <span className="font-mono text-[10px] text-[#8B9A8C]">
                  {mod.subtopics.length} key concepts
                </span>
                <button
                  type="button"
                  onClick={() => onStartTopicQuiz(mod.topic)}
                  className="rounded-full px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:opacity-90 flex items-center gap-1.5"
                  style={{ background: "#2F6B4F" }}
                >
                  <span>Practice Subject</span>
                  <span>→</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Course Material Ingestion Section */}
      <div className="rounded-2xl border bg-white p-6 shadow-xs" style={{ borderColor: "#D8DED4" }}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b pb-4" style={{ borderColor: "#D8DED4" }}>
          <div>
            <h3 className="font-display text-lg font-semibold text-[#14231C] flex items-center gap-2">
              <span>📄</span> Custom Document Ingestion & Quiz Generator
            </h3>
            <p className="text-xs text-[#8B9A8C] mt-0.5">
              Upload textbook chapters, placement notes, or interview sheets (PDF/TXT) to parse, index, and generate grounded tests.
            </p>
          </div>

          <div>
            <label className="inline-flex cursor-pointer items-center gap-2 rounded-full px-5 py-2.5 text-xs font-semibold text-white transition hover:opacity-90 shadow-xs" style={{ background: "#2F6B4F" }}>
              <span>{uploading ? "Ingesting Document..." : "+ Upload Material (PDF/TXT)"}</span>
              <input
                type="file"
                accept=".pdf,.txt,.md"
                disabled={uploading}
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          </div>
        </div>

        {uploadSuccessMsg && (
          <div className="mt-4 rounded-xl border border-[#BBF7D0] bg-[#F0FDF4] p-3 text-xs text-[#166534] flex items-center justify-between">
            <span>✅ {uploadSuccessMsg}</span>
            <button type="button" onClick={() => setUploadSuccessMsg("")} className="font-bold">✕</button>
          </div>
        )}

        {uploadError && (
          <div className="mt-4 rounded-xl border border-[#FECACA] bg-[#FEF2F2] p-3 text-xs text-[#991B1B] flex items-center justify-between">
            <span>❌ {uploadError}</span>
            <button type="button" onClick={() => setUploadError("")} className="font-bold">✕</button>
          </div>
        )}

        {/* Ingested Documents List */}
        <div className="mt-5">
          <h4 className="font-mono text-xs uppercase tracking-wider text-[#8B9A8C] mb-3">
            Available Documents ({documents.length})
          </h4>

          {documents.length === 0 ? (
            <p className="text-xs text-[#8B9A8C] italic py-3">
              No custom documents uploaded yet. Upload a PDF above to generate custom topic quizzes!
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b text-[#8B9A8C] font-mono" style={{ borderColor: "#D8DED4" }}>
                    <th className="py-2.5 px-3">Document</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Indexed Chunks</th>
                    <th className="py-2.5 px-3">Uploaded Date</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => {
                    const isReady = doc.status?.toLowerCase() === "ready";
                    const isFailed = doc.status?.toLowerCase() === "failed";
                    const isProcessing = doc.status?.toLowerCase() === "processing" || doc.status?.toLowerCase() === "pending";

                    let statusBadge = (
                      <span className="rounded-full px-2.5 py-0.5 text-[10px] font-semibold bg-[#E8F5E9] text-[#2F6B4F] capitalize">
                        Ready
                      </span>
                    );
                    if (isProcessing) {
                      statusBadge = (
                        <span className="rounded-full px-2.5 py-0.5 text-[10px] font-semibold bg-[#FEF3C7] text-[#B45309] capitalize animate-pulse">
                          Processing...
                        </span>
                      );
                    } else if (isFailed) {
                      statusBadge = (
                        <span className="rounded-full px-2.5 py-0.5 text-[10px] font-semibold bg-[#FEE2E2] text-[#B91C1C] capitalize">
                          Failed
                        </span>
                      );
                    }

                    return (
                      <tr key={doc.id} className="border-b transition hover:bg-[#F7F8F4]" style={{ borderColor: "#D8DED4" }}>
                        <td className="py-3 px-3 font-medium text-[#14231C] flex items-center gap-2">
                          <span className="text-base">📄</span>
                          <span>{doc.filename}</span>
                        </td>
                        <td className="py-3 px-3">{statusBadge}</td>
                        <td className="py-3 px-3 font-mono text-[#3D4A40]">
                          {doc.chunk_count > 0 ? `${doc.chunk_count} chunks` : "—"}
                        </td>
                        <td className="py-3 px-3 text-[#8B9A8C] font-mono">
                          {new Date(doc.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-3 px-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            {isReady && (
                              <button
                                type="button"
                                disabled={generatingDocId === doc.id}
                                onClick={() => handleGenerateFromDoc(doc)}
                                className="rounded-full px-3 py-1 text-xs font-semibold text-white transition hover:opacity-90 shadow-2xs"
                                style={{ background: "#2F6B4F" }}
                              >
                                {generatingDocId === doc.id ? "Generating..." : "⚡ Generate Quiz from Document"}
                              </button>
                            )}
                            {(isFailed || isProcessing) && (
                              <button
                                type="button"
                                onClick={() => handleReingest(doc.id)}
                                className="rounded-full border border-[#D8DED4] bg-white px-2.5 py-1 text-xs font-semibold text-[#14231C] hover:bg-[#F7F8F4]"
                              >
                                🔄 Retry
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
