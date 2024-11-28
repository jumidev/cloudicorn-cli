SHELL := /bin/bash

install: uninstall
	python3 setup.py install --user
	rm -rf build dist *egg-info

uninstall:
	pip3 uninstall cloudicorn-cli -y

pydebug_cmd:
	@echo python3 -m debugpy --listen 5678  --wait-for-client -m cloudicorn.cloudicorn
