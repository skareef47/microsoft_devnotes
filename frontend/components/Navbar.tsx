"use client";

import React from "react";
import { UserProfile } from "@/types";

interface NavbarProps {
  apiStatus: "checking" | "ok" | "error";
  hindsightStatus?: "ok" | "unavailable" | "unknown";
  user: UserProfile | null;
  onSignOut: () => void;
  onOpenAuth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  apiStatus,
  hindsightStatus = "ok",
  user,
  onSignOut,
  onOpenAuth,
}) => {
  return (
    <header className="border-b border-zinc-800 bg-zinc-950/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Branding */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <span className="text-white text-lg font-bold">🧠</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white text-lg tracking-tight">ContextIQ</span>
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                P0 Persistent Memory
              </span>
            </div>
            <p className="text-xs text-zinc-400 hidden sm:block">
              &ldquo;This agent is more useful because it remembers.&rdquo;
            </p>
          </div>
        </div>

        {/* Right: Status & User */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* API Status badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs">
            <span className="text-zinc-400">Backend:</span>
            <span className="inline-flex items-center gap-1.5 font-medium">
              <span
                className={`w-2 h-2 rounded-full ${
                  apiStatus === "ok" ? "bg-emerald-500" : "bg-rose-500"
                }`}
              />
              <span className={apiStatus === "ok" ? "text-emerald-400" : "text-rose-400"}>
                {apiStatus === "ok" ? "200 OK" : "Offline"}
              </span>
            </span>
          </div>

          {/* Hindsight Status badge */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs">
            <span className="text-zinc-400">Hindsight:</span>
            <span className="inline-flex items-center gap-1.5 font-medium">
              <span
                className={`w-2 h-2 rounded-full ${
                  hindsightStatus === "ok"
                    ? "bg-emerald-500 animate-pulse"
                    : "bg-rose-500"
                }`}
              />
              <span
                className={
                  hindsightStatus === "ok"
                    ? "text-emerald-400"
                    : "text-rose-400"
                }
              >
                {hindsightStatus === "ok" ? "Self-Hosted Online" : "Degraded / Offline"}
              </span>
            </span>
          </div>

          {/* Team Bank info */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-950/40 border border-indigo-800/40 text-xs text-indigo-300">
            <span className="font-medium text-zinc-400">Team:</span>
            <span className="font-mono text-[11px] text-indigo-200">contextiq-team</span>
          </div>

          {/* User Auth state */}
          {user ? (
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="text-right hidden sm:block">
                <p className="text-xs font-medium text-zinc-200 truncate max-w-[160px]">
                  {user.email}
                </p>
                <p className="text-[10px] text-zinc-500">Shared Engineering Team</p>
              </div>
              <button
                onClick={onSignOut}
                className="px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs text-zinc-300 transition-colors"
                title="Sign out of current session"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-colors shadow-md shadow-indigo-600/20"
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
