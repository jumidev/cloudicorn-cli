#!/usr/bin/python3

# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup

url = 'https://github.com/jumidev/cloudicorn-cli'

md_regex = r"\[([^\[]+)\](\(.*\))"


with open("README.md", "r") as fh:
    long_description = fh.read()


# convert links in readme to absolute paths
matches = re.finditer(md_regex, long_description, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    replace = '(' + url + '/blob/master/' + match.groups(1)[1][1:-1] + ')'
    long_description = long_description.replace(match.groups(1)[1], replace)


with open("requirements.txt", "r") as fh:
    install_requires = fh.readlines()

release_version=os.environ["CLOUDICORN_RELEASE"]

setup(name='cloudicorn-opentofu',
    version=release_version,
    description='Replaces terraform backend with opentofu',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    author='krezreb',
    author_email='josephbeeson@gmail.com',
    license='MIT',
    packages=["."],
    zip_safe=False,
    install_requires=install_requires,

)
