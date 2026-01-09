// File-Level Comment:
// Azure Bicep Template for SentinelFlow.
// Provisions a Serverless Python Function App and dependent resources.
// Deploy with: az deployment group create --resource-group <RG_NAME> --template-file main.bicep

param location string = resourceGroup().location
param appNamePrefix string = 'sentinelflow-${uniqueString(resourceGroup().id)}'

// 1. Storage Account (Required for Function App state)
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: '${appNamePrefix}sa'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

// 2. Application Insights (Monitoring & Logging)
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${appNamePrefix}-ai'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

// 3. App Service Plan (Consumption / Serverless)
resource hostingPlan 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: '${appNamePrefix}-plan'
  location: location
  sku: {
    name: 'Y1' // The consumption plan SKU
    tier: 'Dynamic'
  }
  properties: {
    reserved: true // Required for Linux
  }
}

// 4. Function App (Linux / Python)
resource functionApp 'Microsoft.Web/sites@2021-03-01' = {
  name: '${appNamePrefix}-func'
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11' // Explicitly setting Python version
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsights.properties.InstrumentationKey
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true' // Enables remote build
        }
      ]
    }
  }
}
