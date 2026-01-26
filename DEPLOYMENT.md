# Deployment Checklist for 001-Activity-Tracking

## Current Status
✅ **All 46 tasks completed** (T001-T046)
✅ **All backend tests passing** (36 tests: 31 unit + 3 contract + 2 integration)
✅ **Devcontainer configured** with Azure CLI, Azure Developer CLI, Functions Core Tools, SWA CLI
✅ **Infrastructure files ready** (Bicep templates for dev and prod environments)
✅ **Frontend tests ready** (Playwright configured)

## ⚠️ Important: Rebuild Devcontainer First

**Before proceeding with deployment**, you need to rebuild the devcontainer to get Azure CLI (az) and Azure Developer CLI (azd) installed:

1. Press `F1` in VS Code
2. Type "Dev Containers: Rebuild Container"
3. Select it and wait for rebuild to complete
4. After rebuild, verify tools:
   ```bash
   az --version
   azd version
   func --version
   swa --version
   ```

## Local Testing (Before Deployment)

### 1. Run Backend Tests
```bash
cd /workspaces/fit-app/backend/tests
pytest -v
# Expected: 36 passed
```

### 2. Start Backend Locally
```bash
cd /workspaces/fit-app/backend/functions
func start
# Backend will run on http://localhost:7071
```

### 3. Start Frontend Locally
```bash
# In a new terminal
swa start /workspaces/fit-app/frontend/src --api-location http://localhost:7071
# Frontend will run on http://localhost:4280
```

### 4. Run Playwright Tests
```bash
cd /workspaces/fit-app/frontend/tests/functional
npm test
```

## Azure Deployment Steps

### Prerequisites
- Azure subscription
- Appropriate permissions to create resource groups and resources
- Azure CLI logged in (`az login`)

### Step 1: Login to Azure
```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"
```

### Step 2: Validate Infrastructure (Dev)
```bash
cd /workspaces/fit-app

# Preview what will be created (what-if analysis)
az deployment sub what-if \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/dev.bicepparam
```

### Step 3: Deploy Infrastructure (Dev)
```bash
# Deploy all resources
az deployment sub create \
  --name fitapp-dev-$(date +%Y%m%d-%H%M%S) \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/dev.bicepparam
```

**Expected resources created:**
- `rg-fitapp-dev-monitoring` - Log Analytics Workspace, Application Insights
- `rg-fitapp-dev-cosmos` - Cosmos DB account, database, container
- `rg-fitapp-dev-frontend` - Static Web App
- `rg-fitapp-dev-backend` - Function App, App Service Plan

### Step 4: Configure Function App Settings
After infrastructure is deployed, the Function App needs environment variables:

```bash
# Get Cosmos DB endpoint
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name fitapp-dev-cosmos \
  --resource-group rg-fitapp-dev-cosmos \
  --query documentEndpoint -o tsv)

# Set Function App settings
az functionapp config appsettings set \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend \
  --settings \
    COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
    COSMOS_DATABASE_NAME="fitappdb" \
    COSMOS_CONTAINER_NAME="activities"
```

### Step 5: Deploy Backend Code
```bash
cd /workspaces/fit-app/backend/functions
func azure functionapp publish fitapp-dev-func
```

### Step 6: Deploy Frontend Code
```bash
# Get Static Web App deployment token
TOKEN=$(az staticwebapp secrets list \
  --name fitapp-dev-swa \
  --resource-group rg-fitapp-dev-frontend \
  --query "properties.apiKey" -o tsv)

# Deploy frontend
cd /workspaces/fit-app/frontend
swa deploy ./src \
  --deployment-token "$TOKEN" \
  --env production
```

### Step 7: Verify Deployment
```bash
# Check resource groups
az group list --query "[?contains(name, 'fitapp-dev')].name" -o table

# Get Function App URL
az functionapp show \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend \
  --query defaultHostName -o tsv

# Get Static Web App URL
az staticwebapp show \
  --name fitapp-dev-swa \
  --resource-group rg-fitapp-dev-frontend \
  --query defaultHostname -o tsv

# Verify Cosmos DB RBAC
PRINCIPAL_ID=$(az functionapp identity show \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend \
  --query principalId -o tsv)

az cosmosdb sql role assignment list \
  --account-name fitapp-dev-cosmos \
  --resource-group rg-fitapp-dev-cosmos \
  --query "[?principalId=='$PRINCIPAL_ID']"
```

### Step 8: Test Deployed Application
```bash
# Get Function App URL
FUNC_URL=$(az functionapp show \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend \
  --query defaultHostName -o tsv)

# Test POST endpoint
curl -X POST https://$FUNC_URL/api/activities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Running",
    "duration": 1800,
    "distance": 5.0,
    "date": "2026-01-26"
  }'

# Test GET endpoint
curl https://$FUNC_URL/api/activities
```

## Production Deployment

Once dev is validated, deploy to production:

```bash
# Validate prod infrastructure
az deployment sub what-if \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/prod.bicepparam

# Deploy prod infrastructure
az deployment sub create \
  --name fitapp-prod-$(date +%Y%m%d-%H%M%S) \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/params/prod.bicepparam

# Repeat Steps 4-7 above for production (replace 'dev' with 'prod')
```

## Monitoring & Observability

### View Application Insights
```bash
# Get Application Insights App ID
az monitor app-insights component show \
  --app fitapp-dev-backend-appi \
  --resource-group rg-fitapp-dev-backend \
  --query appId -o tsv
```

Visit Azure Portal → Application Insights to view:
- Request traces
- Performance metrics
- Failures and exceptions
- Live metrics

### View Logs
```bash
# Stream Function App logs
az functionapp log tail \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend
```

## Troubleshooting

### Function App won't start
```bash
# Check logs
az functionapp log tail \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend

# Verify app settings
az functionapp config appsettings list \
  --name fitapp-dev-func \
  --resource-group rg-fitapp-dev-backend
```

### Cosmos DB connection issues
- Verify RBAC role assignment is configured
- Check that managed identity is enabled on Function App
- Verify environment variables are set correctly

### Static Web App deployment fails
- Verify deployment token is correct
- Check SWA CLI version: `swa --version` (should be 2.0.7 or higher)
- Review build logs in Azure Portal

## Cost Management

### Estimated Monthly Costs (Dev)
- Cosmos DB (400 RU/s): ~$24/month
- Function App (Consumption): ~$0-10/month (based on usage)
- Static Web App (Free tier): $0/month
- Application Insights: ~$0-5/month (based on data ingestion)
- **Total: ~$29-39/month**

### Estimated Monthly Costs (Prod)
- Cosmos DB (autoscale): ~$50-150/month (based on usage)
- Function App (Premium EP1): ~$150/month
- Static Web App (Standard): ~$9/month
- Application Insights: ~$10-50/month (based on data ingestion)
- **Total: ~$219-359/month**

## Next Steps

1. ✅ Rebuild devcontainer to get Azure CLI tools
2. ⬜ Run local tests to verify everything works
3. ⬜ Login to Azure (`az login`)
4. ⬜ Deploy dev infrastructure
5. ⬜ Deploy dev application code
6. ⬜ Test dev deployment
7. ⬜ Deploy to production
8. ⬜ Set up monitoring alerts
9. ⬜ Configure CI/CD for automated deployments

## CI/CD Integration (Future)

The repository already has CI workflows (`.github/workflows/ci.yml` and `.github/workflows/codeql.yml`). To enable automated deployments:

1. Add Azure credentials to GitHub Secrets
2. Create deployment workflow (`.github/workflows/deploy.yml`)
3. Configure branch protection rules
4. Set up environment approvals for production

## Support & Documentation

- **Quickstart Guide**: `/workspaces/fit-app/specs/001-activity-tracking/quickstart.md`
- **Implementation Plan**: `/workspaces/fit-app/specs/001-activity-tracking/plan.md`
- **API Contracts**: `/workspaces/fit-app/specs/001-activity-tracking/contracts/openapi.yaml`
- **Architecture**: `/workspaces/fit-app/specs/001-activity-tracking/data-model.md`
