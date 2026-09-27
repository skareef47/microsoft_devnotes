"use client";

import React, { useEffect, useState } from "react";
import { MemoryItem } from "@/types";

interface MemoryInspectorModalProps {
  memory: MemoryItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export const MemoryInspectorModal: React.FC<MemoryInspectorModalProps> = ({
  memory,
  isOpen,
  onClose,
}) => {
  const [copied, setCopied] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !memory) return null;

  const handleCopyId = () => {
    if (memory.id) {
      navigator.clipboard.writeText(memory.id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getCategoryBadgeClass = (category: string) => {
    const c = category.toLowerCase();
    if (c.includes("decision") || c.includes("standard")) {
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    }
    if (c.includes("preference")) {
      return "bg-purple-500/10 text-purple-400 border-purple-500/30";
    }
    if (c.includes("architecture")) {
      return "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
    }
    if (c.includes("convention")) {
      return "bg-sky-500/10 text-sky-400 border-sky-500/30";
    }
    if (c.includes("incident") || c.includes("lesson")) {
      return "bg-amber-500/10 text-amber-400 border-amber-500/30";
    }
    return "bg-zinc-800 text-zinc-300 border-zinc-700";
  };

  const formatTimestamp = (ts?: string | null) => {
    if (!ts) return null;
    try {
      const d = new Date(ts);
      if (isNaN(d.getTime())) return ts;
      return d.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        timeZoneName: "short",
      });
    } catch {
      return ts;
    }
  };

  const formattedDate = formatTimestamp(memory.created_at);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      {/* Backdrop click to close */}
      <div className="absolute inset-0" onClick={onClose} />

      <div className="relative w-full max-w-lg bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden z-10 space-y-0 animate-scaleUp">
        {/* Modal Header */}
        <div className="p-4 border-b border-zinc-800 bg-zinc-950/60 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm">🧠</span>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Memory Detail & Inspector
            </h3>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-900 border border-zinc-800 text-zinc-400">
              contextiq-team
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors text-xs"
          >
            ✕
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 space-y-4 max-h-[75vh] overflow-y-auto">
          {/* Category */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-500 font-medium">Category:</span>
              <span
                className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${getCategoryBadgeClass(
                  memory.category || "decision"
                )}`}
              >
                {memory.category || "context"}
              </span>
            </div>
            {memory.status && (
              <span className="text-[10px] font-mono text-zinc-500">
                status: {memory.status}
              </span>
            )}
          </div>

          {/* Full Memory Statement */}
          <div className="space-y-1.5">
            <label className="text-xs text-zinc-500 font-medium">
              Durable Engineering Statement:
            </label>
            <div className="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800 text-zinc-100 text-sm leading-relaxed font-sans">
              {memory.text}
            </div>
          </div>

          {/* Hindsight Metadata Grid */}
          <div className="space-y-2 pt-1 border-t border-zinc-800/80">
            <label className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              Hindsight Metadata
            </label>

            <div className="grid grid-cols-1 gap-2 text-xs">
              {/* Memory ID */}
              <div className="p-2.5 rounded-lg bg-zinc-950/70 border border-zinc-850 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-zinc-500 block">Memory ID</span>
                  <span className="font-mono text-zinc-300 text-[11px] select-all break-all">
                    {memory.id}
                  </span>
                </div>
                <button
                  onClick={handleCopyId}
                  className="px-2 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-[10px] text-zinc-300 font-medium transition-colors ml-2 shrink-0"
                >
                  {copied ? "✓ Copied" : "Copy ID"}
                </button>
              </div>

              {/* Timestamp if available */}
              {formattedDate && (
                <div className="p-2.5 rounded-lg bg-zinc-950/70 border border-zinc-850">
                  <span className="text-[10px] text-zinc-500 block">
                    Recorded / Mentioned At
                  </span>
                  <span className="font-mono text-zinc-300 text-[11px]">
                    {formattedDate}
                  </span>
                </div>
              )}

              {/* Source metadata if safely available */}
              {memory.source && (
                <div className="p-2.5 rounded-lg bg-zinc-950/70 border border-zinc-850">
                  <span className="text-[10px] text-zinc-500 block">
                    Source Link
                  </span>
                  <span className="font-mono text-zinc-400 text-[11px] break-all">
                    {memory.source}
                  </span>
                </div>
              )}

              {/* Memory Bank info */}
              <div className="p-2.5 rounded-lg bg-zinc-950/70 border border-zinc-850 flex justify-between items-center">
                <div>
                  <span className="text-[10px] text-zinc-500 block">
                    Memory Engine & Bank
                  </span>
                  <span className="font-mono text-zinc-300 text-[11px]">
                    contextiq-team
                  </span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                  Hindsight Docker
                </span>
              </div>
            </div>
          </div>

          {/* Explainability Callout */}
          <div className="p-3 rounded-xl bg-indigo-500/5 border border-indigo-500/20 text-xs text-indigo-300 space-y-1">
            <p className="font-semibold text-[11px]">
              💡 How ContextIQ uses this memory
            </p>
            <p className="text-[11px] text-zinc-400 leading-relaxed">
              This statement persists in the team bank. When queries mention
              relevant technologies or architecture decisions, Hindsight Recall
              retrieves this item to align responses across all conversations.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-3.5 border-t border-zinc-800 bg-zinc-950/80 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-xs font-semibold text-zinc-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
