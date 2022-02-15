#!/usr/bin/env python
from setuptools import setup
import otii_tcp_client  # For accessing __version__ in __init__.py

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="otii_tcp_client",
    packages=["otii_tcp_client"],
    version=otii_tcp_client.__version__,
    license="MIT",
    description="Qoitech Otii tcp client library",
    author="Qoitech AB",
    author_email="support@qoitech.com",
    long_description=long_description,
    url="https://www.qoitech.com/",
    keywords=["qoitech", "otii", "arc", "tcp"],
    install_requires=["python-dateutil>=2.7.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
