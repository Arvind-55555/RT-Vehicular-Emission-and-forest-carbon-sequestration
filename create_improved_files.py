#!/usr/bin/env python3
"""
Script to create all the improved files in the repository
"""

import os
from pathlib import Path

def write_file(filepath: str, content: str):
    """Write content to file, creating directories if needed"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"📄 Created: {filepath}")

def create_all_improved_files(repo_path: str = "."):
    """Create all the improved files we discussed"""
    base_path = Path(repo_path)
    
    # 1. Create requirements.txt
    requirements_content = """pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0
scikit-learn>=1.0.0
jupyter>=1.0.0
geopandas>=0.10.0
folium>=0.12.0
statsmodels>=0.13.0
scipy>=1.7.0
black>=22.0.0
pylint>=2.12.0
pytest>=6.0.0
pytest-cov>=3.0.0
flake8>=4.0.0
mypy>=0.910
safety>=2.0.0
bandit>=1.7.0
papermill>=2.0.0
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
"""
    write_file(base_path / "requirements.txt", requirements_content)
    
    # 2. Create setup.py
    setup_content = '''from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rt-emissions-sequestration",
    version="1.0.0",
    author="Arvind",
    author_email="arvind.saane.11@gmail.com",
    description="Real-time Vehicle Emissions and Forest Carbon Sequestration Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arvind-55555/RT-Vehicular-Emission-and-forest-carbon-sequestration",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "emissions-analysis=src.main:main",
        ],
    },
)'''
    write_file(base_path / "setup.py", setup_content)
    
    # 3. Create improved README.md
    readme_content = """# Real-Time Vehicle Emissions and Forest Carbon Sequestration Analysis

## 🎯 Overview
Comprehensive analysis platform for monitoring vehicle emissions and forest carbon sequestration in real-time.

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/Arvind-55555/RT-Vehicular-Emission-and-forest-carbon-sequestration
cd RT-Vehicular-Emission-and-forest-carbon-sequestration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .