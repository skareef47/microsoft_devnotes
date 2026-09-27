export type MemoryCategory =
  | "preference"
  | "architecture"
  | "decision"
  | "incident"
  | "standard";

export interface MemoryItem {
  id: string;
  category: MemoryCategory | string;
  text: string;
  created_at?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  memoriesUsed?: MemoryItem[];
  memoriesStored?: MemoryItem[];
}

export interface ChatRequest {
  message: string;
  conversation_id: string;
  memory_enabled: boolean;
}

export interface ChatResponse {
  response: string;
  memory_enabled: boolean;
  memories_used: MemoryItem[];
  memories_stored: Record<string, unknown>[];
  memory_status: "available" | "unavailable" | "degraded";
}

export interface HealthResponse {
  api: string;
  database?: string;
  hindsight?: string;
  llm?: string;
}
