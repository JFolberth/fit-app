// infra/modules/data.bicep
// Data resources: Cosmos DB Account, Database, and Containers

@description('Location for resources')
param location string

@description('Tags applied to all resources')
param tags object

@description('Cosmos DB account name')
param cosmosAccountName string

@description('Cosmos DB database name')
param cosmosDatabaseName string

@description('Cosmos DB activities container name')
param cosmosActivitiesContainerName string

@description('Enable zone redundancy')
param zoneRedundant bool

@description('Log Analytics Workspace resource ID for diagnostics')
param logAnalyticsWorkspaceId string

// ============================================================================
// Cosmos DB Account with SQL Database and Container
// ============================================================================
module cosmos 'br/public:avm/res/document-db/database-account:0.11.0' = {
  name: 'cosmos-deployment'
  params: {
    name: cosmosAccountName
    location: location
    tags: tags
    disableLocalAuth: true
    minimumTlsVersion: 'Tls12'
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: zoneRedundant
      }
    ]
    sqlDatabases: [
      {
        name: cosmosDatabaseName
        containers: [
          {
            name: cosmosActivitiesContainerName
            paths: ['/type']
            kind: 'Hash'
            indexingPolicy: {
              automatic: true
              indexingMode: 'consistent'
              includedPaths: [
                {
                  path: '/*'
                }
              ]
              excludedPaths: [
                {
                  path: '/"_etag"/?'
                }
              ]
              compositeIndexes: [
                [
                  {
                    path: '/date'
                    order: 'descending'
                  }
                  {
                    path: '/type'
                    order: 'ascending'
                  }
                ]
              ]
            }
          }
        ]
      }
    ]
    // Diagnostic settings commented out due to cross-RG dependency timing issues
    // Can be re-enabled after initial deployment or configured separately
    // diagnosticSettings: [
    //   {
    //     workspaceResourceId: logAnalyticsWorkspaceId
    //     logCategoriesAndGroups: [
    //       {
    //         categoryGroup: 'allLogs'
    //       }
    //     ]
    //     metricCategories: [
    //       {
    //         category: 'AllMetrics'
    //       }
    //     ]
    //   }
    // ]
  }
}

// ============================================================================
// Outputs
// ============================================================================
@description('Cosmos DB account endpoint')
output cosmosEndpoint string = cosmos.outputs.endpoint

@description('Cosmos DB account resource ID')
output cosmosAccountId string = cosmos.outputs.resourceId

@description('Cosmos DB account name')
output cosmosAccountName string = cosmosAccountName

@description('Cosmos DB database name')
output cosmosDatabaseName string = cosmosDatabaseName

@description('Cosmos DB activities container name')
output cosmosActivitiesContainerName string = cosmosActivitiesContainerName
