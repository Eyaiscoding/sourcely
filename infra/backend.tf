terraform {
  backend "azurerm" {
    # These values should match your manually bootstrapped state storage account
    # Uncomment and populate after bootstrap, or pass via backend-config flags during init
    # resource_group_name  = "<state_resource_group>"
    # storage_account_name = "<state_storage_account_name>"
    # container_name       = "<state_container_name>"
    # key                  = "sourcely.tfstate"
    # use_azuread_auth     = true
  }
}
