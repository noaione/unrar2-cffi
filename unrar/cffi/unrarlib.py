from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator, Optional

from ._unrarlib import ffi  # type: ignore
from ._unrarlib.lib import (  # type: ignore
    C_ERAR_BAD_PASSWORD,
    C_ERAR_MISSING_PASSWORD,
    C_ERAR_SUCCESS,
    C_RAR_OM_EXTRACT,
    C_RAR_OM_LIST_INCSPLIT,
    C_RAR_SKIP,
    C_RAR_TEST,
    C_RHDF_DIRECTORY,
    UCM_PROCESSDATA,
    PyUNRARCALLBACKStub,
    RARCloseArchive,
    RARGetUnrarVersionCallback,
    RAROpenArchiveEx,
    RARProcessFileW,
    RARReadHeaderEx,
    RARSetCallbackPtr,
    RARSetPassword,
)

if TYPE_CHECKING:
    from os import PathLike

__all__ = (
    "RarArchive",
    "RarHeader",
    "RAROpenArchiveDataEx",
    "BadRarFile",
    "get_unrar_version",
    "FLAGS_RHDF_DIRECTORY",
    "FLAGS_SUCCESS",
    "FLAGS_MISSING_PASSWORD",
    "FLAGS_BAD_PASSWORD",
)

FLAGS_RHDF_DIRECTORY: int = C_RHDF_DIRECTORY
FLAGS_SUCCESS: int = C_ERAR_SUCCESS
FLAGS_MISSING_PASSWORD: int = C_ERAR_MISSING_PASSWORD
FLAGS_BAD_PASSWORD: int = C_ERAR_BAD_PASSWORD


@ffi.def_extern("PyUNRARCALLBACKStub")
def PyUNRARCALLBACKSkeleton(msg, user_data, p1, p2):
    callback = ffi.from_handle(user_data)
    return callback(msg, p1, p2)


class RarArchive:
    def __init__(self, filename: "PathLike", mode: int, *, pwd: Optional[str] = None) -> None:
        self.comment = ""
        archive = RAROpenArchiveDataEx(filename, mode)
        self.handle = RAROpenArchiveEx(archive.value)
        self._password_set = bool(pwd)
        self._filename  = filename
        if self._password_set:
            RARSetPassword(self.handle, pwd.encode("ascii"))
        if archive.value.OpenResult != C_ERAR_SUCCESS:
            if archive.value.OpenResult == FLAGS_MISSING_PASSWORD:
                raise BadRarPassword(
                    archive.value.OpenResult,
                    "Cannot open {}: Missing password".format(filename),
                )
            elif archive.value.OpenResult == FLAGS_BAD_PASSWORD:
                raise BadRarPassword(
                    archive.value.OpenResult,
                    "Cannot open {}: Bad password".format(filename),
                )
            else:
                raise BadRarFile(
                    archive.value.OpenResult,
                    "Cannot open {}: Error code is {}".format(
                        filename, archive.value.OpenResult
                    )
                )
        self.comment = ffi.string(archive.value.CmtBufW)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback) -> None:
        result = RARCloseArchive(self.handle)
        assert result == C_ERAR_SUCCESS

    def __repr__(self):
        attributes = {
            "pwd": self._password_set,
            "comment": self.comment,
        }
        merged_str = ", ".join(f"{k}={v!r}" for k, v in attributes.items())
        return "<RarArchive: {} {}>".format(self._filename, merged_str)

    def iterate_headers(self) -> Generator["RarHeader", Any, None]:
        header_data = RARHeaderDataEx()
        res = RARReadHeaderEx(self.handle, header_data)
        while res == C_ERAR_SUCCESS:
            yield RarHeader(self, header_data)
            header_data = RARHeaderDataEx()
            res = RARReadHeaderEx(self.handle, header_data)

    @staticmethod
    def open_for_metadata(filename: "PathLike", *, pwd: Optional[str] = None) -> "RarArchive":
        return RarArchive(filename, C_RAR_OM_LIST_INCSPLIT, pwd=pwd)

    @staticmethod
    def open_for_processing(filename: "PathLike", *, pwd: Optional[str] = None) -> "RarArchive":
        return RarArchive(filename, C_RAR_OM_EXTRACT, pwd=pwd)


def null_callback(*args):
    pass


class RarHeader:
    def __init__(self, archive, headerDataEx):
        self.handle = archive.handle
        self._is_password = archive._password_set
        self.headerDataEx = headerDataEx

    @property
    def FileNameW(self) -> str:
        return ffi.string(self.headerDataEx.FileNameW)

    @property
    def FileTime(self):
        return self.headerDataEx.FileTime

    @property
    def PackSize(self) -> int:
        return self.headerDataEx.PackSize

    @property
    def PackSizeHigh(self) -> int:
        return self.headerDataEx.PackSizeHigh

    @property
    def UnpSize(self) -> int:
        return self.headerDataEx.UnpSize

    @property
    def UnpSizeHigh(self) -> int:
        return self.headerDataEx.UnpSizeHigh

    @property
    def UnpVer(self) -> int:
        return self.headerDataEx.UnpVer

    @property
    def FileCRC(self) -> int:
        return self.headerDataEx.FileCRC

    @property
    def Flags(self) -> int:
        return self.headerDataEx.Flags

    @property
    def HostOS(self) -> int:
        return self.headerDataEx.HostOS

    @property
    def Method(self) -> int:
        return self.headerDataEx.Method

    def skip(self) -> None:
        RARProcessFileW(self.handle, C_RAR_SKIP, ffi.NULL, ffi.NULL)

    def test(self, callback=null_callback):
        def wrapper(msg, p1, p2):
            if msg == UCM_PROCESSDATA:
                chunk = ffi.buffer(ffi.cast("char *", p1), p2)
                callback(bytes(chunk))
            return 1

        user_data = ffi.new_handle(wrapper)
        RARSetCallbackPtr(self.handle, PyUNRARCALLBACKStub, user_data)
        result = RARProcessFileW(self.handle, C_RAR_TEST, ffi.NULL, ffi.NULL)
        RARSetCallbackPtr(self.handle, ffi.NULL, ffi.NULL)
        if result != C_ERAR_SUCCESS:
            if result == FLAGS_BAD_PASSWORD or (result == FLAGS_MISSING_PASSWORD and self._is_password):
                raise BadRarPassword(
                    result,
                    "Cannot open {}: Bad password".format(self.FileNameW),
                )
            elif result == FLAGS_MISSING_PASSWORD and not self._is_password:
                raise BadRarPassword(
                    result,
                    "Cannot open {}: Password protected".format(self.FileNameW),
                )
            else:
                raise BadRarFile(result, "Rarfile corrupted: error code is %d" % result)


class BadRarFile(Exception):
    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class BadRarPassword(BadRarFile):
    pass


class RAROpenArchiveDataEx:
    def __init__(self, filename: "PathLike", mode: int) -> None:
        COMMENT_MAX_SIZE = 64 * 1024
        self.arcNameW = ffi.new("wchar_t[]", str(filename))
        self.cmtBufW = ffi.new("wchar_t[{}]".format(COMMENT_MAX_SIZE))
        self.value = ffi.new(
            "struct RAROpenArchiveDataEx *",
            {
                "ArcNameW": self.arcNameW,
                "OpenMode": mode,
                "CmtBufSize": ffi.sizeof("wchar_t") * COMMENT_MAX_SIZE,
                "CmtBufW": self.cmtBufW,
            },
        )

    def value(self):
        return self.value


def RARHeaderDataEx():
    return ffi.new("struct RARHeaderDataEx *")


def get_unrar_version() -> tuple[int, int, int]:
    """Get current unrar library version used when doing compilation.

    :return: 3-tuple of major, minor and patch version numbers
    :rtype: tuple[int, int, int]
    """

    c_major = ffi.new("int *")
    c_minor = ffi.new("int *")
    c_patch = ffi.new("int *")

    RARGetUnrarVersionCallback(c_major, c_minor, c_patch)
    # Convert to 3-tuple of int
    return (c_major[0], c_minor[0], c_patch[0])
