variable "subscription_id" {
  description = "Azure subscription ID for the project resources"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the Azure resource group for the project"
  type        = string
}

variable "location" {
  description = "Azure region where resources will be deployed"
  type        = string
  default     = "eastus"
}

variable "storage_account_name" {
  description = "Name of the Azure Storage account for corpus blob storage (must be globally unique, 3-24 lowercase alphanumeric characters)"
  type        = string
}

variable "state_storage_account_name" {
  description = "Name of the Azure Storage account for Terraform remote state (must be manually bootstrapped first)"
  type        = string
}

variable "state_container_name" {
  description = "Name of the blob container for Terraform state files (must be manually bootstrapped first)"
  type        = string
  default     = "tfstate"
}

variable "state_resource_group" {
  description = "Name of the resource group containing the Terraform state storage account (must be manually bootstrapped first)"
  type        = string
}
