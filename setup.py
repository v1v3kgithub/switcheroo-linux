#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="switcheroo-linux",
    version="1.0.0",
    packages=find_packages(),
    package_data={
        "switcheroo.ui": ["*.css"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "switcheroo = switcheroo.app:main",
        ],
    },
)
