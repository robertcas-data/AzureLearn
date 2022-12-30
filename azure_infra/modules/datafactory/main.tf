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
