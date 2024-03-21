from unrar.cffi._unrarlib.lib import RARGetDllVersion  # type: ignore


def test_rar_version() -> None:
    version = RARGetDllVersion()
    if version < 8:
        raise AssertionError("UnRAR library version is too old")
