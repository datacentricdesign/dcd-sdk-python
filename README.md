# [DCD SDK Python](https://datacentricdesign.org/tools/sdk-python/)

Python SDK for the tools of the Data-Centric Design Lab

![version](https://img.shields.io/badge/version-0.1.6-blue.svg)
![license](https://img.shields.io/badge/license-MIT-blue.svg)
[![GitHub issues open](https://img.shields.io/github/issues/datacentricdesign/dcd-sdk-python.svg?maxAge=2592000)]()
[![GitHub issues closed](https://img.shields.io/github/issues-closed-raw/datacentricdesign/dcd-sdk-python.svg?maxAge=2592000)]()

[SDK page](https://datacentricdesign.org/tools/sdk-python/)




# Thing

* Thing()

Instantiate a connection to Bucket for a Thing

  * thing_id (required), the id of the Thing to connect
  * private_key_path (optional), the path to the private key. If no path is provided, it looks for the file "private.pem" in the current folder.

* thing.read()

Fetch the Thing details from Bucket. This method is automatically called Thing() connection succeed.

* thing.to_json()

Format all Thing details as a JSON object.

* thing.find_property_by_name()

  * property_name_to_find (required) the name of the property we are looking for

* thing.create_property()

  * name (required)
  * typeId (required)

* thing.update_property()
  * prop (required)
  * file_name (optional)


* thing.read_property()
  * property_id (required)
  * from_ts (optional)
  * to_ts (optional)

* thing.find_or_create_property()
  * property_name (required)
  * typeId (required)

## Developers

To publish a new version of the SDK:

```python
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/dcd-sdk-0.0.5.tar.gz
```

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2020-08-24

### Added
- Automatic generation of property IP_ADDRESS

## [0.1.3] - 2020-08-13

### Added
- Extended MQTT API

