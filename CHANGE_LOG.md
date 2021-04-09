
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.15] - 2020-10-23

### Added
- `connect` param on Thing for loading Thing without connecting MQTT
- fixes on read property so that it works for both properties and shared properties

## [0.1.13] - 2020-10-15

### Added
- Management of shared properties

## [0.1.12] - 2020-09-25

### Fixed

- log folders and file names without colons
- env var for token validity

## [0.1.11] - 2020-09-14

### Added
- DigiCertCA env var

## [0.1.8] - 2020-09-13

### Fixed

- default path to private key from env var

## [0.1.7] - 2020-08-24

### Added
- Refactored in smaller classes
- Documented with 'Read the Doc', Sphinx and DocStrings
- Log data locally
- environment variables

### Removed
- provisionning of external token

## [0.1.4] - 2020-08-24

### Added
- Automatic generation of property IP_ADDRESS

## [0.1.3] - 2020-08-13

### Added
- Extended MQTT API