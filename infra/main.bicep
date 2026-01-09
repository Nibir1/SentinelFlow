// ============================================================================
// SentinelFlow — Azure Bicep Template
// Deploys a Python 3.11 Linux Function App with Functions v4
// UPDATES: Enforced Storage naming & Added CORS support for Power Apps
// ============================================================================

param location string = resourceGroup().location

// Generate a unique suffix per resource group
var uniqueSuffix = uniqueString(resourceGroup().id)

// Resource names
var storageAccountName = take('stsentinel${uniqueSuffix}', 24) // max 24 chars, no hyphens
var appPlanName = 'sentinelflow-${uniqueSuffix}-plan'
var appInsightsName = 'sentinelflow-${uniqueSuffix}-ai'
var functionAppName = 'sentinelflow-${uniqueSuffix}-func'

// ============================================================================
// 1. Storage Account
// ============================================================================
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}

// ============================================================================
// 2. Application Insights
// ============================================================================
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

// ============================================================================
// 3. App Service Plan (Linux Consumption / Serverless)
// ============================================================================
resource hostingPlan 'Microsoft.Web/serverfarms@2021-03-01' = {
  name: appPlanName
  location: location
  sku: {
    name: 'Y1'      // Consumption tier
    tier: 'Dynamic' // Serverless
  }
  properties: {
    reserved: true  // Required for Linux
  }
}

// ============================================================================
// 4. Function App (Linux, Python 3.11, Functions v4)
// ============================================================================
resource functionApp 'Microsoft.Web/sites@2021-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      
      // NEW: CORS Configuration
      // Allows Power Apps (and any other client) to call the API
      cors: {
        allowedOrigins: [
          '*'
        ]
      }
      
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
          value: 'true'
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
      ]
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================
output functionAppName string = functionApp.name
output storageAccount string = storageAccount.name
output appInsightsName string = appInsights.name
output appPlanName string = hostingPlan.name
