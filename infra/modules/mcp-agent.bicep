// infra/modules/mcp-agent.bicep
// MCP Agent resources: Container Apps Environment + Container App
// Deploys the Cosmos DB MCP server as an Azure Container App

@description('Location for resources')
param location string

@description('Tags applied to all resources')
param tags object

@description('Container App name')
param containerAppName string

@description('Container Apps Environment name')
param containerAppEnvName string

@description('Log Analytics Workspace resource ID for diagnostics')
param logAnalyticsWorkspaceId string

@description('ACR login server (e.g., crfitappmcpdev.azurecr.io)')
param acrLoginServer string

@description('Container image name and tag')
param containerImage string = 'fitapp-mcp:latest'

@description('Cosmos DB endpoint URL')
param cosmosEndpoint string

@description('Cosmos DB database name')
param cosmosDatabaseName string

@description('Cosmos DB container name')
param cosmosContainerName string

@description('User-assigned managed identity resource ID for ACR pull')
param userAssignedIdentityId string

// ============================================================================
// Container Apps Environment
// ============================================================================
resource containerAppEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppEnvName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceId, '2023-09-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceId, '2023-09-01').primarySharedKey
      }
    }
  }
}

// ============================================================================
// Container App (MCP Server)
// ============================================================================
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned, UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        transport: 'http'
        allowInsecure: true
        corsPolicy: {
          allowedHeaders: ['*']
          allowedOrigins: ['https://portal.azure.com']
          allowCredentials: false
        }
      }
      registries: [
        {
          server: acrLoginServer
          identity: userAssignedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'mcp-server'
          image: '${acrLoginServer}/${containerImage}'
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'COSMOS_URI'
              value: cosmosEndpoint
            }
            {
              name: 'COSMOS_DATABASE'
              value: cosmosDatabaseName
            }
            {
              name: 'COSMOS_CONTAINER'
              value: cosmosContainerName
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================
@description('Container App FQDN')
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn

@description('Container App MCP endpoint URL')
output mcpEndpoint string = 'https://${containerApp.properties.configuration.ingress.fqdn}/mcp'

@description('Container App managed identity principal ID')
output containerAppPrincipalId string = containerApp.identity.principalId
