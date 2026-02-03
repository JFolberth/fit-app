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
  - `count_document`: Check total activity count for context
  - `list_distinct_values`: Get activity types or other categorical data
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
p95 < 3 seconds for `/api/coach/today` endpoint

### Breakdown
- MCP queries: ~500ms (parallel if possible)
- Training context build: ~100ms
- AI agent call: ~1500ms
- Response validation: ~50ms
- Buffer: ~850ms

### Rationale
- 3s is acceptable for a "load home page" interaction
- User sees loading state during fetch
- Allows for AI agent processing time
- Fallback on timeout ensures no user waits 30s+

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

## Open Questions / Future Work

1. **MCP Python Client**: Need to identify specific Python library for Streamable HTTP MCP protocol
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
