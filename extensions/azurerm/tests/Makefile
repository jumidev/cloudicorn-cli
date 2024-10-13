SHELL := /bin/bash

setup:
	terraform --version > /dev/null  2>&1 || (echo "terraform not installed, exiting" && false) 
	python3 -m venv venv
	source .envtest && pip uninstall cloudicorn -y
	source .envtest && cd .. && pip install setuptools pytest 
	source .envtest && cd ../../../cli && python3 setup.py install  
	source .envtest && cd .. && python3 setup.py install 
	source .envtest && cd .. && pip install -r requirements.txt

test: setup
	source .envtest && python3 -m pytest 0*py

test_TEST_FILTER: setup
	source .envtest && python3 -m pytest $(TEST_FILTER)*

azurerm_delete_test_tfstate:
	az storage blob delete-batch  \
	--source $(TEST_AZURE_STORAGE_CONTAINER) \
	--account-name $(TEST_AZURE_STORAGE_ACCOUNT) \
	--account-key `az storage account keys list --account-name $(TEST_AZURE_STORAGE_ACCOUNT)  | jq  '.[0]["value"]' -r` 

cleanup:
	cd .. && rm -rf __pycache__ dist build *egg-info