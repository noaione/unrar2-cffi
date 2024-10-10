import platform
import subprocess
from distutils import log
from distutils.cmd import Command
from distutils.command.build import build
from os import getenv
from os.path import dirname, join, realpath
from pathlib import Path

UNRARSRC = "unrarsrc"

# UNIX like OS
SOURCE_PARAMETERS = {
    "extra_objects": ["{}/libunrar.a".format(UNRARSRC)],
    "include_dirs": ["unrar/cffi", UNRARSRC],
    "libraries": ["stdc++"],
}
DATA_FILES = []
BUILD_CMD = [getenv("MAKE", "make"), "-C", UNRARSRC, "lib"]
PREPROCESS_CMD = [
    getenv("CC", "cc"),
    "-I",
    UNRARSRC,
    "-P",
    "-U",
    "__cplusplus",
    "-E",
    "unrar/cffi/unrarlib_py.h",
]

if platform.system() == "Windows":
    bits = platform.architecture()[0][0:2]
    build_platform = "x64" if bits == "64" else "Win32"
    build_dir = join(realpath(dirname(__file__)), "unrar/cffi")  # noqa: PTH118,PTH120
    build_platform_toolset = getenv("PLATFORM_TOOLSET", "v143")
    SOURCE_PARAMETERS = {
        "library_dirs": [build_dir],
        "include_dirs": ["unrar/cffi", UNRARSRC],
        "libraries": ["unrar"],
        "extra_link_args": ["/DEF:{}/dll.def".format(UNRARSRC)],
    }
    DATA_FILES = [("unrar/cffi", ["{}/unrar.dll".format(build_dir)])]
    BUILD_CMD = [
        "MSBuild.exe",
        "{}/UnRARDll.vcxproj".format(UNRARSRC),
        "/p:PlatformToolset={}".format(build_platform_toolset),
        "/p:Configuration=Release",
        "/p:Platform={}".format(build_platform),
        "/p:OutDir={}".format(build_dir),
    ]

    PREPROCESS_CMD = [
        "CL.exe",
        "/EP",
        "/I{}".format(UNRARSRC),
        "/D",
        "CALLBACK=WINAPI",
        "/D",
        "PASCAL=WINAPI",
        "/U",
        "__cplusplus",
        "unrar/cffi/unrarlib_py.h",
    ]


class BuildUnrarCommand(Command):
    description = "build unrar library"
    user_options = []  # noqa: RUF012

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _windows_patch(self):
        if platform.system() != "Windows":
            # Not Windows
            return

        log.info("running patches for windows")
        ROOT_DIR = Path(__file__).absolute().parent
        patch_files = [
            ROOT_DIR / "patches" / "0001-build-retarget-to-vs2022-10.0-v143.patch"
        ]

        for patch in patch_files:
            log.info(f"applying patch: {patch.stem}")
            subprocess.run(["git", "apply", str(patch)])

    def run(self):
        log.info("compiling unrar library")
        # In Windows, we need to retarget the project to v143
        self._windows_patch()
        subprocess.check_call(BUILD_CMD)
        log.info("compiled unrar library")


class BuildOverride(build):
    def run(self):
        self.run_command("build_unrar")
        first_mod = self.distribution.ext_modules[0]
        first_source = first_mod.sources[0]
        # Retrigger the cffi distribution data
        dist_parent = create_builder().distutils_extension()
        log.info("data: %s", dist_parent.sources)

        if first_source == "$PLACEHOLDER":
            self.distribution.ext_modules[0].sources[0] = "build/unrar/cffi/_unrarlib.c"
        build.run(self)


def create_builder():
    from cffi import FFI

    log.info("preprocessing extension headers")
    preprocess = subprocess.check_output(PREPROCESS_CMD, universal_newlines=True)

    builder = FFI()
    builder.cdef(preprocess, packed=True)

    with Path("unrar/cffi/unrarlib_ext.c").open() as f:
        builder.set_source("unrar.cffi._unrarlib", f.read(), **SOURCE_PARAMETERS)

    return builder
