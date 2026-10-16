# InsightAgent — Multi-Step AI Research Agent

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/langchain-core-green)
![Pattern](https://img.shields.io/badge/pattern-ReAct-purple)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

An **AI agent** that investigates open-ended questions with **multi-step reasoning and
tool use**. Give it a decision to make — it searches the web, summarizes what it finds,
reasons step by step, and returns a **structured decision brief** (recommendation, key
findings, options compared, risks, sources).

## Problem statement

LLMs answer from frozen training data and can't browse, compare live options, or show
their work. InsightAgent closes that gap with an explicit **ReAct loop** (Thought →
Action → Observation): the agent plans, calls tools, reads the results, and only then
commits to an answer — with every step visible in the trajectory.

## Features

- 🔁 Transparent **ReAct loop** — no framework magic; every Thought/Action/Observation is printed and saved
- 🔍 **Web search tool** (DuckDuckGo, no API key needed) for current information
- 📝 **Summarization tool** (LLM) to condense long search results before deciding
- 📋 **Decision brief output**: recommendation, key findings, options compared, risks, sources
- 🛡️ Robust parsing: unknown tools and tool errors become observations, not crashes
- ⚙️ Tunable via `.env` (model, temperature, max steps) and `--max-steps` flag

## Architecture

```
                    ┌─────────────────────┐
                    │   Research question │
                    └──────────┬──────────┘
                               ▼
              ┌────────────────────────────────┐
              │  ReAct loop (max 8 steps)      │
              │  Thought → Action → Observation│
              └──┬───────────┬─────────────┬───┘
                 ▼           ▼             ▼
          ┌────────────┐ ┌─────────┐ ┌────────────┐
          │ web_search │ │summarize│ │    LLM     │
          │(DuckDuckGo)│ │  (LLM)  │ │  reasoning │
          └────────────┘ └─────────┘ └────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   Decision brief    │
                    │ Recommendation +    │
                    │ findings + sources  │
                    └─────────────────────┘
```

**Flow:** the agent receives the task plus the full trajectory so far, emits either a
`Thought/Action/Action Input` triple or a `Final Answer`, the chosen tool runs, and its
output is appended as an `Observation`. The loop ends when the agent outputs a final
answer or hits `MAX_STEPS`. The whole trajectory is printed live and saved as a
markdown report.

## Project structure

```
insight-agent/
├── main.py                  # CLI: research "<question>" [--max-steps N]
├── requirements.txt
├── .env.example
├── src/
│   ├── config.py            # settings + validation
│   ├── tools.py             # web_search + summarize tool definitions
│   └── agent.py             # ReAct loop, step parser, InsightAgent class
└── examples/
    ├── sample_outputs.md    # annotated sample run
    └── report-*.md          # generated per research run
```

## Installation

```bash
git clone <your-repo-url> insight-agent
cd insight-agent
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # then add your OPENAI_API_KEY
```

You need an [OpenAI API key](https://platform.openai.com/api-keys) for the reasoning
model. Web search via DuckDuckGo needs no key.

## Usage

```bash
python main.py research "Should a seed-stage SaaS startup choose PostgreSQL or MongoDB?"
python main.py research "LangGraph vs CrewAI for multi-agent workflows?" --max-steps 10
```

Example (abbreviated):

```
--- Step 1 ---
Thought: I need current comparisons of PostgreSQL vs MongoDB for startups...
Action: web_search(PostgreSQL vs MongoDB seed stage SaaS startup 2026)
Observation: Multiple comparisons note Postgres's reliability, JSONB...

--- Step 3 ---
Thought: The search results are long. Let me condense the key trade-offs...
Action: summarize(<comparison text>)
Observation: - Postgres: ACID guarantees, JSONB for flexible schema...

============================================================
## Recommendation
Choose PostgreSQL as the primary database...
## Key findings
...
============================================================

Full report saved to examples/report-should-a-seed-stage-saas-startup-choose-postgresql-or-mongodb.md
```

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `OPENAI_API_KEY` | — | **Required.** OpenAI API key |
| `CHAT_MODEL` | `gpt-4o-mini` | Reasoning model |
| `TEMPERATURE` | `0.2` | Low temperature keeps tool calls reliable |
| `MAX_STEPS` | `8` | Max Thought→Action→Observation cycles |

## Sample outputs

See [examples/sample_outputs.md](examples/sample_outputs.md) for an annotated run:
trajectory plus the final decision brief.

## How the ReAct parsing works

Each LLM turn is parsed with regexes for `Thought:` / `Action:` / `Action Input:` /
`Final Answer:`. Unknown tool names and tool exceptions are fed back as observations
so the agent can self-correct instead of crashing — see `parse_step()` in
`src/agent.py`.

## Limitations & future work

- DuckDuckGo results vary in quality; a rerank step would improve source selection.
- No persistent memory between runs — a vector-backed memory of past research is a natural extension.
- The brief format is fixed; making it schema-validated (Pydantic) output is planned.
- Planned: streaming trajectory, a second opinion / critic step before the final brief.

## License

MIT — see [LICENSE](LICENSE) (add one, e.g. via `gh repo create` template or choosealicense.com).
