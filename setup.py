#!/usr/bin/env python3
"""Setup script for Ppcsim."""

from setuptools import setup, find_packages

with open("Readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ppcsim",
    version="1.0.0",
    author="Ppcsim Contributors",
    description="A Simple PowerPC Simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ryandabao1982/Ppcsim",
    py_modules=["ppcsim"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Interpreters",
        "Topic :: System :: Emulators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "ppcsim=ppcsim:main",
        ],
    },
)
