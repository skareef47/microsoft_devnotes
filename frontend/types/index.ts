export type MemoryCategory =
  | "decision"
  | "preference"
  | "fact"
  | "lesson"
  | "convention"
  | "architecture"
  | "incident"
  | "standard"
  | "other";

export interface MemoryItem {
  id: string;
  category: MemoryCategory | string;
  text: string;
  status?: string;
  created_at?: string | null;
  source?: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  memoryEnabled?: boolean;
  memoriesUsed?: MemoryItem[];
  memoriesStored?: MemoryItem[];
  memoryStatus?: "available" | "unavailable" | "disabled";
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
  memories_stored: MemoryItem[];
  memory_status: "available" | "unavailable" | "disabled";
}

export interface UserProfile {
  user_id: string;
  email: string;
  full_name?: string;
  team_id: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  team_id: string;
}

export interface TeamMemoriesResponse {
  team_id: string;
  bank_id: string;
  count: number;
  memories: MemoryItem[];
  status: string;
}

export interface SeedResponse {
  status: string;
  message: string;
  seeded_count: number;
  bank_id: string;
  items: unknown[];
}

export interface HealthResponse {
  api: string;
  database?: string;
  hindsight?: string;
  llm?: string;
}
