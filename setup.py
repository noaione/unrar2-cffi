from setuptools import setup

setup(
    cffi_modules=["buildconf.py:create_builder"],
)
