import { useState } from "react";
import TreeMotif from "../components/TreeMotif";
import { apiRequest, setAccessToken } from "../lib/api";

export default function SignupPage() {
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (form.password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (form.password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const data = await apiRequest("/api/auth/signup", {
        method: "POST",
        body: JSON.stringify({
          email: form.email.trim().toLowerCase(),
          password: form.password,
          full_name: form.full_name.trim() || null,
        }),
      });

      if (data && data.access_token) {
        setAccessToken(data.access_token, true);
        window.location.href = "/dashboard";
      } else {
        throw new Error("Could not initialize session token.");
      }
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
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
      `}</style>

      {/* Branded Left Side */}
      <div className="relative hidden flex-col justify-between overflow-hidden px-12 py-10 md:flex select-none" style={{ background: "#14231C", color: "#F7F8F4" }}>
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

        <div className="my-auto mx-auto w-full max-w-xs opacity-90">
          <TreeMotif className="w-full" animate={true} />
        </div>

        <blockquote className="font-display max-w-sm text-2xl font-medium leading-snug">
          Find the branch that needs
          <br />
          a little more attention.
        </blockquote>
      </div>

      {/* Signup Form */}
      <div className="flex flex-col justify-center px-6 py-12 sm:px-12 lg:px-16 overflow-y-auto">
        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 flex items-center justify-between md:hidden">
            <a href="/" className="flex items-center gap-2">
              <span className="font-display text-lg font-semibold">CogniTree</span>
            </a>
            <a href="/" className="text-xs font-medium text-[#2F6B4F]">← Home</a>
          </div>

          <h1 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight">Create your account</h1>
          <p className="font-body mt-2 text-sm text-[#8B9A8C]">
            Start building a clearer, adaptive map of what you know.
          </p>

          <form onSubmit={handleSubmit} className="font-body mt-8 flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="signup-name" className="text-sm font-medium text-[#14231C]">
                Full Name <span className="font-normal text-[#8B9A8C]">(optional)</span>
              </label>
              <input
                id="signup-name"
                name="full_name"
                value={form.full_name}
                onChange={updateField}
                autoComplete="name"
                placeholder="Alex Morgan"
                disabled={loading}
                className="ct-input rounded-xl border bg-white px-4 py-2.5 text-sm"
                style={{ borderColor: "#D8DED4", color: "#14231C" }}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="signup-email" className="text-sm font-medium text-[#14231C]">
                Email address
              </label>
              <input
                id="signup-email"
                name="email"
                type="email"
                required
                autoComplete="email"
                value={form.email}
                onChange={updateField}
                placeholder="you@school.edu"
                disabled={loading}
                className="ct-input rounded-xl border bg-white px-4 py-2.5 text-sm"
                style={{ borderColor: "#D8DED4", color: "#14231C" }}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="signup-password" className="text-sm font-medium text-[#14231C]">
                Password
              </label>
              <div className="relative">
                <input
                  id="signup-password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={8}
                  autoComplete="new-password"
                  value={form.password}
                  onChange={updateField}
                  placeholder="At least 8 characters"
                  disabled={loading}
                  className="ct-input w-full rounded-xl border bg-white px-4 py-2.5 pr-11 text-sm"
                  style={{ borderColor: "#D8DED4", color: "#14231C" }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1.5 text-[#8B9A8C] hover:text-[#14231C] transition rounded-md"
                >
                  {showPassword ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label htmlFor="signup-confirm-password" className="text-sm font-medium text-[#14231C]">
                Confirm password
              </label>
              <input
                id="signup-confirm-password"
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Re-enter password"
                disabled={loading}
                className="ct-input rounded-xl border bg-white px-4 py-2.5 text-sm"
                style={{ borderColor: "#D8DED4", color: "#14231C" }}
              />
            </div>

            {error && (
              <div role="alert" className="mt-2 flex items-start gap-2.5 rounded-xl border border-[#FCA5A5] bg-[#FDF2F2] p-3 text-xs font-medium text-[#991B1B]">
                <svg className="h-4 w-4 shrink-0 text-[#B3491F] mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="mt-3 flex items-center justify-center gap-2 rounded-full py-3.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-60"
              style={{ background: "#2F6B4F" }}
            >
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>

          <p className="font-body mt-8 text-center text-sm text-[#8B9A8C]">
            Already have an account?{" "}
            <a href="/login" className="font-semibold text-[#14231C] underline decoration-[#D8DED4] underline-offset-4 hover:decoration-[#2F6B4F]">
              Log in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}