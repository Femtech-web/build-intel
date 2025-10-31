"""
Setup configuration for BuildIntel Server
"""
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="buildintel-server",
    version="0.1.0",
    description="BuildIntel Agent Server - Discover what stack a crypto project actually uses",
    author="BuildIntel Team",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=requirements,
    python_requires=">=3.11",
)
