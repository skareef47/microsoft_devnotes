"use client";

import React, { useEffect, useRef, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { AuthModal } from "@/components/AuthModal";
import { MemorySidebar } from "@/components/MemorySidebar";
import { MemoryInspectorModal } from "@/components/MemoryInspectorModal";
import {
  clearStoredToken,
  getCurrentUserProfile,
  getHealthStatus,
  getStoredToken,
  getTeamMemories,
  seedDemoMemories,
  sendChatMessage,
} from "@/lib/api";
import { ChatMessage, HealthResponse, MemoryItem, UserProfile } from "@/types";

export default function ContextIQChatApp() {
  // Session & User
  const [user, setUser] = useState<UserProfile | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  // Connection & Health
  const [healthStatus, setHealthStatus] = useState<"checking" | "ok" | "error">(
    "checking"
  );
  const [hindsightStatus, setHindsightStatus] = useState<"ok" | "unavailable">(
    "ok"
  );

  // Conversation & Messages
  const [conversationId, setConversationId] = useState<string>(() =>
    `conv_${Math.random().toString(36).substring(2, 9)}`
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [memoryEnabled, setMemoryEnabled] = useState(true);

  // Team Memories
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [memoriesLoading, setMemoriesLoading] = useState(false);
  const [memoriesStatus, setMemoriesStatus] = useState("available");
  const [isSeeding, setIsSeeding] = useState(false);

  // Notifications Toast
  const [notification, setNotification] = useState<{
    type: "info" | "success" | "error";
    message: string;
  } | null>(null);

  // Expanded memories dropdown per message
  const [expandedMemoryMsgId, setExpandedMemoryMsgId] = useState<string | null>(
    null
  );

  // Memory Inspector Modal State
  const [inspectedMemory, setInspectedMemory] = useState<MemoryItem | null>(null);
  const [isInspectorOpen, setIsInspectorOpen] = useState(false);

  // Mobile drawer toggle for memory sidebar
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending]);

  const showNotification = (
    type: "info" | "success" | "error",
    msg: string
  ) => {
    setNotification({ type, message: msg });
    setTimeout(() => {
      setNotification(null);
    }, 4500);
  };

  const fetchMemories = async (token?: string | null) => {
    setMemoriesLoading(true);
    try {
      const data = await getTeamMemories(token);
      setMemories(data.memories || []);
      setMemoriesStatus(data.status || "available");
      if (data.status === "unavailable") {
        setHindsightStatus("unavailable");
      } else {
        setHindsightStatus("ok");
      }
    } catch {
      setMemoriesStatus("unavailable");
      setHindsightStatus("unavailable");
    } finally {
      setMemoriesLoading(false);
    }
  };

  // Initial user auth & health check
  useEffect(() => {
    const initApp = async () => {
      // 1. Health check
      try {
        const health: HealthResponse = await getHealthStatus();
        if (health.api === "ok") {
          setHealthStatus("ok");
          setHindsightStatus(health.hindsight === "ok" ? "ok" : "unavailable");
        } else {
          setHealthStatus("error");
        }
      } catch {
        setHealthStatus("error");
        setHindsightStatus("unavailable");
      }

      // 2. Auth verification
      const token = getStoredToken();
      if (token) {
        try {
          const profile = await getCurrentUserProfile(token);
          setUser(profile);
          fetchMemories(token);
        } catch {
          clearStoredToken();
          setUser(null);
        }
      }
    };

    initApp();
  }, []);

  const handleOpenInspector = (memory: MemoryItem) => {
    setInspectedMemory(memory);
    setIsInspectorOpen(true);
  };

  const handleSeedDemo = async () => {
    if (!user) {
      setAuthModalOpen(true);
      return;
    }
    setIsSeeding(true);
    try {
      const res = await seedDemoMemories();
      showNotification("success", res.message || "Demo memories seeded.");
      await fetchMemories();
    } catch (err: unknown) {
      showNotification(
        "error",
        err instanceof Error ? err.message : "Failed to seed demo memory."
      );
    } finally {
      setIsSeeding(false);
    }
  };

  const handleNewConversation = () => {
    const newId = `conv_${Math.random().toString(36).substring(2, 9)}`;
    setConversationId(newId);
    setMessages([]);
    showNotification(
      "info",
      "New conversation started. Persistent team memory remains available."
    );
  };

  const handleClearConversation = () => {
    setMessages([]);
    showNotification("info", "Conversation view cleared.");
  };

  const handleSignOut = () => {
    clearStoredToken();
    setUser(null);
    setMessages([]);
    showNotification("info", "Signed out successfully.");
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    if (!user) {
      setAuthModalOpen(true);
      return;
    }

    const messageText = inputMessage.trim();
    setInputMessage("");

    // Optimistic user message
    const userMsgId = `msg_u_${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: "user",
      content: messageText,
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      memoryEnabled,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);

    try {
      const response = await sendChatMessage({
        message: messageText,
        conversation_id: conversationId,
        memory_enabled: memoryEnabled,
      });

      const assistantMsg: ChatMessage = {
        id: `msg_a_${Date.now()}`,
        role: "assistant",
        content: response.response,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        memoryEnabled: response.memory_enabled,
        memoriesUsed: response.memories_used,
        memoriesStored: response.memories_stored,
        memoryStatus: response.memory_status,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // If memory was stored, refresh memory list in sidebar
      if (
        response.memories_stored &&
        response.memories_stored.some((m) => m.status === "saved")
      ) {
        fetchMemories();
        showNotification(
          "success",
          "✓ Engineering context saved to Hindsight team memory."
        );
      }
    } catch (err: unknown) {
      let friendlyError = "Unable to reach ContextIQ.";
      if (err instanceof Error) {
        const msg = err.message.toLowerCase();
        if (msg.includes("401") || msg.includes("unauthorized") || msg.includes("session")) {
          friendlyError = "Session expired. Please sign in again.";
        } else if (msg.includes("hindsight") || msg.includes("503") || msg.includes("unavailable")) {
          friendlyError = "Memory service temporarily unavailable.";
        } else if (msg.includes("llm") || msg.includes("generation")) {
          friendlyError = "AI response service unavailable.";
        } else if (msg.includes("failed to fetch") || msg.includes("network") || msg.includes("connect")) {
          friendlyError = "Unable to reach ContextIQ.";
        } else if (err.message && !err.message.includes("Error:") && !err.message.includes("status:")) {
          friendlyError = err.message;
        }
      }

      const errorMsg: ChatMessage = {
        id: `msg_err_${Date.now()}`,
        role: "assistant",
        content: friendlyError,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        memoryStatus: "unavailable",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  // Keyboard shortcut: Enter sends message, Shift+Enter creates newline (IME-safe)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getCategoryColor = (category?: string) => {
    const c = (category || "").toLowerCase();
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

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans">
      <Navbar
        apiStatus={healthStatus}
        hindsightStatus={hindsightStatus}
        user={user}
        onSignOut={handleSignOut}
        onOpenAuth={() => setAuthModalOpen(true)}
      />

      {/* Floating Notification Toast */}
      {notification && (
        <div className="fixed top-20 right-6 z-50 animate-slideIn">
          <div
            className={`px-4 py-2.5 rounded-xl border text-xs shadow-xl backdrop-blur-md flex items-center gap-2 ${
              notification.type === "success"
                ? "bg-emerald-950/80 border-emerald-500/30 text-emerald-300"
                : notification.type === "error"
                ? "bg-rose-950/80 border-rose-500/30 text-rose-300"
                : "bg-indigo-950/80 border-indigo-500/30 text-indigo-300"
            }`}
          >
            <span>
              {notification.type === "success"
                ? "✓"
                : notification.type === "error"
                ? "✗"
                : "ℹ"}
            </span>
            <span className="font-medium">{notification.message}</span>
          </div>
        </div>
      )}

      {/* Main Container */}
      <div className="flex-1 max-w-7xl w-full mx-auto flex flex-col lg:flex-row overflow-hidden border-x border-zinc-900">
        {/* Left Column: Chat Experience */}
        <main className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-zinc-950 overflow-hidden">
          {/* Action Bar / Controls */}
          <div className="p-3 border-b border-zinc-800 bg-zinc-900/40 flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <button
                onClick={handleNewConversation}
                className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-xs font-medium text-zinc-200 transition-colors flex items-center gap-1.5 border border-zinc-700/60 shadow-sm"
                title="Start a new conversation while preserving team memories"
              >
                <span>➕</span> New conversation
              </button>

              <button
                onClick={handleClearConversation}
                className="px-2.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-xs text-zinc-400 hover:text-zinc-200 transition-colors border border-zinc-800"
                title="Clear messages on screen"
              >
                🗑️ Clear
              </button>

              <span className="text-[11px] font-mono text-zinc-500 hidden md:inline ml-1">
                ID: {conversationId}
              </span>
            </div>

            {/* Memory Toggle & Mobile Drawer Toggle */}
            <div className="flex items-center gap-2">
              {/* Memory ON/OFF Toggle with Tooltip UX */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setMemoryEnabled(!memoryEnabled)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 border transition-all ${
                    memoryEnabled
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-sm shadow-emerald-500/10 hover:bg-emerald-500/20"
                      : "bg-zinc-800/80 text-zinc-400 border-zinc-700 hover:bg-zinc-800"
                  }`}
                  title={
                    memoryEnabled
                      ? "🧠 Memory ON: ContextIQ can use relevant team memories."
                      : "○ Memory OFF: This response will not use team memory."
                  }
                >
                  <span
                    className={`w-2 h-2 rounded-full ${
                      memoryEnabled ? "bg-emerald-400 animate-pulse" : "bg-zinc-500"
                    }`}
                  />
                  <span>{memoryEnabled ? "🧠 Memory ON" : "○ Memory OFF"}</span>
                </button>
              </div>

              {/* Mobile Memory Sidebar Drawer Trigger */}
              <button
                onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
                className="lg:hidden px-2.5 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 flex items-center gap-1"
                title="Toggle Memory Sidebar"
              >
                <span>📋</span>
                <span className="font-mono text-[11px]">{memories.length}</span>
              </button>
            </div>
          </div>

          {/* Memory Status Explanation Banner */}
          <div className="px-4 py-1.5 bg-zinc-900/20 border-b border-zinc-850/60 text-[11px] text-zinc-500 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <span>{memoryEnabled ? "💡" : "ℹ️"}</span>
              <span>
                {memoryEnabled
                  ? "Memory ON — ContextIQ recalls durable team decisions from Hindsight."
                  : "Memory OFF — Transient mode. Hindsight Recall is bypassed completely."}
              </span>
            </span>
            <span className="font-mono text-[10px] text-zinc-500 hidden sm:inline">
              bank: contextiq-team
            </span>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto p-6 space-y-4">
                <div className="w-12 h-12 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-2xl shadow-inner">
                  🧠
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-white">
                    ContextIQ Team Assistant
                  </h3>
                  <p className="text-xs text-zinc-400 leading-relaxed">
                    Persistent team memory is connected via self-hosted Hindsight.
                    Decisions and technology choices are remembered across
                    conversations.
                  </p>
                </div>

                {/* Deterministic Demo Sequence Card */}
                <div className="w-full pt-2 space-y-2 text-left">
                  <div className="p-2 rounded-lg bg-zinc-900/60 border border-zinc-800/80 text-[11px] text-zinc-400 space-y-1">
                    <p className="font-semibold text-zinc-300">
                      🎯 Interactive P1 Demo Sequence:
                    </p>
                    <p className="text-[10px] text-zinc-500">
                      Follow these steps to experience persistent team memory in action:
                    </p>
                  </div>

                  <button
                    onClick={() => {
                      setMemoryEnabled(false);
                      setInputMessage(
                        "What queue system should I use for this new email job?"
                      );
                    }}
                    className="w-full p-2.5 rounded-xl border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-900 text-xs text-zinc-300 text-left transition-colors flex items-center justify-between"
                  >
                    <div>
                      <span className="font-semibold text-zinc-200">1. Ask with Memory OFF:</span>
                      <span className="text-zinc-400 block text-[11px]">
                        &quot;What queue system should I use for this new email job?&quot; (Generic answer)
                      </span>
                    </div>
                    <span className="text-zinc-500 ml-2">→</span>
                  </button>

                  <button
                    onClick={() => {
                      setMemoryEnabled(true);
                      setInputMessage(
                        "Our team standardized on BullMQ for background jobs."
                      );
                    }}
                    className="w-full p-2.5 rounded-xl border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-900 text-xs text-zinc-300 text-left transition-colors flex items-center justify-between"
                  >
                    <div>
                      <span className="font-semibold text-emerald-400">2. Retain with Memory ON:</span>
                      <span className="text-zinc-400 block text-[11px]">
                        &quot;Our team standardized on BullMQ for background jobs.&quot; (Retained)
                      </span>
                    </div>
                    <span className="text-zinc-500 ml-2">→</span>
                  </button>

                  <button
                    onClick={() => {
                      setMemoryEnabled(true);
                      handleNewConversation();
                      setInputMessage(
                        "What queue system should I use for this new email job?"
                      );
                    }}
                    className="w-full p-2.5 rounded-xl border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-900 text-xs text-zinc-300 text-left transition-colors flex items-center justify-between"
                  >
                    <div>
                      <span className="font-semibold text-indigo-400">3. In New Conversation:</span>
                      <span className="text-zinc-400 block text-[11px]">
                        Ask again — assistant recalls BullMQ decision!
                      </span>
                    </div>
                    <span className="text-zinc-500 ml-2">→</span>
                  </button>
                </div>
              </div>
            ) : (
              messages.map((msg) => {
                const isMemoryInformed =
                  msg.role === "assistant" &&
                  msg.memoriesUsed &&
                  msg.memoriesUsed.length > 0;

                return (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${
                      msg.role === "user" ? "items-end" : "items-start"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1 px-1">
                      <span className="text-[11px] font-semibold text-zinc-400">
                        {msg.role === "user" ? "You" : "ContextIQ Assistant"}
                      </span>
                      {isMemoryInformed && (
                        <span className="px-1.5 py-0.2 rounded text-[9px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                          🧠 Memory-Informed Response
                        </span>
                      )}
                      <span className="text-[10px] text-zinc-600">
                        {msg.timestamp}
                      </span>
                    </div>

                    {/* Message Bubble */}
                    <div
                      className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-sm leading-relaxed whitespace-pre-wrap ${
                        msg.role === "user"
                          ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/10 rounded-tr-sm"
                          : isMemoryInformed
                          ? "bg-zinc-900/90 border border-indigo-500/30 text-zinc-100 rounded-tl-sm shadow-md shadow-indigo-950/20"
                          : "bg-zinc-900 border border-zinc-800 text-zinc-100 rounded-tl-sm shadow-sm"
                      }`}
                    >
                      {msg.content}
                    </div>

                    {/* Assistant Metadata Indicators */}
                    {msg.role === "assistant" && (
                      <div className="mt-2 flex flex-wrap items-center gap-2 px-1">
                        {/* 1. Recall Indicator & Explanation */}
                        {msg.memoriesUsed && msg.memoriesUsed.length > 0 ? (
                          <div className="relative">
                            <button
                              onClick={() =>
                                setExpandedMemoryMsgId(
                                  expandedMemoryMsgId === msg.id ? null : msg.id
                                )
                              }
                              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-500/20 transition-colors shadow-sm"
                            >
                              <span>🧠</span>
                              <span>
                                {msg.memoriesUsed.length}{" "}
                                {msg.memoriesUsed.length === 1
                                  ? "memory"
                                  : "memories"}{" "}
                                used
                              </span>
                              <span className="text-[9px]">
                                {expandedMemoryMsgId === msg.id ? "▲" : "▼"}
                              </span>
                            </button>

                            {/* Recall Explanation Popover */}
                            {expandedMemoryMsgId === msg.id && (
                              <div className="absolute left-0 mt-2 z-20 w-80 sm:w-96 rounded-xl border border-zinc-800 bg-zinc-900 p-3.5 shadow-2xl space-y-2.5 text-xs animate-fadeIn">
                                <div className="font-semibold text-zinc-200 border-b border-zinc-800 pb-2 flex justify-between items-center">
                                  <span className="text-[11px] uppercase tracking-wider">
                                    Memories Used in Response
                                  </span>
                                  <span className="font-mono text-[10px] text-zinc-500">
                                    bank: contextiq-team
                                  </span>
                                </div>

                                <p className="text-[11px] text-zinc-400">
                                  The assistant recalled the following team
                                  decisions to align this answer:
                                </p>

                                <div className="space-y-2 max-h-48 overflow-y-auto">
                                  {msg.memoriesUsed.map((mem, i) => (
                                    <div
                                      key={mem.id || i}
                                      onClick={() => handleOpenInspector(mem)}
                                      className="group p-2.5 rounded-lg bg-zinc-950 border border-zinc-850 hover:border-indigo-500/40 cursor-pointer transition-all space-y-1"
                                    >
                                      <div className="flex items-center justify-between">
                                        <span
                                          className={`text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${getCategoryColor(
                                            mem.category
                                          )}`}
                                        >
                                          {mem.category || "decision"}
                                        </span>
                                        <span className="text-[10px] text-zinc-500 group-hover:text-indigo-400 transition-colors">
                                          Inspect →
                                        </span>
                                      </div>
                                      <p className="text-zinc-200 text-xs">
                                        {mem.text}
                                      </p>
                                    </div>
                                  ))}
                                </div>

                                <div className="pt-1.5 border-t border-zinc-800/80 text-[10px] text-zinc-500">
                                  <span>
                                    Current user instructions always take
                                    precedence over past memories.
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        ) : msg.memoryEnabled ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] text-zinc-500 bg-zinc-900 border border-zinc-800">
                            No relevant team memory
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] text-zinc-500 bg-zinc-900 border border-zinc-800">
                            ○ Memory OFF (Recall bypassed)
                          </span>
                        )}

                        {/* 2. Saved-Memory Indicator & Inspection Trigger */}
                        {msg.memoriesStored && msg.memoriesStored.length > 0 && (
                          <>
                            {msg.memoriesStored.map((m, idx) => {
                              const isSaved = m.status === "saved";
                              const catLabel = m.category || "decision";

                              return (
                                <button
                                  key={m.id || idx}
                                  onClick={() => handleOpenInspector(m)}
                                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border transition-all cursor-pointer ${
                                    isSaved
                                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20"
                                      : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                                  }`}
                                  title="Click to inspect retained memory"
                                >
                                  <span>{isSaved ? "✓" : "⚠"}</span>
                                  <span>
                                    {isSaved
                                      ? `✓ ${
                                          catLabel.charAt(0).toUpperCase() +
                                          catLabel.slice(1)
                                        } saved to team memory`
                                      : "⚠ Could not save to team memory"}
                                  </span>
                                  {isSaved && (
                                    <span className="text-[9px] opacity-70">
                                      🔍
                                    </span>
                                  )}
                                </button>
                              );
                            })}
                          </>
                        )}

                        {/* 3. Degraded Mode Warning */}
                        {msg.memoryStatus === "unavailable" && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30">
                            <span>⚠️</span> Memory service temporarily
                            unavailable
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}

            {/* In-Flight Thinking Indicator */}
            {isSending && (
              <div className="flex flex-col items-start space-y-1">
                <div className="flex items-center gap-2 mb-1 px-1">
                  <span className="text-[11px] font-semibold text-zinc-400">
                    ContextIQ Assistant
                  </span>
                </div>
                <div className="rounded-2xl rounded-tl-sm p-3.5 bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
                  <span>Thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Composer */}
          <div className="p-4 border-t border-zinc-800 bg-zinc-950">
            <form onSubmit={handleSendMessage} className="relative">
              <textarea
                ref={textareaRef}
                rows={2}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  user
                    ? "Ask ContextIQ or state an engineering decision..."
                    : "Sign in to chat with persistent team memory..."
                }
                className="w-full resize-none rounded-xl bg-zinc-900 border border-zinc-800 p-3 pr-24 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />

              <div className="absolute right-2.5 bottom-3.5 flex items-center gap-2">
                <button
                  type="submit"
                  disabled={isSending || !inputMessage.trim()}
                  className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:hover:bg-indigo-600 text-white text-xs font-semibold transition-all shadow-md shadow-indigo-600/20 flex items-center gap-1.5"
                >
                  {isSending ? (
                    <span>...</span>
                  ) : (
                    <>
                      <span>Send</span>
                      <span>↵</span>
                    </>
                  )}
                </button>
              </div>
            </form>
            <div className="flex justify-between items-center mt-2 text-[11px] text-zinc-500">
              <span>
                Press <kbd className="px-1 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">Enter</kbd> to send, <kbd className="px-1 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">Shift+Enter</kbd> for newline
              </span>
              <span className="font-mono text-[11px]">
                {memoryEnabled ? "🧠 Recall Active" : "⚪ Memory OFF (Bypassed)"}
              </span>
            </div>
          </div>
        </main>

        {/* Right Column / Mobile Drawer: Team Memory Sidebar */}
        <div
          className={`fixed lg:static inset-y-0 right-0 z-40 transform lg:transform-none transition-transform duration-300 ease-in-out ${
            mobileSidebarOpen ? "translate-x-0" : "translate-x-full lg:translate-x-0"
          }`}
        >
          <div className="h-full flex">
            {mobileSidebarOpen && (
              <div
                className="fixed inset-0 bg-black/60 lg:hidden -z-10"
                onClick={() => setMobileSidebarOpen(false)}
              />
            )}
            <MemorySidebar
              memories={memories}
              isLoading={memoriesLoading}
              isSeeding={isSeeding}
              status={memoriesStatus}
              onRefresh={() => fetchMemories()}
              onSeedDemo={handleSeedDemo}
              onSelectMemory={handleOpenInspector}
            />
          </div>
        </div>
      </div>

      {/* Memory Inspector Modal */}
      <MemoryInspectorModal
        memory={inspectedMemory}
        isOpen={isInspectorOpen}
        onClose={() => {
          setIsInspectorOpen(false);
          setInspectedMemory(null);
        }}
      />

      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={(loggedUser) => {
          setUser(loggedUser);
          showNotification("success", `Welcome back, ${loggedUser.email}!`);
          fetchMemories();
        }}
      />
    </div>
  );
}
