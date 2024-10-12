SHELL := /bin/bash

setup:
	terraform --version > /dev/null  2>&1 || (echo "terraform not installed, exiting" && false) 
	python3 -m venv venv
	source .envtest && pip uninstall cloudicorn -y
	source .envtest && cd .. && pip install -r requirements.txt && pip install setuptools pytest
	source .envtest && cd ../../../cli && python3 setup.py install  
	source .envtest && cd .. && python3 setup.py install 

test: setup
	source .envtest && python3 -m pytest aws_0*py

test_last: setup
	source .envtest && python3 -m pytest `ls aws_*py | sort | tail -n 1`
