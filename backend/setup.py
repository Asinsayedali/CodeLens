"""Setup script for CodeLens CLI"""

from setuptools import setup, find_packages

setup(
    name="codelens",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.7.0",
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
    ],
    entry_points={
        "console_scripts": [
            "codelens=cli.main:main",
        ],
    },
    author="CodeLens Team",
    description="Intelligent Repository Analysis Platform",
    python_requires=">=3.11",
)

# Made with Bob
