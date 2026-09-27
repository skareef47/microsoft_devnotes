"use client";

import React, { useState } from "react";
import { MemoryItem } from "@/types";

interface MemorySidebarProps {
  memories: MemoryItem[];
  isLoading: boolean;
  isSeeding: boolean;
  status: string;
  onRefresh: () => void;
  onSeedDemo: () => void;
  onSelectMemory?: (memory: MemoryItem) => void;
}

export const MemorySidebar: React.FC<MemorySidebarProps> = ({
  memories,
  isLoading,
  isSeeding,
  status,
  onRefresh,
  onSeedDemo,
  onSelectMemory,
}) => {
  const [filterCategory, setFilterCategory] = useState<string>("all");

  const getCategoryBadge = (category: string) => {
    const c = category.toLowerCase();
    if (c.includes("decision") || c.includes("standard")) {
      return {
        badge: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
        label: "Decision",
      };
    }
    if (c.includes("preference")) {
      return {
        badge: "bg-purple-500/10 text-purple-400 border-purple-500/30",
        label: "Preference",
      };
    }
    if (c.includes("architecture")) {
      return {
        badge: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30",
        label: "Architecture",
      };
    }
    if (c.includes("convention")) {
      return {
        badge: "bg-sky-500/10 text-sky-400 border-sky-500/30",
        label: "Convention",
      };
    }
    if (c.includes("incident") || c.includes("lesson")) {
      return {
        badge: "bg-amber-500/10 text-amber-400 border-amber-500/30",
        label: "Incident / Lesson",
      };
    }
    if (c.includes("fact")) {
      return {
        badge: "bg-zinc-800 text-zinc-300 border-zinc-700",
        label: "Fact",
      };
    }
    return {
      badge: "bg-zinc-800 text-zinc-400 border-zinc-700",
      label: category || "Other",
    };
  };

  const formatTimestamp = (ts?: string | null) => {
    if (!ts) return null;
    try {
      const d = new Date(ts);
      if (isNaN(d.getTime())) return null;
      return d.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      });
    } catch {
      return null;
    }
  };

  const filteredMemories =
    filterCategory === "all"
      ? memories
      : memories.filter(
          (m) =>
            (m.category || "").toLowerCase() === filterCategory.toLowerCase()
        );

  return (
    <aside className="w-full lg:w-80 border-t lg:border-t-0 lg:border-l border-zinc-800 bg-zinc-950 flex flex-col h-full overflow-hidden">
      {/* Sidebar Header */}
      <div className="p-3.5 border-b border-zinc-800 bg-zinc-900/30 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Team Memory
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-900 border border-zinc-800 text-zinc-400">
              contextiq-team
            </span>
          </div>
          <p className="text-[11px] text-zinc-500 mt-0.5">
            {memories.length} {memories.length === 1 ? "memory" : "memories"} in Hindsight
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={isLoading}
          title="Refresh memories from Hindsight"
          className="p-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors text-xs flex items-center gap-1 disabled:opacity-50"
        >
          <span className={isLoading ? "animate-spin inline-block" : ""}>🔄</span>
          <span className="text-[10px] hidden sm:inline">Refresh</span>
        </button>
      </div>

      {/* Demo Seed Action Bar */}
      <div className="p-2.5 bg-zinc-900/40 border-b border-zinc-800/80 flex items-center justify-between">
        <span className="text-[11px] text-zinc-400 font-medium">Demo Data</span>
        <button
          onClick={onSeedDemo}
          disabled={isSeeding || isLoading}
          className="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-[11px] font-medium text-zinc-300 transition-colors disabled:opacity-50 flex items-center gap-1"
        >
          {isSeeding ? (
            <>
              <span className="animate-spin text-[10px]">⏳</span>
              <span>Seeding...</span>
            </>
          ) : (
            <span>Seed Demo Memory</span>
          )}
        </button>
      </div>

      {/* Optional Category Filter Pill Bar */}
      {memories.length > 0 && (
        <div className="px-3 py-2 border-b border-zinc-800/60 flex items-center gap-1.5 overflow-x-auto text-[10px] scrollbar-none">
          <button
            onClick={() => setFilterCategory("all")}
            className={`px-2 py-0.5 rounded-md border transition-colors ${
              filterCategory === "all"
                ? "bg-zinc-800 text-white border-zinc-700"
                : "text-zinc-500 border-transparent hover:text-zinc-300"
            }`}
          >
            All ({memories.length})
          </button>
          {["decision", "preference", "architecture", "incident"].map((cat) => {
            const count = memories.filter(
              (m) => (m.category || "").toLowerCase() === cat
            ).length;
            if (count === 0) return null;
            return (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`px-2 py-0.5 rounded-md border capitalize transition-colors ${
                  filterCategory === cat
                    ? "bg-zinc-800 text-white border-zinc-700"
                    : "text-zinc-500 border-transparent hover:text-zinc-300"
                }`}
              >
                {cat} ({count})
              </button>
            );
          })}
        </div>
      )}

      {/* Memory List Container */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {status === "unavailable" ? (
          <div className="p-4 rounded-xl border border-amber-500/20 bg-amber-500/5 text-amber-300 text-xs space-y-1">
            <p className="font-semibold flex items-center gap-1.5">
              <span>⚠️</span> Memory service temporarily unavailable
            </p>
            <p className="text-zinc-400 text-[11px] leading-relaxed">
              Unable to load team memory from Hindsight. System is running in degraded mode.
            </p>
          </div>
        ) : isLoading ? (
          <div className="p-6 text-center text-xs text-zinc-500 space-y-2">
            <div className="animate-spin w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full mx-auto" />
            <p>Loading team memory...</p>
          </div>
        ) : memories.length === 0 ? (
          <div className="p-6 text-center text-xs text-zinc-500 space-y-2">
            <div className="text-xl">📭</div>
            <p className="font-semibold text-zinc-400">No team memories yet.</p>
            <p className="text-[11px] text-zinc-600 leading-relaxed">
              State an engineering decision in chat (e.g. standardizing on a queue) or click &quot;Seed Demo Memory&quot; to populate.
            </p>
          </div>
        ) : (
          filteredMemories.map((mem, idx) => {
            const { badge, label } = getCategoryBadge(mem.category || "fact");
            const dateStr = formatTimestamp(mem.created_at);

            return (
              <div
                key={mem.id || idx}
                onClick={() => onSelectMemory && onSelectMemory(mem)}
                className="group p-3 rounded-xl border border-zinc-800/80 bg-zinc-900/60 hover:bg-zinc-900 hover:border-zinc-700 transition-all cursor-pointer space-y-1.5 shadow-sm"
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${badge}`}
                  >
                    {label}
                  </span>
                  <div className="flex items-center gap-1 text-[10px] text-zinc-600 font-mono">
                    {dateStr && <span>{dateStr}</span>}
                    <span className="group-hover:text-indigo-400 transition-colors">
                      🔍
                    </span>
                  </div>
                </div>

                <p className="text-xs text-zinc-200 leading-relaxed font-sans line-clamp-3">
                  {mem.text}
                </p>

                <div className="flex items-center justify-between pt-1 text-[10px] text-zinc-600 font-mono">
                  <span>{mem.id ? mem.id.slice(0, 8) : `#${idx + 1}`}</span>
                  <span className="group-hover:text-zinc-400 transition-colors">
                    Click to inspect →
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Memory Count Footer */}
      <div className="p-3 border-t border-zinc-800 bg-zinc-950/90 text-[11px] text-zinc-500 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>Hindsight persistent bank</span>
        </span>
        <span className="font-mono text-zinc-300 font-semibold">
          {memories.length} {memories.length === 1 ? "item" : "items"}
        </span>
      </div>
    </aside>
  );
};
