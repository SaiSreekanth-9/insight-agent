# Sample outputs

> Sample run of `python main.py research "Should a seed-stage SaaS startup choose
> PostgreSQL or MongoDB for its primary database?"` (trajectory abbreviated).

## Reasoning trajectory (abbreviated)

**Step 1**
- **Thought:** I need current comparisons of PostgreSQL vs MongoDB for startups. Let me search for that first.
- **Action:** `web_search`
- **Action Input:** `PostgreSQL vs MongoDB seed stage SaaS startup 2026`
- **Observation:** Multiple comparisons note Postgres's reliability, rich ecosystem (JSONB covers many document use cases), and managed options (Supabase, Neon, RDS)...

**Step 2**
- **Thought:** I have general comparisons. Now let me check the specific angle of operational cost and scaling pain points.
- **Action:** `web_search`
- **Action Input:** `MongoDB vs PostgreSQL operational cost scaling pain points startups`
- **Observation:** Reports of MongoDB Atlas costs growing steeply with scale; Postgres connection pooling (PgBouncer) as a known scaling pattern...

**Step 3**
- **Thought:** The search results are long. Let me condense the key trade-offs before deciding.
- **Action:** `summarize`
- **Action Input:** `<full text of the comparison results>`
- **Observation:** - Postgres: ACID guarantees, JSONB for flexible schema, mature tooling...
  - MongoDB: flexible schema from day one, horizontal sharding story...

**Step 4**
- **Thought:** I have enough for a decision brief with a clear recommendation and caveats.
- **Action:** *(none — final answer)*

## Decision brief

## Recommendation
Choose **PostgreSQL** as the primary database. Its JSONB support covers the flexible-schema cases that used to require MongoDB, while giving you ACID transactions, a mature ecosystem, and cheaper managed hosting at seed stage.

## Key findings
- PostgreSQL's JSONB handles semi-structured data well enough that most SaaS products never need a document store.
- Managed Postgres (Supabase, Neon, RDS) is significantly cheaper than MongoDB Atlas at low-to-mid scale.
- Hiring is easier: far more engineers know Postgres deeply.
- MongoDB's advantage is strongest when the data model is genuinely document-shaped *and* needs horizontal sharding early — rare at seed stage.

## Options compared
| | PostgreSQL | MongoDB |
|---|---|---|
| Data model | Relational + JSONB | Document |
| Transactions | Full ACID, multi-row | Multi-document (newer, less mature) |
| Seed-stage cost | Low (many cheap managed options) | Higher (Atlas pricing) |
| Ecosystem | Very mature | Mature, smaller talent pool |

## Risks / open questions
- If the product later needs multi-region active-active writes, reassess (neither is trivial; consider CockroachDB/Spanner then).
- Team familiarity matters more than benchmarks: if the founding team only knows MongoDB, the calculus changes.

## Sources
- Web search results on Postgres vs MongoDB startup comparisons (see trajectory observations above).
