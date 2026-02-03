// infra/main.bicep
// Main orchestrator - deploys to separate resource groups per best practices

targetScope = 'subscription'

@description('Environment name (e.g., dev, prod)')
param env string

@description('Location for resources')
param location string

@description('Base name for resources')
param baseName string = 'fitapp'

@description('Tags applied to all resources')
param tags object = {
  app: 'fitapp'
  env: env
}

@description('Cosmos DB account name')
param cosmosAccountName string

@description('Cosmos DB database name')
param cosmosDatabaseName string

@description('Cosmos DB activities container name')
param cosmosActivitiesContainerName string

@description('Static Web App name')
param staticWebAppName string

@description('App Service Plan name')
param appServicePlanName string

@description('Function App name')
param functionAppName string

@description('Log Analytics Workspace name')
param logAnalyticsWorkspaceName string

@description('Frontend Application Insights name')
param frontendAppInsightsName string

@description('Backend Application Insights name')
param backendAppInsightsName string

@description('SKU for App Service Plan')
param appServicePlanSku string

@description('Enable zone redundancy')
param zoneRedundant bool

@description('Azure AI Foundry endpoint URL')
param aiFoundryEndpoint string = 'https://fit-app-resource.services.ai.azure.com/api/projects/fit-app'

@description('Azure AI Foundry model name')
param aiFoundryModel string = 'gpt-5-mini'

@description('MCP Server endpoint URL')
param mcpServerEndpoint string = 'https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp'

@description('Azure AI Foundry resource ID (optional - for RBAC assignment)')
param aiFoundryResourceId string = ''

// ============================================================================
// Resource Groups
// ============================================================================
resource observabilityRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${baseName}-${env}-monitoring'
  location: location
  tags: union(tags, {
    component: 'observability'
  })
}

resource dataRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${baseName}-${env}-cosmos'
  location: location
  tags: union(tags, {
    component: 'data'
  })
}

resource frontendRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${baseName}-${env}-frontend'
  location: location
  tags: union(tags, {
    component: 'frontend'
  })
}

resource backendRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${baseName}-${env}-backend'
  location: location
  tags: union(tags, {
    component: 'backend'
  })
}

// ============================================================================
// Module Deployments
// ============================================================================

// 1. Observability (Log Analytics Workspace) - foundation for all diagnostics
module observability 'modules/observability.bicep' = {
  name: 'observability-deployment'
  scope: observabilityRg
  params: {
    location: location
    tags: union(tags, {
      component: 'observability'
    })
    logAnalyticsWorkspaceName: logAnalyticsWorkspaceName
  }
}

// 2. Data (Cosmos DB)
module data 'modules/data.bicep' = {
  name: 'data-deployment'
  scope: dataRg
  params: {
    location: location
    tags: union(tags, {
      component: 'data'
    })
    cosmosAccountName: cosmosAccountName
    cosmosDatabaseName: cosmosDatabaseName
    cosmosActivitiesContainerName: cosmosActivitiesContainerName
    zoneRedundant: zoneRedundant
    logAnalyticsWorkspaceId: observability.outputs.logAnalyticsWorkspaceId
  }
}

// 3. Frontend (Static Web App + App Insights)
module frontend 'modules/frontend.bicep' = {
  name: 'frontend-deployment'
  scope: frontendRg
  params: {
    location: location
    tags: union(tags, {
      component: 'frontend'
    })
    staticWebAppName: staticWebAppName
    appInsightsName: frontendAppInsightsName
    logAnalyticsWorkspaceId: observability.outputs.logAnalyticsWorkspaceId
  }
}

// 4. Backend (Functions + App Service Plan + App Insights)
module backend 'modules/backend.bicep' = {
  name: 'backend-deployment'
  scope: backendRg
  params: {
    location: location
    tags: union(tags, {
      component: 'backend'
    })
    appServicePlanName: appServicePlanName
    functionAppName: functionAppName
    appInsightsName: backendAppInsightsName
    appServicePlanSku: appServicePlanSku
    logAnalyticsWorkspaceId: observability.outputs.logAnalyticsWorkspaceId
    cosmosEndpoint: data.outputs.cosmosEndpoint
    cosmosDatabaseName: data.outputs.cosmosDatabaseName
    cosmosActivitiesContainerName: data.outputs.cosmosActivitiesContainerName
    aiFoundryEndpoint: aiFoundryEndpoint
    aiFoundryModel: aiFoundryModel
    mcpServerEndpoint: mcpServerEndpoint
  }
}

// ============================================================================
// Data Plane Role Assignment: Functions MI -> Cosmos DB Built-in Data Contributor
// ============================================================================
// Role definition ID for "Cosmos DB Built-in Data Contributor"
var cosmosDataContributorRoleId = '00000000-0000-0000-0000-000000000002'

module cosmosRoleAssignment 'modules/cosmos-rbac.bicep' = {
  name: 'cosmos-rbac-deployment'
  scope: dataRg
  params: {
    cosmosAccountName: data.outputs.cosmosAccountName
    functionAppPrincipalId: backend.outputs.functionAppPrincipalId
    roleDefinitionId: cosmosDataContributorRoleId
  }
}

// ============================================================================
// RBAC Role Assignment: Functions MI -> Azure AI Foundry (Cognitive Services User)
// ============================================================================
// This role assignment is conditional - only created if aiFoundryResourceId is provided
// The Cognitive Services User role allows the Function App to call AI Foundry APIs
// Role definition ID: a97b65f3-24c7-4388-baec-2e87135dc908

module aiFoundryRoleAssignment 'modules/ai-foundry-rbac.bicep' = if (!empty(aiFoundryResourceId)) {
  name: 'ai-foundry-rbac-deployment'
  scope: subscription()
  params: {
    aiFoundryResourceId: aiFoundryResourceId
    functionAppPrincipalId: backend.outputs.functionAppPrincipalId
  }
}

// ============================================================================
// Outputs
// ============================================================================
@description('Resource group names')
output resourceGroups object = {
  observability: observabilityRg.name
  data: dataRg.name
  frontend: frontendRg.name
  backend: backendRg.name
}

@description('Static Web App URL')
output staticWebAppUrl string = frontend.outputs.staticWebAppUrl

@description('Static Web App resource ID')
output staticWebAppId string = frontend.outputs.staticWebAppId

@description('Function App URL')
output functionAppUrl string = backend.outputs.functionAppUrl

@description('Function App resource ID')
output functionAppId string = backend.outputs.functionAppId

@description('Function App managed identity principal ID')
output functionAppPrincipalId string = backend.outputs.functionAppPrincipalId

@description('Cosmos DB endpoint')
output cosmosEndpoint string = data.outputs.cosmosEndpoint

@description('Cosmos DB account resource ID')
output cosmosAccountId string = data.outputs.cosmosAccountId

@description('Log Analytics Workspace resource ID')
output logAnalyticsWorkspaceId string = observability.outputs.logAnalyticsWorkspaceId

@description('Frontend Application Insights connection string')
output frontendAppInsightsConnectionString string = frontend.outputs.appInsightsConnectionString

@description('Backend Application Insights connection string')
output backendAppInsightsConnectionString string = backend.outputs.appInsightsConnectionString
