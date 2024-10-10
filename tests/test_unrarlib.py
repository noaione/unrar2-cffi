from unrar.cffi._unrarlib.lib import RARGetDllVersion  # type: ignore
from unrar.cffi.unrarlib import get_unrar_version


def test_rar_version() -> None:
    version = RARGetDllVersion()
    assert version == 9


def test_unrar_version():
    version = get_unrar_version()
    assert version == (7, 1, 0)
