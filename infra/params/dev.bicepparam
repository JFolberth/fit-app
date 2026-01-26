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
