# Implementation Plan: Activity Edit & Delete

**Branch**: `[003-activity-edit-delete]` | **Date**: 2026-02-03 | **Spec**: specs/003-activity-edit-delete/spec.md
**Input**: Feature specification from `/specs/003-activity-edit-delete/spec.md`

## Summary

Extend the existing Activity Tracking frontend to include Edit and Delete capabilities for logged activities. The backend API already supports PUT and DELETE operations; this feature focuses on frontend UI implementation, user experience, and comprehensive test coverage. Maintains the simple, accessible design language established in the initial feature.

## Technical Context

**Language/Version**: JavaScript (ES6 modules), HTML5, CSS3  
**Primary Dependencies**: Existing api.js (updateActivity, deleteActivity), Notification.js, styles.css  
**Storage**: Azure Cosmos DB via existing backend API (no backend changes required)  
**Testing**: Playwright for functional/E2E tests; existing pytest for backend (if any edge cases need coverage)  
**Target Platform**: Web (Azure Static Web Apps) — responsive desktop/mobile  
**Project Type**: Frontend enhancement to existing web application  
**Constraints**: No new dependencies; maintain existing design system; keyboard accessible

## Constitution Check

*GATE: Must pass before implementation.*

- Tests required: Functional tests for edit/delete UI flows; integration tests if new backend paths exercised.
- Devcontainer-first: All work runnable inside container.
- CI quality gates: Functional tests must pass before merge.
- Azure-optimized: No infrastructure changes; uses existing API.

Status: PASS

## Architecture Decisions

### UI Pattern: Modal-based Edit

**Decision**: Use a modal dialog for editing activities rather than inline editing.

**Rationale**:
- Consistent with mobile-friendly design (modals work well on small screens)
- Clear visual separation between viewing and editing modes
- Easier to implement cancel/discard without complex state management
- Matches confirmation dialog pattern for delete

### Delete Confirmation: Native-style Dialog

**Decision**: Use a simple confirmation modal rather than browser `confirm()`.

**Rationale**:
- Consistent styling with the rest of the application
- Can be styled and made accessible
- Browser `confirm()` cannot be customized and blocks the UI thread

### State Management: Reload on Success

**Decision**: Reload the activity list from the API after successful edit/delete.

**Rationale**:
- Ensures data consistency with server state
- Simple implementation without complex client-side state
- Performance acceptable for current scale (<1000 activities)

## Project Structure

### Files to Modify

```text
frontend/
├── src/
│   ├── pages/
│   │   └── history.html          # Add edit/delete buttons, modal markup, event handlers
│   └── components/
│       └── styles.css            # Add modal, button, and dialog styles
└── tests/
    └── functional/
        └── test_history.spec.ts  # Add edit/delete test scenarios
```

### Files Unchanged (Dependencies)

```text
frontend/
└── src/
    └── services/
        └── api.js                # Already exports updateActivity, deleteActivity
    └── components/
        └── Notification.js       # Already supports success/error notifications

backend/
└── functions/
    └── activities/
        └── __init__.py           # Already handles PUT/DELETE (no changes needed)
```

## Implementation Phases

### Phase 1: UI Components

1. Add Edit/Delete buttons to each activity item in history.html
2. Create Edit Modal component with form fields matching log-activity.html
3. Create Delete Confirmation Dialog component
4. Add CSS styles for new components

### Phase 2: Event Handling

1. Wire Edit button to open modal with pre-populated data
2. Wire Delete button to open confirmation dialog
3. Implement form submission with validation error handling
4. Implement delete confirmation flow
5. Add loading states during API calls
6. Refresh list on successful operations

### Phase 3: Testing

1. Add Playwright tests for edit flow (happy path, validation errors, cancel)
2. Add Playwright tests for delete flow (confirm, cancel)
3. Verify no regression in existing history tests

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Edit modal styling inconsistent | Reuse existing form styles from log-activity.html |
| Accessibility issues with modal | Implement focus trap, keyboard navigation, ARIA attributes |
| Race condition on rapid edit/delete | Disable buttons during API calls |
| 404 on edit/delete of stale item | Show error notification, refresh list |
