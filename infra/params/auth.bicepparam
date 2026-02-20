using './../main.bicep'

param env = 'auth'

param tags = {
  app: 'fitapp'
  env: 'auth'
  owner: 'JFolberth'
}

param aadClientId = 'db3dc51d-880e-454b-a4b3-6d66612edd80' // fitapp-auth app registration
