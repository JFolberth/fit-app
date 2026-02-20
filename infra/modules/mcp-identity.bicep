// infra/modules/mcp-identity.bicep
// User-assigned managed identity for the MCP Container App
// Created separately so AcrPull can be assigned BEFORE the Container App deploys

@description('Location for resources')
param location string

@description('Tags applied to all resources')
param tags object

@description('Name for the user-assigned managed identity')
param identityName string

resource mcpIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: tags
}

@description('Principal ID of the managed identity')
output principalId string = mcpIdentity.properties.principalId

@description('Resource ID of the managed identity')
output identityResourceId string = mcpIdentity.id

@description('Client ID of the managed identity')
output clientId string = mcpIdentity.properties.clientId
