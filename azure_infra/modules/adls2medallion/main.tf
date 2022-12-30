# variables passed by module call
variable "project" {
}

variable "environment" {
}

variable "region" {
}

variable "resource-group"{
}

variable "storage-name-short"{
}

locals {
  tags = {
    environment = var.environment
  }
}

# import resourse group
data "azurerm_resource_group" "used-rg" {
  name = var.resource-group
}

resource "azurerm_storage_account" "medallion" {
  name                     = "sahr${var.project}${var.storage-name-short}${var.environment}"
  resource_group_name      = var.resource-group
  location                 = data.azurerm_resource_group.used-rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  access_tier              = "Hot"
  shared_access_key_enabled = "false"
  infrastructure_encryption_enabled = "true"
  is_hns_enabled                    = "true"

  tags = local.tags
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.medallion.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.medallion.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.medallion.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "meta" {
  name                  = "meta"
  storage_account_name  = azurerm_storage_account.medallion.name
  container_access_type = "private"
}