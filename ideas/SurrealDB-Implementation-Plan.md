# SurrealDB Implementation Plan for Genesis Brain Light

## Executive Summary

SurrealDB is **not currently running** - the previous container was stopped/removed. We need to implement it from scratch following the Genesis Brain Light design adapted for the TCC knowledge base.

## Current Status

| Component | Status |
|-----------|--------|
| SurrealDB container | ❌ Not running |
| SurrealDB binary | ❌ Not installed |
| Knowledge base pipeline | ❌ Not implemented |
| Schema | ❌ Not created |

---

## Implementation Plan

### Phase 1: SurrealDB Setup (2-3 hours)

#### 1.1 Docker Configuration

```yaml
# skills/knowledge-base/docker-compose.yml
version: '3.8'
services:
  surrealdb:
    image: surrealdb/surrealdb:latest
    container_name: surrealdb-tcc
    ports:
      - "8765:8765"
    command: start --log trace --user root --pass ${SURREAL_PASS} --ns tcc --db knowledge_base
    volumes:
      - ${HERMES_KB_DATA_DIR}:/data
    restart: unless-stopped
```

#### 1.2 Environment Variables

Add to Hermes profile `.env`:
```bash
SURREAL_URL=ws://127.0.0.1:8765/rpc
SURREAL_USER=root
SURREAL_PASS=<generate secure password>
SURREAL_NS=tcc
SURREAL_DB=knowledge_base
HERMES_KB_DATA_DIR=~/.hermes/tcc/state/knowledge-base/surreal-data
OPENROUTER_API_KEY=<existing key>
EMBED_MODEL=openai/text-embedding-3-small
EXTRACT_MODEL=anthropic/claude-haiku-4-5
```

#### 1.3 Directory Structure creation
- `~/.hermes/tcc/state/knowledge-base/surreal-data/` - persistent DB storage
- `skills/knowledge-base/pipeline/` - Python code
- `skills/knowledge-base/scripts/` - Shell interfaces

---

### Phase 2: SurrealDB Schema (1-2 hours)

#### 2.1 Tables (from GENESIS-BRAIN-ARCHITECTURE.md)

```sql
-- Execute at startup (idempotent)
DEFINE TABLE document SCHEMALESS;
DEFINE TABLE chunk SCHEMALESS;
DEFINE TABLE concept SCHEMALESS;
DEFINE TABLE community SCHEMALESS;

DEFINE FIELD title ON document TYPE string;
DEFINE FIELD path ON document TYPE string;
DEFINE FIELD git_hash ON document TYPE string;
DEFINE FIELD created_at ON document TYPE datetime;
DEFINE FIELD updated_at ON document TYPE datetime;

DEFINE FIELD text ON chunk TYPE string;
DEFINE FIELD embedding ON chunk TYPE array<float>;
DEFINE FIELD token_count ON chunk TYPE int;

DEFINE FIELD name ON concept TYPE string;
DEFINE FIELD kind ON concept TYPE string;
DEFINE FIELD description ON concept TYPE string;
DEFINE FIELD embedding ON concept TYPE array<float>;

DEFINE FIELD verb ON relates TYPE string;
DEFINE FIELD weight ON relates TYPE float;

-- HNSW Indexes
DEFINE INDEX chunk_embedding ON chunk COLUMNS embedding HNSW;
DEFINE INDEX concept_embedding ON concept COLUMNS embedding HNSW;

-- Edges
DEFINE TABLE contains SCHEMALESS;
DEFINE TABLE mentions SCHEMALESS;
DEFINE TABLE relates SCHEMALESS;
DEFINE TABLE belongs_to SCHEMALESS;

-- Metadata table
DEFINE TABLE kb_meta SCHEMALESS;
```

---

### Phase 3: Python Pipeline (4-6 hours)

#### 3.1 File Structure
```
skills/knowledge-base/pipeline/
├── requirements.txt     # surrealdb, openai, tiktoken, requests
├── db.py               # Connection + schema init
├── chunker.py          # Markdown → chunks (~512 tokens)
├── embedder.py         # OpenRouter embeddings
├── extractor.py        # LLM concept + relation extraction
├── entity_resolver.py  # Deduplication (exact + vector similarity)
├── ingest.py           # Orchestrate single file
├── reindex.py          # Full/incremental reindex driver
└── tests/
```

#### 3.2 Key Functions

**db.py**:
```python
async def get_db():  # Async connection to SurrealDB
async def init_schema():  # Idempotent schema setup
async def get_last_indexed_commit():  # From kb_meta table
async def set_last_indexed_commit(commit_hash):  # Update kb_meta
```

**chunker.py**:
```python
def chunk_markdown(content: str) -> List[Chunk]:
    # - Split on headings first
    # - ~512 token segments with overlap
    # - Extract title from first # heading
```

**embedder.py**:
```python
def embed_texts(texts: List[str]) -> List[List[float]]:
    # OpenRouter with openai/text-embedding-3-small
    # Batch size 20
    # Returns 1536-dim vectors
```

**extractor.py**:
```python
def extract_concepts_relations(text: str) -> Dict:
    # Claude Haiku extraction prompt
    # Returns {concepts: [...], relations: [...]}
```

**ingest.py**:
```python
async def ingest_file(path: str, commit_hash: str = None):
    # Full pipeline: read → chunk → embed → extract → upsert
```

**reindex.py**:
```python
# Incremental: git diff → changed files → ingest
# Full: traverse all research/*.md → ingest
# --dry-run option
```

---

### Phase 4: Shell Scripts (1-2 hours)

```bash
# skills/knowledge-base/scripts/query.sh "<query>" [limit=5]
# skills/knowledge-base/scripts/relate.sh "<A>" "<B>"
# skills/knowledge-base/scripts/stats.sh
# skills/knowledge-base/scripts/capture.sh "<text>"
# skills/knowledge-base/scripts/ingest.sh <path>
```

Each script:
- Activates `.venv`
- Sets env vars
- Calls Python module
- Returns JSON

---

### Phase 5: Hermes Integration (1-2 hours)

#### 5.1 Cron Job
```bash
# Daily at 03:00
0 3 * * * cd /opt/hermes/ARK/skills/knowledge-base && python pipeline/reindex.py
```

#### 5.2 Skill Definition (SKILL.md)
```markdown
# When to use:
- query.sh before questions needing graph context  
- ingest.sh when new files added
- relate.sh for "how does X connect to Y"
- capture.sh for "remember this"
- stats.sh for graph health
```

---

## Dependencies

| Component | Required |
|-----------|----------|
| Docker | ✅ Installed |
| Python 3.11+ | ✅ Available |
| OpenRouter API key | ✅ Available |
| Hermes profile env | Needs SURREAL_PASS, HERMES_KB_DATA_DIR |

---

## Verification Checklist

- [ ] SurrealDB container running on port 8765
- [ ] Database accessible via WebSocket
- [ ] Schema initialized
- [ ] Python pipeline venv created
- [ ] db.py: surrealdb connection working
- [ ] chunker.py: chunks markdown correctly
- [ ] embedder.py: returns 1536-dim vectors
- [ ] extractor.py: extracts concepts/relations
- [ ] entity_resolver.py: deduplicates via similarity
- [ ] ingest.py: processes single file end-to-end
- [ ] reindex.py: incremental mode works
- [ ] All shell scripts return valid JSON
- [ ] Cron job configured for daily runs

---

## Reference Documents

- [Genesis Brain Light Design](../../research/regentribe/GENESIS-BRAIN-LIGHT-DESIGN.md)
- [GENESIS-BRAIN-ARCHITECTURE.md](../../research/regentribe/GENESIS-BRAIN-ARCHITECTURE.md)
- [TCC MVP Specification](../plan/The Coherence Company/metis-hermes-01/mvp.md)

---

## Open Questions

1. **Which repo to use for document layer?** ARK repo (`research/` directory) vs separate knowledge-base repo?
2. **Should we reuse existing Genesis pipeline code** from the Genesis VPS, or reimplement fresh?
3. **Port conflicts?** Need to verify 8765 is available (Genesis may use 8000)
4. **Authentication**: Single profile vs multi-user API keys? MVP uses single, but production needs auth