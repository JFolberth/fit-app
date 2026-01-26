// infra/modules/backend.bicep
// Backend resources: App Service Plan + Azure Functions + Application Insights

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

// ============================================================================
// Storage Account (required for Flex Consumption)
// ============================================================================
module storageAccount 'br/public:avm/res/storage/storage-account:0.15.0' = {
  name: 'storageAccount-deployment'
  params: {
    name: 'st${replace(functionAppName, '-', '')}' // Storage account names must be 3-24 chars, lowercase alphanumeric
    location: location
    tags: tags
    skuName: 'Standard_LRS'
    kind: 'StorageV2'
    allowBlobPublicAccess: false
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
  }
}

// ============================================================================
// Application Insights for Backend (using AVM)
// ============================================================================
module appInsights 'br/public:avm/res/insights/component:0.4.2' = {
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
// App Service Plan (for Azure Functions)
// ============================================================================
module appServicePlan 'br/public:avm/res/web/serverfarm:0.4.0' = {
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
// Azure Functions App
// ============================================================================
module functionApp 'br/public:avm/res/web/site:0.12.0' = {
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
    // Flex Consumption requires functionAppConfig
    functionAppConfig: {
      runtime: {
        name: 'python'
        version: '3.11'
      }
      scaleAndConcurrency: {
        maximumInstanceCount: 100
        instanceMemoryMB: 2048
      }
    }
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      use32BitWorkerProcess: false
    }
    appSettingsKeyValuePairs: {
      FUNCTIONS_WORKER_RUNTIME: 'python'
      FUNCTIONS_EXTENSION_VERSION: '~4'
      APPLICATIONINSIGHTS_CONNECTION_STRING: appInsights.outputs.connectionString
      // Use managed identity for storage (best practice for Flex Consumption)
      AzureWebJobsStorage__accountName: storageAccount.outputs.name
      AzureWebJobsStorage__blobServiceUri: storageAccount.outputs.primaryBlobEndpoint
      AzureWebJobsStorage__queueServiceUri: 'https://${storageAccount.outputs.name}.queue.${environment().suffixes.storage}'
      AzureWebJobsStorage__tableServiceUri: 'https://${storageAccount.outputs.name}.table.${environment().suffixes.storage}'
      WEBSITE_CONTENTSHARE: functionAppName
      COSMOS_ENDPOINT: cosmosEndpoint
      COSMOS_DATABASE: cosmosDatabaseName
      COSMOS_ACTIVITIES_CONTAINER: cosmosActivitiesContainerName
      COSMOS_PARTITION_KEY: 'type'
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
// RBAC: Grant Function App access to Storage Account
// ============================================================================
// Use the AVM authorization module for role assignments
module storageRoleAssignments 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  name: 'storage-rbac-assignments'
  params: {
    resourceId: storageAccount.outputs.resourceId
    principalId: functionApp.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalType: 'ServicePrincipal'
  }
}

module storageQueueRoleAssignments 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  name: 'storage-queue-rbac-assignments'
  params: {
    resourceId: storageAccount.outputs.resourceId
    principalId: functionApp.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88') // Storage Queue Data Contributor
    principalType: 'ServicePrincipal'
  }
}

module storageTableRoleAssignments 'br/public:avm/ptn/authorization/resource-role-assignment:0.1.1' = {
  name: 'storage-table-rbac-assignments'
  params: {
    resourceId: storageAccount.outputs.resourceId
    principalId: functionApp.outputs.systemAssignedMIPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3') // Storage Table Data Contributor
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
output functionAppPrincipalId string = functionApp.outputs.systemAssignedMIPrincipalId

@description('Backend Application Insights connection string')
output appInsightsConnectionString string = appInsights.outputs.connectionString

@description('Backend Application Insights instrumentation key')
output appInsightsInstrumentationKey string = appInsights.outputs.instrumentationKey

@description('Storage Account resource ID')
output storageAccountId string = storageAccount.outputs.resourceId

@description('Storage Account name')
output storageAccountName string = storageAccount.outputs.name
