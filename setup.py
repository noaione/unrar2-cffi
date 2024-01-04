# Explicitly use sys to get buildconf.py from the current directory because
# build_meta backend by pyproject is not finding the file properly.

import sys
from distutils.command.build import build

from setuptools import setup

sys.path.insert(0, "")

# Import buildconf.py
from buildconf import BuildUnrarCommand  # noqa: E402


class BuildUnrarBeforeBuild(build):
    def run(self):
        self.run_command("build_unrar")
        build.run(self)


setup(
    cmdclass={"build": BuildUnrarBeforeBuild, "build_unrar": BuildUnrarCommand},
)
