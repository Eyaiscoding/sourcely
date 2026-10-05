# Sourcely Infrastructure

This directory contains Terraform configuration for provisioning the Azure infrastructure required by Sourcely, including:

- Azure Resource Group
- Azure Storage Account (for raw corpus blob storage)
- Blob Container (`raw-corpus`)

The Terraform state is stored remotely in Azure Storage with locking enabled for safe concurrent operations.

## Prerequisites

1. **Azure CLI** - [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Terraform** - [Install Terraform](https://developer.hashicorp.com/terraform/downloads) (version >= 1.0)
3. **Azure Subscription** - An active Azure subscription with Contributor or Owner role

## Step 1: Bootstrap Terraform State Storage

Before you can use this Terraform configuration, you must manually create a storage account to hold the Terraform state files. This is a one-time setup per subscription.

### Option A: Using Azure CLI (Recommended)

```powershell
# Login to Azure
az login

# Set your subscription
az account set --subscription "<your-subscription-id>"

# Create resource group for Terraform state
az group create --name "rg-terraform-state" --location "eastus"

# Create storage account for Terraform state (must be globally unique)
az storage account create `
  --name "sttfstateXXXXX" `
  --resource-group "rg-terraform-state" `
  --location "eastus" `
  --sku "Standard_LRS" `
  --encryption-services blob

# Create blob container for state files
az storage container create `
  --name "tfstate" `
  --account-name "sttfstateXXXXX" `
  --auth-mode login
```

**Important**: Replace `sttfstateXXXXX` with a globally unique name (3-24 lowercase alphanumeric characters). Storage account names must be unique across all of Azure.

### Option B: Using Azure Portal

1. Navigate to the [Azure Portal](https://portal.azure.com)
2. Create a new Resource Group named `rg-terraform-state` in your desired region
3. Create a new Storage Account:
   - Name: Choose a globally unique name (e.g., `sttfstate12345`)
   - Performance: Standard
   - Replication: LRS (Locally Redundant Storage)
   - Region: Same as your resource group
4. Inside the storage account, create a new Blob Container named `tfstate` with private access

## Step 2: Configure Terraform Variables

1. Copy the example variables file:
   ```powershell
   Copy-Item terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` and populate with your actual values:
   ```hcl
   subscription_id = "your-actual-subscription-id"
   resource_group_name = "rg-sourcely-dev"
   location = "eastus"
   storage_account_name = "stcsourcelydevXXXXX"  # Must be globally unique
   state_resource_group = "rg-terraform-state"
   state_storage_account_name = "sttfstateXXXXX"  # From bootstrap step
   state_container_name = "tfstate"
   ```

   **Important**: 
   - `storage_account_name` must be globally unique across all of Azure
   - Use only lowercase letters and numbers (3-24 characters)
   - Consider adding a random suffix or your initials for uniqueness

3. The `terraform.tfvars` file is automatically gitignored and should never be committed to version control.

## Step 3: Initialize Terraform

Initialize Terraform to download providers and configure the backend:

```powershell
# Navigate to the infra directory
cd infra

# Initialize Terraform with backend configuration
terraform init `
  -backend-config="resource_group_name=rg-terraform-state" `
  -backend-config="storage_account_name=sttfstateXXXXX" `
  -backend-config="container_name=tfstate" `
  -backend-config="key=sourcely.tfstate"
```

Replace the backend-config values with those from your bootstrap step.

**Alternative**: Instead of using command-line flags, you can uncomment and populate the values in `backend.tf` before running `terraform init`.

## Step 4: Plan and Apply Infrastructure

1. **Review the execution plan**:
   ```powershell
   terraform plan
   ```
   
   This shows you what resources will be created without making any changes.

2. **Apply the configuration**:
   ```powershell
   terraform apply
   ```
   
   Review the plan output and type `yes` to confirm.

3. **Verify the deployment**:
   ```powershell
   terraform show
   ```

## Migration to a New Subscription

To migrate this infrastructure to a different Azure subscription:

1. **Update `terraform.tfvars`** with the new subscription ID and any changed resource names
2. **Bootstrap state storage** in the new subscription (if not already done)
3. **Re-initialize Terraform** with the new backend configuration:
   ```powershell
   terraform init -reconfigure `
     -backend-config="resource_group_name=<new-state-rg>" `
     -backend-config="storage_account_name=<new-state-account>" `
     -backend-config="container_name=tfstate" `
     -backend-config="key=sourcely.tfstate"
   ```
4. **Import existing resources** (if migrating, not creating fresh):
   ```powershell
   terraform import azurerm_resource_group.main /subscriptions/<sub-id>/resourceGroups/<rg-name>
   terraform import azurerm_storage_account.corpus /subscriptions/<sub-id>/resourceGroups/<rg-name>/providers/Microsoft.Storage/storageAccounts/<account-name>
   ```
5. **Plan and apply** to ensure the state matches:
   ```powershell
   terraform plan
   terraform apply
   ```

## Common Commands

```powershell
# Format Terraform files
terraform fmt

# Validate configuration syntax
terraform validate

# Show current state
terraform show

# List all resources in state
terraform state list

# Destroy all resources (use with caution)
terraform destroy
```

## Troubleshooting

### "Storage account name not available"
Storage account names must be globally unique across Azure. Try adding a random suffix to your storage account name.

### "Insufficient permissions"
Ensure your Azure account has Contributor or Owner role on the subscription.

### "Backend initialization required"
Run `terraform init` again with the correct backend configuration parameters.

### State locking errors
If Terraform crashes during an operation, the state may remain locked. You can force-unlock it:
```powershell
terraform force-unlock <lock-id>
```

## Security Notes

- Never commit `terraform.tfvars` to version control (it's gitignored by default)
- Store sensitive values like subscription IDs as environment variables or in Azure Key Vault
- Use Azure AD authentication for state storage (`use_azuread_auth = true` in backend config)
- Enable soft delete on the state storage account to protect against accidental deletion

## Resources

- [Terraform Azure Provider Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Storage Account Naming Rules](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftstorage)
- [Terraform Remote State in Azure](https://developer.hashicorp.com/terraform/language/settings/backends/azurerm)
