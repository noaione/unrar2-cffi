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
        if pwd is not None and pwd:
            archive.set_password(pwd)
        self.handle = RAROpenArchiveEx(archive.value)
        if archive.value.OpenResult != C_ERAR_SUCCESS:
            if archive.value.OpenResult == C_ERAR_MISSING_PASSWORD:
                raise BadRarPassword(
                    archive.value.OpenResult,
                    "Cannot open {}: Missing password".format(filename),
                )
            elif archive.value.OpenResult == C_ERAR_BAD_PASSWORD:
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

    def iterate_headers(self) -> Generator["RarHeader", Any, None]:
        header_data = RARHeaderDataEx()
        res = RARReadHeaderEx(self.handle, header_data)
        while res == C_ERAR_SUCCESS:
            yield RarHeader(self.handle, header_data)
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
    def __init__(self, handle, headerDataEx):
        self.handle = handle
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

    def set_password(self, password: str) -> None:
        password_ffi = ffi.new("char[]", password.encode("ascii"))
        RARSetPassword(self.value, password_ffi)


def RARHeaderDataEx():
    return ffi.new("struct RARHeaderDataEx *")
