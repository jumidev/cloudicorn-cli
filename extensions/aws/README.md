# cloudicorn_aws

Installs addons for handling aws backend components.

# setting up credentials

Once you have [installed and authenticated](https://aws.amazon.com/cli/) to your aws cli, grab your credentials and save them to environemnt vars  (see `.envrc.tpl`)

## running tests

Create an s3 bucket above aws account can write to 

`make test` Uses terraform modules in `https://github.com/jumidev/cloudicorn-testmodules-aws`

- runs a set of components

## testing with opentofu instead of terraform

opentofu can now be used as a drop in replacement for terraform and can be tested independently of terraform.  You'll need to enable the opentofu extension in the test virtual env by running. `make enable_opentofu`

Be sure to also run `cloudicorn_setup` and install opentofu from the main menu.  Confirm this extension is installed by running `make setup`.  You should see a message at the bottom 

```
opentofu installed and up to date
```

Once it is installed, run `make test` as you would normally