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