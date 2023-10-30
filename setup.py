from distutils.command.build import build

from setuptools import setup

from buildconf import BuildUnrarCommand

with open("README.md", "r") as fh:
    long_description = fh.read()


class BuildUnrarBeforeBuild(build):
    def run(self):
        self.run_command("build_unrar")
        build.run(self)


setup(
    cmdclass={"build": BuildUnrarBeforeBuild, "build_unrar": BuildUnrarCommand},
    name="unrar2-cffi",
    license="apache-2.0",
    description="Read RAR file from python -- cffi edition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Davide Romanini",
    author_email="davide.romanini@gmail.com",
    url="https://github.com/davide-romanini/unrar2-cffi",
    keywords=["rar", "unrar", "archive", "cffi"],
    use_scm_version=True,
    packages=("unrar.cffi",),
    install_requires=["cffi"],
    # setup_requires=["cffi", "pytest-runner", "wheel", "setuptools_scm"],
    tests_require=["pytest"],
    package_dir={"unrar.cffi": "unrar/cffi"},
    package_data={"unrar.cffi": ["*.dll"]},
    include_package_data=True,
    cffi_modules=["buildconf.py:create_builder"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
)
