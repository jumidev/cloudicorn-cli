SHELL := /bin/bash

install:
	cd cli && make install

install_aws: install
	cd extensions/aws && python3 setup.py install --user &&	rm -rf build dist *egg-info

install_azurerm: install
	cd extensions/azurerm && python3 setup.py install --user &&	rm -rf build dist *egg-info

build_test_docker:
	docker build . -f Dockerfile-tests -t test-cloudicorn

test:
	cd tests && make test

test_last:
	cd tests && make test_last

test_aws:
	cd extensions/aws/tests && make test

test_azurerm:
	cd tests && make test_azurerm

test_aws_last:
	cd tests && make test_aws_last

test_docker: build_test_docker
	docker run -it test-cloudicorn

publish_pypi:
	cd cli && rm -rf dist build && \
	python3 setup.py sdist bdist_wheel && \
	python3 -m twine upload dist/*
	# aws
	cd extensions/aws     &&  rm -rf dist build && \
	python3 setup.py sdist bdist_wheel && \
	python3 -m twine upload dist/*
	# azurerm
	cd extensions/azurerm &&  rm -rf dist build && \
	python3 setup.py sdist bdist_wheel && \
	python3 -m twine upload dist/*

clean:
	find -type d -name "dist" -exec rm -rf {} \;
	find -type d -name "__pycache__" -exec rm -rf {} \;
	find -type d -name "*egg-info"  -exec rm -rf {} \;
	rm -rf cli/build
	rm -rf extensions/*/build