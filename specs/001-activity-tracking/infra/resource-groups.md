# Resource Groups Plan (Azure AVM)

## Environments
- dev
- prod

## Resource Group Split (per environment)
- Frontend: `rg-fitapp-<env>-frontend` (Azure Static Web App and frontend App Insights)
- Backend: `rg-fitapp-<env>-backend` (Azure Functions — Python and backend App Insights)
- Data: `rg-fitapp-<env>-cosmos` (Azure Cosmos DB NoSQL)
- Observability: `rg-fitapp-<env>-monitoring` (Log Analytics)

## RBAC & Identity
- Backend Functions: System-Assigned Managed Identity
- Role assignment: Grant Functions MI "Cosmos DB Built-in Data Contributor" at Cosmos account scope (data-plane).
- Rationale: Frontend (SWA) should not access Cosmos directly; API mediates all CRUD with validation.

## AVM Modules (Bicep) to Use
- Cosmos DB account (`Microsoft.DocumentDB/databaseAccounts`) + database + containers
- Static Web App (`Microsoft.Web/staticSites`)
- Log Analytics Workspace (`Microsoft.OperationalInsights/workspaces`) + App Insights (`Microsoft.Insights/components`)
- Role assignments (`Microsoft.Authorization/roleAssignments`) for data-plane contributor

## Naming & Tags
- Names include env suffix; tags: `app=fitapp`, `env=<env>`, `owner=JFolberth`, `component=<frontend|backend|data|observability>`

## Deployment Strategy
- Deploy each RG independently via Bicep under `infra/` using AVM modules.
- Validation via `what-if`; promote from `dev` to `prod` after gates pass.
