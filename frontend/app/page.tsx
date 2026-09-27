"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { ArchitectureLoop } from "@/components/ArchitectureLoop";
import { getHealthStatus } from "@/lib/api";
import { HealthResponse } from "@/types";

export default function Home() {
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [healthState, setHealthState] = useState<"checking" | "ok" | "error">(
    "checking"
  );
  const [latency, setLatency] = useState<number | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<string>("");

  const checkHealth = async () => {
    setHealthState("checking");
    setErrorMsg(null);
    const start = performance.now();
    try {
      const data = await getHealthStatus();
      const end = performance.now();
      setLatency(Math.round(end - start));
      setHealthData(data);
      if (data.api === "ok") {
        setHealthState("ok");
      } else {
        setHealthState("error");
      }
      setLastChecked(new Date().toLocaleTimeString());
    } catch (err: unknown) {
      setHealthState("error");
      setErrorMsg(
        err instanceof Error
          ? err.message
          : "Could not reach FastAPI backend. Make sure it is running on port 8000."
      );
      setLastChecked(new Date().toLocaleTimeString());
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      <Navbar apiStatus={healthState} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
        {/* Hero Section */}
        <section className="text-center space-y-4 max-w-3xl mx-auto pt-6 pb-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wide uppercase">
            <span>✨</span> Phase 1 Project Foundation
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            This agent is more useful because{" "}
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              it remembers.
            </span>
          </h1>
          <p className="text-base sm:text-lg text-zinc-400 leading-relaxed">
            ContextIQ is a persistent-memory AI assistant for software engineering
            teams, retaining architecture decisions, technology standards, and
            incident postmortems via Hindsight Cloud.
          </p>
        </section>

        {/* Live System Status & Health Card */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Health Check Card */}
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono text-zinc-400 uppercase tracking-wider">
                  Health Probe
                </span>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${
                    healthState === "ok"
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                      : healthState === "checking"
                      ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                      : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                  }`}
                >
                  {healthState === "ok"
                    ? "200 OK"
                    : healthState === "checking"
                    ? "Probing..."
                    : "Failed"}
                </span>
              </div>
              <h3 className="text-lg font-bold text-white mb-1">
                GET /api/health
              </h3>
              <p className="text-xs text-zinc-400 mb-4">
                Independent backend verification without mocking external services
                prematurely.
              </p>

              <div className="bg-zinc-950 rounded-xl p-3 border border-zinc-800/80 font-mono text-xs space-y-1 mb-4">
                <div className="flex justify-between text-zinc-400">
                  <span>Endpoint:</span>
                  <span className="text-zinc-200">http://127.0.0.1:8000/api/health</span>
                </div>
                <div className="flex justify-between text-zinc-400">
                  <span>Latency:</span>
                  <span className="text-emerald-400 font-semibold">
                    {latency !== null ? `${latency} ms` : "—"}
                  </span>
                </div>
                <div className="flex justify-between text-zinc-400">
                  <span>Last Checked:</span>
                  <span className="text-zinc-300">{lastChecked || "—"}</span>
                </div>
                <div className="pt-2 border-t border-zinc-800 text-zinc-300">
                  <span className="text-zinc-500 block mb-1">Payload:</span>
                  <code className="text-indigo-300">
                    {healthData ? JSON.stringify(healthData, null, 2) : errorMsg || "No response yet"}
                  </code>
                </div>
              </div>
            </div>

            <button
              onClick={checkHealth}
              disabled={healthState === "checking"}
              className="w-full py-2 px-4 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-semibold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <span>🔄</span> Refresh Backend Health
            </button>
          </div>

          {/* Architecture Guardrails Card */}
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono text-zinc-400 uppercase tracking-wider">
                  Security Guardrails
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Strict Compliance
                </span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">
                Hindsight Isolation
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed mb-4">
                The frontend never directly communicates with Hindsight Cloud. All
                Retain & Recall operations are strictly authenticated and mediated
                by FastAPI.
              </p>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 flex items-start gap-2">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-zinc-300">
                    <strong>Server-Controlled Bank:</strong> Frontend cannot supply arbitrary bank IDs.
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 flex items-start gap-2">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-zinc-300">
                    <strong>Zero Client Secrets:</strong> No Hindsight or LLM API keys on frontend.
                  </span>
                </div>
                <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800 flex items-start gap-2">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-zinc-300">
                    <strong>Separation of Concerns:</strong> PostgreSQL stores app state only.
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-zinc-800 text-[11px] text-zinc-500">
              PRD Sections 5, 23 & 27 compliant
            </div>
          </div>

          {/* Foundation Tech Stack Card */}
          <div className="rounded-2xl border border-zinc-800 bg-zinc-900/50 p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono text-zinc-400 uppercase tracking-wider">
                  Foundation Stack
                </span>
                <span className="text-xs px-2.5 py-0.5 rounded-full font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  Verified
                </span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">
                Technology Baseline
              </h3>
              <ul className="space-y-2 text-xs text-zinc-300 mb-4">
                <li className="flex items-center justify-between p-2 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-zinc-400">Frontend</span>
                  <span className="font-mono text-zinc-200">Next.js 16 (App Router) + TS</span>
                </li>
                <li className="flex items-center justify-between p-2 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-zinc-400">Backend</span>
                  <span className="font-mono text-zinc-200">FastAPI + Python 3.8/3.11</span>
                </li>
                <li className="flex items-center justify-between p-2 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-zinc-400">Styling</span>
                  <span className="font-mono text-zinc-200">Tailwind CSS</span>
                </li>
                <li className="flex items-center justify-between p-2 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-zinc-400">Database</span>
                  <span className="font-mono text-zinc-200">SQLAlchemy / PostgreSQL</span>
                </li>
                <li className="flex items-center justify-between p-2 rounded-lg bg-zinc-950 border border-zinc-800">
                  <span className="text-zinc-400">Auth & Tokens</span>
                  <span className="font-mono text-zinc-200">JWT (python-jose) + bcrypt</span>
                </li>
              </ul>
            </div>

            <div className="p-2.5 rounded-lg bg-indigo-950/30 border border-indigo-900/40 text-[11px] text-indigo-300">
              Ready for Phase 2: Hindsight Retain & Recall activation
            </div>
          </div>
        </section>

        {/* Core Architecture Loop */}
        <section>
          <ArchitectureLoop />
        </section>
      </main>

      <footer className="border-t border-zinc-800 bg-zinc-950 py-6 text-center text-xs text-zinc-500">
        ContextIQ v2.2 — 48-Hour Execution Edition • Powered by Hindsight Cloud
      </footer>
    </div>
  );
}
