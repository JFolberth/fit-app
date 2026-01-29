# Implementation Plan: AI Daily Half Marathon Coach (Home Page)

**Branch**: `[002-ai-homepage-coach]` | **Date**: 2026-01-26 | **Spec**: [specs/002-ai-homepage-coach/spec.md](specs/002-ai-homepage-coach/spec.md)
**Input**: Feature specification from `specs/002-ai-homepage-coach/spec.md`

## Summary

Add a new backend endpoint that produces a structured “today’s workout” recommendation for half-marathon training using recent activities from Cosmos DB and the existing AI Agent + AI Search integration. Render this recommendation on the home page, with user-friendly fallbacks and errors, and refresh it naturally after an activity is logged (current flow already redirects to Home).

## Technical Context

**Language/Version**: Python 3.11 (Azure Functions) + vanilla JS (frontend)  
**Primary Dependencies**: Azure Functions Python, Pydantic validation (backend), Playwright (tests)  
**Storage**: Azure Cosmos DB (activities container)  
**AI Platform**: Azure AI Foundry agent (resource `fit-app-resource`, project `fit-app`) + Azure AI Search (existing/manual)  
**Testing**: pytest (backend), Playwright (frontend functional)  
**Target Platform**: Azure Functions + Azure Static Web Apps  
**Project Type**: Web application (backend/ + frontend/)  
**Performance Goals**: Recommendation endpoint p95 < 3s; fallback under timeout  
**Constraints**: No secrets in frontend; return safe defaults; user-friendly errors  
**Scale/Scope**: Single-user MVP, single daily recommendation

## Constitution Check

GATE: Must pass before implementation.

- Determinism: tooling and dependencies pinned; avoid environment-only behavior.
- Devcontainer-first: all commands must run inside the devcontainer; CI should mirror the container.
- Test-first: add/adjust unit + functional + integration tests for new behavior.
- CI quality gates: CI must pass before merge; no bypassing checks.
- Azure-optimized: use managed identity where possible; no secrets in frontend or repo; use App Settings/Key Vault.


## Project Structure

### Documentation (this feature)

```text
specs/002-ai-homepage-coach/
├── plan.md
├── research.md
├── quickstart.md
└── contracts/
    └── openapi.yaml
```

### Source Code (repository root)

```text
backend/
  functions/
    activities/
    shared/
    (new) coach/               # New Function endpoint for recommendation

frontend/
  src/
    index.html                 # Home page renders recommendation card
    services/
      api.js                   # Add recommendation API call
```

**Structure Decision**: Option 2 (web application) with a new Azure Function endpoint and a small homepage UI enhancement.

## Architecture & Data Flow

1. Home page loads.
2. Frontend calls `GET /api/coach/today`.
3. Backend:
   - Loads recent activities (last N days) from Cosmos.
   - Builds a concise training context summary.
   - Calls the existing AI agent/AI Search integration to generate a structured recommendation (JSON).
   - Validates and normalizes output.
   - Returns JSON response.
4. Frontend renders recommendation card.
5. After logging an activity, existing redirect-to-home flow triggers a fresh fetch.

## API Design

### New endpoint

- `GET /api/coach/today`

Response (200):

```json
{
  "date": "2026-01-26",
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

Response (200, fallback): `fallback: true` and a generic safe workout.

Response (500): should be avoided; prefer fallback 200.

NEEDS CLARIFICATION:
- Agent invocation details: we know the Foundry resource is `fit-app-resource` and project is `fit-app`, but we still need the agent identifier (name/id), invocation method (SDK vs REST), and auth (managed identity vs key).

## Frontend UX

- Add a card on Home below the hero section:
  - Title: “Today’s Half Marathon Training”
  - Body: workout title, key details list, short rationale
  - Loading state: skeleton or “Generating today’s workout…”
  - Failure: “Using a default suggestion today” + default workout

## Error Handling

- Backend returns user-safe text only; frontend shows friendly message.
- Timeouts and agent failures return a fallback recommendation with `fallback: true`.
- Frontend never displays raw error payloads.

## Testing Strategy

- Backend unit tests:
  - Context building from recent activities.
  - Fallback behavior when agent call fails.
  - Output validation schema.

- Frontend functional tests (Playwright):
  - Home page renders recommendation from mocked endpoint.
  - After save redirect, toast appears and recommendation fetch occurs.

## Rollout

- Phase 1: Add endpoint returning a deterministic placeholder recommendation (no agent call) to validate UI.
- Phase 2: Wire in agent + search integration.
- Phase 3: Tune prompt/rules and add caching if needed.
