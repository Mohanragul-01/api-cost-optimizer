# AI-Assisted API Cost Optimizer

Project that monitors multi-LLM API usage in real time,
controls costs using token estimation, priority queuing, and circuit breaking,
and surfaces AI-generated routing recommendations via an embedded Llama 3.3 analysis layer.

![Dashboard demo](api-cost-optimizer.mp4)

---

## What It Does

Most teams using LLM APIs have no visibility into what they are spending, which
calls are failing, or whether a cheaper model could do the same job. This project
solves that with four systems working together:

| System            | What it does                                                                     |
| ----------------- | -------------------------------------------------------------------------------- |
| Token Estimator   | Counts tokens and calculates cost _before_ each API call using tiktoken          |
| Priority Queue    | Ranks pending calls by urgency ÷ cost — urgent cheap calls go first              |
| Circuit Breaker   | Blocks calls to a failing provider after error rate exceeds 50% in 60s           |
| AI Analysis Layer | Reads the last 100 call logs and returns routing suggestions + projected savings |

---

## Tech Stack

| Layer      | Tool                                 | Why                                                                          |
| ---------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| Backend    | Python 3.11 + Flask                  | Lightweight, readable, right-weight for this API surface                     |
| Database   | SQLite                               | Zero setup, file-based, sufficient for portfolio-scale log storage           |
| AI Layer   | OpenRouter → Llama 3.3 70B           | Free tier, avoids using paid OpenAI for the analysis layer itself            |
| Frontend   | React 18 + TypeScript                | Type-safe API response handling; TS catches shape mismatches at compile time |
| Styling    | Tailwind CSS                         | Utility-first; no context switching between CSS files and components         |
| Deployment | Render (backend) + Vercel (frontend) | Both have free tiers; Render runs Python natively                            |

---

## Architecture

Seed script (mock logs)
↓
Flask Backend
├── Token Estimator — tiktoken + pricing constants → cost before call
├── Priority Queue — heapq ranked by urgency / estimated_cost
├── Circuit Breaker — CLOSED → OPEN → HALF_OPEN per provider, persisted to SQLite
└── SQLite — stores every call: model, tokens, cost, latency, status
↓
AI Analysis Layer
└── OpenRouter (Llama 3.3) reads log summary → returns JSON recommendations
↓
Flask REST API (4 endpoints)
↓
React + TypeScript Dashboard
├── Budget Gauge — spend vs mock budget, color-coded progress bar
├── Call Log Table — paginated, sortable by timestamp
├── Circuit Breaker Panel — green / yellow / red per provider, pulses when OPEN
└── AI Recommendation Card — triggered on demand, shows suggestions + savings

---

## Project Structure

root/
├── backend/
│ ├── app.py # Flask entry point, CORS, blueprint registration
│ ├── constants.py # All config values and pricing tables — never hardcoded inline
│ ├── estimator.py # estimate_tokens(prompt, model) → cost dict
│ ├── priority_queue.py # CostAwarePriorityQueue — thread-safe heapq wrapper
│ ├── circuit_breaker.py # CircuitBreaker — 3-state FSM persisted to SQLite
│ ├── requirements.txt # All Python dependencies
│ ├── render.yaml # Render deployment config
│ ├── db/
│ │ ├── schema.py # Table definitions + get_connection()
│ │ └── seed.py # Generates 75 realistic mock call rows
│ └── routes/
│ ├── stats.py # GET /api/stats
│ ├── calls.py # GET /api/calls (paginated)
│ ├── circuit_breakers.py # GET /api/circuit-breakers
│ └── analyze.py # POST /api/analyze → Llama 3.3 → validated JSON
├── frontend/
│ ├── src/
│ │ ├── config.ts # API base URL — switches between local and deployed
│ │ ├── App.tsx # Root layout, shared data fetching, 30s polling
│ │ ├── types/
│ │ │ └── api.ts # TypeScript interfaces for every API response shape
│ │ └── components/
│ │ ├── BudgetGauge.tsx
│ │ ├── CallLogTable.tsx
│ │ ├── CircuitBreakerPanel.tsx
│ │ └── AIRecommendations.tsx
│ ├── vercel.json # Vercel deployment config
│ └── tailwind.config.js
└── README.md

---

## Run Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- A free [OpenRouter API key](https://openrouter.ai/keys)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/api-cost-optimizer.git
cd api-cost-optimizer
```

### 2. Backend setup

```bash
cd backend

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your OpenRouter key
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Create tables and seed mock data
python db/schema.py
python db/seed.py

# Start Flask
python app.py
```

Flask runs at `http://localhost:5000`

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

React runs at `http://localhost:5173`

### 4. Open the dashboard

Navigate to `http://localhost:5173` in your browser.

---

## API Endpoints

| Method | Endpoint                         | Description                                         |
| ------ | -------------------------------- | --------------------------------------------------- |
| GET    | `/api/stats`                     | Budget summary, total spend, call counts            |
| GET    | `/api/calls?page=1&page_size=20` | Paginated call log, newest first                    |
| GET    | `/api/circuit-breakers`          | State per provider (CLOSED / OPEN / HALF_OPEN)      |
| POST   | `/api/analyze`                   | Triggers Llama 3.3 analysis, returns validated JSON |

### Example — `/api/stats`

```json
{
  "mock_budget_usd": 10.0,
  "total_spend_usd": 0.031842,
  "budget_remaining": 9.968158,
  "budget_used_pct": 0.32,
  "total_calls": 75,
  "success_count": 45,
  "error_count": 12
}
```

### Example — `/api/analyze`

```json
{
  "summary": "Spend is low but error rate on gpt-4o is elevated at 28%.",
  "recommendations": [
    {
      "title": "Route low-urgency calls to Llama 3.3",
      "detail": "Urgency 1-2 calls currently sent to gpt-4o can be served by llama-3.3-70b at 80% lower cost.",
      "estimated_saving_usd": 0.0041
    }
  ],
  "projected_savings_usd": 0.0041
}
```

---

## Deploy to Render + Vercel

### Step 1 — Deploy backend to Render

1. Push your repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → connect your repo
3. Set root directory to `backend/`
4. Render auto-detects `render.yaml` — no manual config needed
5. In Render dashboard → Environment → add:
   - `OPENROUTER_API_KEY` = your key
6. Copy your Render URL: `https://your-backend.onrender.com`

### Step 2 — Deploy frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → New Project → connect your repo
2. Set root directory to `frontend/`
3. In Vercel → Settings → Environment Variables → add:
   - `VITE_API_BASE` = `https://your-backend.onrender.com`
4. Deploy. Copy your Vercel URL: `https://your-app.vercel.app`

### Step 3 — Wire CORS

1. In Render dashboard → Environment → add:
   - `ALLOWED_ORIGIN` = `https://your-app.vercel.app`
2. Redeploy backend on Render (Manual Deploy button)

Done — your live dashboard now talks to your live backend with CORS locked to your domain.

---

## Core Concepts Used

**Token estimation** — tiktoken encodes the prompt string into tokens using the
model's actual tokenizer. Cost = `(token_count / 1000) × per_token_price`.
Completion tokens are unknown before the call so we estimate at 25% of prompt length.

**Priority queue** — Python's `heapq` module implements a min-heap. We negate the
score `urgency / cost` so the highest-value call surfaces first. A `threading.Lock`
wraps every push and pop because APScheduler runs on a background thread.

**Circuit breaker** — a finite state machine with three states. CLOSED means normal
operation. If error rate exceeds 50% in a 60-second window, it trips to OPEN and
blocks all calls. After 30 seconds it moves to HALF_OPEN and allows one test call
through. A clean result resets to CLOSED; another failure returns to OPEN.
State is persisted to SQLite so Flask restarts don't lose it.

**Structured LLM output** — the prompt instructs Llama 3.3 to return only a JSON
object matching a defined schema. The response is stripped of markdown fences,
parsed with `json.loads`, and validated for required keys before any data reaches
the frontend. Malformed output returns a 502 with a safe error message.

---

## Known Limitations (by design — MVP scope)

- Mock logs only — no real LLM calls are proxied through the optimizer
- No authentication — single-user localhost/demo use only
- Budget limit is hardcoded — not user-configurable in the UI
- No live streaming — token counts update on page refresh or 30s poll
- No prompt rewriting — AI suggests changes, does not apply them
