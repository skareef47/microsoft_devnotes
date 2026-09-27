# ContextIQ 🧠

> **"A persistent-memory AI engineering assistant powered by Hindsight."**

ContextIQ is a persistent-memory AI assistant built specifically for software engineering teams. It remembers durable engineering context—architectural decisions, technology preferences, library standards, and past incident solutions—across separate conversations using a self-hosted **Hindsight** memory engine.

---

## 1. Problem

Standard AI assistants are stateless across conversations. When a developer asks:
> *"What queue system should I use for this new email job?"*

A generic assistant gives a generic list of options (RabbitMQ, Redis, Kafka, Celery, SQS). It has no memory that two weeks ago, their engineering team standardized on **BullMQ** after suffering operational issues with previous queues. The developer must repeatedly copy-paste context, leading to architectural fragmentation, repeated mistakes, and friction.

---

## 2. Solution

ContextIQ connects an engineering team to a shared, persistent memory bank powered by **Hindsight**.
1. When an engineer states a durable decision (*"Our team standardized on BullMQ for background jobs"*), ContextIQ automatically **Retains** it into the team bank.
2. In subsequent or separate conversations, when any engineer asks a technical question, ContextIQ **Recalls** relevant team decisions and injects them as authoritative background context.
3. The response aligns with existing team practices, displaying an inspectable indicator: `🧠 1 memory used`.

---

## 3. Why Memory Matters

Engineering velocity depends on shared context. ContextIQ ensures that:
- **Decisions Persist**: Architectural choices survive beyond single chat threads and browser tabs.
- **Context is Shared**: Decisions made by one engineer inform answers given to teammates.
- **Explainability**: Every memory-informed answer provides a direct link to the exact recalled memory item, category, and timestamp.
- **Safety & Precedence**: Current user instructions always take precedence over past memories. Memories provide context; they never override explicit user choices.

---

## 4. Key Features

- **Team Memory Sidebar**: Real-time view of persistent items in the team bank, categorized by `DECISION`, `PREFERENCE`, `ARCHITECTURE`, `CONVENTION`, and `INCIDENT`.
- **Memory Detail / Inspector**: Lightweight inspector modal displaying exact Hindsight UUIDs, categories, timestamps, and source links without data fabrication.
- **Recall Explanation**: Clicking `🧠 X memories used` surfaces the exact memories that influenced the response.
- **Saved-Memory Feedback**: Real-time `✓ Decision saved to team memory` feedback with 1-click inspection of newly retained context.
- **Memory ON/OFF Toggle**: Instant toggle between contextual memory mode and transient generic mode. When OFF, Hindsight Recall is strictly bypassed.
- **Degraded Mode Resiliency**: If the memory service is temporarily unavailable, chat proceeds smoothly without crashing, informing the user with clear degraded status.
- **Zero-Key Local Dev**: Ships with a deterministic mock LLM fallback, enabling full end-to-end evaluation without requiring external paid API credits.

---

## 5. Architecture

```text
┌──────────────────────┐
│      Developer       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   ContextIQ Web UI   │
│     (Next.js)        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      FastAPI         │
│  Agent Orchestrator  │
└───────┬───────┬──────┘
        │       │
        │       ▼
        │   ┌───────────┐
        │   │    LLM    │ (Gemini / OpenAI / Mock Fallback)
        │   └───────────┘
        ▼
┌──────────────────────┐
│      Hindsight       │
│  Shared Team Memory  │ (ghcr.io/vectorize-io/hindsight:latest)
└──────────────────────┘
```

### Architectural Principles:
1. **Frontend Isolation**: The Next.js client **never** talks directly to Hindsight. All memory calls are governed and authenticated through FastAPI.
2. **Server-Side Bank Resolution**: The frontend cannot specify an arbitrary bank ID. The backend maps the authenticated JWT user to the authorized team bank (`contextiq-team`).
3. **Single Memory Source of Truth**: Application state (users, teams, tokens) resides in PostgreSQL/SQLite. Durable engineering memory resides exclusively in Hindsight.
4. **Deterministic Retention Gate**: A regex/keyword gate detects durable engineering signals without adding costly LLM classification latency to the critical path.

---

## 6. Hindsight Integration

The integration with self-hosted Hindsight uses the official REST API endpoints:

```text
User Message
     │
     ▼
Retention Gate
     ├── Durable Context Detected ──> Hindsight RETAIN ──> Stored in Bank
     │
Memory ON?
     ├── YES ────────────────────────> Hindsight RECALL ──> Augmented Prompt ──> LLM ──> Contextual Answer
     └── NO  ────────────────────────> (Recall Bypassed) ─> Clean Prompt ─────> LLM ──> Generic Answer
```

- **RETAIN** (`POST /v1/default/banks/{bank_id}/memories`):
  Called when a message contains durable engineering statements (e.g. *"We standardized on..."*, *"Our architecture uses..."*). Stores the text, category, and metadata into Hindsight.
- **RECALL** (`POST /v1/default/banks/{bank_id}/memories/recall`):
  Called when Memory is ON to retrieve relevant memories. Normalized, deduplicated, and ranked so relevant context appears first.
- **LIST** (`GET /v1/default/banks/{bank_id}/memories/list`):
  Lists all persistent memories in the bank for the Team Memory Sidebar and Inspector.

---

## 7. Memory ON vs Memory OFF

| Feature | 🧠 Memory ON | ○ Memory OFF |
| :--- | :--- | :--- |
| **Recall Behavior** | Calls Hindsight Recall for relevant memories | Completely bypasses Hindsight Recall |
| **Context Assembly** | Injects recalled team memories into background prompt | Standard prompt without past context |
| **Response Style** | Team-aligned (e.g. recommends BullMQ, FastAPI, PostgreSQL) | Standard general industry options |
| **Response Pill** | Displays `🧠 X memories used` (inspectable) | Displays `○ Memory OFF (Bypassed)` |
| **Retain Behavior** | Active (retains durable engineering statements) | Retain evaluates statements if submitted |

---

## 8. Canonical Demo Flow

A reviewer can experience persistent team memory in 6 clear steps:

1. **Step 1 — Login**: Sign in using the one-click **"Sign In as Demo Engineer"** button (`engineer@contextiq.dev`).
2. **Step 2 — Memory OFF**: Switch to `○ Memory OFF`. Ask:
   > *"What queue system should I use for this new email job?"*
   - Assistant provides a generic list of industry options.
   - Indicator displays `○ Memory OFF (Recall bypassed)`.
3. **Step 3 — Memory ON & Retain**: Switch to `🧠 Memory ON`. Send:
   > *"Our team standardized on BullMQ for background jobs."*
   - Assistant acknowledges and displays `✓ Decision saved to team memory`.
   - The memory card immediately appears in the Team Memory sidebar.
4. **Step 4 — New Conversation & Recall**: Click `➕ New conversation`. Ask:
   > *"What queue system should I use for this new email job?"*
   - Assistant answers with BullMQ context based on team standard.
   - Indicator displays `🧠 1 memory used`.
5. **Step 5 — Inspect Memory**: Click `🧠 1 memory used` or click the memory in the sidebar:
   - Memory Inspector opens, revealing the exact statement, category (`DECISION`), real Hindsight UUID, timestamp, and bank name (`contextiq-team`).
6. **Step 6 — Persistence Verification**: Click `➕ New conversation` again. Ask:
   > *"What queue was chosen for background tasks?"*
   - Assistant continues to recall BullMQ, proving memory persists across conversations.

---

## 9. Tech Stack

- **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind CSS, Lucide icons
- **Backend**: FastAPI, Python 3.8+, Pydantic v2, SQLAlchemy, Uvicorn
- **Memory Engine**: Self-hosted Hindsight (`ghcr.io/vectorize-io/hindsight:latest`)
- **Database**: PostgreSQL 16 (Docker) / SQLite (local dev fallback)
- **Containerization**: Docker Compose

---

## 10. Local Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.8+ (for local backend dev)

### Option A: Docker Compose (All Services)
```bash
# 1. Clone & copy environment variables
cp .env.example .env

# 2. Launch the entire stack
docker compose up -d

# Services will be available at:
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000 (Docs: /docs)
# Hindsight: http://localhost:8888 (Health: /health)
```

### Option B: Local Development
```bash
# 1. Start self-hosted Hindsight
docker compose up -d hindsight

# 2. Start Backend
cd backend
python -m venv .venv
# Activate: source .venv/bin/activate (Linux/Mac) or .venv\Scripts\Activate.ps1 (Windows)
pip install -r requirements.txt
uvicorn app.main:app --port 8000

# 3. Start Frontend
cd ../frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 11. Environment Variables

Configure `.env` in project root:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./contextiq.db` |
| `JWT_SECRET` | Secret key for signing JWT tokens | `dev_jwt_secret_min_32_chars` |
| `HINDSIGHT_BASE_URL` | Self-hosted Hindsight API URL | `http://localhost:8888` |
| `HINDSIGHT_API_KEY` | Hindsight API key (blank for self-hosted) | `""` |
| `HINDSIGHT_BANK_ID` | Default team memory bank | `contextiq-team` |
| `LLM_PROVIDER` | LLM provider (`gemini`, `openai`, `mock`) | `mock` (or `gemini`) |
| `LLM_API_KEY` | API key for LLM provider | `""` (mock requires no key) |
| `LLM_MODEL` | Model identifier | `gemini-1.5-flash` |
| `NEXT_PUBLIC_API_URL`| Backend URL for frontend | `http://localhost:8000` |

---

## 12. Testing

Run full automated backend test suite:
```bash
cd backend
pytest -rs
```
*Current test suite: 22 passed.*

Run frontend linter and production build:
```bash
cd frontend
npm run lint
npm run build
```

Run end-to-end demo verification:
```bash
python scripts/verify_final_demo.py
```

---

## 13. Deployment

Production deployment is fully containerized via `docker-compose.yml`:
- Persistent storage for Hindsight is mapped to Docker volume `hindsight-data:/home/hindsight/.pg0`.
- Application state is persisted to Docker volume `pgdata:/var/lib/postgresql/data`.
- Backend gracefully handles restart recovery and verifies connectivity on startup.
- All secrets remain server-side and are never exposed to the client.
