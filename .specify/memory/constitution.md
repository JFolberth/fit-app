# fit-app Constitution
<!-- Foundational policies for development, testing, CI/CD, and operations. -->

## Core Principles

### I. Determinism & Consistency First
We prioritize predictable, repeatable behavior across environments (desktop and mobile) above all else.
- Pinned tooling and dependencies; lockfiles are mandatory.
- Environment parity: local/dev/CI must run the same tasks the same way.
- Reproducible builds: source-of-truth is the dev container; CI executes inside the same image.
- Platform parity: features must behave identically on Windows/macOS/Linux and iOS/Android with documented exceptions.

### II. Dev Container–First
A fully specified dev container defines the canonical build/test environment.
- Optimize image size, prebuilt caches, and startup time.
- All developer tasks (build, test, lint, format) are runnable inside the container.
- GitHub Codespaces is supported; local VS Code devcontainer is equivalent.
- CI jobs use the devcontainer image to ensure environment consistency.

### III. Test-First (Non‑Negotiable)
Every feature must ship with unit, functional, and integration tests.
- Unit tests: cover business logic and edge cases.
- Functional tests: validate user‑facing behavior and flows.
- Integration tests: validate cross‑component/service contracts and data paths.
- Coverage targets: ≥90% for core business logic; critical paths require integration tests.


### IV. CI Quality Gates
All code changes are gated by automated build and test before merge.
- Required checks: build, lint, unit, functional, integration, and security scan.
- Branch protection: `main` requires successful checks and review approvals.
- Matrix builds to ensure cross‑platform behavior (desktop OSes, mobile targets when applicable).
- No direct pushes to protected branches; PRs only.

### V. Azure‑Optimized by Default
Decisions favor Azure services and practices for deployment, observability, and operations.
- Infrastructure as Code: prefer Bicep stored in-repo; environments are reproducible. Leverage Azure Verified Modules when we can
- Secrets managed via Azure Key Vault; no secrets in code or history.
- Telemetry via Azure Monitor/Application Insights; structured logs with correlation IDs.
- Use least privilege, managed identities where possible, and documented roles.
- Cost/performance posture reviewed regularly; scale settings versioned with infra.

## Platform Standards & Deployment Policy

### Cross‑Platform Requirements (Mobile + Desktop)
- Target platforms: Windows, macOS, Linux; iOS and Android.
- Cross‑platform frameworks are preferred to ensure feature parity.
- Platform‑specific behavior must be documented with rationale and tests.

### Reproducibility & Redeployability
- A dev container defines the canonical toolchain; onboarding is “clone → open in container → run”.
- Provide `.env.example` with required configuration; document `make`/task scripts for common flows.
- README must include “Redeploy from GitHub” steps for fresh environments.
- CI can build and package artifacts directly from a clean checkout.

### Versioning, Security, and Compliance
- Semantic Versioning; breaking changes require migration notes and deprecation windows.
- Secrets: never stored in repo; use Key Vault or local dev secrets store.
- SAST/Dependency scanning runs on PRs; high‑severity issues block merge.

### Infrastructure & Environments
- Environments: `dev`, `prod` with clear promotion workflow.
- Infra changes are reviewed and tested; drift detection is part of CI. Achieve this via Deployment Stacks

## Development Workflow & Gates

### Branching & Reviews
- Trunk‑based development with feature branches; `main` is protected.
- Code Owners approval required.

### Required PR Contents
- Tests (unit, functional, integration) updated/added for new or changed behavior.
- Documentation updates: README, deployment notes, and changelog.
- If infra changed: include environment impact and rollback plan.

### CI/CD Gates
- Build, lint, unit, functional, integration tests must pass.
- Security scans and license checks must pass.
- CI uses the devcontainer image to guarantee parity.

### Releases & Promotion
- Tag releases; publish artifacts; document deployment steps.
- Automated deployment to `dev` on merge; manual approvals for `prod`.

## Governance
The constitution supersedes other practices. Amendments require documentation, approval, and a migration plan.

### Enforcement
- All PRs/reviews verify compliance with this constitution.
- Complexity must be justified; prefer simple, maintainable solutions.
- Runtime development guidance follows the devcontainer and Azure best practices documented in-repo.

**Version**: 1.0.0 | **Ratified**: 2026-01-21 | **Last Amended**: 2026-01-21
<!-- Keep versioning and amendment dates current with changes. -->
