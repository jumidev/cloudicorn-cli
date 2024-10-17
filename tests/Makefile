SHELL := /bin/bash

setup:
	python3 -m venv venv
	source .envtest && pip uninstall cloudicorn-cli -y
	source .envtest && pip install -r requirements.txt && pip install setuptools
	source .envtest && cd ../cli && python3 setup.py install 
	source .envtest && cloudicorn --check-setup

enable_opentofu:
	source .envtest && cd ../extensions/opentofu && python3 setup.py install 
	source .envtest && cloudicorn --check-setup

disable_opentofu:
	source .envtest && pip uninstall cloudicorn-opentofu -y

test: setup
	source .envtest && python3 -m pytest 0*py

test_last: setup
	source .envtest && python3 -m pytest `ls 0*py | sort | tail -n 1`

test_TEST_FILTER: setup
	source .envtest && python3 -m pytest $(TEST_FILTER)