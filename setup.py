from setuptools import setup, find_packages
import sys, os
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()

setup(
    name="dcd-sdk",
    version="0.1.28",
    author="Data-Centric Design Lab",
    author_email="lab@datacentricdesign.org",
    description="Python SDK for the tools of the Data-Centric Design Lab",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datacentricdesign/dcd-sdk-python",
    license='MIT',
    packages=find_packages(exclude=("tests", "docs")),
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
        "requests",
        "pyjwt",
        "python-dotenv",
        "asyncio",
        "paho-mqtt",
        "cryptography"
    ],
)
