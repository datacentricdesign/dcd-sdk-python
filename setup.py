from setuptools import setup, find_packages

with open('README.md') as f:
    README = f.read()

with open('LICENSE') as f:
    sdk_license = f.read()

setup(
    name='dcd-sdk',
    version='0.0.12',
    author='Jacky Bourgeois',
    author_email='jacky@datacentricdesign.org',
    description='A Python SDK to interact with the Data-Centric Design Hub',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/datacentricdesign/dcd-sdk-python',
    license=sdk_license,
    packages=find_packages(exclude=('tests', 'docs')),
    data_files = [('', ['LICENSE','requirements.txt'])],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'Topic :: Software Development :: Build Tools',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ]
)
