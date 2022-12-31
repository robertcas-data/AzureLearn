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

resource "azurerm_databricks_access_connector" "adb-con" {
  name                = "adb-ac-${var.project}-${var.environment}"
  resource_group_name = azurerm_resource_group.rg-adb.name
  location            = azurerm_resource_group.rg-adb.location

  identity {
    type = "SystemAssigned"
  }

  tags = local.tags
}

resource "azurerm_role_assignment" "synapse-role-assignment" {
  scope                = azurerm_storage_account.data-lake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.adb-con.identity[0].principal_id
}

output "databricks_host" {
  value = "https://${azurerm_databricks_workspace.adb-ws.workspace_url}/"
}