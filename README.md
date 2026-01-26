# Fit App - Activity Tracking

A fitness activity tracking application built with Azure Static Web Apps, Azure Functions (Python), and Azure Cosmos DB.

## Features

- **Activity Logging**: Log running, rowing, or rucking activities with duration, distance, optional BPM, and comments
- **Activity History**: View chronological history with type-based filtering
- **Responsive Design**: PWA-ready, mobile-friendly interface
- **Secure**: Managed identity authentication, no keys in code
- **Observable**: Application Insights + Log Analytics integration

## Architecture

- **Frontend**: Azure Static Web App (vanilla JS, responsive)
- **Backend**: Azure Functions (Python 3.11) with HTTP triggers
- **Database**: Azure Cosmos DB (NoSQL) with data-plane RBAC
- **Observability**: Application Insights (frontend & backend) + Log Analytics Workspace
- **Infrastructure**: Bicep with Azure Verified Modules (AVM)

## Project Structure

```text
fit-app/
├── backend/
│   ├── functions/          # Azure Functions endpoints
│   │   ├── activities/     # CRUD for activities
│   │   └── shared/         # Validation, Cosmos client, logging
│   └── tests/              # Unit, integration, contract tests
├── frontend/
│   ├── src/                # Static site code
│   │   ├── pages/          # HTML pages
│   │   ├── components/     # UI components
│   │   └── services/       # API client
│   └── tests/functional/   # Playwright E2E tests
├── infra/
│   ├── main.bicep          # Subscription-scoped orchestrator
│   ├── modules/            # Resource group scoped modules
│   └── params/             # Environment-specific parameters
└── .devcontainer/          # Development environment config
```

## Getting Started

### Prerequisites

- [VS Code](https://code.visualstudio.com/) with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Azure subscription](https://azure.microsoft.com/free/)

### Local Development

1. **Clone and open in devcontainer**:
   ```bash
   git clone https://github.com/JFolberth/fit-app.git
   cd fit-app
   code .
   ```
   Select "Reopen in Container" when prompted.

2. **Start backend** (from `/backend/functions`):
   ```bash
   cd backend/functions
   func start
   ```

3. **Start frontend** (separate terminal):
   ```bash
   swa start frontend/src --api-location backend/functions
   ```

4. Open http://localhost:4280

### Environment Variables

Create `backend/functions/local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_ENDPOINT": "https://fitapp-dev-cosmos.documents.azure.com:443/",
    "COSMOS_DATABASE_NAME": "fitappdb",
    "COSMOS_CONTAINER_NAME": "activities"
  }
}
```

**Note**: Never commit `local.settings.json` to source control. Use `.env.example` as a template.

## Testing

### Backend Tests
```bash
# All tests
cd backend
pytest

# Specific test types
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/contract/       # Contract tests
```

### Frontend Tests
```bash
# Playwright functional tests
cd frontend
npx playwright test

# With UI
npx playwright test --ui
```

### Security Scans
```bash
# Python security audit
pip-audit
bandit -r backend/functions/

# CodeQL (via GitHub Actions)
```

## Deployment

### Infrastructure

Deploy using Bicep with environment-specific parameters:

```bash
# Validate (what-if)
az deployment sub what-if \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/dev.bicepparam

# Deploy to dev
az deployment sub create \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/dev.bicepparam

# Deploy to prod
az deployment sub create \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/prod.bicepparam
```

### Application

GitHub Actions workflows handle CI/CD:
- `.github/workflows/ci.yml`: Build, test, security scans on PRs
- `.github/workflows/codeql.yml`: Security analysis

## Infrastructure Resources

Per environment, the following resource groups are created:

- **rg-fitapp-{env}-monitoring**: Log Analytics Workspace
- **rg-fitapp-{env}-cosmos**: Cosmos DB account, database, container
- **rg-fitapp-{env}-frontend**: Static Web App + Application Insights
- **rg-fitapp-{env}-backend**: Function App + App Service Plan + Application Insights

All resources use System-Assigned Managed Identity and data-plane RBAC (no connection strings).

## Configuration

- **Cosmos DB Partition Key**: `/type` (Running, Rowing, Rucking)
- **Cosmos DB Indexing**: Composite index on `date DESC, type ASC`
- **Zone Redundancy**: Disabled in dev, enabled in prod
- **App Service Plan**: Y1 (Consumption) for dev, EP1 (Elastic Premium) for prod

## Contributing

1. Follow the [constitution](.specify/constitution.md) requirements
2. Ensure all tests pass locally before pushing
3. Update documentation for new features
4. Security scans must pass (bandit, pip-audit, CodeQL)

## License

MIT - See [LICENSE](LICENSE)

## Quick Reference

- **Spec**: `specs/001-activity-tracking/spec.md`
- **Plan**: `specs/001-activity-tracking/plan.md`
- **Tasks**: `specs/001-activity-tracking/tasks.md`
- **Quickstart**: `specs/001-activity-tracking/quickstart.md`
- **Data Model**: `specs/001-activity-tracking/data-model.md`
- **API Contracts**: `specs/001-activity-tracking/contracts/`