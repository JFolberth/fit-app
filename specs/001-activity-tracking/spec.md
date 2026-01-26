# Feature Specification: Activity Tracking

**Feature Branch**: `[001-activity-tracking]`  
**Created**: 2026-01-21  
**Status**: Draft  
**Input**: User description: "Build a fitness tracking app that tracks running, rowing, and rucking. For runs: duration and distance. For rowing: duration. For rucking: duration and distance. All activities: average heart rate (BPM), comments, and activity date (default current day). Users can quickly see a history of all activities and an additional comments feed. Future: training plan page via an Azure Agent in Foundry (later). Focus now: tracking activities."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Log an Activity (Priority: P1)

A user records an activity (running, rowing, or rucking) with required fields per type, plus optional comments. The activity date defaults to today but can be overridden.

**Why this priority**: Core value of the app is capturing training data quickly and accurately.

**Independent Test**: User can submit a valid activity form and see it saved in history without any other features present.

**Acceptance Scenarios**:

1. **Given** the user selects "Run" and enters duration and distance, **When** the user submits, **Then** the activity is saved with average BPM (if provided), comments, and date (default today if not changed).
2. **Given** the user selects "Rowing" and enters duration only, **When** the user submits, **Then** the activity is saved with required fields and optional BPM/comments/date.
3. **Given** the user selects "Rucking" and enters duration and distance, **When** the user submits, **Then** the activity is saved with optional BPM/comments/date.
4. **Given** a valid submission, **When** the system saves the activity, **Then** the user sees a success notification.
5. **Given** an invalid submission (e.g., missing required fields or out-of-range values), **When** the user submits, **Then** the user sees an error notification with actionable guidance.

---

### User Story 2 - View Activity History (Priority: P2)

A user views a chronological list of all recorded activities with key details and can filter by activity type.

**Why this priority**: Users need quick visibility into past training for tracking progress.

**Independent Test**: With existing activities in storage, user can load a history list, see entries ordered by date, and apply a type filter.

**Acceptance Scenarios**:

1. **Given** multiple activities exist, **When** the user opens History, **Then** activities are shown sorted by most recent first with type, duration, distance (if applicable), average BPM, comments indicator, and date.
2. **Given** activities of various types exist, **When** the user applies a filter for "Running", **Then** only running entries are displayed.

---

### Edge Cases

- Activity date in the future or far past is entered. If in the future this should fail. If more then a year then the current date it should fail.
- Missing required fields per activity type (e.g., run without distance).
- Non-numeric or out-of-range values (e.g., BPM < 20 or > 240; duration <= 0; distance <= 0).
- Duplicate submissions from double-click or offline retries.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST allow users to record an activity of type Running, Rowing, or Rucking.
- **FR-002**: For Running, system MUST require duration and distance, BPM, and date with date defaulting to current day. Comments are optional
- **FR-003**: For Rowing, system MUST require duration, BPM, comments, and date with date defaulting to current day. Comments are optional
- **FR-004**: For Rucking, system MUST require duration and distance, BPM, comments, and date defaulting to current day. Comments are optional
- **FR-005**: System MUST capture average heart rate (BPM) when provided and validate it within a reasonable human range (20–240 BPM).
- **FR-006**: System MUST store optional per-activity comments (free text) with each activity.
- **FR-007**: System MUST default the activity date to the current day with the ability to override.
- **FR-008**: System MUST present a history view listing all activities sorted by most recent first.
- **FR-009**: System MUST support filtering the history by activity type.
- **FR-010**: System MUST validate numeric inputs (duration, distance, BPM) are positive and within sensible ranges.
- **FR-011**: System MUST persist recorded activities and comments for later retrieval.
- **FR-012**: System MUST support editing or deleting an existing activity entry.
- **FR-013**: System MUST prevent duplicate submissions within a short time window.
- **FR-014**: System MUST display clear validation errors and allow correction before submission.
- **FR-016**: System MUST notify the user of success or failure for create, update, and delete actions.

*Clarifications:*

- **FR-015**: single-user without authentication

### Key Entities *(include if feature involves data)*

- **Activity**: Represents a logged training session.
  - Attributes: `id`, `type` (Running|Rowing|Rucking), `duration`, `distance` (nullable for Rowing), `avgBpm` (optional), `comments` (optional text), `date` (defaults to current day), `createdAt`, `updatedAt`.
- **Comment**: Represents an entry in the global comments feed (not tied to a specific activity).
  - Attributes: `id`, `text`, `createdAt`, `author` (optional subject if multi-user), `reactions` (optional future enhancement).

## Assumptions & Dependencies

- Assumption: Until clarified, treat the app as single-user with no authentication; multi-user and auth may be introduced later. See FR-015.
- Assumption: Default units are minutes for duration and miles for distance; users can change units later if needed.
- Assumption: Comments are plain text without rich media initially.
- Out of Scope (for this feature): Training plan page via Azure Agent in Foundry; device integrations for heart rate; advanced analytics.
- Dependency: Persistent storage layer to retain activities and comments.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Users can log a valid activity in under 30 seconds.
- **SC-002**: 95% of history page loads display entries in under 1 second for up to 1,000 stored activities.
- **SC-003**: 90% of users can successfully log an activity on first attempt without error.
- **SC-004**: 100% of recorded activities and comments persist and remain visible after application restart.
- **SC-005**: Validation prevents 99% of malformed submissions (e.g., negative duration/distance, out-of-range BPM).
- **SC-006**: Success/failure notification appears within 1 second of action, and users rate clarity of messages at 4/5 or higher in usability tests.
