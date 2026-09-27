import React from "react";

export const ArchitectureLoop: React.FC = () => {
  const steps = [
    {
      num: "01",
      title: "Engineering Context",
      desc: "Architectural choices, production incidents, tech stack standards, and team decisions.",
      tag: "Input",
      badgeColor: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    },
    {
      num: "02",
      title: "Hindsight Retain",
      desc: "Deterministic retention gate identifies durable engineering facts and persists them to the team bank.",
      tag: "Memory Write",
      badgeColor: "bg-purple-500/10 text-purple-400 border-purple-500/20",
    },
    {
      num: "03",
      title: "New Conversation",
      desc: "Engineers start queries in a fresh session hours or weeks later without repeating context.",
      tag: "Session",
      badgeColor: "bg-zinc-800 text-zinc-300 border-zinc-700",
    },
    {
      num: "04",
      title: "Hindsight Recall",
      desc: "Backend retrieves relevant team memories from the authorized Hindsight Cloud bank.",
      tag: "Memory Read",
      badgeColor: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    },
    {
      num: "05",
      title: "Context Augmented LLM",
      desc: "Prompt is augmented with recalled memories before invoking the configured LLM provider.",
      tag: "Inference",
      badgeColor: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    },
    {
      num: "06",
      title: "Contextual Answer",
      desc: "Agent produces a team-tailored solution with visible memories-used indicator.",
      tag: "Output",
      badgeColor: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    },
  ];

  return (
    <div className="rounded-2xl border border-zinc-800 bg-zinc-900/40 p-6 backdrop-blur-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-white">Core Memory Loop</h3>
          <p className="text-xs text-zinc-400">
            End-to-end durable memory flow powered by Hindsight Cloud
          </p>
        </div>
        <span className="text-[11px] font-mono px-2.5 py-1 rounded-md bg-zinc-800/80 text-zinc-300 border border-zinc-700">
          Shared Team Bank
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {steps.map((step) => (
          <div
            key={step.num}
            className="rounded-xl border border-zinc-800/80 bg-zinc-950/60 p-4 relative overflow-hidden group hover:border-zinc-700 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono text-zinc-500">{step.num}</span>
              <span
                className={`text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded-full border ${step.badgeColor}`}
              >
                {step.tag}
              </span>
            </div>
            <h4 className="text-sm font-semibold text-zinc-200 mb-1 group-hover:text-white transition-colors">
              {step.title}
            </h4>
            <p className="text-xs text-zinc-400 leading-relaxed">{step.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
