---
description: "Task list for Activity Edit & Delete feature implementation"
---

# Tasks: Activity Edit & Delete

**Input**: Design documents from `/specs/003-activity-edit-delete/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Required per constitution — include functional tests for all UI flows.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: UI Components (Shared)

**Purpose**: Create the visual components needed for edit and delete functionality

- [X] T001 [P] Add Edit/Delete action buttons to activity items in `frontend/src/pages/history.html`
- [X] T002 [P] Create Edit Modal markup in `frontend/src/pages/history.html`
- [X] T003 [P] Create Delete Confirmation Dialog markup in `frontend/src/pages/history.html`
- [X] T004 [P] Add modal, dialog, and action button styles in `frontend/src/components/styles.css`

**Checkpoint**: Visual components exist but are not yet functional

---

## Phase 2: User Story 1 - Edit an Activity (Priority: P1)

**Goal**: Users can edit any activity field with validation

**Independent Test**: Edit button opens modal, form validates, successful edit updates history

### Tests for User Story 1

- [X] T005 [US1] Functional test for edit modal opening with pre-populated data in `frontend/tests/functional/test_history.spec.ts`
- [X] T006 [US1] Functional test for edit validation errors in `frontend/tests/functional/test_history.spec.ts`
- [X] T007 [US1] Functional test for successful edit flow in `frontend/tests/functional/test_history.spec.ts`
- [X] T008 [US1] Functional test for edit cancel flow in `frontend/tests/functional/test_history.spec.ts`

### Implementation for User Story 1

- [X] T009 [US1] Implement edit button click handler to open modal in `frontend/src/pages/history.html`
- [X] T010 [US1] Implement modal form pre-population with activity data in `frontend/src/pages/history.html`
- [X] T011 [US1] Implement edit form submission with API call in `frontend/src/pages/history.html`
- [X] T012 [US1] Implement validation error display in edit modal in `frontend/src/pages/history.html`
- [X] T013 [US1] Implement modal close/cancel behavior in `frontend/src/pages/history.html`
- [X] T014 [US1] Implement history refresh after successful edit in `frontend/src/pages/history.html`

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 3: User Story 2 - Delete an Activity (Priority: P1)

**Goal**: Users can delete activities with confirmation

**Independent Test**: Delete button opens confirmation, confirm deletes activity, cancel preserves activity

### Tests for User Story 2

- [X] T015 [US2] Functional test for delete confirmation dialog in `frontend/tests/functional/test_history.spec.ts`
- [X] T016 [US2] Functional test for successful delete flow in `frontend/tests/functional/test_history.spec.ts`
- [X] T017 [US2] Functional test for delete cancel flow in `frontend/tests/functional/test_history.spec.ts`

### Implementation for User Story 2

- [X] T018 [US2] Implement delete button click handler to open confirmation in `frontend/src/pages/history.html`
- [X] T019 [US2] Implement confirmation dialog confirm action with API call in `frontend/src/pages/history.html`
- [X] T020 [US2] Implement confirmation dialog cancel action in `frontend/src/pages/history.html`
- [X] T021 [US2] Implement history refresh after successful delete in `frontend/src/pages/history.html`

**Checkpoint**: User Story 2 should be fully functional and testable independently

---

## Phase 4: Polish & Accessibility

**Purpose**: Ensure quality, accessibility, and cross-browser compatibility

- [X] T022 [P] Add keyboard navigation support for modal (Tab, Escape) in `frontend/src/pages/history.html`
- [X] T023 [P] Add ARIA attributes for accessibility in `frontend/src/pages/history.html`
- [X] T024 [P] Add loading states during API operations in `frontend/src/pages/history.html`
- [X] T025 [P] Test mobile responsiveness of modal and dialogs
- [X] T026 Verify all existing tests still pass (regression check)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (UI Components)**: No dependencies — can start immediately
- **Phase 2 (Edit)**: Depends on T001, T002, T004 (edit button, modal, styles)
- **Phase 3 (Delete)**: Depends on T001, T003, T004 (delete button, dialog, styles)
- **Phase 4 (Polish)**: Depends on Phases 2 and 3 completion

### Parallel Execution

- T001-T004 can run in parallel (different concerns)
- US1 and US2 implementation can run in parallel after Phase 1
- Tests should be written before or alongside implementation (TDD encouraged)
