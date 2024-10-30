SHELL := /bin/bash

setup:
	python3 -m venv venv
	source .envtest && pip uninstall cloudicorn-cli -y
	source .envtest && cd .. && pip install setuptools pytest debugpy
	source .envtest && cd ../../../cli && python3 setup.py install  
	source .envtest && cd .. && python3 setup.py install 
	source .envtest && cd .. && pip install -r requirements.txt
	source .envtest && cloudicorn --check-setup

test: setup
	source .envtest && python3 -m pytest 0*py

enable_opentofu:
	source .envtest && cd ../../../extensions/opentofu && python3 setup.py install 
	source .envtest && cloudicorn --check-setup

disable_opentofu:
	source .envtest && pip uninstall cloudicorn-opentofu -y


test_last: setup
	source .envtest && python3 -m pytest `ls *py | sort | tail -n 1`

test_TEST_FILTER: setup
	source .envtest && python3 -m pytest $(TEST_FILTER)*

debug_TEST_FILTER: setup
	source .envtest && python3 -m debugpy --listen 5678  --wait-for-client -m pytest $(TEST_FILTER)*
