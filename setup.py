from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LICENSE", "r", encoding="utf-8") as f:
    sdk_license = f.read()

setup(
    name="dcd-sdk",
    version="0.1.17",
    author="Data-Centric Design Lab",
    author_email="lab@datacentricdesign.org",
    description="Python SDK for the tools of the Data-Centric Design Lab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datacentricdesign/dcd-sdk-python",
    license=sdk_license,
    packages=find_packages(exclude=("tests", "docs")),
    data_files = [("", ["LICENSE","requirements.txt"])],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Environment :: Console",
        "Topic :: Software Development :: Build Tools",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "markdown",
        "requests",
        "jwt",
        "python-dotenv",
        "asyncio",
        "paho-mqtt",
    ],
)
