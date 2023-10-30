from unrar.cffi._unrarlib.lib import RARGetDllVersion  # type: ignore


def test_rar_version() -> None:
    assert RARGetDllVersion() == 8
