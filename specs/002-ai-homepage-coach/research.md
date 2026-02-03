# Research & Technical Decisions: AI Daily Half Marathon Coach

**Feature**: AI Daily Half Marathon Coach (Home Page)  
**Branch**: `002-ai-homepage-coach`  
**Date**: 2026-02-03  
**Status**: All clarifications resolved

---

## 1. Azure AI Foundry Agent Configuration ✓

### Decision
- **Endpoint**: `https://fit-app-resource.services.ai.azure.com/api/projects/fit-app`
- **Model**: `gpt-5-mini`
- **Authentication**: Managed Identity (system-assigned or user-assigned)
- **SDK**: Azure AI Foundry Python SDK (`azure-ai-inference` or `azure-ai-projects`) with `azure-identity`

### Rationale
- The AI Foundry agent and AI Search infrastructure are already manually deployed
- `gpt-5-mini` provides good balance of cost and quality for structured recommendations
- Managed identity aligns with the constitution's Azure-optimized principle (no secrets in code)
- Azure AI Foundry SDK provides native support for agent interactions and structured outputs

### Alternatives Considered
- **API Key Authentication**: Rejected because it requires storing secrets; less secure than managed identity
- **Direct OpenAI API**: Rejected because Foundry agent already has AI Search integration configured
- **gpt-4 or gpt-4o**: Rejected for cost reasons; gpt-5-mini is sufficient for this use case

### Implementation Notes
- Function App identity needs RBAC role on AI Foundry resource
- SDK dependencies: `azure-ai-inference` (or `azure-ai-projects`), `azure-identity`
- Use `DefaultAzureCredential` for local dev (via Azure CLI) and production (via managed identity)

---

## 2. MCP Server Integration for Cosmos Data Access ✓

### Decision
- **Endpoint**: `https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp`
- **Protocol**: Streamable HTTP (SSE-based)
- **Authentication**: None (unauthenticated for dev environment)
- **Available Tools**: `query_cosmos`, `count_document`, `list_distinct_values`

### Rationale
- Centralizes Cosmos DB access through a dedicated MCP server
- Streamable HTTP/SSE allows for efficient, event-driven communication
- MCP tools provide standardized interface for querying activity data
- No authentication needed in dev environment simplifies initial implementation

### Alternatives Considered
- **Direct Cosmos DB Access**: Rejected to avoid duplicating connection logic; MCP server exists
- **JSON-RPC Protocol**: Streamable HTTP chosen for better support of streaming responses
- **Authenticated MCP**: Deferred to future iteration; dev environment doesn't require it now

### Implementation Notes
- MCP client SDK: Need Python client that supports Streamable HTTP (SSE)
- Tools to use:
  - `query_cosmos`: Get recent activities (last 7-14 days)
    - Parameters: `query` (SQL-like query string), `limit` (max results)
    - Returns: `{"documents": [...]}` with activity records
  - `count_document`: Check total activity count for context
    - Parameters: `query` (filter predicate)
    - Returns: `{"count": <number>}`
  - `list_distinct_values`: Get activity types or other categorical data
    - Parameters: `field` (field name), `query` (optional filter)
    - Returns: `{"values": [...]}`
- Fallback strategy: If MCP server unavailable, return generic fallback recommendation
- Error handling: Timeout after 2s for MCP calls (within 3s total endpoint budget)

---

## 3. Data Access Pattern ✓

### Decision
Use MCP server to fetch last 14 days of activities, summarize into training context

### Rationale
- 14 days provides sufficient context for understanding training load and patterns
- MCP tools allow flexible queries without coupling to Cosmos SDK
- Training context summary keeps token count low for AI agent call

### Alternatives Considered
- **All Historical Data**: Too much data; unnecessary for daily recommendation
- **Last 7 Days**: Too short to detect patterns like weekly long runs
- **Direct Activity Feed**: Would require more complex processing; summarization is cleaner

### Implementation Notes
- Query activities where `date >= today - 14 days`
- Summarize into context:
  - Total volume (distance/duration)
  - Last hard workout (date, type, intensity)
  - Last long run (date, distance)
  - Recent rest days
  - Activity types distribution
- Keep summary under 500 tokens for efficient AI processing

---

## 4. Response Structure & Validation ✓

### Decision
Use Pydantic models for structured response validation

### Rationale
- Pydantic already in use in backend (see `shared/validation.py`)
- Ensures AI agent output conforms to expected schema
- Type safety for frontend integration
- Enables easy fallback generation with same structure

### Alternatives Considered
- **Plain Dictionaries**: No validation, error-prone
- **JSON Schema Only**: Less Pythonic, harder to maintain

### Implementation Notes
- Create Pydantic models:
  - `WorkoutDetails`: type, durationMinutes, details[]
  - `DailyRecommendation`: date, goal, title, workout, rationale, confidence, fallback
- Use `model_validate()` to parse AI agent response
- On validation failure, return fallback recommendation

---

## 5. Error Handling & Fallback Strategy ✓

### Decision
Always return 200 with `fallback: true` for recoverable errors

### Rationale
- User experience: Always show something useful, never an error page
- Constitution requirement: User-friendly errors, no raw stack traces
- Graceful degradation: Fallback recommendation is still valuable

### Fallback Triggers
- MCP server timeout/unavailable
- AI agent timeout/unavailable
- Malformed AI response
- Validation errors

### Fallback Recommendation
```json
{
  "date": "<today>",
  "goal": "half-marathon",
  "title": "Easy aerobic run",
  "workout": {
    "type": "Running",
    "durationMinutes": 45,
    "details": [
      "Easy conversational pace for 35-45 minutes",
      "Focus on comfortable breathing",
      "Optional: 4-6 x 20s strides"
    ]
  },
  "rationale": "A moderate aerobic run is a safe default for maintaining fitness and building endurance.",
  "confidence": "low",
  "fallback": true
}
```

---

## 6. Training Policy & AI Prompt ✓

### Decision
AI-driven recommendations with structured output schema and training guidelines

### Rationale
- AI agent with AI Search has access to training knowledge base
- Structured output ensures consistent, parseable responses
- Guidelines prevent unsafe recommendations (e.g., hard sessions back-to-back)

### Training Guidelines for AI Prompt
1. **Polarized Training**: Mix easy runs, threshold work, and recovery
2. **No hard efforts on consecutive days** without recovery justification
3. **Weekly long run**: Recommend at least one longer endurance run per week
4. **Recovery**: After hard sessions or long runs, prioritize easy/rest days
5. **Progression**: Gradual volume increase (10% rule)
6. **Strides**: Include short speed pickups on easy days for neuromuscular stimulus

### Alternatives Considered
- **Rule-Based Only**: Too rigid, doesn't adapt to user patterns
- **Fully Open AI**: Risk of unsafe recommendations without guidelines

---

## 7. Performance Budget ✓

### Decision
p95 < 30 seconds for `/api/coach/today` endpoint (updated from original 3s target)

### Observed Performance
GPT-5 mini is a reasoning model that uses internal "thinking" tokens before producing output:
- Average latency: 15-28 seconds
- p95 observed: ~28 seconds
- Reasoning tokens: ~1500-1800 tokens (not visible in output)
- Output tokens: ~200-400 tokens

### Breakdown (Updated)
- MCP queries: ~500ms (parallel if possible)
- Training context build: ~100ms
- AI agent call: ~15-25s (reasoning model)
- Response validation: ~50ms

### Rationale
- GPT-5 mini's reasoning capability provides higher quality recommendations
- The extended thinking time results in better training advice
- User sees loading state during fetch
- Fallback on timeout (30s) ensures no indefinite waits
- Consider caching recommendations for same-day repeat requests

### Alternatives Considered
- **Switch to faster model**: Would sacrifice recommendation quality
- **Reduce max_completion_tokens**: Model requires ~2000 for reasoning + output
- **Stream response**: Could improve perceived performance (future enhancement)

---

## 8. Dependencies & SDK Versions ✓

### Required New Dependencies
- **Azure AI Foundry SDK**: `azure-ai-inference>=1.0.0` (or `azure-ai-projects`)
- **Azure Identity**: `azure-identity>=1.17.1`
- **MCP Client**: Research Python MCP client supporting Streamable HTTP/SSE
- **HTTP Client**: `httpx>=0.28.1` (for MCP Streamable HTTP/SSE if needed)

### Rationale
- Constitution requires pinned dependencies for determinism
- Versions will be pinned without caret ranges in final requirements.txt

---

## 9. MCP Server Tools Usage ✓

### Overview
The MCP server provides Cosmos DB access through a standardized tool interface using Streamable HTTP (SSE) protocol. The coach function uses these tools to fetch training history for recommendation context.

### Server Configuration
- **Endpoint**: `https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp`
- **Protocol**: Streamable HTTP with Server-Sent Events (SSE)
- **Authentication**: None required (dev environment)
- **Content-Type**: `application/json` (requests), `text/event-stream` (responses)

### Available Tools

#### `query_cosmos`
Query the activities container with optional filters.

**Parameters:**
```json
{
  "query": "SELECT * FROM c WHERE c.date >= @startDate ORDER BY c.date DESC",
  "parameters": [{"name": "@startDate", "value": "2026-01-20"}],
  "limit": 50
}
```

**Response:**
```json
{
  "documents": [
    {
      "id": "uuid",
      "date": "2026-01-26",
      "type": "Running",
      "distance_miles": 6.2,
      "duration_minutes": 52,
      "notes": "Easy pace, felt good"
    }
  ]
}
```

#### `count_document`
Count documents matching a filter.

**Parameters:**
```json
{
  "query": "c.type = 'Running'"
}
```

**Response:**
```json
{
  "count": 42
}
```

#### `list_distinct_values`
Get distinct values for a field.

**Parameters:**
```json
{
  "field": "type",
  "query": "c.date >= '2026-01-01'"
}
```

**Response:**
```json
{
  "values": ["Running", "Cycling", "Swimming"]
}
```

### Implementation Pattern

The coach function uses the MCP client as follows:

```python
from shared.mcp_client import MCPClient

async with MCPClient(endpoint=MCP_SERVER_ENDPOINT) as client:
    # Initialize session
    await client.initialize()
    
    # Query recent activities
    activities = await client.call_tool("query_cosmos", {
        "query": "SELECT * FROM c WHERE c.date >= @startDate",
        "parameters": [{"name": "@startDate", "value": cutoff_date}],
        "limit": 100
    })
    
    # Build training context from activities
    context = build_training_context(activities["documents"])
```

### SSE Response Parsing

The MCP server returns responses in SSE format:
```
event: message
data: {"jsonrpc":"2.0","id":"1","result":{"content":[{"type":"text","text":"{...}"}]}}
```

The MCPClient parses this format automatically:
1. Reads SSE events from the response stream
2. Extracts the `data:` line content
3. Parses JSON-RPC response
4. Extracts tool result from `result.content[0].text`

### Error Handling

- **Connection timeout**: 2s timeout on MCP calls
- **Server unavailable**: Falls back to generic recommendation
- **Invalid response**: Logs error, returns fallback
- **Empty results**: Valid scenario, indicates no recent activity

### Testing Considerations

- Unit tests mock the MCP client responses
- Integration tests verify connectivity to the actual MCP server
- Fallback paths are tested with simulated failures

---

## Open Questions / Future Work

1. ~~**MCP Python Client**: Need to identify specific Python library for Streamable HTTP MCP protocol~~ ✓ Custom httpx-based client implemented
2. **Caching**: Should same-day recommendations be cached? (Defer to Phase 3)
3. **Production MCP Authentication**: Will production require auth? If so, what mechanism?
4. **Multi-user**: Current scope is single-user MVP
5. **Recommendation History**: Should we store past recommendations for analysis?
6. **Race Date**: User profile with target race date for periodization?

---

## References

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-services/ai-foundry/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Constitution](/.specify/memory/constitution.md)
- [Feature Spec](spec.md)
- [Implementation Plan](plan.md)
