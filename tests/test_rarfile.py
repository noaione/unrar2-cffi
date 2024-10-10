from pathlib import Path

from pytest import fixture, raises

from unrar.cffi.rarfile import RarFile, RarFileError, RarInfo, is_rarfile
from unrar.cffi.unrarlib import FLAGS_BAD_PASSWORD, FLAGS_MISSING_PASSWORD, BadRarPassword

CURRENT_DIR = Path(__file__).absolute().parent


@fixture
def rar() -> RarFile:
    return RarFile(CURRENT_DIR / "test_rar.rar")


@fixture
def rar_no_comment() -> RarFile:
    return RarFile(CURRENT_DIR / "test_no_cmt.rar")


@fixture
def bad_rar() -> RarFile:
    return RarFile(CURRENT_DIR / "test_corrupted.rar")


def test_is_rarfile_good():
    good_rar = CURRENT_DIR / "test_rar.rar"
    assert is_rarfile(good_rar) is True


def test_is_rarfile_bad():
    non_rar = __file__
    assert is_rarfile(non_rar) is False


def test_is_rarfile_not_existing():
    non_existant = CURRENT_DIR / "non_existing.rar"
    assert is_rarfile(non_existant) is False


def test_open_not_existing():
    with raises(RarFileError):
        RarFile(CURRENT_DIR / "non_existing.rar")


def test_rar_namelist(rar: RarFile):
    assert rar.namelist() == [
        "test_file.txt",
        "test_file2.txt",
        str(Path("testdir") / "testfile"),
        "testdir",
    ]


def test_rar_read(rar: RarFile):
    assert rar.read("test_file.txt") == b"This is for test."
    assert rar.read("test_file2.txt") == b"This is another test!\n"
    assert rar.read(rar.getinfo("test_file2.txt")) == b"This is another test!\n"


def test_rar_open(rar: RarFile):
    assert rar.open("test_file.txt").read() == b"This is for test."
    assert rar.open(rar.getinfo("test_file.txt")).read() == b"This is for test."
    with raises(ValueError):
        rar.open("not_existing")


def test_rar_comment(rar: RarFile):
    assert rar.comment == bytes("this is a test rar comment àòùç€\n", "utf-8")


def test_rar_comment_empty(rar_no_comment: RarFile):
    assert rar_no_comment.comment == b""


def test_rar_testrar_good(rar: RarFile):
    assert rar.testrar() is None


def test_rar_testrar_bad(bad_rar: RarFile):
    assert bad_rar.testrar() == "test_file.txt"


@fixture
def info_test_file_txt():
    return {
        "filename": "test_file.txt",
        "date_time": (2013, 4, 14, 19, 3, 36),
        "compress_type": 0x33,
        "create_system": 3,
        "extract_version": 29,
        "flag_bits": 0,
        "CRC": 2911469160,
        "crc_hex": "AD897E68",
        "compress_size": 29,
        "file_size": 17,
    }


@fixture
def info_test_file2_txt():
    return {
        "filename": "test_file2.txt",
        "date_time": (2019, 9, 21, 22, 47, 34),
        "compress_type": 0x30,
        "create_system": 3,
        "extract_version": 29,
        "flag_bits": 0,
        "CRC": 1864074135,
        "crc_hex": "6F1B8397",
        "compress_size": 22,
        "file_size": 22,
    }


def _get_rar_info(rar_inf: RarInfo):
    assets = {}
    for key in dir(rar_inf):
        if key.startswith("_"):
            continue
        data = getattr(rar_inf, key)
        if callable(data):
            continue
        assets[key] = data
    return assets


def test_rar_infolist(rar: RarFile, info_test_file_txt: dict, info_test_file2_txt: dict):
    assert _get_rar_info(rar.infolist()[0]) == info_test_file_txt
    assert _get_rar_info(rar.infolist()[1]) == info_test_file2_txt


def test_rar_getinfo(rar: RarFile, info_test_file_txt: dict):
    assert _get_rar_info(rar.getinfo("test_file.txt")) == info_test_file_txt
    with raises(KeyError):
        rar.getinfo("not_existing")


def test_rar_is_dir(rar):
    testfile = Path("testdir") / "testfile"
    assert rar.getinfo(str(testfile)).is_dir() is False
    assert rar.getinfo("testdir").is_dir()


def test_rar_with_password():
    rar = RarFile(CURRENT_DIR / "test_rar_pwd.rar", pwd="test")
    assert rar.namelist() == ["test_file.txt"]


def test_rar_bad_password():
    with raises(BadRarPassword) as exc_info:
        x = RarFile(CURRENT_DIR / "test_rar_pwd.rar", pwd="wrong")
        x.read("test_file.txt")
    assert exc_info.value.code == FLAGS_BAD_PASSWORD


def test_rar_missing_pass():
    with raises(BadRarPassword) as exc_info:
        x = RarFile(CURRENT_DIR / "test_rar_pwd.rar")
        x.read("test_file.txt")
    assert exc_info.value.code == FLAGS_MISSING_PASSWORD
