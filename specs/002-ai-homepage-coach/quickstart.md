# Quickstart: AI Daily Half Marathon Coach

**Feature**: Display AI-generated daily workout recommendations on the home page  
**Branch**: `002-ai-homepage-coach`

---

## Prerequisites

- Devcontainer environment (see repository README)
- Azure AI Foundry resource deployed: `fit-app-resource` with project `fit-app`
- MCP server running at: `https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp`
- Function App with managed identity granted RBAC access to AI Foundry

---

## Local Development

### 1. Start Backend (Azure Functions)

```bash
cd /workspaces/fit-app/backend/functions
func start
```

Backend runs on `http://localhost:7071`

### 2. Serve Frontend (Static Web App)

```bash
npx -y serve /workspaces/fit-app/frontend/src -l 4280
```

Frontend runs on `http://localhost:4280`

### 3. Open Home Page

Navigate to `http://localhost:4280/` and verify the recommendation card loads.

---

## Configuration

### Backend Environment Variables

For local development, add these to `backend/functions/local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AI_FOUNDRY_ENDPOINT": "https://fit-app-resource.services.ai.azure.com/api/projects/fit-app",
    "AI_FOUNDRY_MODEL": "gpt-5-mini",
    "MCP_SERVER_ENDPOINT": "https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp",
    "COSMOS_ENDPOINT": "https://fitapp-dev-cosmos.documents.azure.com:443/",
    "COSMOS_DATABASE_NAME": "fitappdb",
    "COSMOS_CONTAINER_NAME": "activities",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": ""
  }
}
```

**Note**: Managed identity authentication requires Azure CLI login locally:
```bash
az login
```

### For Azure Deployment

Add these App Settings to the Function App (via Azure Portal or Bicep):
- `AI_FOUNDRY_ENDPOINT`: `https://fit-app-resource.services.ai.azure.com/api/projects/fit-app`
- `AI_FOUNDRY_MODEL`: `gpt-5-mini`
- `MCP_SERVER_ENDPOINT`: `https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp`

Ensure Function App has **system-assigned managed identity** enabled and RBAC role assignment on AI Foundry resource.

---

## Implementation Phases

### Phase 1: UI Validation (Placeholder Backend)

**Goal**: Verify frontend rendering without external dependencies

1. **Backend**: Create `/api/coach/today` endpoint returning hardcoded recommendation JSON
2. **Frontend**: Add `fetchRecommendation()` to `services/api.js`
3. **Frontend**: Add recommendation card to `index.html`
4. **Test**: Home page displays placeholder recommendation
5. **Deploy**: Push to dev environment

**Success Criteria**:
- Home page shows "Today's Half Marathon Training" card
- Card displays title, workout details, rationale
- After logging activity, redirect to home shows success toast

### Phase 2: AI Integration

**Goal**: Wire real MCP and AI agent calls

1. **Backend**: Add MCP client to fetch activities from Cosmos
2. **Backend**: Build training context summary from activities
3. **Backend**: Call Azure AI Foundry agent with structured output request
4. **Backend**: Validate response with Pydantic models
5. **Backend**: Return fallback on errors/timeouts
6. **Test**: Integration tests with real MCP and AI agent
7. **Deploy**: Push to dev environment

**Success Criteria**:
- Recommendation reflects actual activity data
- Fallback triggers when services unavailable
- p95 latency < 3s
- No raw errors shown to user

### Phase 3: Optimization & Tuning

**Goal**: Improve quality and performance

1. **Tune AI prompt** for better recommendations
2. **Add caching** for same-day repeat requests (optional)
3. **Monitor telemetry** in Application Insights
4. **Adjust timeouts** based on real-world latency data

---

## Testing Strategy

### Unit Tests

```bash
cd /workspaces/fit-app/backend
pytest tests/unit/test_coach.py -v
```

**Coverage**:
- Training context summarization
- Fallback recommendation generation
- Pydantic validation
- Mocked MCP and AI responses

### Integration Tests

```bash
pytest tests/integration/test_coach_integration.py -v
```

**Coverage**:
- MCP server connectivity
- AI agent invocation
- End-to-end recommendation flow

### Functional Tests (Playwright)

```bash
cd /workspaces/fit-app/frontend/tests/functional
npm test -- test_coach.spec.ts
```

**Coverage**:
- Home page renders recommendation card
- Loading and error states display correctly
- After activity save, recommendation refreshes

---

## API Endpoint Reference

### `GET /api/coach/today`

**Description**: Returns today's AI-generated half marathon training recommendation

**Response 200** (AI-generated):
```json
{
  "date": "2026-02-03",
  "goal": "half-marathon",
  "title": "Easy aerobic run + strides",
  "workout": {
    "type": "Running",
    "durationMinutes": 45,
    "details": [
      "Easy pace for 35 minutes",
      "6 x 20s strides with full recovery",
      "Cool down 5 minutes"
    ]
  },
  "rationale": "Based on your last hard run 2 days ago and total volume this week, today is best used for aerobic recovery and leg turnover.",
  "confidence": "medium",
  "fallback": false
}
```

**Response 200** (Fallback):
```json
{
  "date": "2026-02-03",
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

## Troubleshooting

### MCP Server Connection Fails

**Symptom**: Backend returns fallback recommendation  
**Check**:
- MCP server is running: `curl https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp`
- Network connectivity from Function App to MCP server
- MCP client timeout settings (default: 2s)

### AI Agent Call Fails

**Symptom**: Fallback recommendation returned  
**Check**:
- Function App managed identity has RBAC role on AI Foundry resource
- AI Foundry endpoint and model name correct in App Settings
- Azure CLI login valid locally: `az account show`
- Application Insights logs for detailed error messages

### Frontend Card Not Displaying

**Symptom**: Home page shows no recommendation  
**Check**:
- Browser console for JavaScript errors
- Network tab shows successful `/api/coach/today` call
- Backend is running: `curl http://localhost:7071/api/coach/today`
- CORS configuration allows frontend origin

### Slow Response Times

**Symptom**: Recommendation takes >3s to load  
**Check**:
- Application Insights for latency breakdown
- MCP query performance (consider parallel queries)
- AI agent response time (consider simpler prompt)
- Network latency between services

---

## Next Steps

1. **Phase 1**: Implement placeholder endpoint and UI
2. **Phase 2**: Wire MCP and AI agent integration
3. **Phase 3**: Tune and optimize based on telemetry

See [plan.md](plan.md) for detailed implementation plan and [research.md](research.md) for technical decisions.
