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

Use [opentofu](https://opentofu.org/) instead of terraform

- `pip3 install cloudicorn_opentofu`


**or install by cloning repo**

```
git clone https://github.com/jumidev/cloudicorn-cli.git
cd cloudicorn-cli
make install_aws             # installs AWS requirements
make install_azurerm         # installs Azure Requirements
make install_opentofu        # Use opentofu instead of terraform
```

If you are on python 3.11 or newer you'll get an error message when you  `make install_`

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
```

To fix this:

`python3 -m pip config set global.break-system-packages true`



### Initial setup

```
cloudicorn_setup --install        # downloads and installs terraform (or opentofu)
```

## Bootstrapping a project

```
mkdir my_project && cd my_project
cloudicorn_setup # select 'New Project' from main menu
```

### Installing & using terraform modules

`cloudicorn` can work with any terraform code that follows [these guidelines.](component_guidelines.md)  Below are repos for the big three cloud providers.

- [aws](https://github.com/jumidev/terraform-modules-auto-aws)
- [azurerm](https://github.com/jumidev/terraform-modules-auto-azurerm)

