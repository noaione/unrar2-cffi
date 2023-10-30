[![Build](https://github.com/noaione/unrar2-cffi/actions/workflows/build.yml/badge.svg)](https://github.com/noaione/unrar2-cffi/actions/workflows/build.yml)

# unrar2-cffi -- Work with RAR files.

## Description

unrar2-cffi is a python extension that exposes [unrar library](https://rarlab.com/rar_add.htm)
functionality through a [`zipfile`](https://docs.python.org/3/library/zipfile.html)-like interface.

This is a fork/modified version of [unrar-cffi](https://pypi.org/project/unrar-cffi/) that supports modern Python starting from 3.9+

This build also target unrar 6.x instead of unrar 5.x from the original unrar-cffi project.

## Difference

This packages has some difference to the original one:
- Added typing information
- Added `__slots__` to improve performance a bit.
- Moved all the `RarInfo` into at-property data
  - Now you can access the raw header data by using `file._header`
- Added docstring to most functions.
- Implement `RarFile.printdir()`

## Features

The package implements the following `RarFile` functions:

 * `namelist()`
 * `infolist()`
 * `getinfo()`
 * `read()`
 * `open()`
 * `testrar()`
 * `rarfile.is_rar_file()`

## Usage

 1. Install with PIP:

    `pip install unrar2-cffi`

 2. Use from code:

```python
    from unrar.cffi import rarfile

    rar = rarfile.RarFile('sample.rar')

    assert rar.testrar() == None

    for filename in rar.namelist():
        info = rar.getinfo(filename)
        print("Reading {}, {}, {} bytes ({} bytes compressed)".format(info.filename, info.date_time, info.file_size, info.compress_size))
        data = rar.read(filename)
        print("\t{}...\n".format(data[:100]))
```

## Build

### Requirements

Linux/macOS:
 * gcc compiler suite (`build-essential` packages should be enough)
 * docker (only for `buildmanylinux`)

Windows:
 * VS2022 Build Tools (PLATFORM_TOOLSET=v143)
 * Visual C++ compiler suite
 * `vswhere`

### Compile and test

 1. `./build.sh init`
 2. `./build.sh build`
 3. `./build.sh test`

If you have docker installed, you can build all the [manylinux](https://github.com/pypa/manylinux) 
wheels:

 1. `./build.sh within [manylinux docker image] buildmanylinux`
 2. `./build.sh within [manylinux docker image] testmanylinux`

By deafult the image `quay.io/pypa/manylinux2010_x86_64` will be used.
Use `$DOCKER_IMAGE` and `$PLAT` variables to customize the build.

### Problems

Windows:
* If you need to retarget solution, apply the `0001-build-retarget-to-vs2022-10.0-v143.patch` that will utilize the latest version.

macOS:
* The macOS version are monkeypatching unrar 6.x makefile to utilize C++11
