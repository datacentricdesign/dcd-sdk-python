from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    sdk_license = f.read()

setup(
    name='dcd-sdk',
    version='0.0.1',
    description='A Python SDK to interact with the Data-Centric Design Hub',
    long_description=readme,
    author='Jacky Bourgeois',
    author_email='jacky@datacentricdesign.org',
    url='https://github.com/datacentricdesign/dcd-sdk-python',
    license=sdk_license,
    packages=find_packages(exclude=('tests', 'docs'))
)
