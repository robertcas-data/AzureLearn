# default envirnoment independant variables
variable "region" {
  type = string
  default = "westeurope"
}

variable "project" {
  type = string
  default = "azurelearn"
}

variable "environment" {
  type = string
  default = "dev"
}

# dynamic deployment
variable "deploy-databricks"{
  type = bool
  default = true
}

variable "deploy-synapse"{
  type = bool
  default = true
}

variable "deploy-datafactory"{
  type = bool
  default = true
}

variable "deploy-mssql"{
  type = bool
  default = true
}