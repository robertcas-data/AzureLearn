terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  storage_use_azuread = true
  features {}
}

# local variables

# import required data objects
data "azurerm_client_config" "current" {
}

# Create a resource group
resource "azurerm_resource_group" "allstorage" {
  name     = "rg-dev-allstorage"
  location = "East US"
}

resource "azurerm_storage_account" "phone-backup" {
  name                     = "sahrdadevphonebackup"
  resource_group_name      = azurerm_resource_group.allstorage.name
  location                 = azurerm_resource_group.allstorage.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  access_tier              = "Cool"
  shared_access_key_enabled = "false"
  infrastructure_encryption_enabled = "true"
  is_hns_enabled                    = "true"

  tags = {
    environment = "private"
  }
}

# Create Databricks Workspace and Storage
module "adb-learn" {
  source = "./modules/databricks"
  count = var.deploy-databricks == true ? 1 : 0
  project = var.project
  environment = var.environment
  region = var.region
}

# Create Synapse Workspace, Storage and later Keyvault
module "synapse-learn" {
  source = "./modules/synapse"
  count = var.deploy-synapse == true ? 1 : 0
  project = var.project
  environment = var.environment
  region = var.region
}

# Create Azure Data Factory
module "adf-learn" {
  source = "./modules/datafactory"
  count = var.deploy-datafactory == true ? 1 : 0
  project = var.project
  storage-name-short = "adf"
  environment = var.environment
  region = var.region
}