from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="rt-emissions-sequestration",
    version="1.0.0",
    author="Arvind",
    author_email="arvind.saane.111@gmail.com",
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
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "emissions-analysis=src.main:main",
        ],
    },
)
