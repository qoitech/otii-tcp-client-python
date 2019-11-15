#!/usr/bin/env python
from distutils.core import setup
import otii_tcp_client  # For accessing __version__ in __init__.py

setup(
    name="otii_tcp_client",
    packages=["otii_tcp_client"],
    version=otii_tcp_client.__version__,
    license="MIT",
    description="Qoitech Otii tcp client library",
    author="Qoitech",
    url="https://www.qoitech.com/",
    keywords=["qoitech", "otii", "arc", "tcp"],
    install_requires=[""],
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
