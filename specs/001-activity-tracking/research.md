# Phase 0 Research: Activity Tracking

## Decisions

- Decision: Azure Static Web Apps + Python Azure Functions backend
  - Rationale: SWA provides a global CDN and easy static hosting; Python Functions offer serverless API to interact with Cosmos DB.
  - Alternatives considered: App Service (heavier for simple static+API), Container Apps (overkill for MVP), pure client-side with REST keys (rejected: no secrets and managed identity required).

- Decision: Cosmos DB (NoSQL) with data-plane RBAC and Managed Identity
  - Rationale: Schema-less storage fits variable activity/comment payloads; data-plane RBAC enables least-privilege managed identity access; avoids keys.
  - Alternatives considered: Azure Table Storage (limited query model), SQLite/file storage (not Azure-first), PostgreSQL (requires schema; less flexible for MVP).

- Decision: Azure Verified Modules (AVM) for infra
  - Rationale: AVM accelerates secure, consistent IaC for Cosmos DB and related resources; aligns with constitution Azure-optimized principle.
  - Alternatives considered: raw Bicep (more boilerplate), Terraform (possible; but Bicep preferred per constitution).

- Decision: Devcontainer-first
  - Rationale: Deterministic build/test environment; CI runs inside same image; speeds onboarding and redeploy.
  - Alternatives considered: local-only setup (inconsistent), per-developer configuration (fragile).

- Decision: Testing strategy (unit, functional, integration)
  - Rationale: Aligns with constitution Test-First, coverage goals, and CI gates; Playwright ensures UI flows; pytest covers logic and API integration.
  - Alternatives considered: Cypress (JavaScript-only; acceptable but Python-first repo favors Playwright), unit-only (insufficient coverage of flows).

- Decision: Notifications for CRUD success/failure
  - Rationale: Clear user feedback and acceptance criteria; supports PWA UX.
  - Alternatives considered: silent failures (rejected), status-only banners (less actionable).

## Best Practices consulted

- Static Web Apps CLI: use `swa init`, `swa build`, `swa deploy` and let CLI generate config files; do not create `staticwebapp.config.json` manually.
- Cosmos DB access: use Managed Identity; enable data-plane RBAC; avoid key-based authentication; implement retry/backoff; monitor.
- Infra: prefer Bicep under `infra/` using AVM modules; latest API versions; Key Vault for secrets; role assignments with least privilege.
- CI: build/lint/test/security gates; branch protection; matrix as needed; devcontainer parity.

## Open Items resolved

- Identity: Single-user scope confirmed (FR-015); auth deferred.
- Role assignment: API’s managed identity needs Cosmos DB Built-in Data Contributor (data-plane) to read/write items.

## References

- Azure Static Web Apps CLI best practices (tool guidance)
- General Azure best practices (security, RBAC, MI, IaC)
