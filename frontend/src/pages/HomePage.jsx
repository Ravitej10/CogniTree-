// HomePage.jsx
// Landing page. Design tokens (see palette below) stay consistent with
// LoginPage.jsx and TreeMotif.jsx — keep them in sync if you change one.
//
// Palette:
//   --paper   #F7F8F4  page background
//   --ink     #14231C  primary text
//   --forest  #2F6B4F  primary accent / "mastered" state
//   --amber   #E2A73E  secondary accent / "gap" state
//   --sage    #8B9A8C  muted text, hairlines, branch lines
//   --line    #D8DED4  dividers
//
// Type: Fraunces (display), Inter (body), IBM Plex Mono (data/labels).
// If this lives inside a Next.js app, move the @import in <style> below
// into globals.css instead — it's inlined here so the file is self-contained.

import TreeMotif from "../components/TreeMotif";

const PROBLEMS = [
  {
    label: "01",
    title: "Pinpoint exact placement gaps",
    body: "Not \"weak in DSA or OS\" — weak in one specific concept (e.g., AVL rotations, Banker's algorithm), in one sub-topic, on one cognitive skill.",

  },
  {
    label: "02",
    title: "Separate knowing from doing",
    body: "Memorizing a definition and applying it in a problem are tracked as two different abilities.",
  },
  {
    label: "03",
    title: "Built from your materials",
    body: "Every question is generated from the textbooks, slides, and notes you actually study.",
  },
  {
    label: "04",
    title: "Tests that adapt",
    body: "No two students get the same quiz twice — each one targets that student's live weak points.",
  },
];

const PIPELINE = [
  { phase: "Phase 1", name: "Ingestion", detail: "Course material is parsed, chunked, and indexed." },
  { phase: "Phase 2", name: "Generation", detail: "Questions are generated and schema-validated." },
  { phase: "Phase 3", name: "Diagnosis", detail: "Answers build a live topic × skill performance map." },
];

export default function HomePage() {
  return (
    <div className="min-h-screen" style={{ background: "#F7F8F4", color: "#14231C" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');
        .font-display { font-family: 'Fraunces', serif; font-optical-sizing: auto; }
        .font-body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'IBM Plex Mono', monospace; }
      `}</style>

      {/* Nav */}
      <header className="font-body sticky top-0 z-20 border-b" style={{ borderColor: "#D8DED4", background: "#F7F8F4CC", backdropFilter: "blur(6px)" }}>
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <a href="/" className="flex items-center gap-2">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="6" r="3" fill="#2F6B4F" />
              <circle cx="6" cy="18" r="2.5" fill="#E2A73E" />
              <circle cx="18" cy="18" r="2.5" fill="#2F6B4F" />
              <path d="M12 9V13M12 13L6 15.5M12 13L18 15.5" stroke="#8B9A8C" strokeWidth="1.6" strokeLinecap="round" />
            </svg>
            <span className="font-display text-lg font-semibold tracking-tight">CogniTree</span>
          </a>
          <nav className="hidden items-center gap-8 text-sm font-medium sm:flex" style={{ color: "#3D4A40" }}>
            <a href="#how-it-works" className="hover:opacity-70">How it works</a>
            <a href="#modules" className="hover:opacity-70">Modules</a>
            <a href="/login" className="hover:opacity-70">Log in</a>
          </nav>
          <a
            href="/signup"
            className="rounded-full px-4 py-2 text-sm font-semibold text-white transition hover:opacity-90"
            style={{ background: "#2F6B4F" }}
          >
            Get started
          </a>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-12 px-6 py-16 sm:py-24 md:grid-cols-2 md:gap-8">
        <div>
          <span className="font-mono inline-block rounded-full border px-3 py-1 text-xs uppercase tracking-wide" style={{ borderColor: "#D8DED4", color: "#8B9A8C" }}>
            Adaptive learning diagnostics
          </span>
          <h1 className="font-display mt-6 text-5xl font-semibold leading-[1.05] tracking-tight sm:text-6xl">
            Every gap
            <br />
            has a shape.
          </h1>
          <p className="font-body mt-6 max-w-md text-lg leading-relaxed" style={{ color: "#3D4A40" }}>
            CogniTree maps what a student knows down to the sub-topic and the
            thinking skill — not just a test score — then builds the exact
            practice test that closes the gap.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <a
              href="/signup"
              className="rounded-full px-6 py-3 text-sm font-semibold text-white transition hover:opacity-90"
              style={{ background: "#2F6B4F" }}
            >
              Start diagnosing
            </a>
            <a
              href="#how-it-works"
              className="text-sm font-semibold underline decoration-[#D8DED4] underline-offset-4 hover:decoration-current"
            >
              See how it works →
            </a>
          </div>
          <div className="mt-10 flex items-center gap-6 text-sm font-body" style={{ color: "#8B9A8C" }}>
            <span className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: "#2F6B4F" }} />
              Mastered topic
            </span>
            <span className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full" style={{ background: "#E2A73E" }} />
              Diagnosed gap
            </span>
          </div>
        </div>

        <div className="mx-auto w-full max-w-sm md:max-w-none">
          <TreeMotif className="w-full" />
        </div>
      </section>

      {/* Problems -> value props */}
      <section id="modules" className="border-t" style={{ borderColor: "#D8DED4" }}>
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
            Test scores tell you what.
            <br />
            <span style={{ color: "#8B9A8C" }}>CogniTree tells you where.</span>
          </h2>
          <div className="mt-12 grid grid-cols-1 gap-px overflow-hidden rounded-2xl sm:grid-cols-2" style={{ background: "#D8DED4" }}>
            {PROBLEMS.map((p) => (
              <div key={p.label} className="p-8" style={{ background: "#FFFFFF" }}>
                <span className="font-mono text-xs" style={{ color: "#8B9A8C" }}>{p.label}</span>
                <h3 className="font-display mt-3 text-xl font-semibold">{p.title}</h3>
                <p className="font-body mt-2 text-sm leading-relaxed" style={{ color: "#3D4A40" }}>{p.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section id="how-it-works" className="border-t" style={{ borderColor: "#D8DED4" }}>
        <div className="mx-auto max-w-6xl px-6 py-20">
          <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">How a quiz gets built</h2>
          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
            {PIPELINE.map((step, i) => (
              <div key={step.phase}>
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs" style={{ color: "#8B9A8C" }}>{step.phase}</span>
                  {i < PIPELINE.length - 1 && (
                    <span className="hidden h-px flex-1 sm:block" style={{ background: "#D8DED4" }} />
                  )}
                </div>
                <h3 className="font-display mt-3 text-xl font-semibold">{step.name}</h3>
                <p className="font-body mt-2 text-sm leading-relaxed" style={{ color: "#3D4A40" }}>{step.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t" style={{ borderColor: "#D8DED4" }}>
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-10 text-sm sm:flex-row" style={{ color: "#8B9A8C" }}>
          <span className="font-display font-semibold" style={{ color: "#14231C" }}>CogniTree</span>
          <span className="font-body">Precision diagnostics for personalized remediation.</span>
        </div>
      </footer>
    </div>
  );
}
