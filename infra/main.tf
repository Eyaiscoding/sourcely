terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    project     = "sourcely"
    environment = "dev"
    managed_by  = "terraform"
  }
}

resource "azurerm_storage_account" "corpus" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    project     = "sourcely"
    environment = "dev"
    managed_by  = "terraform"
    purpose     = "corpus-storage"
  }
}

resource "azurerm_storage_container" "raw_corpus" {
  name                  = "raw-corpus"
  storage_account_name  = azurerm_storage_account.corpus.name
  container_access_type = "private"
}
