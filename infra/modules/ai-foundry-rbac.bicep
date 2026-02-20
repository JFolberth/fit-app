// infra/modules/ai-foundry-rbac.bicep
// RBAC role assignment for Function App managed identity to access Azure AI Foundry

// Scoped to resource group - role assignment will be applied to the specific AI Foundry resource

@description('Azure AI Foundry account name')
param aiFoundryAccountName string

@description('Function App managed identity principal ID')
param functionAppPrincipalId string

// Cognitive Services User role - allows calling Cognitive Services APIs
// This role is required for the Function App to call Azure AI Foundry
var cognitiveServicesUserRoleDefinitionId = 'a97b65f3-24c7-4388-baec-2e87135dc908'

// Reference the existing AI Foundry (Cognitive Services) account
resource aiFoundryAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: aiFoundryAccountName
}

// Create role assignment scoped to the AI Foundry resource (not subscription)
resource aiFoundryRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiFoundryAccount.id, functionAppPrincipalId, cognitiveServicesUserRoleDefinitionId)
  scope: aiFoundryAccount
  properties: {
    principalId: functionAppPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cognitiveServicesUserRoleDefinitionId)
    principalType: 'ServicePrincipal'
    description: 'Allow Function App to call Azure AI Foundry APIs'
  }
}

@description('Role assignment resource ID')
output roleAssignmentId string = aiFoundryRoleAssignment.id

@description('AI Foundry base endpoint')
output aiFoundryBaseEndpoint string = aiFoundryAccount.properties.endpoint
