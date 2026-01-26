// infra/modules/observability.bicep
// Observability resources: Log Analytics + Application Insights

@description('Location for resources')
param location string

@description('Tags applied to all resources')
param tags object

@description('Log Analytics Workspace name')
param logAnalyticsWorkspaceName string

// ============================================================================
// Log Analytics Workspace
// ============================================================================
module logAnalytics 'br/public:avm/res/operational-insights/workspace:0.9.1' = {
  name: 'logAnalytics-deployment'
  params: {
    name: logAnalyticsWorkspaceName
    location: location
    tags: tags
  }
}

// ============================================================================
// Outputs
// ============================================================================
@description('Log Analytics Workspace resource ID')
output logAnalyticsWorkspaceId string = logAnalytics.outputs.resourceId

@description('Log Analytics Workspace name')
output logAnalyticsWorkspaceName string = logAnalyticsWorkspaceName
