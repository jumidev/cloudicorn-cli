# Installation

### System Requirements

- Linux or Windows WSL
- python3 with pip3 in your $PATH

### Install

- `pip3 install cloudicorn-cli`

**or install using setup.py**

```
git clone https://github.com/jumidev/cloudicorn-cli.git
cd cloudicorn-cli/cli
make install             # installs the cloudicorn CLI tool with python requirements
```

### Initial setup

```
cloudicorn_setup --install        # downloads and installs terraform
```

### Installing & using terraform modules

`cloudicorn` can work with any terraform code that follows [these guidelines.](component_guidelines.md)  Below are repos for the big three cloud providers.

- [aws](https://github.com/jumidev/terraform-modules-auto-aws)
- [azurerm](https://github.com/jumidev/terraform-modules-auto-azurerm)
- [gcp](https://github.com/jumidev/terraform-modules-auto-gcp)

