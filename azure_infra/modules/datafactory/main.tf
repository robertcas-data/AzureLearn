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

resource "azurerm_data_factory_linked_service_data_lake_storage_gen2" "link-bronze" {
  name                  = "bronze"
  data_factory_id       = azurerm_data_factory.adf.id
  use_managed_identity  = true
  url                   = "https://sahr${var.project}${var.storage-name-short}${var.environment}.blob.core.windows.net/bronze"
}

resource "azurerm_data_factory_linked_service_data_lake_storage_gen2" "link-silver" {
  name                  = "silver"
  data_factory_id       = azurerm_data_factory.adf.id
  use_managed_identity  = true
  url                   = "https://sahr${var.project}${var.storage-name-short}${var.environment}.blob.core.windows.net/silver"
}

resource "azurerm_data_factory_linked_service_data_lake_storage_gen2" "link-gold" {
  name                  = "gold"
  data_factory_id       = azurerm_data_factory.adf.id
  use_managed_identity  = true
  url                   = "https://sahr${var.project}${var.storage-name-short}${var.environment}.blob.core.windows.net/gold"
}