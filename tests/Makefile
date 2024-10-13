SHELL := /bin/bash

setup:
	terraform --version > /dev/null  2>&1 || (echo "terraform not installed, exiting" && false) 
	python3 -m venv venv
	source .envtest && pip uninstall cloudicorn -y
	source .envtest && pip install -r requirements.txt && pip install setuptools
	source .envtest && cd ../cli && python3 setup.py install 

test: setup
	source .envtest && python3 -m pytest 0*py

test_last: setup
	source .envtest && python3 -m pytest `ls 0*py | sort | tail -n 1`

