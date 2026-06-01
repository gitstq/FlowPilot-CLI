"""
FlowPilot-CLI Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

setup(
    name="flowpilot-cli",
    version="1.0.0",
    author="FlowPilot Team",
    author_email="hello@flowpilot.dev",
    description="🚀 FlowPilot-CLI - Lightweight Terminal Workflow Orchestration Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/FlowPilot-CLI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flowpilot=flowpilot.cli.main:main",
            "fp=flowpilot.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "flowpilot": ["templates/builtin/*.yml"],
    },
    keywords="workflow automation cli devops pipeline task runner",
    project_urls={
        "Bug Reports": "https://github.com/gitstq/FlowPilot-CLI/issues",
        "Source": "https://github.com/gitstq/FlowPilot-CLI",
        "Documentation": "https://github.com/gitstq/FlowPilot-CLI#readme",
    },
)
