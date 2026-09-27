import {
  AuthResponse,
  ChatRequest,
  ChatResponse,
  HealthResponse,
  SeedResponse,
  TeamMemoriesResponse,
  UserProfile,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TOKEN_KEY = "contextiq_access_token";

export function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearStoredToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
}

function getAuthHeaders(token?: string | null): HeadersInit {
  const t = token || getStoredToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (t) {
    headers["Authorization"] = `Bearer ${t}`;
  }
  return headers;
}

/**
 * Fetch backend health status from GET /api/health.
 */
export async function getHealthStatus(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/health`, {
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error(`Health check failed with status: ${res.status}`);
  }

  return res.json();
}

/**
 * Register a new user.
 */
export async function registerUser(payload: {
  email: string;
  password: string;
  full_name?: string;
}): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Registration failed with status ${res.status}`);
  }

  setStoredToken(data.access_token);
  return data;
}

/**
 * Login user and retrieve JWT token.
 */
export async function loginUser(payload: {
  email: string;
  password: string;
}): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Login failed with status ${res.status}`);
  }

  setStoredToken(data.access_token);
  return data;
}

/**
 * Fetch authenticated user profile.
 */
export async function getCurrentUserProfile(token?: string | null): Promise<UserProfile> {
  const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getAuthHeaders(token),
  });

  if (!res.ok) {
    throw new Error(`Session expired or unauthorized (${res.status})`);
  }

  return res.json();
}

/**
 * Send chat message to backend POST /api/chat.
 */
export async function sendChatMessage(
  req: ChatRequest,
  token?: string | null
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: getAuthHeaders(token),
    body: JSON.stringify(req),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Chat request failed with status: ${res.status}`);
  }

  return data;
}

/**
 * List team memories from backend GET /api/memories.
 */
export async function getTeamMemories(token?: string | null): Promise<TeamMemoriesResponse> {
  const res = await fetch(`${API_BASE_URL}/api/memories`, {
    cache: "no-store",
    headers: getAuthHeaders(token),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Failed to fetch memories: ${res.status}`);
  }

  return data;
}

/**
 * Seed deterministic demo memories directly into Hindsight via POST /api/demo/seed.
 */
export async function seedDemoMemories(token?: string | null): Promise<SeedResponse> {
  const res = await fetch(`${API_BASE_URL}/api/demo/seed`, {
    method: "POST",
    headers: getAuthHeaders(token),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || `Failed to seed demo memories: ${res.status}`);
  }

  return data;
}
