// infra/modules/swa-backend-link.bicep
// Links an Azure Functions backend to a Static Web App
// This enables SWA to proxy /api/* requests and forward auth headers

@description('Static Web App name')
param staticWebAppName string

@description('Function App resource ID to link as backend')
param functionAppResourceId string

@description('Region of the backend resource')
param backendRegion string

resource staticWebApp 'Microsoft.Web/staticSites@2024-04-01' existing = {
  name: staticWebAppName
}

resource linkedBackend 'Microsoft.Web/staticSites/linkedBackends@2024-04-01' = {
  parent: staticWebApp
  name: 'backend'
  properties: {
    backendResourceId: functionAppResourceId
    region: backendRegion
  }
}
