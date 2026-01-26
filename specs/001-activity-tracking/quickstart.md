# Quickstart: Activity Tracking

Complete guide for local development, testing, and deployment of the Fit App activity tracking feature.

## Prerequisites

- VS Code with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Docker Desktop (running)
- Azure subscription with appropriate permissions

## Local Development Setup

### 1. Open in Devcontainer

The devcontainer automatically installs all dependencies:
- Python 3.11
- Azure Functions Core Tools v4
- Static Web Apps CLI
- Node.js LTS
- All Python packages from `backend/requirements.txt`

```bash
git clone https://github.com/JFolberth/fit-app.git
cd fit-app
code .
```

Select **"Reopen in Container"** when prompted (or use Command Palette: `Dev Containers: Reopen in Container`).

### 2. Configure Local Settings

Create `backend/functions/local.settings.json` (never commit this file):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "COSMOS_ENDPOINT": "https://fitapp-dev-cosmos.documents.azure.com:443/",
    "COSMOS_DATABASE_NAME": "fitappdb",
    "COSMOS_CONTAINER_NAME": "activities",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": ""
  }
}
```

**For local development without Azure resources**, use Cosmos DB Emulator or Azure Cosmos DB local emulator:
```bash
# Install Cosmos DB Emulator (Windows)
# Or use Docker container (Linux/Mac):
docker run -p 8081:8081 -p 10251:10251 -p 10252:10252 -p 10253:10253 -p 10254:10254 \
  mcr.microsoft.com/cosmosdb/linux/azure-cosmos-emulator
```

Update `COSMOS_ENDPOINT` to `https://localhost:8081/` for emulator.

### 3. Run the Application Locally

**Terminal 1 - Backend (Azure Functions)**:
```bash
cd backend/functions
func start
```

Expected output:
```
Azure Functions Core Tools
Functions:
  activities: [POST,GET,PUT,DELETE] http://localhost:7071/api/activities
```

**Terminal 2 - Frontend (Static Web Apps CLI)**:
```bash
swa start frontend/src --api-location http://localhost:7071
```

Expected output:
```
Azure Static Web Apps emulator started at http://localhost:4280
```

**Access the app**: Open http://localhost:4280

## Testing

### Backend Tests

All tests use pytest and are organized by type:

```bash
cd backend

# Run all tests
pytest

# Run specific test types
pytest tests/unit/              # Unit tests (fast, no external dependencies)
pytest tests/integration/       # Integration tests (requires Cosmos DB)
pytest tests/contract/          # Contract tests (API validation)

# Run with coverage
pytest --cov=functions --cov-report=html

# Run with verbose output
pytest -v

# Stop on first failure
pytest --maxfail=1
```

### Frontend Tests

Playwright is used for functional/E2E tests:

```bash
cd frontend

# Install Playwright browsers (first time only)
npx playwright install

# Run all tests
npx playwright test

# Run with UI mode
npx playwright test --ui

# Run specific test file
npx playwright test tests/functional/test_log_activity.spec.ts

# View test report
npx playwright show-report
```

### Security Scans

```bash
# Python dependency vulnerabilities
pip-audit

# Python security linting
bandit -r backend/functions/

# CodeQL runs automatically in CI (see .github/workflows/codeql.yml)
```

## Infrastructure Deployment

### Prerequisites

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "Your Subscription Name"

# Verify Bicep CLI
az bicep version
```

### Deploy to Dev Environment

```bash
# Validate infrastructure (what-if)
az deployment sub what-if \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/dev.bicepparam

# Deploy infrastructure
az deployment sub create \
  --name fitapp-dev-$(date +%Y%m%d-%H%M%S) \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/dev.bicepparam
```

Expected resources created:
- 4 Resource Groups (monitoring, cosmos, frontend, backend)
- Log Analytics Workspace
- 2x Application Insights (frontend, backend)
- Cosmos DB account + database + container
- Static Web App
- Function App + App Service Plan

### Deploy Application Code

**Backend (Function App)**:
```bash
cd backend/functions
func azure functionapp publish fitapp-dev-func
```

**Frontend (Static Web App)**:
```bash
# Get deployment token
az staticwebapp secrets list \
  --name fitapp-dev-swa \
  --resource-group rg-fitapp-dev-frontend \
  --query "properties.apiKey" -o tsv

# Deploy
cd frontend
swa deploy ./src \
  --deployment-token <token-from-above> \
  --env production
```

### Deploy to Production

```bash
# Validate first
az deployment sub what-if \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/prod.bicepparam

# Deploy after validation
az deployment sub create \
  --name fitapp-prod-$(date +%Y%m%d-%H%M%S) \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/prod.bicepparam
```

Production uses:
- Zone-redundant Cosmos DB
- Elastic Premium (EP1) Function App
- Enhanced monitoring and alerting

## Verification Steps

After deployment, validate the infrastructure:

### 1. Check Resource Groups
```bash
az group list --query "[?contains(name, 'fitapp-dev')].name" -o table
```

Expected output:
```
rg-fitapp-dev-backend
rg-fitapp-dev-cosmos
rg-fitapp-dev-frontend
rg-fitapp-dev-monitoring
```

### 2. Verify Cosmos DB RBAC
```bash
# Get Function App Managed Identity principal ID
PRINCIPAL_ID=$(az functionapp identity show \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend \
  --query principalId -o tsv)

# Check role assignment
az cosmosdb sql role assignment list \
  --account-name fitapp-dev-cosmos \
  --resource-group rg-fitapp-dev-cosmos \
  --query "[?principalId=='$PRINCIPAL_ID']"
```

### 3. Test API Endpoints
```bash
# Get Function App URL
FUNC_URL=$(az functionapp show \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend \
  --query defaultHostName -o tsv)

# Test health (if implemented)
curl https://$FUNC_URL/api/health

# Test POST activity
curl -X POST https://$FUNC_URL/api/activities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Running",
    "duration": 1800,
    "distance": 5.0,
    "date": "2026-01-22"
  }'
```

### 4. Check Application Insights
```bash
# Verify frontend App Insights
az monitor app-insights component show \
  --app fitapp-dev-frontend-appi \
  --resource-group rg-fitapp-dev-frontend

# Verify backend App Insights
az monitor app-insights component show \
  --app fitapp-dev-backend-appi \
  --resource-group rg-fitapp-dev-backend
```

## Troubleshooting

### Function App Not Starting
```bash
# Check logs
az functionapp log tail \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend

# Check app settings
az functionapp config appsettings list \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend
```

### Cosmos DB Connection Issues
```bash
# Verify endpoint in function app settings
az functionapp config appsettings list \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend \
  --query "[?name=='COSMOS_ENDPOINT']"

# Test connectivity from function app
az functionapp run \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend \
  --command "curl https://fitapp-dev-cosmos.documents.azure.com:443/"
```

### Static Web App Deploy Fails
```bash
# Verify deployment token
az staticwebapp secrets list \
  --name fitapp-dev-swa \
  --resource-group rg-fitapp-dev-frontend

# Check build logs in portal or CLI
az staticwebapp show \
  --name fitapp-dev-swa \
  --resource-group rg-fitapp-dev-frontend
```

## Environment Variables Reference

### Backend (`local.settings.json`)

| Variable | Description | Example |
|----------|-------------|---------|
| `COSMOS_ENDPOINT` | Cosmos DB account endpoint | `https://fitapp-dev-cosmos.documents.azure.com:443/` |
| `COSMOS_DATABASE_NAME` | Database name | `fitappdb` |
| `COSMOS_CONTAINER_NAME` | Activities container name | `activities` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights connection string | `InstrumentationKey=...` |
| `FUNCTIONS_WORKER_RUNTIME` | Runtime for Functions | `python` |

### Frontend (Environment-specific)

Frontend configuration is handled via SWA configuration and API proxying - no explicit environment variables needed for local development.

## CI/CD Integration

GitHub Actions workflows are configured:

- **`.github/workflows/ci.yml`**: Runs on PRs
  - Build backend and frontend
  - Run linting (pylint, eslint)
  - Execute unit tests (pytest)
  - Run integration tests (pytest with Cosmos)
  - Execute functional tests (Playwright)
  - Security scans (bandit, pip-audit)

- **`.github/workflows/codeql.yml`**: Security analysis
  - Scans Python and JavaScript code
  - Identifies security vulnerabilities
  - Runs on push to main and PRs

## Performance Benchmarks

Expected performance targets:

- **API Response Time**: p95 < 200ms for CRUD operations
- **History Load**: < 1s for ≤1000 activities
- **Cosmos DB**: RU/s configured for anticipated load (dev: 400 RU/s, prod: auto-scale)

## Next Steps

1. ✅ Complete infrastructure deployment
2. ✅ Validate all tests pass locally
3. ✅ Deploy to dev environment
4. Validate dev deployment
5. Deploy to prod environment
6. Set up monitoring alerts
7. Configure GitHub Actions secrets for automated deployments

## Additional Resources

- **Specification**: `specs/001-activity-tracking/spec.md`
- **Implementation Plan**: `specs/001-activity-tracking/plan.md`
- **Data Model**: `specs/001-activity-tracking/data-model.md`
- **API Contracts**: `specs/001-activity-tracking/contracts/`
- **Tasks**: `specs/001-activity-tracking/tasks.md`
