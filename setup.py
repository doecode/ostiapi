#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Setup and install the OSTI API client library."""
from os import path
from setuptools import setup, find_packages


setup(
    name="ostiapi",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="OSTI Client API",
    url="https://github.com/doecode/ostiapi/",
    long_description=open(
        path.join(path.abspath(path.dirname(__file__)), "README.md")
    ).read(),
    long_description_content_type="text/markdown",
    author="Neal Ensor",
    author_email="EnsorN@osti.gov",
    packages=find_packages(include=["ostiapi"]),
    install_requires=["requests", "dicttoxml"],
)
