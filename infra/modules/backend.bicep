// infra/modules/backend.bicep
// Backend resources: App Service Plan + Azure Functions + Application Insights
// Uses Azure Verified Modules (AVM) with Flex Consumption configuration

@description('Location for resources')
param location string

@description('Tags applied to all resources')
param tags object

@description('App Service Plan name')
param appServicePlanName string

@description('Function App name')
param functionAppName string

@description('Application Insights name for backend')
param appInsightsName string

@description('SKU for App Service Plan')
param appServicePlanSku string

@description('Log Analytics Workspace resource ID for diagnostics')
param logAnalyticsWorkspaceId string

@description('Cosmos DB endpoint')
param cosmosEndpoint string

@description('Cosmos DB database name')
param cosmosDatabaseName string

@description('Cosmos DB activities container name')
param cosmosActivitiesContainerName string

@description('Azure AI Foundry endpoint URL')
param aiFoundryEndpoint string = 'https://fit-app-resource.services.ai.azure.com/api/projects/fit-app'

@description('Azure AI Foundry model name')
param aiFoundryModel string = 'gpt-5-mini'

@description('MCP Server endpoint URL')
param mcpServerEndpoint string = 'https://ca-fitapp-mcp-auth.braveground-fdce88f6.eastus2.azurecontainerapps.io/mcp'

@description('Static Web App hostname for CORS')
param staticWebAppHostname string

// ============================================================================
// Storage Account (required for Azure Functions Flex Consumption)
// Native resource for direct RBAC scope reference
// ============================================================================
var storageAccountName = take('st${replace(replace(functionAppName, '-', ''), '_', '')}', 24)

resource functionStorageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

// Blob container for Function App deployment package
resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: functionStorageAccount
  name: 'default'
}

resource functionContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobServices
  name: 'function-container'
  properties: {
    publicAccess: 'None'
  }
}

// ============================================================================
// Application Insights for Backend (using AVM)
// ============================================================================
module appInsights 'br/public:avm/res/insights/component:0.7.1' = {
  name: 'backendAppInsights-deployment'
  params: {
    name: appInsightsName
    location: location
    tags: tags
    kind: 'web'
    applicationType: 'web'
    workspaceResourceId: logAnalyticsWorkspaceId
  }
}

// ============================================================================
// App Service Plan (for Azure Functions Flex Consumption)
// ============================================================================
module appServicePlan 'br/public:avm/res/web/serverfarm:0.5.0' = {
  name: 'appServicePlan-deployment'
  params: {
    name: appServicePlanName
    location: location
    tags: tags
    skuName: appServicePlanSku
    reserved: true // Linux plan
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspaceId
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
      }
    ]
  }
}

// ============================================================================
// Azure Functions App (Flex Consumption with managed identity)
// ============================================================================
module functionApp 'br/public:avm/res/web/site:0.19.4' = {
  name: 'functionApp-deployment'
  params: {
    name: functionAppName
    location: location
    tags: tags
    kind: 'functionapp,linux'
    serverFarmResourceId: appServicePlan.outputs.resourceId
    managedIdentities: {
      systemAssigned: true
    }
    // Flex Consumption configuration with managed identity authentication
    functionAppConfig: {
      deployment: {
        storage: {
          value: '${functionStorageAccount.properties.primaryEndpoints.blob}function-container'
          type: 'blobContainer'
          authentication: {
            type: 'SystemAssignedIdentity'
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.11'
      }
      scaleAndConcurrency: {
        instanceMemoryMB: 512
        maximumInstanceCount: 40
      }
    }
    siteConfig: {
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      cors: {
        allowedOrigins: [
          'https://${staticWebAppHostname}'
          'http://localhost:4280'
          'http://127.0.0.1:4280'
        ]
        supportCredentials: true
      }
      appSettings: [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.outputs.connectionString
        }
        {
          name: 'AzureWebJobsStorage__accountName'
          value: functionStorageAccount.name
        }
        {
          name: 'COSMOS_ENDPOINT'
          value: cosmosEndpoint
        }
        {
          name: 'COSMOS_DATABASE'
          value: cosmosDatabaseName
        }
        {
          name: 'COSMOS_ACTIVITIES_CONTAINER'
          value: cosmosActivitiesContainerName
        }
        {
          name: 'COSMOS_PARTITION_KEY'
          value: 'type'
        }
        {
          name: 'AI_FOUNDRY_ENDPOINT'
          value: aiFoundryEndpoint
        }
        {
          name: 'AI_FOUNDRY_MODEL'
          value: aiFoundryModel
        }
        {
          name: 'MCP_SERVER_ENDPOINT'
          value: mcpServerEndpoint
        }
      ]
    }
    diagnosticSettings: [
      {
        workspaceResourceId: logAnalyticsWorkspaceId
        logCategoriesAndGroups: [
          {
            categoryGroup: 'allLogs'
          }
        ]
        metricCategories: [
          {
            category: 'AllMetrics'
          }
        ]
      }
    ]
  }
}

// ============================================================================
// Auth Settings: Configure for SWA linked backend
// Platform auth must be enabled with AllowAnonymous so the azureStaticWebApps
// provider can validate SWA tokens and populate X-MS-CLIENT-PRINCIPAL header.
// Our Python code enforces auth by checking for the header.
// Note: The SWA backend link auto-registers the azureStaticWebApps provider
// with the correct clientId — we just need to ensure the right settings.
// ============================================================================
resource functionAppAuth 'Microsoft.Web/sites/config@2023-12-01' = {
  name: '${functionAppName}/authsettingsV2'
  properties: {
    platform: {
      enabled: true
      runtimeVersion: '~1'
    }
    globalValidation: {
      unauthenticatedClientAction: 'AllowAnonymous'
    }
    identityProviders: {
      azureStaticWebApps: {
        enabled: true
      }
      azureActiveDirectory: {
        enabled: false
      }
    }
    httpSettings: {
      requireHttps: true
      forwardProxy: {
        convention: 'NoProxy'
      }
      routes: {
        apiPrefix: '/.auth'
      }
    }
    login: {
      tokenStore: {
        enabled: true
      }
    }
  }
  dependsOn: [
    functionApp
  ]
}

// ============================================================================
// RBAC: Grant Function App access to Storage Account
// Per MS Learn: Flex Consumption needs Storage Blob Data Owner for deployments
// ============================================================================

// Storage Blob Data Owner (required for Flex Consumption deployment storage)
resource storageBlobOwnerRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, functionAppName, 'storage-blob-owner')
  scope: functionStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b')
    principalId: functionApp.outputs.systemAssignedMIPrincipalId!
    principalType: 'ServicePrincipal'
  }
}

// Storage Blob Data Contributor
resource storageBlobRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, functionAppName, 'storage-blob-contributor')
  scope: functionStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: functionApp.outputs.systemAssignedMIPrincipalId!
    principalType: 'ServicePrincipal'
  }
}

// Storage Queue Data Contributor
resource storageQueueRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, functionAppName, 'storage-queue-contributor')
  scope: functionStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')
    principalId: functionApp.outputs.systemAssignedMIPrincipalId!
    principalType: 'ServicePrincipal'
  }
}

// Storage Table Data Contributor
resource storageTableRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, functionAppName, 'storage-table-contributor')
  scope: functionStorageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3')
    principalId: functionApp.outputs.systemAssignedMIPrincipalId!
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Outputs
// ============================================================================
@description('Function App default hostname')
output functionAppUrl string = functionApp.outputs.defaultHostname

@description('Function App resource ID')
output functionAppId string = functionApp.outputs.resourceId

@description('Function App system-assigned managed identity principal ID')
output functionAppPrincipalId string = functionApp.outputs.systemAssignedMIPrincipalId!

@description('Backend Application Insights connection string')
output appInsightsConnectionString string = appInsights.outputs.connectionString

@description('Backend Application Insights instrumentation key')
output appInsightsInstrumentationKey string = appInsights.outputs.instrumentationKey

@description('Storage Account resource ID')
output storageAccountId string = functionStorageAccount.id

@description('Storage Account name')
output storageAccountOutputName string = functionStorageAccount.name
