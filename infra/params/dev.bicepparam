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

// Functions App Service Plan SKU
param appServicePlanSku = 'FC1' // Flex Consumption for dev

// Observability
param logAnalyticsWorkspaceName = 'fitapp-dev-law'

// AI Coach configuration
param aiFoundryModel = 'gpt-5-mini'
