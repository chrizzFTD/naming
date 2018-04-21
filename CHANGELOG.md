# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)

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