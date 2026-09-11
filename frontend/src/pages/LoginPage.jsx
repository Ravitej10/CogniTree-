import { useState, useEffect } from "react";
import TreeMotif from "../components/TreeMotif";
import { apiRequest, setAccessToken, getAccessToken } from "../lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [hasExistingSession, setHasExistingSession] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const token = getAccessToken();
    if (token) {
      setHasExistingSession(true);
    }
  }, []);

  function handleDemoFill(role) {
    setError("");
    if (role === "student") {
      setEmail("student@cognitree.edu");
      setPassword("password123");
    } else if (role === "teacher") {
      setEmail("teacher@cognitree.edu");
      setPassword("password123");
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    // Basic client validation
    if (!email.trim() || !password) {
      setError("Please fill in both your email address and password.");
      return;
    }

    setLoading(true);
    try {
      const data = await apiRequest("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      if (data && data.access_token) {
        setAccessToken(data.access_token, rememberMe);
        window.location.href = "/dashboard";
      } else {
        throw new Error("No access token received from server.");
      }
    } catch (err) {
      setError(err.message || "Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen grid-cols-1 md:grid-cols-2" style={{ background: "#F7F8F4", color: "#14231C" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');
        .font-display { font-family: 'Fraunces', serif; font-optical-sizing: auto; }
        .font-body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'IBM Plex Mono', monospace; }
        .ct-input:focus-visible { outline: 2px solid #2F6B4F; outline-offset: 2px; }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(6px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out forwards;
        }
      `}</style>

      {/* Left Branded Panel (Desktop) */}
      <div
        className="relative hidden flex-col justify-between overflow-hidden px-12 py-10 md:flex select-none"
        style={{ background: "#14231C", color: "#F7F8F4" }}
      >
        <div className="flex items-center justify-between">
          <a href="/" className="flex items-center gap-2.5 transition hover:opacity-90">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl" style={{ background: "rgba(47, 107, 79, 0.4)", border: "1px solid rgba(139, 154, 140, 0.3)" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="6" r="3" fill="#2F6B4F" />
                <circle cx="6" cy="18" r="2.5" fill="#E2A73E" />
                <circle cx="18" cy="18" r="2.5" fill="#2F6B4F" />
                <path d="M12 9V13M12 13L6 15.5M12 13L18 15.5" stroke="#8B9A8C" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
            </div>
            <span className="font-display text-xl font-semibold tracking-tight">CogniTree</span>
          </a>
          <span className="font-mono text-xs uppercase tracking-widest px-2.5 py-1 rounded-full border border-[rgba(255,255,255,0.15)] text-[#8B9A8C]">
            Auth v0.1
          </span>
        </div>

        <div className="my-auto flex flex-col items-center text-center">
          <div className="mx-auto w-full max-w-xs opacity-95 transition hover:scale-105 duration-500">
            <TreeMotif className="w-full" animate={true} />
          </div>

          <div className="mt-8 flex items-center justify-center gap-4 text-xs font-mono text-[#8B9A8C]">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-[#2F6B4F]"></span>
              Topic Mastery
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-[#E2A73E]"></span>
              Gap Analysis
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-[#8B9A8C]"></span>
              Adaptive Test
            </span>
          </div>
        </div>

        <div className="space-y-4">
          <blockquote className="font-display max-w-md text-2xl font-medium leading-snug">
            &ldquo;Not weak in the subject &mdash;
            <br />
            weak in one branch of it.&rdquo;
          </blockquote>
          <p className="font-body text-xs text-[#8B9A8C] leading-relaxed">
            CogniTree diagnoses granular cognitive gaps and builds adaptive remediation quizzes for students.
          </p>
        </div>
      </div>

      {/* Right Login Form Container */}
      <div className="flex flex-col justify-center px-6 py-12 sm:px-12 lg:px-16 overflow-y-auto">
        <div className="mx-auto w-full max-w-md">
          {/* Mobile brand header */}
          <div className="mb-8 flex items-center justify-between md:hidden">
            <a href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg" style={{ background: "#14231C" }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="6" r="3" fill="#2F6B4F" />
                  <circle cx="6" cy="18" r="2.5" fill="#E2A73E" />
                  <circle cx="18" cy="18" r="2.5" fill="#2F6B4F" />
                  <path d="M12 9V13M12 13L6 15.5M12 13L18 15.5" stroke="#8B9A8C" strokeWidth="1.6" strokeLinecap="round" />
                </svg>
              </div>
              <span className="font-display text-lg font-semibold">CogniTree</span>
            </a>
            <a href="/" className="font-body text-xs font-medium text-[#2F6B4F] hover:underline">
              ← Back to Home
            </a>
          </div>

          <div className="space-y-2">
            <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight text-[#14231C]">
              Welcome back
            </h1>
            <p className="font-body text-sm text-[#8B9A8C] leading-relaxed">
              Log in to your account to review diagnostics and adaptive practice sessions.
            </p>
          </div>

          {/* Existing active session helper banner */}
          {hasExistingSession && (
            <div className="mt-6 flex items-center justify-between rounded-xl p-3.5 text-xs font-body border border-[#D8DED4] bg-white shadow-xs animate-fade-in">
              <div className="flex items-center gap-2">
                <span className="flex h-2 w-2 rounded-full bg-[#2F6B4F]"></span>
                <span className="text-[#3D4A40]">You have an active session.</span>
              </div>
              <a
                href="/dashboard"
                className="font-semibold text-[#2F6B4F] hover:underline flex items-center gap-1"
              >
                Go to Dashboard →
              </a>
            </div>
          )}

          {/* Quick Demo Credentials Pill Bar */}
          <div className="mt-6 rounded-xl border border-[#D8DED4] bg-white p-3.5 shadow-xs">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs uppercase tracking-wider text-[#8B9A8C] flex items-center gap-1.5">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
                  <polyline points="10 17 15 12 10 7"/>
                  <line x1="15" y1="12" x2="3" y2="12"/>
                </svg>
                Quick Demo Fill
              </span>
              <span className="text-[11px] text-[#8B9A8C]">Click to auto-fill</span>
            </div>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => handleDemoFill("student")}
                className="inline-flex items-center gap-1.5 rounded-lg border border-[#D8DED4] bg-[#F7F8F4] px-2.5 py-1 text-xs font-medium text-[#14231C] transition hover:border-[#2F6B4F] hover:bg-white"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-[#2F6B4F]"></span>
                Student Demo
              </button>
              <button
                type="button"
                onClick={() => handleDemoFill("teacher")}
                className="inline-flex items-center gap-1.5 rounded-lg border border-[#D8DED4] bg-[#F7F8F4] px-2.5 py-1 text-xs font-medium text-[#14231C] transition hover:border-[#2F6B4F] hover:bg-white"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-[#E2A73E]"></span>
                Teacher Demo
              </button>
            </div>
          </div>

          {/* Error Alert Box */}
          {error && (
            <div
              role="alert"
              className="mt-6 flex items-start gap-3 rounded-xl border border-[#FCA5A5] bg-[#FDF2F2] p-3.5 text-sm text-[#991B1B] animate-fade-in"
            >
              <svg className="h-5 w-5 shrink-0 text-[#B3491F] mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div className="flex-1 font-body text-xs font-medium leading-relaxed">
                {error}
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="font-body mt-6 flex flex-col gap-4">
            {/* Email Field */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="login-email" className="text-sm font-medium text-[#14231C]">
                Email address
              </label>
              <div className="relative">
                <input
                  id="login-email"
                  type="email"
                  required
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@school.edu"
                  disabled={loading}
                  className="ct-input w-full rounded-xl border bg-white px-4 py-2.5 text-sm transition placeholder:text-[#8B9A8C] disabled:opacity-50"
                  style={{ borderColor: "#D8DED4", color: "#14231C" }}
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <label htmlFor="login-password" className="text-sm font-medium text-[#14231C]">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setShowForgotModal(true)}
                  className="text-xs font-semibold text-[#2F6B4F] hover:underline"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  disabled={loading}
                  className="ct-input w-full rounded-xl border bg-white px-4 py-2.5 pr-11 text-sm transition placeholder:text-[#8B9A8C] disabled:opacity-50"
                  style={{ borderColor: "#D8DED4", color: "#14231C" }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1.5 text-[#8B9A8C] hover:text-[#14231C] transition rounded-md"
                >
                  {showPassword ? (
                    /* Eye Off Icon */
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    /* Eye Icon */
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="h-4 w-4 rounded border-[#D8DED4] text-[#2F6B4F] focus:ring-[#2F6B4F]"
                />
                <span className="text-xs font-medium text-[#3D4A40]">
                  Remember me on this device
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="mt-3 flex items-center justify-center gap-2 rounded-full py-3.5 px-6 text-sm font-semibold text-white shadow-sm transition-all hover:opacity-95 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
              style={{ background: "#2F6B4F" }}
            >
              {loading ? (
                <>
                  <svg className="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Log in</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </>
              )}
            </button>
          </form>

          {/* Navigation to Signup */}
          <div className="mt-8 border-t pt-6 text-center text-sm font-body" style={{ borderColor: "#D8DED4" }}>
            <p className="text-[#8B9A8C]">
              Don&apos;t have an account yet?{" "}
              <a href="/signup" className="font-semibold text-[#14231C] underline decoration-[#D8DED4] underline-offset-4 hover:decoration-[#2F6B4F]">
                Create an account
              </a>
            </p>
          </div>

          <div className="mt-6 text-center">
            <a href="/" className="text-xs text-[#8B9A8C] hover:text-[#14231C] transition">
              ← Return to CogniTree Homepage
            </a>
          </div>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-fade-in font-body">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl border border-[#D8DED4]">
            <div className="flex items-center justify-between pb-3 border-b border-[#D8DED4]">
              <h3 className="font-display text-lg font-semibold text-[#14231C]">Password Reset</h3>
              <button
                type="button"
                onClick={() => setShowForgotModal(false)}
                className="rounded-lg p-1 text-[#8B9A8C] hover:bg-[#F7F8F4] hover:text-[#14231C]"
              >
                ✕
              </button>
            </div>
            <div className="mt-4 space-y-3 text-sm text-[#3D4A40] leading-relaxed">
              <p>
                In the demo environment, you can sign in directly using the pre-configured accounts or create a new student account at{" "}
                <a href="/signup" className="font-semibold text-[#2F6B4F] underline">
                  Sign up
                </a>.
              </p>
              <p className="rounded-lg bg-[#F7F8F4] p-3 text-xs text-[#8B9A8C] border border-[#D8DED4]">
                Default demo accounts:
                <br />
                • Student: <span className="font-mono text-[#14231C]">student@cognitree.edu</span> / <span className="font-mono text-[#14231C]">password123</span>
                <br />
                • Teacher: <span className="font-mono text-[#14231C]">teacher@cognitree.edu</span> / <span className="font-mono text-[#14231C]">password123</span>
              </p>
            </div>
            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={() => setShowForgotModal(false)}
                className="rounded-full px-5 py-2 text-xs font-semibold text-white"
                style={{ background: "#2F6B4F" }}
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
