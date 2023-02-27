# variables passed by module call
variable "project" {
}

variable "environment" {
}

variable "region" {
}

variable "db-sku-name" {
  # docu on sku_name values: https://docs.microsoft.com/en-us/azure/azure-sql/database/resource-limits-vcore-single-databases#general-purpose---serverless-compute---gen5
  default = "GP_S_Gen5_2"
}

variable "db-min-capacity" {
  default = 0.5
}

variable "db-max-size-gb" {
  default = 32
}

variable "db-auto-pause-delay-minutes" {
  default = -1
}

variable "sql-deployment-name-short" {
  default = "mssql"
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

# ms sql resource group
resource "azurerm_resource_group" "rg-mssql" {
  name     = "rg-${var.project}-${var.sql-deployment-name-short}-${var.environment}"
  location = var.region
  tags     = local.tags
}

# server + db
# 1/2 server
resource "azurerm_mssql_server" "server" {
  name                            = "sql-server-${var.project}-${var.sql-deployment-name-short}-${var.environment}"
  resource_group_name             = azurerm_resource_group.rg-mssql.name
  location                        = azurerm_resource_group.rg-mssql.location
  version                         = "12.0"
  minimum_tls_version             = "1.2"
  public_network_access_enabled   = false
  azuread_administrator {
    azuread_authentication_only   = true
    login_username                = "AzureAD Admin"
    object_id                     = data.azurerm_client_config.current.object_id
  }
  tags                            = local.tags
}
output "server" {
  value = azurerm_mssql_server.server
}

# 2/2 db
# SQL Server
### Resources
resource "azurerm_mssql_database" "db" {
  name                        = "sql-db-${var.project}-${var.sql-deployment-name-short}-${var.environment}"
  server_id                   = azurerm_mssql_server.server.id
  collation                   = "SQL_Latin1_General_CP1_CI_AS"
  sku_name                    = "${var.db-sku-name}" 
  min_capacity                = "${var.db-min-capacity}"
  max_size_gb                 = "${var.db-max-size-gb}" 
  auto_pause_delay_in_minutes = "${var.db-auto-pause-delay-minutes}" 
  zone_redundant              = true
  short_term_retention_policy {
    retention_days    = 35
  }
  long_term_retention_policy {
    week_of_year      = 1
    weekly_retention  = "PT0S"
    monthly_retention = "PT0S"
    yearly_retention  = "PT0S"  
  }
  tags                        = local.tags
}
output "db" {
  value = azurerm_mssql_database.db
}