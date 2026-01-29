# Feature Specification: AI Daily Half Marathon Coach (Home Page)

**Feature Branch**: `[002-ai-homepage-coach]`  
**Created**: 2026-01-26  
**Status**: Draft  
**Input**: User description: "Include AI into the home page. On the home page show a summary of what workout would be best suited for training for a half marathon. Plan should be for the current day based off the information in the agent’s knowledge base (Cosmos-backed). It will change after an activity has been logged. For now the agent (Azure AI Foundry; resource `fit-app-resource`, project `fit-app`) and AI Search are already manually stood up to read from Cosmos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See Today’s Recommended Workout (Priority: P1)

As a user, when I open the home page, I can see a concise recommendation for today’s half-marathon training workout based on my recent logged activities.

**Why this priority**: This is the core value of the AI feature and the primary new capability.

**Independent Test**: With mock backend/agent output, the home page renders a recommendation card with a title, workout details, and rationale.

**Acceptance Scenarios**:

1. **Given** the user has logged recent activities, **When** the user opens Home, **Then** the page shows “Today’s Half Marathon Training” with a specific workout recommendation.
2. **Given** the recommendation loads successfully, **When** it renders, **Then** it includes a short rationale referencing recent training patterns (e.g., intensity, volume, rest days).
3. **Given** the agent returns no usable recommendation, **When** Home loads, **Then** the UI shows a safe default (e.g., “Easy run 30–45 minutes”) with a note.

---

### User Story 2 - Recommendation Updates After Logging (Priority: P2)

As a user, after I log a new activity, the recommendation shown on Home updates to reflect the new training state.

**Why this priority**: The app should feel responsive to new data and reinforce the training feedback loop.

**Independent Test**: After a successful log, Home reloads and displays the success toast + updated recommendation.

**Acceptance Scenarios**:

1. **Given** a user logs an activity successfully, **When** they are redirected to Home, **Then** they see a success toast and the recommendation is recalculated from the latest data.

---

### Edge Cases

- User has no activities yet.
- Agent/AI Search is unavailable or times out.
- Recommendation output is malformed or unsafe (missing required fields).
- Very recent race/long run should trigger a recovery suggestion.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST display a “Today’s Half Marathon Training” recommendation card on the home page.
- **FR-002**: The system MUST generate the recommendation for the current day (local date) using the user’s recent activities stored in Cosmos DB.
- **FR-003**: The system MUST call the existing “manually stood up” Azure AI Foundry agent (resource `fit-app-resource`, project `fit-app`) + AI Search integration to produce a recommendation.
- **FR-004**: The system MUST provide user-friendly errors and fallbacks (no raw stack traces or model errors shown to the user).
- **FR-005**: After a successful activity save + redirect to Home, the system MUST refresh the recommendation.
- **FR-006**: The recommendation response MUST be structured JSON (not free-form text), so the UI can render it consistently.

### Non-Functional Requirements

- **NFR-001**: Recommendation endpoint SHOULD respond within 3 seconds p95; otherwise return a fallback recommendation.
- **NFR-002**: The system MUST not expose secrets (API keys) to the frontend.
- **NFR-003**: The system MUST avoid returning personally sensitive data.

### Key Entities

- **DailyRecommendation**: A structured recommendation for a given date (title, workout, rationale, confidence, metadata).
- **TrainingContext**: Derived summary of recent activities (e.g., last 7–14 days volume, last hard session, last long run).

## Success Criteria *(mandatory)*

- **SC-001**: Home page displays a recommendation for 100% of sessions (either AI-driven or fallback).
- **SC-002**: 0 occurrences of raw backend/model error messages shown to users.
- **SC-003**: After logging an activity, the user sees the success toast and the recommendation reflects the latest data (manual verification).