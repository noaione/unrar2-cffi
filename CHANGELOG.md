# Changelog

The following file contains all the changes made in unrar2-cffi, not including changes from unrar-cffi

## Unreleased
### Breaking Changes
- Drop Python 3.9, add Python 3.14 (+ free-threaded)
- Drop Windows 32-bit build

### Build
- Bump to unrar 7.2.6

## [0.4.1] 2025-05-25
### Build
- Fix issues with testing with source distribution.
- Fix Windows wheels to use the correct unrar version.

## [0.4.0] 2024-10-10
### New Features
- Support opening password protected rar file
Similar to the other ZipFile-like API, you can pass a `pwd` parameter to open with password.
- Add support to get the current `unrar` version with `get_unrar_version` via `unrar.cffi.unrarlib`

### Breaking Changes
- Reworked error handling, there is now a new error called `RarFileError` which will be raised on any error.

### Build
- Bump dependencies
- Support Python 3.13 (and the free-threaded/no GIL version)
- Bump `unrar` to 7.0.9

## [0.3.1] 2024-03-21
### Build
- Fix build for sdist
- Move from `setup.py` to `pyproject.toml` for most stuff
- Fix failed FFI build because some unknown reason

## [0.3.0] 2023-10-30
### New Features
- Implement `RarFile.printdir()`

### Changes
- Add typing information
- Add `__slots__` to improve performance a bit.
- Moved all the `RarInfo` into at-property data
- Allow accessing raw header by using `file._header`

### Build
- Support Python 3.9 until 3.12
- Add support for macOS build

### Docs
- Added docstring to most functions
