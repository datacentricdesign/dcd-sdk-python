from setuptools import setup, find_packages

with open("README.md") as f:
    README = f.read()

with open("LICENSE") as f:
    sdk_license = f.read()

setup(
    name="dcd-sdk",
    version="0.1.7",
    author="Data-Centric Design Lab",
    author_email="lab@datacentricdesign.org",
    description="Python SDK for the tools of the Data-Centric Design Lab",
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
