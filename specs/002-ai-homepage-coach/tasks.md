# Tasks: AI Daily Half Marathon Coach (Home Page)

**Feature**: `002-ai-homepage-coach`  
**Input**: Design documents from `/workspaces/fit-app/specs/002-ai-homepage-coach/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Tests**: This feature does NOT explicitly request TDD. Tests will be included as standard practice but not written first.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

---

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: Always starts with `- [ ]`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2) for story-specific tasks only
- **Description**: Clear action with exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project structure for AI coach feature

- [ ] T001 Create backend Function App directory structure: `backend/functions/coach/`
- [ ] T002 Create `backend/functions/coach/__init__.py` with placeholder HTTP trigger
- [ ] T003 Create `backend/functions/coach/function.json` with GET route configuration
- [ ] T004 [P] Add new dependencies to `backend/functions/requirements.txt`: azure-ai-inference, azure-identity, httpx
- [ ] T005 [P] Create `backend/functions/shared/models.py` for Pydantic data models
- [ ] T006 [P] Update `.gitignore` to exclude `local.settings.json` if not already present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create DailyRecommendation Pydantic model in `backend/functions/shared/models.py`
- [ ] T008 [P] Create WorkoutDetails Pydantic model in `backend/functions/shared/models.py`
- [ ] T009 [P] Create TrainingContext Pydantic model in `backend/functions/shared/models.py`
- [ ] T010 Create fallback recommendation generator in `backend/functions/shared/models.py`
- [ ] T011 [P] Create MCP client wrapper in `backend/functions/shared/mcp_client.py` for Streamable HTTP
- [ ] T012 [P] Create AI Foundry client wrapper in `backend/functions/shared/ai_client.py` with managed identity auth
- [ ] T013 Add environment variable configuration in `backend/functions/coach/__init__.py` for AI_FOUNDRY_ENDPOINT, MCP_SERVER_ENDPOINT
- [ ] T014 Create unit tests directory structure: `backend/tests/unit/test_coach_models.py`
- [ ] T015 [P] Create integration tests directory structure: `backend/tests/integration/test_coach_integration.py`
- [ ] T016 [P] Create frontend functional tests: `frontend/tests/functional/test_coach.spec.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - See Today's Recommended Workout (Priority: P1) 🎯 MVP

**Goal**: Display AI-generated daily workout recommendation on home page

**Independent Test**: With mock backend response, home page renders recommendation card with title, workout details, and rationale

### Backend Implementation for User Story 1

- [ ] T017 [P] [US1] Implement placeholder endpoint in `backend/functions/coach/__init__.py` returning hardcoded recommendation JSON
- [ ] T018 [P] [US1] Implement training context builder in `backend/functions/shared/training_context.py`
- [ ] T019 [US1] Implement MCP data fetcher in `backend/functions/coach/__init__.py` to query recent activities
- [ ] T020 [US1] Implement training context summarization logic in `backend/functions/shared/training_context.py`
- [ ] T021 [US1] Implement AI agent caller in `backend/functions/coach/__init__.py` with structured output request
- [ ] T022 [US1] Add response validation with Pydantic in `backend/functions/coach/__init__.py`
- [ ] T023 [US1] Add error handling and fallback logic in `backend/functions/coach/__init__.py`
- [ ] T024 [US1] Add timeout handling (3s budget) in `backend/functions/coach/__init__.py`
- [ ] T025 [US1] Add logging with correlation IDs in `backend/functions/coach/__init__.py`

### Frontend Implementation for User Story 1

- [ ] T026 [P] [US1] Add fetchRecommendation() function to `frontend/src/services/api.js`
- [ ] T027 [US1] Add recommendation card HTML structure to `frontend/src/index.html`
- [ ] T028 [US1] Add recommendation card CSS styles to `frontend/src/components/styles.css`
- [ ] T029 [US1] Implement loading skeleton state in `frontend/src/index.html`
- [ ] T030 [US1] Implement error/fallback display state in `frontend/src/index.html`
- [ ] T031 [US1] Wire recommendation fetch on page load in `frontend/src/index.html`

### Testing for User Story 1

- [ ] T032 [P] [US1] Unit test for DailyRecommendation validation in `backend/tests/unit/test_coach_models.py`
- [ ] T033 [P] [US1] Unit test for WorkoutDetails validation in `backend/tests/unit/test_coach_models.py`
- [ ] T034 [P] [US1] Unit test for fallback generator in `backend/tests/unit/test_coach_models.py`
- [ ] T035 [P] [US1] Unit test for training context builder with mocked MCP data in `backend/tests/unit/test_training_context.py`
- [ ] T036 [P] [US1] Unit test for AI client with mocked responses in `backend/tests/unit/test_ai_client.py`
- [ ] T037 [US1] Integration test for MCP server connectivity in `backend/tests/integration/test_coach_integration.py`
- [ ] T038 [US1] Integration test for AI agent invocation in `backend/tests/integration/test_coach_integration.py`
- [ ] T039 [US1] Integration test for end-to-end recommendation flow in `backend/tests/integration/test_coach_integration.py`
- [ ] T040 [US1] Functional test for home page rendering recommendation in `frontend/tests/functional/test_coach.spec.ts`
- [ ] T041 [US1] Functional test for loading state display in `frontend/tests/functional/test_coach.spec.ts`
- [ ] T042 [US1] Functional test for fallback state display in `frontend/tests/functional/test_coach.spec.ts`

**Checkpoint**: At this point, User Story 1 should be fully functional - home page displays recommendation

---

## Phase 4: User Story 2 - Recommendation Updates After Logging (Priority: P2)

**Goal**: After logging an activity, recommendation updates to reflect new training state

**Independent Test**: After successful activity save, home redirect shows success toast and updated recommendation

### Implementation for User Story 2

- [ ] T043 [US2] Verify existing redirect to home after activity save in `frontend/src/pages/log-activity.html`
- [ ] T044 [US2] Add recommendation refresh trigger on home page load in `frontend/src/index.html`
- [ ] T045 [US2] Verify success toast displays after redirect in `frontend/src/index.html`
- [ ] T046 [US2] Add cache-busting to recommendation API call in `frontend/src/services/api.js`

### Testing for User Story 2

- [ ] T047 [US2] Functional test for activity save redirect flow in `frontend/tests/functional/test_coach.spec.ts`
- [ ] T048 [US2] Functional test for success toast display after save in `frontend/tests/functional/test_coach.spec.ts`
- [ ] T049 [US2] Functional test for recommendation refresh after save in `frontend/tests/functional/test_coach.spec.ts`

**Checkpoint**: At this point, both User Stories 1 AND 2 should work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T050 [P] Update `backend/functions/local.settings.json.example` with AI_FOUNDRY_ENDPOINT and MCP_SERVER_ENDPOINT
- [ ] T051 [P] Add Application Insights custom metrics for recommendation latency in `backend/functions/coach/__init__.py`
- [ ] T052 [P] Add Application Insights custom metrics for fallback rate in `backend/functions/coach/__init__.py`
- [ ] T053 [P] Document MCP server tools usage in `specs/002-ai-homepage-coach/research.md`
- [ ] T054 [P] Add CORS configuration for Function App in `backend/functions/host.json`
- [ ] T055 Validate quickstart.md instructions with fresh local setup
- [ ] T056 Add README section for AI coach feature configuration
- [ ] T057 [P] Security review: verify no secrets exposed to frontend
- [ ] T058 [P] Performance review: verify p95 latency < 3s in Application Insights
- [ ] T059 Update infrastructure as code with App Settings in `infra/modules/backend.bicep`
- [ ] T060 Add managed identity RBAC role assignment in `infra/main.bicep` for AI Foundry access
- [ ] T061 Run all tests: `cd backend && pytest && cd ../frontend/tests/functional && npm test`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion (can run in parallel with US1 if staffed)
- **Polish (Phase 5)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Integrates with US1 but testable independently

### Within Each User Story

1. Backend models and infrastructure first
2. Backend implementation
3. Frontend implementation
4. Tests (can run in parallel with implementation)
5. Story validation and checkpoint

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# All tasks marked [P] can run simultaneously
T004 (requirements.txt) || T005 (models.py) || T006 (.gitignore)
```

**Phase 2 (Foundational)**:
```bash
# After T007 completes, these can run in parallel
T008 (WorkoutDetails) || T009 (TrainingContext) || T011 (MCP client) || T012 (AI client) || T015 (integration tests) || T016 (functional tests)
```

**Phase 3 (User Story 1 Backend)**:
```bash
# After T019-T020 complete, these can run in parallel
T017 (placeholder) || T018 (context builder)
# Then in parallel:
T026-T031 (all frontend tasks)
T032-T042 (all test tasks)
```

**Phase 5 (Polish)**:
```bash
# Most polish tasks can run in parallel
T050 || T051 || T052 || T053 || T054 || T057 || T058
```

---

## Parallel Example: User Story 1

```bash
# After foundational phase, work in 3 parallel streams:

# Stream 1: Backend Core
T017 → T019 → T020 → T021 → T022 → T023 → T024 → T025

# Stream 2: Frontend (can start after T017 placeholder exists)
T026 → T027 → T028 → T029 → T030 → T031

# Stream 3: Tests (can start as soon as code structure exists)
T032 → T033 → T034 → T035 → T036 → T037 → T038 → T039 → T040 → T041 → T042
```

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Goal**: Deliver core value with minimal risk

**Include**:
- User Story 1 (P1) - See Today's Recommended Workout
- Placeholder backend for UI validation (T017)
- Basic frontend rendering (T026-T031)
- Essential tests (T032-T042)

**Defer to Later**:
- User Story 2 (P2) - can be added after US1 validation
- Performance optimizations (Phase 5)
- Caching and advanced features

### Incremental Delivery Approach

1. **Sprint 1**: Phase 1 (Setup) + Phase 2 (Foundational) + T017 (placeholder backend)
2. **Sprint 2**: Complete User Story 1 backend (T019-T025)
3. **Sprint 3**: Complete User Story 1 frontend (T026-T031) + tests (T032-T042)
4. **Sprint 4**: User Story 2 (T043-T049) + Polish (T050-T061)

### Validation Checkpoints

- **After T017**: Home page displays placeholder recommendation (UI validated)
- **After T025**: Backend returns real AI recommendations (integration validated)
- **After T042**: All User Story 1 tests pass (quality validated)
- **After T049**: Activity logging triggers recommendation refresh (US2 validated)
- **After T061**: All tests pass, ready for production deployment

---

## Total Task Count

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 10 tasks
- **Phase 3 (User Story 1)**: 26 tasks
- **Phase 4 (User Story 2)**: 7 tasks
- **Phase 5 (Polish)**: 12 tasks
- **Total**: 61 tasks

**Parallelization**: ~30% of tasks marked [P] can run in parallel with proper team coordination.

**MVP (User Story 1 only)**: 42 tasks (Phases 1, 2, 3)
