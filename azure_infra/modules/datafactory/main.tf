# variables passed by module call
variable "project" {
}

variable "environment" {
}

variable "region" {
}

variable "storage-name-short" {
}

locals {
  tags = {
    environment = var.environment
  }
}

# get current user
data "azurerm_client_config" "current" {
}

data "azurerm_subscription" "primary" {
}

# datafactory resource group
resource "azurerm_resource_group" "rg-adf" {
  name     = "rg-${var.project}-datafactory-${var.environment}"
  location = var.region
  tags     = local.tags
}

resource "azurerm_data_factory" "adf" {
  name                = "adf-${var.project}-${var.environment}"
  location            = azurerm_resource_group.rg-adf.location
  resource_group_name = azurerm_resource_group.rg-adf.name
  identity {
    type = "SystemAssigned"
  }
  github_configuration {
    account_name    = "robertcas-data"
    branch_name     = "dev"
    git_url         = "https://github.com/robertcas-data/AzureLearn"
    repository_name = "AzureLearn"
    root_folder     = "/azure_datafactory/"
  }
}

# create adls2 with medallion architecture
module "medallion-storage" {
  source = "../adls2medallion"
  project = var.project
  storage-name-short = var.storage-name-short
  environment = var.environment
  region = var.region
  resource-group = azurerm_resource_group.rg-adf.name
}

# link containers

data "azurerm_storage_account" "med-storage" {
  name                = "sahr${var.project}${var.storage-name-short}${var.environment}"
  resource_group_name = azurerm_resource_group.rg-adf.name
}

resource "azurerm_role_assignment" "synapse-role-assignment" {
  scope                = data.azurerm_storage_account.med-storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.adf.identity[0].principal_id
}

resource "azurerm_data_factory_linked_service_data_lake_storage_gen2" "link-adf" {
  name                  = "lin_sahr${var.project}${var.storage-name-short}${var.environment}"
  data_factory_id       = azurerm_data_factory.adf.id
  use_managed_identity  = true
  url                   = "https://sahr${var.project}${var.storage-name-short}${var.environment}.dfs.core.windows.net/"
}

# # push custom scrape-pv-prices to adls gen2 container
data "azurerm_storage_container" "meta-container" {
  name                 = "meta"
  storage_account_name = "sahr${var.project}${var.storage-name-short}${var.environment}"
}

resource "azurerm_storage_blob" "push-scrape-pv-prices" {
  name                   = "scripts/python/scrape-pv-prices.py"
  storage_account_name   = data.azurerm_storage_account.med-storage.name
  storage_container_name = data.azurerm_storage_container.meta-container.name
  type                   = "Block"
  source                 = "C:/Git/AzureLearn/ee_code/scrape-pv-prices.py"
}