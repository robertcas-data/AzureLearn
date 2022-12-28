# variables passed by module call
variable "project" {
}

variable "environment" {
}

variable "region" {
}

locals {
  tags = {
    environment = var.environment
  }
}


# databricks resource group
resource "azurerm_resource_group" "rg-adb" {
  name     = "rg-${var.project}-databricks-${var.environment}"
  location = var.region
}

resource "azurerm_storage_account" "data-lake" {
  name                     = "sahr${var.project}adb${var.environment}"
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
  name                        = "adb-ws-${var.project}-${var.environment}"
  resource_group_name         = azurerm_resource_group.rg-adb.name
  location                    = azurerm_resource_group.rg-adb.location
  sku                         = "premium"
  managed_resource_group_name = "rg-${var.project}-databricks-${var.environment}-managed"
  tags                        = local.tags
}

output "databricks_host" {
  value = "https://${azurerm_databricks_workspace.adb-ws.workspace_url}/"
}