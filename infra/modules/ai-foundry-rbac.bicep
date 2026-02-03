// infra/modules/ai-foundry-rbac.bicep
// RBAC role assignment for Function App managed identity to access Azure AI Foundry

targetScope = 'subscription'

@description('Azure AI Foundry resource ID')
param aiFoundryResourceId string

@description('Function App managed identity principal ID')
param functionAppPrincipalId string

// Cognitive Services User role - allows calling Cognitive Services APIs
// This role is required for the Function App to call Azure AI Foundry
var cognitiveServicesUserRoleDefinitionId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

// Azure AI Developer role - alternative role with more permissions
// var azureAIDeveloperRoleDefinitionId = '64702f94-c441-49e6-a78b-ef80e0188fee'

// Create role assignment at resource scope
resource aiFoundryRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiFoundryResourceId, functionAppPrincipalId, cognitiveServicesUserRoleDefinitionId)
  properties: {
    principalId: functionAppPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleDefinitionId)
    principalType: 'ServicePrincipal'
    description: 'Allow Function App to call Azure AI Foundry APIs'
  }
}

@description('Role assignment resource ID')
output roleAssignmentId string = aiFoundryRoleAssignment.id
