# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)

## [0.5.1](https://github.com/chrizzFTD/naming/releases/tag/Release-0.5.1) - 2020-09-18
### Changed
- `setup.py` now uses `setup.cfg` fully.

## [0.5.0](https://github.com/chrizzFTD/naming/releases/tag/Release-0.5.0) - 2020-03-07
### Changed
- Renamed `get_name` method to `get`.
- Provide clearer error messages when setting invalid field values.

## [0.4.1](https://github.com/chrizzFTD/naming/releases/tag/Release-0.4.1) - 2019-10-28
### Fixed
- Fix pattern lookup on compound names
- Name build for compounds when top field is provided

## [0.4.0](https://github.com/chrizzFTD/naming/releases/tag/Release-0.4.0) - 2019-10-26
### Changed
- Renamed `drops` to `drop`
- Renamed `compounds` to `join`
- Added `join_sep` class property

## [0.3.0](https://github.com/chrizzFTD/naming/releases/tag/Release-0.3.0) - 2019-05-06
### Changed
- `BaseName` renamed to just `Name` on `naming` module.
- `Name`, `Pipe` and `File` no longer have a `base` field from their config.

## [0.2.1](https://github.com/chrizzFTD/naming/releases/tag/Release-0.2.1) - 2019-05-04
### Changed
- `BaseName` object is now exposed on main `naming` namespace.

## [0.2.0](https://github.com/chrizzFTD/naming/releases/tag/Release-0.2.0) - 2018-04-21
### Added
- `NameConfig` object that allows subclasses to use more configurations apart from the builtin `config`.

### Changed
- Missing fields now have f-strings syntax: `{missing}` instead of `[missing]`.
- Setting fields or name to an incorrect value raises a `ValueError` instead of a `NameError`.
- `name` is no longer read-only.
- `separator` property is now called `sep`.
- `Pipe.pipe_separator` is now called `Pipe.pipe_sep`
- `File` object now uses `suffix` instead of `extension` as a special field.

### Removed
- Use of metaclasses on `_BaseName`.
- `set_name` method (use `name` property instead).
- `File.full_path` & `File.cwd`. These attributes didn't add more than what the [pathlib](https://docs.python.org/3/library/pathlib.html) module already offers.

### Fixed
- `compounds` attribute allows for more use cases (redefined fields, new field names not present on the `config` attribute)
