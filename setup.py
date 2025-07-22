#!/usr/bin/env python3
"""
Setup configuration for BLS Scraper API
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bls-scraper-api",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Fast, reliable BLS economic data scraper with API server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bls-scraper-api",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bls-scraper=main:main",
            "bls-api=app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)