# ✈️ TripMate AI — A Multi-Agent Travel Planner with LangGraph

An open-source AI travel planner that turns a natural-language trip request into a practical travel plan with flight suggestions, hotel ideas, and a day-by-day itinerary. The project uses a multi-agent workflow built with LangGraph, LangChain, and FastAPI.

## Why this project?

Planning a trip usually means jumping between multiple websites, tools, and spreadsheets. This project brings that flow into one experience by combining:

- a flight-research agent,
- a hotel-research agent,
- an itinerary-planning agent, and
- a final response agent,

all coordinated through an async LangGraph workflow.

## Features

- ✈️ Flight research using AviationStack via MCP
- 🏨 Hotel suggestions using Tavily search via MCP
- 🧠 Multi-agent orchestration with LangGraph
- 📝 Structured travel itinerary generation
- 🌐 FastAPI backend with a clean web interface
- 💾 Conversation state persistence using PostgreSQL (async)
- ⚡ LLM-powered responses with Groq

## Tech Stack

- Python 3.11+
- FastAPI + Uvicorn
- Jinja2 + HTML/CSS/JavaScript frontend
- LangGraph (async workflow)
- LangChain
- Groq LLMs (`openai/gpt-oss-20b`)
- PostgreSQL with `psycopg3` async driver
- Tavily API (remote MCP via `streamable_http`)
- AviationStack API (local MCP via `uvx aviationstack-mcp`)
- MCP via `langchain-mcp-adapters`

## Project Structure

```text
.
├── app.py              # FastAPI entry point — serves UI and /api/travel
├── backend.py          # LangGraph async multi-agent workflow
├── mcp_client.py       # MCP client helpers (Tavily + AviationStack)
├── requirements.txt    # Python dependencies
├── static/
│   ├── style.css       # Frontend styles
│   └── script.js       # Frontend logic
├── templates/
│   └── index.html      # Main UI template
└── tools/
    ├── flight_tool.py  # Standalone AviationStack flight search utility
    └── tavily_tool.py  # Standalone Tavily search utility
```

## How the Workflow Works

```
User Request
     │
     ▼
flight_agent  →  Calls AviationStack MCP (airports, airlines, taxes)
                 Generates flight guidance via LLM
     │
     ▼
hotel_agent   →  Calls Tavily MCP search
                 Returns hotel suggestions
     │
     ▼
itinerary_agent → Combines flight + hotel info
                  Generates day-by-day itinerary via LLM
     │
     ▼
final_agent   →  Formats a polished final travel response via LLM
     │
     ▼
  Response returned to user
```

All agents are `async` and run on the same asyncio event loop as FastAPI/Uvicorn. Checkpointing uses `AsyncPostgresSaver` with an `AsyncConnectionPool`.

## Prerequisites

Before running locally:

- Python 3.11 or newer
- PostgreSQL running and accessible
- `uvx` installed for local AviationStack MCP (`pip install uv` or see [uv install guide](https://docs.astral.sh/uv/getting-started/installation/))
- API keys for:
  - Groq
  - Tavily
  - AviationStack

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
GROQ_API_KEY=your_groq_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
DEFAULT_ORIGIN_IATA=DAC
```

`DEFAULT_ORIGIN_IATA` is the IATA code used as the default departure airport when the user only specifies a destination (e.g. "Plan a Japan trip"). Change it to your home airport.

## Installation

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the App

```bash
python app.py
```

Open your browser at:

```
http://127.0.0.1:8000/
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main UI |
| GET | `/health` | Health check |
| POST | `/api/travel` | Submit a travel request |
| GET | `/static/{file}` | Static assets |

### Example request

```bash
curl -X POST http://127.0.0.1:8000/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message": "Plan a 7-day Japan trip from Bangladesh under 2 lakhs."}'
```

### Example response

```json
{
  "success": true,
  "thread_id": "user_abc123",
  "answer": "## Trip Summary\n...",
  "flight_results": "...",
  "hotel_results": "...",
  "itinerary": "...",
  "llm_calls": 4
}
```

## MCP Integration

| Service | Transport | Details |
|---------|-----------|---------|
| Tavily | `streamable_http` | `https://mcp.tavily.com/mcp/` |
| AviationStack | `stdio` | `uvx aviationstack-mcp` |

The MCP client (`mcp_client.py`) exposes two async helpers used by the agents:

- `tavily_mcp_search(query)` — hotel and travel search
- `aviation_mcp_call(tool_name, tool_args)` — airports, airlines, taxes

## Known Limitations

- **Groq TPM limit**: The free/on-demand tier for `openai/gpt-oss-20b` is capped at 8,000 tokens per minute. Inputs to each agent are truncated to stay within this limit. Upgrading to the Groq Dev tier removes this constraint.
- **AviationStack free tier**: Returns live flight status data only — no ticket prices. Pricing requires a paid AviationStack plan or a separate flight-pricing API (e.g. Amadeus).
- **Static files**: Uses a custom route handler instead of `StaticFiles` mount due to a compatibility issue between `starlette 1.7.0` and `anyio 4.x` on Python 3.14.

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Open a pull request

## Acknowledgments

Built with LangGraph, LangChain, FastAPI, Groq, Tavily, and AviationStack.
