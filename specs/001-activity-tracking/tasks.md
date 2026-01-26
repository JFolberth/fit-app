---

description: "Task list for Activity Tracking feature implementation"
---

# Tasks: Activity Tracking

**Input**: Design documents from `/specs/001-activity-tracking/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Required per constitution — include unit, functional, and integration.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

 - [X] T001 Create project skeleton per plan: backend/, frontend/, infra/, .github/ in repo root
 - [X] T002 [P] Scaffold backend structure: `backend/functions/activities/`, `backend/functions/shared/`
 - [X] T003 [P] Scaffold frontend structure: `frontend/src/pages/`, `frontend/src/components/`, `frontend/src/services/`, `frontend/tests/functional/`
 - [X] T004 [P] Add devcontainer config in `.devcontainer/devcontainer.json`
 - [X] T005 [P] Add devcontainer Dockerfile in `.devcontainer/Dockerfile`
 - [X] T006 [P] Add backend Python deps in `backend/requirements.txt`
 - [X] T007 [P] Initialize Static Web Apps CLI via quickstart doc updates in `specs/001-activity-tracking/quickstart.md`
 - [X] T008 [P] Create CI workflow file in `.github/workflows/ci.yml`
 - [X] T009 [P] Create single infra folder: `infra/`
 - [X] T010 [P] Create `infra/main.bicep` (AVM modules: SWA, Functions, Cosmos, Log Analytics, role assignments)
 - [X] T011 [P] Create `infra/params/dev.bicepparam` and `infra/params/prod.bicepparam`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

 - [X] T010 Define `Activity` validators in `backend/functions/shared/validation.py`
 - [X] T011 [P] Implement Cosmos client with Managed Identity in `backend/functions/shared/cosmos_client.py`
 - [X] T012 [P] Configure logging and telemetry hooks in `backend/functions/shared/logging.py`
 - [X] T013 [P] Create Functions host config in `backend/functions/host.json`
 - [X] T014 [P] Add local settings template (no secrets) in `backend/functions/local.settings.json`
 - [X] T015 [P] Configure SWA to proxy API in `frontend/src/services/api.js`
 - [X] T016 [P] Add `.env.example` and document required variables in `README.md`
 - [X] T017 Establish CI gates (build/lint/unit/functional/integration/security) in `.github/workflows/ci.yml`
 - [X] T018 [P] Add security scan step (e.g., `pip-audit`/`bandit`) in `.github/workflows/ci.yml`
 - [X] T019 [P] Add Playwright setup in `frontend/tests/functional/playwright.config.ts`
 - [X] T020 [P] Add pytest config in `backend/tests/pytest.ini`
 - [X] T021 [P] Add CodeQL workflow in `.github/workflows/codeql.yml` (GitHub Advanced Security)
 - [X] T022 [P] Add Dependabot config in `.github/dependabot.yml` (updates for `pip`, `npm`)
 - [X] T023 [P] Add MCP configuration and VS Code extension settings to `.devcontainer/devcontainer.json`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Log an Activity (Priority: P1) 🎯 MVP

**Goal**: Users can log running, rowing, or rucking with required fields; optional BPM, comments, date default to today

**Independent Test**: Submitting a valid activity saves it and displays success notification; invalid input shows actionable error notification

### Tests for User Story 1

 - [X] T023 [P] [US1] Contract test for `POST /activities` in `backend/tests/contract/test_activities_contract.py`
 - [X] T024 [P] [US1] Integration test for create/update/delete in `backend/tests/integration/test_activities_crud.py`
 - [X] T025 [P] [US1] Functional test for log form UX in `frontend/tests/functional/test_log_activity.spec.ts`

### Implementation for User Story 1

 - [X] T026 [P] [US1] Implement HTTP function route config in `backend/functions/activities/function.json`
 - [X] T027 [US1] Implement handler in `backend/functions/activities/__init__.py` (create/update/delete)
 - [X] T028 [US1] Apply validation rules in `backend/functions/shared/validation.py`
 - [X] T029 [US1] Persist to Cosmos via `backend/functions/shared/cosmos_client.py`
 - [X] T030 [US1] Create log activity page in `frontend/src/pages/log-activity.html`
 - [X] T031 [US1] Implement API calls in `frontend/src/services/api.js` (create/update/delete)
 - [X] T032 [US1] Add success/error notifications in `frontend/src/components/Notification.js`
 - [X] T033 [US1] Add basic styling and accessibility in `frontend/src/components/styles.css`

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Activity History (Priority: P2)

**Goal**: Users can view a chronological history and filter by type

**Independent Test**: With stored activities, history loads <1s for ≤1000 entries and filtering by type works

### Tests for User Story 2

 - [X] T034 [P] [US2] Contract test for `GET /activities` in `backend/tests/contract/test_activities_list_contract.py`
 - [X] T035 [P] [US2] Integration test for list + filter in `backend/tests/integration/test_activities_list.py`
 - [X] T036 [P] [US2] Functional test for history page UX in `frontend/tests/functional/test_history.spec.ts`

### Implementation for User Story 2

 - [X] T037 [P] [US2] Implement list route config in `backend/functions/activities/function.json`
 - [X] T038 [US2] Implement list handler with sort/filter in `backend/functions/activities/__init__.py`
 - [X] T039 [US2] Optimize query/index hints in `backend/functions/shared/cosmos_client.py`
 - [X] T040 [US2] Build history page in `frontend/src/pages/history.html`
 - [X] T041 [US2] Add filter UI and behavior in `frontend/src/components/TypeFilter.js`

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T042 [P] Documentation updates: `README.md`, `specs/001-activity-tracking/quickstart.md`
- [X] T043 Code cleanup and refactoring across `backend/functions/` and `frontend/src/`
- [X] T044 Performance optimization for history queries in `backend/functions/shared/cosmos_client.py`
- [X] T045 [P] Additional unit tests in `backend/tests/unit/`
- [X] T046 Security hardening (headers, input sanitization) in `backend/functions/activities/__init__.py`
- [X] T047 Run quickstart validation steps in `specs/001-activity-tracking/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Independent of US1; shares data/client only

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Examples

### User Story 1

```bash
# Launch tests for US1 together (contract, integration, functional)
backend/tests/contract/test_activities_contract.py
backend/tests/integration/test_activities_crud.py
frontend/tests/functional/test_log_activity.spec.ts

# Create models/validators and handler in parallel
backend/functions/shared/validation.py
backend/functions/activities/__init__.py
```

### User Story 2

```bash
# Launch tests for US2 together (contract, integration, functional)
backend/tests/contract/test_activities_list_contract.py
backend/tests/integration/test_activities_list.py
frontend/tests/functional/test_history.spec.ts
```

 

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. STOP and VALIDATE: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. Stories complete and integrate independently
