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
locals {
  tags = {
    Environment = "dev"
  }
}

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

# databricks resource group
resource "azurerm_resource_group" "rg-adb" {
  name     = "rg-dev-adb"
  location = var.region
}

resource "azurerm_storage_account" "data-lake" {
  name                     = "sahrdadevlakehouse"
  resource_group_name      = azurerm_resource_group.rg-adb.name
  location                 = azurerm_resource_group.rg-adb.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  access_tier              = "Hot"
  shared_access_key_enabled = "false"
  infrastructure_encryption_enabled = "true"
  is_hns_enabled                    = "true"

  tags = local.tags
}

resource "azurerm_databricks_workspace" "adb-ws" {
  name                        = "adb-dev-workspace"
  resource_group_name         = azurerm_resource_group.rg-adb.name
  location                    = azurerm_resource_group.rg-adb.location
  sku                         = "premium"
  managed_resource_group_name = "adb-dev-workspace-managed"
  tags                        = local.tags
}

output "databricks_host" {
  value = "https://${azurerm_databricks_workspace.adb-ws.workspace_url}/"
}