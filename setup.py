from setuptools import setup, find_packages

setup(
    name="nexeDecompiler",
    version="0.0.2",
    author="unex",
    author_email="git@unexceptional.net",
    packages=find_packages(),
    url="https://github.com/unex/nexeDecompiler",
    license="LICENSE",
    description="Extract javascript from nexe binaries",
    entry_points={"console_scripts": ["nexedecompiler = nexedecompiler.cli:cli"]},
)
