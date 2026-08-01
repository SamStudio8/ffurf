# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [0-based versioning](https://0ver.org/).

## 0.3.0
### Added
* Config keys correctly hold lists. `key_type=list` keeps elements as defined,
  `key_type=list[str]` (or `list[int]`, `typing.List[str]`, ...) coerces each
  element to the defined type.
* `add_config_key` takes a `separator` (default `,`) used to split a list read
  from a string, and to join it again for `to_env`. Setting on a non-list key
  raises a `ValueError`.
### Changed
* The minimum python version is now 3.10.
* Packaging moved from poetry to `uv` and `hatchling`, with dependencies
  declared as PEP 621 metadata and pinned in `uv.lock`.
### Fixed
* Various test weirdness caused by my brain evidently not working.
* List values are no longer stringified into `"['x', 'y']"` when loaded from
  `toml` or `json`.
* `from_env` splits list keys instead of exploding the string into characters.
* `frame_to_source` trimmed paths incorrectly, so the reported source was
  always an absolute path.

## 0.2.0
### Changed
* Updated the minimum python version.
* Rich is now an optional dependency.
### Added
* `to_groovy` will output a string representation of a groovy object
* `to_argparse` will output an `argparse.ArgumentParser` built from the
  Ffurf configuration, complete with defaults if the structure is already
  populated
* `load` will infer an appropriate from_x Ffurf loader.
* `validate` will explode and print out a table when misconfigured.

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
