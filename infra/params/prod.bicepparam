using './../main.bicep'

param env = 'prod'
param location = 'eastus2'
param baseName = 'fitapp'

param tags = {
  app: 'fitapp'
  env: 'prod'
  owner: 'JFolberth'
}

// Cosmos DB configuration
param cosmosAccountName = 'fitapp-prod-cosmos'
param cosmosDatabaseName = 'fitappdb'
param cosmosActivitiesContainerName = 'activities'

// Static Web App
param staticWebAppName = 'fitapp-prod-swa'
param staticWebAppSku = 'Standard'

// Functions and App Service Plan
param appServicePlanName = 'fitapp-prod-plan'
param functionAppName = 'fitapp-prod-func'
param appServicePlanSku = 'FC1' // Flex Consumption for production

// Observability
param logAnalyticsWorkspaceName = 'fitapp-prod-law'
param frontendAppInsightsName = 'fitapp-prod-frontend-appi'
param backendAppInsightsName = 'fitapp-prod-backend-appi'

// High availability (true for production)
param zoneRedundant = true

// Authentication
param keyVaultName = 'fitapp-prod-kv'
param aadClientId = '01935310-06f1-4bfd-b164-725fd598d4ce'
param aadAppDisplayName = 'fitapp-prod'

// AI Coach configuration (update these for production AI resources)
param aiFoundryEndpoint = 'https://fit-app-resource.services.ai.azure.com/api/projects/fit-app'
param aiFoundryModel = 'gpt-5-mini'
param mcpServerEndpoint = 'https://ca-fitapp-mcp-auth.braveground-fdce88f6.eastus2.azurecontainerapps.io/mcp'

// AI Foundry RBAC - provide the resource group and account name for RBAC assignment
// Leave empty to skip RBAC assignment (useful if assigning manually or via different process)
param aiFoundryResourceGroup = ''
param aiFoundryAccountName = ''
