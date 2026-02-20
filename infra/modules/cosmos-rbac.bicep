// infra/modules/cosmos-rbac.bicep
// Cosmos DB RBAC role assignment

@description('Cosmos DB account name')
param cosmosAccountName string

@description('Function App managed identity principal ID')
param functionAppPrincipalId string

@description('Cosmos DB role definition ID (Built-in Data Contributor)')
param roleDefinitionId string

// Reference to existing Cosmos account
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-11-15' existing = {
  name: cosmosAccountName
}

// Role assignment
resource roleAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-11-15' = {
  name: guid(functionAppPrincipalId, cosmosAccount.id, roleDefinitionId)
  parent: cosmosAccount
  properties: {
    principalId: functionAppPrincipalId
    roleDefinitionId: '${cosmosAccount.id}/sqlRoleDefinitions/${roleDefinitionId}'
    scope: cosmosAccount.id
  }
}

output roleAssignmentId string = roleAssignment.id

@description('Cosmos DB account endpoint')
output cosmosEndpoint string = cosmosAccount.properties.documentEndpoint
