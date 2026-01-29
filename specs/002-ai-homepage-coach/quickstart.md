# Quickstart: AI Daily Half Marathon Coach

## Goal

Show an AI-generated (or safe fallback) “Today’s Half Marathon Training” workout recommendation on the home page.

## Local Dev (MVP)

1. Start backend:
   - `cd backend/functions`
   - `func start`
2. Serve frontend:
   - `npx -y serve frontend/src -l 4280`
3. Open:
   - `http://localhost:4280/`

## Configuration

Backend (Azure Functions) will need configuration to reach Foundry. Suggested app settings (names TBD):

- `FOUNDRY_RESOURCE_NAME=fit-app-resource`
- `FOUNDRY_PROJECT_NAME=fit-app`
- `FOUNDRY_AGENT_ID` (NEEDS CLARIFICATION)
- `FOUNDRY_ENDPOINT` (NEEDS CLARIFICATION; only if required)

## Implementation Steps (suggested)

1. Create a new backend endpoint `GET /api/coach/today` that returns a deterministic placeholder JSON recommendation.
2. Add a `getTodayCoach()` function to `frontend/src/services/api.js`.
3. Render a “Today’s Half Marathon Training” card in `frontend/src/index.html`.
4. Swap placeholder backend logic for the real agent + search integration and keep schema validation.
