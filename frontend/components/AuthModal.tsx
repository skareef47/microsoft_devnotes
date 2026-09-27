"use client";

import React, { useState } from "react";
import { loginUser, registerUser } from "@/lib/api";
import { UserProfile } from "@/types";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: UserProfile) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isRegister) {
        const res = await registerUser({
          email,
          password,
          full_name: fullName || undefined,
        });
        onSuccess({
          user_id: res.user_id,
          email: res.email,
          team_id: res.team_id,
          full_name: fullName || undefined,
        });
      } else {
        const res = await loginUser({ email, password });
        onSuccess({
          user_id: res.user_id,
          email: res.email,
          team_id: res.team_id,
        });
      }
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        const msg = err.message;
        if (msg.includes("401") || msg.toLowerCase().includes("invalid")) {
          setError("Invalid email or password.");
        } else if (msg.includes("already exists")) {
          setError("An account with this email address already exists.");
        } else {
          setError(msg);
        }
      } else {
        setError("Invalid email or password.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSignIn = async () => {
    setLoading(true);
    setError(null);
    const demoEmail = "engineer@contextiq.dev";
    const demoPassword = "secure_password_123";

    try {
      // Try login first
      try {
        const res = await loginUser({ email: demoEmail, password: demoPassword });
        onSuccess({
          user_id: res.user_id,
          email: res.email,
          team_id: res.team_id,
          full_name: "ContextIQ Demo Engineer",
        });
        onClose();
        return;
      } catch {
        // If login failed, register demo engineer
        const res = await registerUser({
          email: demoEmail,
          password: demoPassword,
          full_name: "ContextIQ Demo Engineer",
        });
        onSuccess({
          user_id: res.user_id,
          email: res.email,
          team_id: res.team_id,
          full_name: "ContextIQ Demo Engineer",
        });
        onClose();
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Quick sign-in failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-md rounded-2xl border border-zinc-800 bg-zinc-900 p-6 sm:p-8 shadow-2xl shadow-black/80 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">🧠</span>
            <h2 className="text-lg font-bold text-white">
              {isRegister ? "Create ContextIQ Account" : "Sign in to ContextIQ"}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-200 text-sm font-semibold p-1"
          >
            ✕
          </button>
        </div>

        <p className="text-xs text-zinc-400">
          Authenticate to access your team&apos;s persistent Hindsight memory bank.
        </p>

        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Engineer"
                className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-100 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="engineer@contextiq.dev"
              className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-100 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 rounded-lg bg-zinc-950 border border-zinc-800 text-zinc-100 text-sm focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-colors shadow-lg shadow-indigo-600/20 disabled:opacity-50"
          >
            {loading ? "Processing..." : isRegister ? "Create Account" : "Sign In"}
          </button>
        </form>

        <div className="relative flex items-center justify-center my-4">
          <div className="border-t border-zinc-800 w-full" />
          <span className="bg-zinc-900 px-3 text-[11px] text-zinc-500 uppercase tracking-wider">
            or
          </span>
        </div>

        {/* Quick Demo Sign In */}
        <button
          onClick={handleDemoSignIn}
          disabled={loading}
          className="w-full py-2 px-4 rounded-lg bg-zinc-800/80 hover:bg-zinc-800 border border-zinc-700/60 text-xs font-medium text-zinc-200 transition-colors flex items-center justify-center gap-2"
        >
          <span>⚡</span> Quick Sign In as Demo Engineer
        </button>

        <div className="text-center pt-2">
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError(null);
            }}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
          >
            {isRegister
              ? "Already have an account? Sign In"
              : "Don't have an account? Create one"}
          </button>
        </div>
      </div>
    </div>
  );
};
