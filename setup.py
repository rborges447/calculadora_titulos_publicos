"""
Setup script para instalação do pacote titulospub
"""
from setuptools import setup, find_packages
import os

# Ler o README se existir
readme_file = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_file):
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="titulospub",
    version="1.0.0",
    description="Sistema completo para cálculo e análise de títulos públicos brasileiros",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sistema de Cálculo de Títulos Públicos",
    packages=find_packages(exclude=["venv", "Testes", "*.tests", "*.tests.*", "tests.*", "tests"]),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.20.0",
        "requests>=2.25.0",
        "openpyxl>=3.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

