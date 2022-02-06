# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [0-based versioning](https://0ver.org/).

## 0.1.4
### Added
* Detailed README
* JSON support via `ffurf.FfurfConfig.from_json`
* Test suite broken out into multiple files

### Fixed
* Untruthy values like `0` now handled correctly
* Blank strings handled appropriately for `is_valid` and `rich_console`
* `from_toml` correctly supports `profile` reading

## 0.0.2
### Added
* CHANGELOG
* `ffurf.FfurfConfig.from_toml` and `ffurf.FfurfConfig.from_env`
