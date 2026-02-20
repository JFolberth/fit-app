using './../main.bicep'

param env = 'dev'

param tags = {
  app: 'fitapp'
  env: 'dev'
  owner: 'JFolberth'
}

param aadClientId = '01935310-06f1-4bfd-b164-725fd598d4ce' // fitapp-dev app registration
