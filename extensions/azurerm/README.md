# cloudicorn_azurerm

Installs addons for handling azurerm backend components.

# setting up credentials

Once you have [installed and authenticated](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) to your azure cli, create a service principal following [these instructions](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_client_secret)

You will get a result something like this:

```
{
  "appId": "00000000-0000-0000-0000-000000000000",
  "displayName": "azure-cli-2017-06-05-10-41-15",
  "name": "http://azure-cli-2017-06-05-10-41-15",
  "password": "0000-0000-0000-0000-000000000000",
  "tenant": "00000000-0000-0000-0000-000000000000"
}
```

Save them to environment variables (see `.envrc.tpl`)

|  value  | env var |
| ------- | ----------------|  
| `appId` | `AZURE_CLIENT_ID` |
| `password` | `AZURE_CLIENT_SECRET` |
| `tenant` | `AZURE_TENANT_ID` |

You'll also need to set `AZURE_SUBSCRIPTION_ID`

## running tests

Create a storage account and container that the above service principal can write to 

`make test` Uses terraform modules in `https://github.com/jumidev/cloudicorn-testmodules-azure`

- runs a set of components

## testing with opentofu instead of terraform

opentofu can now be used as a drop in replacement for terraform and can be tested independently of terraform.  You'll need to enable the opentofu extension in the test virtual env by running. `make enable_opentofu`

Be sure to also run `cloudicorn_setup` and install opentofu from the main menu.  Confirm this extension is installed by running `make setup`.  You should see a message at the bottom 

```
opentofu installed and up to date
```

Once it is installed, run `make test` as you would normally