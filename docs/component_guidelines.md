# Writing Terraform Modules for Cloudicorn

There's lots of ways to write and use terraform code, below is the cloudicorn approach.

- To avoid monolithic code, modules create as few resources as possible and strive to be as generic as possible.
- Where possible, use default values that closely match best practices
- Modules must not specify a remote state provider, this is handled by Cloudicorn
- No remote state data resources, this is handled by Cloudicorn
- Don't assume that terraform workspaces will be used, cloudicorn does not use them


# Coding conventions

To facilitate their ability to work together, these modules adhere to these coding conventions:

### File naming

- **backend.tf**: contains the `terraform` block with required terraform version, plugin version
- **main.tf**: contains the main module code, including local vars, data and resources
- **outputs.tf**: contains outputs
- **variables.tf** contains variables

### Resource naming

For simplicity and consistency, resources are always named `this`, e.g.

```
resource "azurerm_virtual_network" "this" {
...
}
```

When writing modules that create multiple instances of a resource, use terraform's `for_each` meta argument on a `map(map(any))`

```
variable "resource_groups" {
  type        = map(map(any))
  default     = null
}

# example map:
#  rg1 = {
#    location = "northeurope1"
#  }
#  rg2 = {
#    location = "eastus-2"
#  }

resource "azurerm_resource_group" "this" {
  for_each = var.resource_groups
  name     = each.key
  location = each.value.location
}

```


### Handling Remote states

Terraform provides a `backend` mechanism to store remote states and a `remote_state` data type to fetch them. By design, these are tied to a specific remote state backend type, meaning that the module is strongly coupled to a specific remote state storage strategy.

To allow modules to be as generic as possible, cloudicorn handles remote states using a global project level setting.  Likewise, in order to inject values from one resource to another, cloudicorn handles this on the component level with a `component_inputs` block. 


### Variables

Modules use shortest possible variable names, without prefixing.  For example, for an `azurerm_resource_group` the variable used for its name shoudl be `var.name` **not** `var.resource_group_name`

Where applicable, modules should have a `var.tags` which is a map(any) type

In almost all cases, azure resources require a resource group.  This must come from a remote state, **not** from a string, and **not** created in the module its self

In many cases, azure resources need a `location` attribute.  This should come from the attribute of the provided resource group, **not** as a string

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


