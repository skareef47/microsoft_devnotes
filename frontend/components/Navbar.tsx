"use client";

import React from "react";

interface NavbarProps {
  apiStatus: "checking" | "ok" | "error";
}

export const Navbar: React.FC<NavbarProps> = ({ apiStatus }) => {
  return (
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <span className="text-white text-lg font-bold">🧠</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white text-lg tracking-tight">ContextIQ</span>
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Phase 1 MVP
              </span>
            </div>
            <p className="text-xs text-zinc-400 hidden sm:block">
              Persistent-Memory AI Assistant for Engineering Teams
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs">
            <span className="text-zinc-400">Backend API:</span>
            <span className="inline-flex items-center gap-1.5 font-medium">
              <span
                className={`w-2 h-2 rounded-full ${
                  apiStatus === "ok"
                    ? "bg-emerald-500 animate-pulse"
                    : apiStatus === "checking"
                    ? "bg-amber-400 animate-ping"
                    : "bg-rose-500"
                }`}
              />
              <span
                className={
                  apiStatus === "ok"
                    ? "text-emerald-400"
                    : apiStatus === "checking"
                    ? "text-amber-400"
                    : "text-rose-400"
                }
              >
                {apiStatus === "ok"
                  ? "Connected (GET /api/health)"
                  : apiStatus === "checking"
                  ? "Connecting..."
                  : "Unavailable"}
              </span>
            </span>
          </div>

          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-950/40 border border-indigo-800/40 text-xs text-indigo-300">
            <span className="font-medium">Team Bank:</span>
            <span className="font-mono text-[11px] text-indigo-200">Server-Controlled</span>
          </div>
        </div>
      </div>
    </header>
  );
};
