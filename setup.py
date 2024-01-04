from setuptools import Extension, setup

setup(
    ext_modules=[
        Extension(
            "unrar.cffi.unrarlib",
            ["unrar/cffi/unrarlib_ext.c"],
        )
    ]
)
