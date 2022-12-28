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

# get current user
data "azurerm_client_config" "current" {
}

# synapse resource group
resource "azurerm_resource_group" "rg-synapse" {
  name     = "rg-synapse-${var.project}-${var.environment}"
  location = var.region
}

resource "azurerm_storage_account" "lakehouse" {
  name                     = "sahr${var.project}syn${var.environment}"
  resource_group_name      = azurerm_resource_group.rg-synapse.name
  location                 = azurerm_resource_group.rg-synapse.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  access_tier              = "Hot"
  shared_access_key_enabled = "false"
  infrastructure_encryption_enabled = "true"
  is_hns_enabled                    = "true"

  tags = local.tags
}

resource "azurerm_storage_data_lake_gen2_filesystem" "adls-fs-synapse" {
  name               = "fs-${var.project}${var.environment}"
  storage_account_id = azurerm_storage_account.lakehouse.id
}

resource "azurerm_synapse_workspace" "synapse-ws" {
  name                                 =  "synapse-ws-${var.project}-${var.environment}"
  resource_group_name                  = azurerm_resource_group.rg-synapse.name
  location                             = azurerm_resource_group.rg-synapse.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.adls-fs-synapse.id
  sql_administrator_login              = "sqladminuser"
  sql_administrator_login_password     = file("./.secrets/synapse-sql-admin.txt") #data.azurerm_key_vault_secret.data-kv-secret.value

  aad_admin {
    login     = "AzureAD Admin"
    object_id = "7bfba0b6-1452-48c5-a926-b9f8dfb131ac" #bugged: data.azurerm_client_config.current.object_id
    tenant_id = data.azurerm_client_config.current.tenant_id
  }

  identity {
    type = "SystemAssigned"
  }

  tags = local.tags
}

resource "azurerm_synapse_firewall_rule" "synapse-fw" {
  name                 = "AllowAll"
  synapse_workspace_id = azurerm_synapse_workspace.synapse-ws.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "255.255.255.255"
}