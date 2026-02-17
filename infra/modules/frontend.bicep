// infra/modules/frontend.bicep
// Frontend resources: Static Web App + Application Insights + Key Vault (auth secrets)
// + Azure AD app registration configuration via Microsoft Graph

extension microsoftGraphV1_0

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

@description('SKU for Static Web App (Standard required for managed identity / Key Vault references)')
param staticWebAppSku string = 'Standard'

@description('Key Vault name for storing authentication secrets')
param keyVaultName string

@description('Azure AD application (client) ID for SWA authentication')
param aadClientId string

@description('Azure AD app registration display name')
param aadAppDisplayName string

@secure()
@description('Azure AD client secret for SWA authentication')
param aadClientSecret string

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
// Static Web App (with system-assigned managed identity for Key Vault access)
// ============================================================================
module staticWebApp 'br/public:avm/res/web/static-site:0.9.3' = {
  name: 'staticWebApp-deployment'
  params: {
    name: staticWebAppName
    location: location
    tags: tags
    sku: staticWebAppSku
    managedIdentities: {
      systemAssigned: true
    }
  }
}

// ============================================================================
// Key Vault (stores AAD client secret for secure management)
// ============================================================================
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
  }
}

resource aadClientSecretKv 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'AAD-CLIENT-SECRET'
  properties: {
    value: aadClientSecret
  }
}

// ============================================================================
// RBAC: Grant SWA managed identity Key Vault Secrets User role
// ============================================================================
// Key Vault Secrets User role: 4633458b-17de-408a-b874-0445c86b69e6
resource swaKeyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, staticWebAppName, 'key-vault-secrets-user')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: staticWebApp.outputs.systemAssignedMIPrincipalId!
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// SWA Application Settings (AAD auth with Key Vault reference for secret)
// ============================================================================
resource existingSwa 'Microsoft.Web/staticSites@2024-04-01' existing = {
  name: staticWebAppName
}

resource swaAppSettings 'Microsoft.Web/staticSites/config@2024-04-01' = {
  parent: existingSwa
  name: 'appsettings'
  properties: {
    AAD_CLIENT_ID: aadClientId
    AAD_CLIENT_SECRET: '@Microsoft.KeyVault(SecretUri=${aadClientSecretKv.properties.secretUri})'
  }
  dependsOn: [
    staticWebApp
    swaKeyVaultRoleAssignment
  ]
}

// ============================================================================
// Azure AD App Registration Configuration (via Microsoft Graph)
// Enables ID token issuance and sets the SWA auth callback redirect URI
// ============================================================================
resource aadAppRegistration 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: aadClientId
  displayName: aadAppDisplayName
  web: {
    implicitGrantSettings: {
      enableIdTokenIssuance: true
    }
    redirectUris: [
      'https://${staticWebApp.outputs.defaultHostname}/.auth/login/aad/callback'
    ]
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

@description('Key Vault name')
output keyVaultName string = keyVault.name

@description('Key Vault URI')
output keyVaultUri string = keyVault.properties.vaultUri
