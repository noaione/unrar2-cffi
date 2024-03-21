# Changelog

The following file contains all the changes made in unrar2-cffi, not including changes from unrar-cffi

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
