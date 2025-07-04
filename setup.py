#!/usr/bin/env python3
"""
Setup script for md2notion package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="md2notion",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple command-line tool to convert Markdown files to Notion pages",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/md2notion",
    py_modules=["md2notion"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "md2notion=md2notion_cli:main",
        ],
    },
    keywords="markdown notion api converter cli",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/md2notion/issues",
        "Source": "https://github.com/yourusername/md2notion",
        "Documentation": "https://github.com/yourusername/md2notion#readme",
    },
) 