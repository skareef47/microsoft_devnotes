# ContextIQ 🧠

> **"This agent is more useful because it remembers."**

ContextIQ is a persistent-memory AI assistant for software engineering teams. It remembers durable engineering context—such as technology preferences, architectural decisions, previous incidents, successful fixes, known constraints, and team standards—across separate conversations using **Hindsight Cloud**.

---

## 🏛️ Architecture & Core Rules

```text
┌─────────────────┐       ┌─────────────────┐       ┌──────────────────┐
│ Next.js Frontend │ ───> │ FastAPI Backend │ ───> │ Hindsight Cloud  │
│ (TypeScript/TW) │ <─── │                 │       │ (Retain & Recall)│
└─────────────────┘       └────────┬────────┘       └──────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
             ┌──────▼──────┐               ┌──────▼──────┐
             │ PostgreSQL  │               │ LLM Provider│
             │(App state)  │               │(Gemini/OAI) │
             └─────────────┘               └─────────────┘
```

### Architectural Principles:
1. **Frontend Isolation**: The frontend **never** connects directly to Hindsight. All memory operations (Retain & Recall) are proxied and governed through the FastAPI backend.
2. **Server-Controlled Team Memory**: The MVP uses a shared team memory bank. The frontend is **never** allowed to supply an arbitrary `bank_id`. The bank is strictly resolved on the server side:
   ```text
   JWT → Authenticated User → Team Membership → Server-Controlled team_id → Authorized Hindsight bank_id
   ```
3. **Application State vs. Memory**: PostgreSQL is used strictly for application state (`users`, `teams`, `memberships`, `conversations`). Persistent memories reside exclusively in Hindsight.
4. **Deterministic Retention Gate**: A lightweight, deterministic keyword gate evaluates messages before Retain without introducing an expensive LLM classifier into the critical path.

---

## 📁 Repository Structure

```text
contextiq/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entrypoint & middleware
│   │   ├── config.py            # Environment configuration (Pydantic BaseSettings)
│   │   ├── database.py          # SQLAlchemy PostgreSQL/SQLite database session setup
│   │   ├── auth/                # JWT & password hashing utilities
│   │   │   ├── jwt.py
│   │   │   ├── passwords.py
│   │   │   └── routes.py
│   │   ├── agent/               # Agent orchestration & retention gating
│   │   │   ├── orchestrator.py
│   │   │   ├── retention_gate.py
│   │   │   └── context.py
│   │   ├── memory/              # Hindsight Cloud adapter & team bank resolver
│   │   │   ├── hindsight.py
│   │   │   └── bank_resolver.py
│   │   ├── llm/                 # Clean LLM provider abstraction (Gemini/OpenAI)
│   │   │   └── provider.py
│   │   └── api/                 # API route handlers
│   │       ├── health.py        # GET /api/health
│   │       ├── chat.py          # POST /api/chat
│   │       ├── memories.py      # GET /api/memories
│   │       └── demo.py          # POST /api/demo/seed
│   ├── tests/
│   │   └── test_health.py       # API health check test suite
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend container specification
│
├── frontend/
│   ├── app/                     # Next.js App Router (page.tsx, layout.tsx)
│   ├── components/              # Modular UI components
│   ├── lib/                     # Client API helpers
│   ├── types/                   # TypeScript interfaces
│   ├── package.json             # Node dependencies
│   └── Dockerfile               # Frontend container specification
│
├── docker-compose.yml           # Local dev multi-container stack (db, backend, frontend)
├── .env.example                 # Example environment variables (no hardcoded secrets)
├── .gitignore                   # Ignores .env, node_modules, .next, venvs, pycache
└── README.md                    # Setup and operational documentation
```

---

## ⚙️ Quickstart & Local Setup

### 1. Environment Configuration

Copy `.env.example` to `.env` in the root directory:

```bash
cp .env.example .env
```

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string (defaults to local SQLite if unconfigured).
- `JWT_SECRET`: Secret key for signing session tokens.
- `HINDSIGHT_API_KEY`: API credentials for Hindsight Cloud.
- `HINDSIGHT_BANK_ID`: Shared team memory bank ID.
- `LLM_PROVIDER`: `gemini` or `openai`.
- `LLM_API_KEY`: API key for the chosen LLM provider.
- `LLM_MODEL`: e.g. `gemini-1.5-flash` or `gpt-4o-mini`.

---

### 2. Running the Backend Independently

1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # On macOS / Linux:
   python3 -m venv .venv
   source .venv/bin/activate

   # On Windows (PowerShell):
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
5. Verify health:
   ```bash
   curl http://localhost:8000/api/health
   # Expected response: {"api": "ok"}
   ```

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

---

### 3. Running the Frontend Independently

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 4. Running via Docker Compose

To start the database, backend, and frontend together:

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Health check: `http://localhost:8000/api/health`

---

## 🧪 Testing

Run backend automated tests:

```bash
cd backend
pytest
```

---

## 🔒 Security Principles

- **No Secrets in Source**: All API credentials and secrets are managed strictly through environment variables.
- **Backend-Only Keys**: Hindsight and LLM API keys are never bundled into the client build.
- **Team Isolation**: Bank resolution is server-side and immutable from frontend request parameters.
