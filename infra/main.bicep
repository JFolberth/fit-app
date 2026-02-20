// infra/main.bicep
// Main orchestrator - deploys per-environment resources (SWA, Functions, MCP Agent)
// and grants RBAC on shared resources (Cosmos, ACR, AI Foundry, Log Analytics).
// Shared resources are managed outside this template.

targetScope = 'subscription'

// ============================================================================
// Core Parameters
// ============================================================================
@description('Environment name (e.g., dev, auth)')
param env string

@description('Location for resources')
param location string = 'eastus2'

@description('Base name for resources')
param baseName string = 'fitapp'

@description('Tags applied to all resources')
param tags object = {
  app: 'fitapp'
  env: env
}

@description('Azure AD application (client) ID for SWA authentication')
param aadClientId string

// ============================================================================
// Shared Resource Parameters (single instances, defaulted)
// ============================================================================
@description('Cosmos DB account name')
param cosmosAccountName string = 'fitapp-dev-cosmos'

@description('Cosmos DB resource group')
param cosmosResourceGroup string = 'rg-fitapp-dev-cosmos'

@description('Cosmos DB database name')
param cosmosDatabaseName string = 'fitappdb'

@description('Cosmos DB activities container name')
param cosmosActivitiesContainerName string = 'activities'

@description('ACR name')
param acrName string = 'crfitappmcpdev'

@description('ACR resource group')
param acrResourceGroup string = 'rg-acr-dev'

@description('Azure AI Foundry resource group')
param aiFoundryResourceGroup string = 'rg-conhosted-aifoundry-dev-ncus'

@description('Azure AI Foundry account name')
param aiFoundryAccountName string = 'fit-app-resource'

@description('Azure AI Foundry project name')
param aiFoundryProjectName string = 'fit-app'

@description('Azure AI Foundry model name')
param aiFoundryModel string = 'gpt-5-mini'

@description('Log Analytics Workspace name')
param logAnalyticsWorkspaceName string = 'fitapp-dev-law'

@description('Log Analytics Workspace resource group')
param observabilityResourceGroup string = 'rg-fitapp-dev-monitoring'

// ============================================================================
// Overridable Defaults
// ============================================================================
@description('SKU for Static Web App (Standard required for Key Vault references)')
param staticWebAppSku string = 'Standard'

@description('SKU for App Service Plan')
param appServicePlanSku string = 'FC1'

@description('MCP container image name:tag')
param mcpContainerImage string = 'fitapp-mcp:latest'

// ============================================================================
// Derived Per-Environment Names
// ============================================================================
var staticWebAppName = '${baseName}-${env}-swa'
var appServicePlanName = '${baseName}-${env}-plan'
var functionAppName = '${baseName}-${env}-func'
var frontendAppInsightsName = '${baseName}-${env}-frontend-appi'
var backendAppInsightsName = '${baseName}-${env}-backend-appi'
var keyVaultName = '${baseName}-${env}-kv'
var aadAppDisplayName = '${baseName}-${env}'
var mcpContainerAppName = 'ca-${baseName}-mcp-${env}'
var mcpContainerAppEnvName = 'cae-${baseName}-mcp-${env}'

// ============================================================================
// Shared Existing Resource Groups
// ============================================================================
resource cosmosRg 'Microsoft.Resources/resourceGroups@2024-03-01' existing = {
  name: cosmosResourceGroup
}

resource acrRg 'Microsoft.Resources/resourceGroups@2024-03-01' existing = {
  name: acrResourceGroup
}

resource aiFoundryRg 'Microsoft.Resources/resourceGroups@2024-03-01' existing = {
  name: aiFoundryResourceGroup
}

resource observabilityRg 'Microsoft.Resources/resourceGroups@2024-03-01' existing = {
  name: observabilityResourceGroup
}

// Existing Log Analytics Workspace
resource existingLaw 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: logAnalyticsWorkspaceName
  scope: observabilityRg
}

// Existing Cosmos DB account (for endpoint derivation)
resource existingCosmos 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' existing = {
  name: cosmosAccountName
  scope: cosmosRg
}

// Existing AI Foundry account (for endpoint derivation)
resource existingAiFoundry 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: aiFoundryAccountName
  scope: aiFoundryRg
}

// ============================================================================
// Per-Environment Resource Groups
// ============================================================================
resource frontendRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${baseName}-${env}-frontend'
  location: location
  tags: union(tags, {
    component: 'frontend'
    SecurityControl: 'Ignore'
  })
}

resource backendRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${baseName}-${env}-backend'
  location: location
  tags: union(tags, {
    component: 'backend'
    SecurityControl: 'Ignore'
  })
}

resource mcpRg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-${baseName}-${env}-mcp'
  location: location
  tags: union(tags, {
    component: 'mcp'
    SecurityControl: 'Ignore'
  })
}

// ============================================================================
// Module Deployments
// ============================================================================

// 1. Frontend (Static Web App + App Insights + Key Vault)
module frontend 'modules/frontend.bicep' = {
  name: 'frontend-deployment'
  scope: frontendRg
  params: {
    location: location
    tags: union(tags, {
      component: 'frontend'
    })
    staticWebAppName: staticWebAppName
    staticWebAppSku: staticWebAppSku
    appInsightsName: frontendAppInsightsName
    logAnalyticsWorkspaceId: existingLaw.id
    keyVaultName: keyVaultName
    aadClientId: aadClientId
    aadAppDisplayName: aadAppDisplayName
  }
}

// 2. Backend (Functions + App Service Plan + App Insights)
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
    logAnalyticsWorkspaceId: existingLaw.id
    cosmosEndpoint: existingCosmos.properties.documentEndpoint
    cosmosDatabaseName: cosmosDatabaseName
    cosmosActivitiesContainerName: cosmosActivitiesContainerName
    aiFoundryEndpoint: '${existingAiFoundry.properties.endpoint}/api/projects/${aiFoundryProjectName}'
    aiFoundryModel: aiFoundryModel
    mcpServerEndpoint: mcpAgent.outputs.mcpEndpoint
    staticWebAppHostname: frontend.outputs.staticWebAppUrl
  }
}

// 3. MCP Agent (Container App for Cosmos MCP server)
// Deploy user-assigned MI first, then AcrPull, then ACA
module mcpIdentity 'modules/mcp-identity.bicep' = {
  name: 'mcp-identity-deployment'
  scope: mcpRg
  params: {
    location: location
    tags: union(tags, {
      component: 'mcp'
    })
    identityName: 'id-${mcpContainerAppName}'
  }
}

module mcpAgent 'modules/mcp-agent.bicep' = {
  name: 'mcp-agent-deployment'
  scope: mcpRg
  params: {
    location: location
    tags: union(tags, {
      component: 'mcp'
    })
    containerAppName: mcpContainerAppName
    containerAppEnvName: mcpContainerAppEnvName
    logAnalyticsWorkspaceId: existingLaw.id
    acrLoginServer: acrRbac.outputs.acrLoginServer
    containerImage: mcpContainerImage
    cosmosEndpoint: existingCosmos.properties.documentEndpoint
    cosmosDatabaseName: cosmosDatabaseName
    cosmosContainerName: cosmosActivitiesContainerName
    userAssignedIdentityId: mcpIdentity.outputs.identityResourceId
  }
}

// ============================================================================
// Link Functions Backend to Static Web App
// ============================================================================
module swaBackendLink 'modules/swa-backend-link.bicep' = {
  name: 'swa-backend-link-deployment'
  scope: frontendRg
  params: {
    staticWebAppName: staticWebAppName
    functionAppResourceId: backend.outputs.functionAppId
    backendRegion: location
  }
}

// ============================================================================
// RBAC: Functions MI -> Cosmos DB Built-in Data Contributor
// ============================================================================
var cosmosDataContributorRoleId = '00000000-0000-0000-0000-000000000002'

module cosmosRoleAssignment 'modules/cosmos-rbac.bicep' = {
  name: 'cosmos-rbac-deployment'
  scope: cosmosRg
  params: {
    cosmosAccountName: cosmosAccountName
    functionAppPrincipalId: backend.outputs.functionAppPrincipalId
    roleDefinitionId: cosmosDataContributorRoleId
  }
}

// RBAC: MCP Agent MI -> Cosmos DB Built-in Data Contributor
module cosmosRoleAssignmentMcp 'modules/cosmos-rbac.bicep' = {
  name: 'cosmos-rbac-mcp-deployment'
  scope: cosmosRg
  params: {
    cosmosAccountName: cosmosAccountName
    functionAppPrincipalId: mcpAgent.outputs.containerAppPrincipalId
    roleDefinitionId: cosmosDataContributorRoleId
  }
}

// ============================================================================
// RBAC: Functions MI -> Azure AI Foundry (Cognitive Services User)
// ============================================================================
module aiFoundryRoleAssignment 'modules/ai-foundry-rbac.bicep' = {
  name: 'ai-foundry-rbac-deployment'
  scope: aiFoundryRg
  params: {
    aiFoundryAccountName: aiFoundryAccountName
    functionAppPrincipalId: backend.outputs.functionAppPrincipalId
  }
}

// ============================================================================
// RBAC: MCP Agent MI -> ACR (AcrPull)
// ============================================================================
module acrRbac 'modules/acr-rbac.bicep' = {
  name: 'acr-rbac-deployment'
  scope: acrRg
  params: {
    acrName: acrName
    principalId: mcpIdentity.outputs.principalId
  }
}

// ============================================================================
// Outputs
// ============================================================================
@description('Per-environment resource group names')
output resourceGroups object = {
  frontend: frontendRg.name
  backend: backendRg.name
  mcp: mcpRg.name
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
output cosmosEndpoint string = existingCosmos.properties.documentEndpoint

@description('Log Analytics Workspace resource ID')
output logAnalyticsWorkspaceId string = existingLaw.id

@description('Frontend Application Insights connection string')
output frontendAppInsightsConnectionString string = frontend.outputs.appInsightsConnectionString

@description('Backend Application Insights connection string')
output backendAppInsightsConnectionString string = backend.outputs.appInsightsConnectionString

@description('Key Vault name')
output keyVaultName string = frontend.outputs.keyVaultName

@description('Key Vault URI')
output keyVaultUri string = frontend.outputs.keyVaultUri

@description('MCP Agent endpoint URL')
output mcpAgentEndpoint string = mcpAgent.outputs.mcpEndpoint
