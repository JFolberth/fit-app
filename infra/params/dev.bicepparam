using './../main.bicep'

param env = 'dev'
param location = 'eastus2'
param baseName = 'fitapp'

param tags = {
  app: 'fitapp'
  env: 'dev'
  owner: 'JFolberth'
}

// Cosmos DB configuration
param cosmosAccountName = 'fitapp-dev-cosmos'
param cosmosDatabaseName = 'fitappdb'
param cosmosActivitiesContainerName = 'activities'

// Static Web App
param staticWebAppName = 'fitapp-dev-swa'
param staticWebAppSku = 'Standard'

// Functions and App Service Plan
param appServicePlanName = 'fitapp-dev-plan'
param functionAppName = 'fitapp-dev-func'
param appServicePlanSku = 'FC1' // Flex Consumption for dev

// Observability
param logAnalyticsWorkspaceName = 'fitapp-dev-law'
param frontendAppInsightsName = 'fitapp-dev-frontend-appi'
param backendAppInsightsName = 'fitapp-dev-backend-appi'

// High availability (false for dev)
param zoneRedundant = false

// Authentication
param keyVaultName = 'fitapp-dev-kv'
param aadClientId = '01935310-06f1-4bfd-b164-725fd598d4ce'
param aadAppDisplayName = 'fitapp-dev'

// AI Coach configuration
param aiFoundryEndpoint = 'https://fit-app-resource.services.ai.azure.com/api/projects/fit-app'
param aiFoundryModel = 'gpt-5-mini'
param mcpServerEndpoint = 'https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp'

// AI Foundry RBAC - provide the resource group and account name for RBAC assignment
// Leave empty to skip RBAC assignment (useful if assigning manually or via different process)
param aiFoundryResourceGroup = ''
param aiFoundryAccountName = ''
