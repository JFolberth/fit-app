// infra/modules/frontend.bicep
// Frontend resources: Static Web App + Application Insights

@description('Location for resources')
param location string

@description('Tags applied to all resources')
param tags object

@description('Static Web App name')
param staticWebAppName string

@description('Application Insights name for frontend')
param appInsightsName string

@description('Log Analytics Workspace resource ID for diagnostics')
param logAnalyticsWorkspaceId string

@description('SKU for Static Web App')
param staticWebAppSku string = 'Standard'

// ============================================================================
// Application Insights for Frontend (using AVM)
// ============================================================================
module appInsights 'br/public:avm/res/insights/component:0.7.1' = {
  name: 'frontendAppInsights-deployment'
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
// Static Web App
// ============================================================================
module staticWebApp 'br/public:avm/res/web/static-site:0.9.3' = {
  name: 'staticWebApp-deployment'
  params: {
    name: staticWebAppName
    location: location
    tags: tags
    sku: staticWebAppSku
  }
}

// ============================================================================
// Outputs
// ============================================================================
@description('Static Web App default hostname')
output staticWebAppUrl string = staticWebApp.outputs.defaultHostname

@description('Static Web App resource ID')
output staticWebAppId string = staticWebApp.outputs.resourceId

@description('Frontend Application Insights connection string')
output appInsightsConnectionString string = appInsights.outputs.connectionString

@description('Frontend Application Insights instrumentation key')
output appInsightsInstrumentationKey string = appInsights.outputs.instrumentationKey
