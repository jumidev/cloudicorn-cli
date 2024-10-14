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

test_last: setup
	source .envtest && python3 -m pytest `ls *py | sort | tail -n 1`

test_TEST_FILTER: setup
	source .envtest && python3 -m pytest $(TEST_FILTER)*

