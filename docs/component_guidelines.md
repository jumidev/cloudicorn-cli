# Writing Terraform Modules for Cloudicorn

As small and generic as possible

- To avoid monolithic code, modules create as few resources as possible and strive to be as generic as possible.
- Modules must not specify a remote state provider, this is handled by Cloudicorn
- Modules use input variables 
- Module variables expose the attributes of their resources as inputs, with defaults that match most cases. 

# Coding conventions

To facilitate their ability to work together, these modules adhere to these coding conventions:

### File naming

- **backend.tf**: contains the `terraform` block with required terraform version, plugin version
- **main.tf**: contains the main module code, including local vars, data and resources
- **outputs.tf**: contains outputs
- **variables.tf** contains variables

### Resource naming

Resources are always named `this`, e.g.
```
resource "azurerm_virtual_network" "this" {
...
}
```

### Handling Remote states

By design, terraform modules are tied to a specific remote state backend type.  All modules in this repo use the `local` backend type.  This has the disadvantage of requiring the use of third party filesystems to share remote states, however, this prevents having to manually create an azure account and container just to store the remote states.

Remote state inputs are prefixed with `rspath_` e.g.

```
# variables.tf
variable "rspath_resource_group" {
  description = "Remote state key of resource group to deploy resources in."
}

# main.tf
data "terraform_remote_state" "resource_group" {
  backend = "local"
  config = {
    path = "${var.rspath_resource_group}/terraform.tfstate"
  }
}

resource "azurerm_network_security_group" "this" {
  name                = var.name
  location            = data.terraform_remote_state.resource_group.outputs.location
  resource_group_name = data.terraform_remote_state.resource_group.outputs.name

```

### Variables

Modules use shortest possible variable names, without prefixing.  For example, for an `azurerm_resource_group` the variable used for its name shoudl be `var.name` **not** `var.resource_group_name`

Where applicable, modules should have a `var.tags` which is a map(any) type

In almost all cases, azure resources require a resource group.  This must come from a remote state, **not** from a string, and **not** created in the module its self

In many cases, azure resources need a `location` attribute.  This should come from the remote state of the provided resource group, **not** as a string

### Outputs

All modules must provide at least two outputs, **id** and **name**.
These should **not be prefixed with the resource type** e.g. `resource_group_id`)

```
output "id" {
  description = "Id of the storage account created."
  value       = azurerm_storage_account.this.id
}

output "name" {
  description = "Name of the storage account created."
  value       = azurerm_storage_account.this.name
}
```

### Pinned azurerm provider versions

To ensure component stability, the provider plugin version should be pinned.  Preferrably to a recent version.


