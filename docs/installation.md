# Installation

### System Requirements

- Linux or Windows WSL
- python3 with pip3 in your $PATH

### Install

- `pip3 install cloudicorn`

Add AWS Support

- `pip3 install cloudicorn_aws`

Add Azure Support

- `pip3 install cloudicorn_azurerm`


**or install by cloning repo**

```
git clone https://github.com/jumidev/cloudicorn-cli.git
cd cloudicorn-cli/cli
make install_aws             # installs the cloudicorn CLI tool with python requirements for AWS
make install_azurerm         # installs the cloudicorn CLI tool with python requirements for AWS
```

### Initial setup

```
cloudicorn_setup --install        # downloads and installs terraform
```

## Bootstrapping a project

`cloudicorn_setup`

```
mkdir my_project && cd my_project
cloudicorn_setup
```


### Installing & using terraform modules

`cloudicorn` can work with any terraform code that follows [these guidelines.](component_guidelines.md)  Below are repos for the big three cloud providers.

- [aws](https://github.com/jumidev/terraform-modules-auto-aws)
- [azurerm](https://github.com/jumidev/terraform-modules-auto-azurerm)

