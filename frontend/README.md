# Fintech Intel Squad
### Autonomous Research · Compliance Audit · Verified Briefs

A multi-agent AI system that autonomously researches, audits and writes fintech intelligence briefs — with a human in the loop at every critical decision point.

Built with **LangGraph**, **FastAPI**, and **React**.

---

## What It Does

You ask a question. The squad goes to work.

A **Scout** searches the web across high-trust regional sources. A **Skeptic** audits the findings for quality, source trust and regulatory relevance — and sends the scout back if the answer isn't good enough. A **Writer** synthesises everything into a structured intelligence brief. At key checkpoints, a **human can approve, reject, or redirect** the entire research direction before the final brief is produced.

---



###Agent Roles

| **Scout** | Searches across regional fintech sources using Tavily. Accumulates findings across iterations.

| **Skeptic** | Audits research quality, verifies sources, checks for red flags, decides whether to loop or escalate.

| **Human Review** | Interrupts the graph and waits for human input before proceeding.

| **Writer** | Synthesises verified research into a structured `IntelligenceBrief`.

---

## Key Features

- **Human-in-the-Loop** — execution pauses for human approval at every audit checkpoint
- **Closed-loop verification** — the skeptic tracks all previously attempted queries and forces novel follow-ups
- **Region-aware auditing** — different compliance policies for NG, US, UK, EU and GLOBAL markets
- **Query-scoped red flags** — red flags are only applied when relevant to the query type
- **Full article extraction** — scout fetches complete article content, not just snippets
- **Real-time SSE streaming** — agent activity streams live to the frontend
- **Persistent review history** — all human decisions are visible throughout the session

---

## Tech Stack

**Backend**
- LangGraph — multi-agent orchestration and state management
- FastAPI — async API with Server-Sent Events streaming
- LangChain OpenAI — GPT-4o-mini for all agents
- Tavily — web search with domain filtering
- Pydantic — typed state and structured outputs

**Frontend**
- React — component-based UI
- EventSource API — real-time SSE stream handling
- Custom CSS with CSS variables for theming

---




## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key
- Tavily API key

### Backend Setup

```bash
cd ResearchAgents/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add environment variables
cp .env.example .env
# Fill in OPENAI_API_KEY and TAVILY_API_KEY

# Start the server
python -m uvicorn api:api --reload --port 8000
```

### Frontend Setup

```bash
cd ResearchAgents/frontend

npm install
npm start  # runs on http://localhost:3000
```

---

## Environment Variables

### Backend `.env`
```
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```

### Frontend `.env`
```
REACT_APP_API_URL=http://localhost:8000
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/run` | Start a new research session, returns `thread_id` |
| `GET` | `/stream/{thread_id}` | SSE stream — live agent activity |
| `POST` | `/review/{thread_id}` | Submit human verdict (approve / reject / comment) |
| `GET` | `/resume/{thread_id}` | SSE stream — resume after human review |

---

## Supported Markets

| Market | Policy Focus | Key Sources |
|---|---|---|
| 🇳🇬 NG | CBN circulars, SEC Nigeria, Naira stablecoin | cbn.gov.ng, nairametrics.com, techcabal.com |
| 🇺🇸 US | SEC filings, FinCEN updates, Series A-E funding | sec.gov, techcrunch.com, reuters.com |
| 🇬🇧 UK | FCA Consumer Duty, Open Banking, SDR labels | fca.org.uk, bankofengland.co.uk, finextra.com |
| 🇪🇺 EU | MiCA compliance, DORA audits, PSD3/PSR | esma.europa.eu, eba.europa.eu, ec.europa.eu |
| 🌍 GLOBAL | Cross-border trends, global funding | bloomberg.com, bis.org, fsb.org, finextra.com |

---

## Example Queries

```
"What are the latest CBN guidelines on Open Banking API standards 
 and which Nigerian fintechs have achieved compliance as of 2026?"

"Which African fintech companies closed Series B or above funding 
 rounds in Q1 2026 and what were the lead investors and valuations?"

"How are MiCA regulations affecting African and emerging market 
 fintechs seeking EU market access in 2026?"

"How is the CBN's agent banking exclusivity rule impacting OPay, 
 PalmPay and Moniepoint's market share in 2026?"
```


---

## Skills Demonstrated

- Multi-agent system design and orchestration
- Human-in-the-Loop patterns with LangGraph `interrupt()` and `update_state()`
- Async state management across graph interrupts and resumptions
- SSE streaming with FastAPI and React EventSource
- Prompt engineering for structured outputs and stopping criteria
- Region-aware compliance policy design
- Full-stack integration (FastAPI + React)

---