SHELL := /bin/bash

setup:
	terraform --version > /dev/null  2>&1 || (echo "terraform not installed, exiting" && false) 
	python3 -m venv venv
	source .envtest && pip uninstall cloudicorn -y
	source .envtest && cd .. && pip install -r requirements.txt && pip install setuptools pytest
	source .envtest && cd ../../../cli && python3 setup.py install  
	source .envtest && cd .. && python3 setup.py install 

test: setup
	source .envtest && python3 -m pytest azurerm_0*py

azurerm_delete_test_tfstate:
	az storage blob delete-batch  \
	--source $(TEST_AZURE_STORAGE_CONTAINER) \
	--account-name $(TEST_AZURE_STORAGE_ACCOUNT) \
	--account-key `az storage account keys list --account-name $(TEST_AZURE_STORAGE_ACCOUNT)  | jq  '.[0]["value"]' -r` 
