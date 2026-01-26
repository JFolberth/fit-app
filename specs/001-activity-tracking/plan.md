# Implementation Plan: Activity Tracking

**Branch**: `[001-activity-tracking]` | **Date**: 2026-01-21 | **Spec**: specs/001-activity-tracking/spec.md
**Input**: Feature specification from `/specs/001-activity-tracking/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Python-based Azure Static Web App with a minimal responsive frontend (PWA-ready) and a Python Azure Functions API that persists activities to Azure Cosmos DB (NoSQL, schema-less). Use Azure Verified Modules (AVM) for infra provisioning and assign data-plane RBAC so the API (via managed identity) has Cosmos DB Built-in Data Contributor. Enforce devcontainer-first reproducibility and CI quality gates (build/lint/unit/functional/integration/security) aligned to the constitution.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: Azure Functions (Python), Azure SDK for Cosmos DB (NoSQL), Playwright (functional/E2E), pytest (unit/integration)  
**Storage**: Azure Cosmos DB (NoSQL) with data-plane RBAC and managed identity  
**Testing**: pytest for unit/integration; Playwright for functional/E2E; coverage ≥90% for core logic  
**Target Platform**: Web (Azure Static Web Apps) — responsive desktop/mobile; PWA-ready  
**Project Type**: Web (frontend static site + Python Functions API)  
**Performance Goals**: History loads <1s for ≤1000 activities; API p95 <200ms on dev/test  
**Constraints**: Devcontainer parity; deterministic builds; no secrets in repo; managed identity only  
**Scale/Scope**: Single-user scope initially; future expansion to multi-user auth

## Infrastructure & Resource Groups

Resource group separation is required per best practices to isolate blast radius, access scopes, and lifecycle:

- Environments: `dev`, `prod` (extendable to `test` if needed)

Per environment, create distinct resource groups:
- Frontend RG: `rg-fitapp-<env>-frontend` (Azure Static Web App)
- Backend RG: `rg-fitapp-<env>-backend` (Azure Functions — Python API)
- Data RG: `rg-fitapp-<env>-cosmos` (Azure Cosmos DB — NoSQL account, database, containers)
- Observability RG: `rg-fitapp-<env>-monitoring` (Log Analytics Workspace, Application Insights)

RBAC & Identity:
- Backend Functions use a System-Assigned Managed Identity.
- Assign Cosmos DB data-plane role to the Functions MI at the Cosmos account scope: Built-in role "Cosmos DB Built-in Data Contributor". This enables CRUD on items without keys.
- Note: The Static Web App (frontend) should not access Cosmos directly. All data access occurs via the backend API for least-privilege and controlled validation.

AVM Modules (Bicep):
- Cosmos DB account, database, and container modules (AVM) in `infra/`.
- Static Web App module (AVM) in `infra/`.
- Log Analytics Workspace module (AVM) and Application Insights linkage.
- Role Assignment module (or raw bicep resource) to grant Functions MI data-plane contributor at the Cosmos scope.

Naming & Tags:
- Resource names and RGs include environment suffix; apply tags: `app=fitapp`, `env=<env>`, `owner=JFolberth`, `component=frontend|backend|data|observability`.

Deployment:
- Single `infra/` folder with environment-specific `.bicepparam` files (e.g., `infra/params/dev.bicepparam`, `infra/params/prod.bicepparam`).
- Deploy the same `main.bicep` with different parameters per environment; use `what-if` prior to apply.
- Promotion flow: provision `dev` → validate → promote to `prod` with prod params.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Tests required: Unit, functional (UI flows), integration (API↔Cosmos). Target coverage ≥90% (core).
- Devcontainer-first: All build/test/lint run inside container; CI uses same image.
- CI quality gates: Build, lint, unit, functional, integration, security scan; branch protection on `main`.
- Azure-optimized: Infra via Bicep using AVM; Key Vault for secrets; managed identity + least privilege.

Status: PASS (committed to implementing gates in plan and artifacts below).

Post-Design Re-check: PASS (Phase 0/1 artifacts include testing strategy, devcontainer parity commitment, CI gate definitions, and Azure-first IaC with AVM).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
backend/
├── functions/                 # Azure Functions (Python) HTTP API
│   ├── activities/            # CRUD endpoints for activities
│   └── comments/              # CRUD endpoints for comments
└── tests/
  ├── unit/
  ├── integration/
  └── contract/

frontend/
├── src/
│   ├── pages/
│   ├── components/
│   └── services/              # client-side API calls
└── tests/
  └── functional/            # Playwright scenarios
```

**Structure Decision**: Web application with `frontend/` static site and `backend/functions/` Python Azure Functions API. Tests organized under `backend/tests` and `frontend/tests`. Contracts and feature docs in `specs/001-activity-tracking/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
