// infra/modules/acr-rbac.bicep
// Grants AcrPull role to a managed identity on an existing ACR

@description('ACR name')
param acrName string

@description('Principal ID to grant AcrPull role')
param principalId string

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

// AcrPull role definition: 7f951dda-4ed3-4680-a7ca-43fe172d538d
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, principalId, 'acr-pull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

@description('ACR login server')
output acrLoginServer string = acr.properties.loginServer
