# Feature Specification: Activity Edit & Delete

**Feature Branch**: `[003-activity-edit-delete]`  
**Created**: 2026-02-03  
**Status**: Draft  
**Input**: User request: "We need the ability to edit or delete items out of the activity log. We should be able to do this while maintaining our simple user interface. Additionally we should have tests to accommodate for this scenario. Any record that is edited will still go through the existing validation checks."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Edit an Activity (Priority: P1)

A user can modify any field of a previously logged activity from the history view. The edited activity must pass all existing validation rules before saving.

**Why this priority**: Users frequently need to correct mistakes (typos in duration, wrong date, missing comments) without deleting and re-entering the entire activity.

**Independent Test**: User can click edit on an activity, modify fields, save successfully, and see updated values in history.

**Acceptance Scenarios**:

1. **Given** a user views the activity history, **When** they click the edit button on an activity, **Then** an edit form appears pre-populated with the activity's current values.
2. **Given** a user modifies valid fields in the edit form, **When** they submit, **Then** the activity is updated and a success notification appears.
3. **Given** a user enters invalid data (e.g., negative duration, BPM out of range), **When** they submit, **Then** the form displays validation errors and does not save.
4. **Given** an edit is successful, **When** the history reloads, **Then** the updated values are displayed with the correct `updatedAt` timestamp.
5. **Given** a user opens the edit form, **When** they click cancel, **Then** no changes are saved and the form closes.

---

### User Story 2 - Delete an Activity (Priority: P1)

A user can permanently remove an activity from their history with a confirmation step to prevent accidental deletion.

**Why this priority**: Users need to remove incorrectly logged or duplicate activities to maintain accurate records.

**Independent Test**: User can click delete on an activity, confirm deletion, and the activity is removed from history.

**Acceptance Scenarios**:

1. **Given** a user views the activity history, **When** they click the delete button on an activity, **Then** a confirmation dialog appears asking to confirm deletion.
2. **Given** the confirmation dialog is shown, **When** the user confirms, **Then** the activity is deleted and a success notification appears.
3. **Given** the confirmation dialog is shown, **When** the user cancels, **Then** no deletion occurs and the dialog closes.
4. **Given** a successful deletion, **When** the history reloads, **Then** the deleted activity no longer appears.

---

### Edge Cases

- Attempting to edit an activity that was deleted by another session (returns 404).
- Editing to change activity type (e.g., Running → Rowing) should adjust required fields (distance becomes null for Rowing).
- Concurrent edit attempts on the same activity (last write wins, per existing behavior).
- Delete confirmation dismissed by clicking outside the dialog (should cancel, not delete).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display Edit and Delete action buttons for each activity in the history view.
- **FR-002**: System MUST present an edit form/modal pre-populated with the activity's current values when Edit is clicked.
- **FR-003**: System MUST validate all edited fields using the same validation rules as activity creation (FR-010 from 001-activity-tracking).
- **FR-004**: System MUST display validation errors inline in the edit form without closing it.
- **FR-005**: System MUST update the activity in storage upon successful edit submission.
- **FR-006**: System MUST update the `updatedAt` timestamp on successful edit.
- **FR-007**: System MUST display a confirmation dialog before executing a delete action.
- **FR-008**: System MUST remove the activity from storage only after user confirms deletion.
- **FR-009**: System MUST display success notifications for successful edit and delete operations.
- **FR-010**: System MUST display error notifications if edit or delete operations fail (e.g., 404 Not Found).
- **FR-011**: System MUST refresh the history list after successful edit or delete to reflect changes.
- **FR-012**: System MUST maintain the simple, accessible UI design consistent with existing pages.

### Non-Functional Requirements

- **NFR-001**: Edit and delete operations SHOULD complete in under 500ms (API round-trip).
- **NFR-002**: UI MUST remain responsive during edit/delete operations (show loading state).
- **NFR-003**: Edit/delete buttons MUST be keyboard accessible (Tab navigation, Enter/Space activation).
- **NFR-004**: Confirmation dialog MUST trap focus for accessibility compliance.

### Key Entities *(unchanged from 001)*

- **Activity**: Existing entity with `id`, `type`, `duration`, `distance`, `avgBpm`, `comments`, `date`, `createdAt`, `updatedAt`.

## Assumptions & Dependencies

- **Assumption**: Backend API already supports PUT /activities/{id} and DELETE /activities/{id} (verified in 001-activity-tracking).
- **Assumption**: Frontend api.js already exports `updateActivity(id, payload)` and `deleteActivity(id)` functions.
- **Dependency**: Existing validation logic in `backend/functions/shared/validation.py`.
- **Dependency**: Existing notification component in `frontend/src/components/Notification.js`.
- **Out of Scope**: Undo functionality, bulk edit/delete, activity versioning/audit trail.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can edit any activity field and save within 3 clicks (Edit → modify → Save).
- **SC-002**: Users can delete an activity within 3 clicks (Delete → Confirm → Done).
- **SC-003**: 100% of edit validation errors display user-friendly messages matching creation form behavior.
- **SC-004**: Edit/delete functional tests pass with 100% success rate in CI.
- **SC-005**: No regression in existing history page load time or functionality.
