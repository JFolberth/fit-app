# Research: AI Daily Half Marathon Coach

## Open Questions (NEEDS CLARIFICATION)

1. **Agent integration details**
   - How do we invoke the “manually stood up” agent in Azure AI Foundry (resource `fit-app-resource`, project `fit-app`)?
     - SDK (Azure AI Foundry Agents? OpenAI-compatible endpoint? Custom HTTP?)
     - Auth mechanism (managed identity? API key? App settings?)
     - Request/response contract

2. **AI Search topology**
   - What is the search index name and schema?
   - Does the agent already have a tool configured to query it?
   - Are we expected to call Search directly from Functions, or only via the agent?

3. **Training policy**
   - How do we define “best suited workout”?
     - Simple heuristics + AI explanation?
     - AI-only with guardrails?
   - Minimum/maximum intensity rules (e.g., avoid hard sessions back-to-back)

4. **User profile / target date**
   - Is there any concept of planned race date, current weekly mileage target, or injury status?

## Proposed Decisions

- Use a structured JSON response schema (`DailyRecommendation`) validated in backend.
- Prefer returning `200` with `fallback: true` rather than hard failing.
- Use last 14 days of activities to derive training context.

## Next Steps

- Capture the existing agent endpoint + credentials format.
- Decide the endpoint path (`/api/coach/today` vs `/api/recommendation/today`) and standardize naming.
- Define a minimal prompt/template for the agent output schema.
