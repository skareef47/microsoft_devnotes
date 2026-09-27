import { ChatRequest, ChatResponse, HealthResponse } from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
 * Send chat message to backend POST /api/chat.
 */
export async function sendChatMessage(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    throw new Error(`Chat request failed with status: ${res.status}`);
  }

  return res.json();
}

/**
 * List team memories from backend GET /api/memories.
 */
export async function getTeamMemories(): Promise<{
  team_id: string;
  bank_id: string;
  count: number;
  memories: unknown[];
}> {
  const res = await fetch(`${API_BASE_URL}/api/memories`, {
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch memories: ${res.status}`);
  }

  return res.json();
}
