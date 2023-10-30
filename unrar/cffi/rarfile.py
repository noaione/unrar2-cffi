from __future__ import annotations

import io
import typing as t
from collections import OrderedDict

from .unrarlib import FLAGS_RHDF_DIRECTORY, BadRarFile, RarArchive, RarHeader

if t.TYPE_CHECKING:
    from os import PathLike

__all__ = (
    "RarFile",
    "RarInfo",
    "RarFileError",
    "is_rarfile",
)
DateTime = t.Tuple[int, int, int, int, int, int]


class RarFileError(Exception):
    pass


def is_rarfile(filename: t.Union["PathLike", str]) -> bool:
    """Return true if file is a valid RAR file."""
    try:
        with RarArchive.open_for_metadata(filename):
            return True
    except Exception:
        return False


class RarFile:
    """Class with methods to open, read, close list rar files.

    Examples::

        r = RarFile(rarpath)
        r.namelist()

    Parameters
    ----------
    filename: :class:`os.PathLike`
        The filename of the RAR archive to load, can be a
        :class:`str` or :class:`pathlib.Path`.
    """

    comment: bytes
    infos: t.OrderedDict[str, RarInfo]

    __slots__ = ("infos", "_filename", "comment")

    def __init__(self, filename: "PathLike") -> None:
        """Load a RAR archive from a file specified by the filename.

        Parameters
        ----------
        filename: :class:`os.PathLike`
            The filename of the RAR archive to load, can be a
            :class:`str` or :class:`pathlib.Path`.

        Raises
        ------
        :class:`RarFileError`
            If the RAR archive is invalid.
        """

        self._filename: "PathLike" = filename

        self.comment: bytes = b""
        self.infos: t.OrderedDict[str, RarInfo] = OrderedDict()

        try:
            with RarArchive.open_for_processing(filename) as rar:
                self.comment = rar.comment.encode("utf-8")
                for header in rar.iterate_headers():
                    self.infos[header.FileNameW] = RarInfo(header)
                    header.skip()
        except BadRarFile as err:
            raise RarFileError("Error opening rar: {0}".format(err))

    @property
    def filename(self) -> str:
        """:class:`str`: The filename of the RAR archive."""
        return str(self._filename)

    def namelist(self) -> t.List[str]:
        """:class:`list`: Return a list of archive members by name."""
        return list(self.infos.keys())

    def infolist(self) -> t.List["RarInfo"]:
        """:class:`list`: Return a list of :class:`RarInfo` objects for all members of the archive."""
        return list(self.infos.values())

    def getinfo(self, file: t.Union[str, RarInfo]) -> "RarInfo":
        """:class:`RarInfo`: Return a :class:`RarInfo` object for the file named ``filename``."""
        filename = file.filename if isinstance(file, RarInfo) else file
        return self.infos[filename]

    def printdir(self, file) -> None:
        """Print a table of contents for the RAR file.

        Parameters
        ----------
        file: :class:`io.TextIOBase` | ``None``
            The file to write the table of contents to, default to ``sys.stdout``.
        """

        print("%-46s %19s %12s" % ("File Name", "Modified    ", "Size"), file=file)
        for zinfo in self.infolist():
            date = "%d-%02d-%02d %02d:%02d:%02d" % zinfo.date_time[:6]
            print("%-46s %s %12d" % (zinfo.filename, date, zinfo.file_size), file=file)

    def read(self, member: t.Union[str, RarInfo]) -> bytes:
        """Return the bytes of the archive member ``member``.

        Parameters
        ----------
        member: :class:`str` | :class:`RarInfo`
            The filename of the archive member to read or a :class:`RarInfo` object.

        Returns
        -------
        :class:`bytes`
            The bytes of the archive member.

        Raises
        ------
        :class:`ValueError`
            If the archive member cannot be found in the RAR archive.
        """
        return self.open(member).read()

    def open(self, file_or_info: t.Union[str, RarInfo]) -> io.BytesIO:
        """Return a file-like object for the archive member ``member``.

        Parameters
        ----------
        member: :class:`str` | :class:`RarInfo`
            The filename of the archive member to read or a :class:`RarInfo` object.

        Returns
        -------
        :class:`io.BytesIO`
            A file-like object for the archive member.

        Raises
        ------
        :class:`ValueError`
            If the archive member cannot be found in the RAR archive.
        """
        member = (
            file_or_info.filename if isinstance(file_or_info, RarInfo) else file_or_info
        )
        with RarArchive.open_for_processing(self.filename) as rar:
            for header in rar.iterate_headers():
                if header.FileNameW == member:
                    callback = InMemoryCollector()
                    header.test(callback)
                    return callback.bytes_io
                header.skip()
        raise ValueError(
            "Cannot open member file %s in rar %s" % (member, self.filename)
        )

    def testrar(self) -> t.Optional[str]:
        with RarArchive.open_for_processing(self.filename) as rar:
            for header in rar.iterate_headers():
                try:
                    header.test()
                except BadRarFile:
                    return header.FileNameW


class InMemoryCollector:
    __slots__ = ("_data",)

    def __init__(self):
        self._data = b""

    def __call__(self, chunk) -> None:
        self._data += chunk

    @property
    def bytes_io(self) -> io.BytesIO:
        return io.BytesIO(self._data)


class RarInfo:
    """Class with attributes describing each member in the RAR archive."""

    __slots__ = ("_header",)

    def __init__(self, header: RarHeader) -> None:
        """Initialize a RarInfo object with a member header data."""
        self._header: RarHeader = header

    def is_dir(self) -> bool:
        """:class:`bool`: Return ``True`` if the member is a directory."""
        return bool(self.flag_bits & FLAGS_RHDF_DIRECTORY)

    @property
    def filename(self) -> str:
        """:class:`str`: The filename of the archive member."""
        return self._header.FileNameW

    @property
    def date_time(self) -> DateTime:
        """:class:`tuple`: The date and time of the archive member."""
        return dostime_to_timetuple(self._header.FileTime)

    @property
    def compress_size(self) -> int:
        """:class:`int`: The compressed size of the archive member."""
        return self._header.PackSize + (self._header.PackSizeHigh << 32)

    @property
    def file_size(self) -> int:
        """:class:`int`: The uncompressed size of the archive member."""
        return self._header.UnpSize + (self._header.UnpSizeHigh << 32)

    @property
    def create_system(self) -> int:
        """:class:`int`: The system that created the archive member."""
        return self._header.HostOS

    @property
    def extract_version(self) -> int:
        """:class:`int`: The version of the archive member."""
        return self._header.UnpVer

    @property
    def CRC(self) -> int:
        """:class:`int`: The CRC of the archive member."""
        return self._header.FileCRC

    @property
    def flag_bits(self) -> int:
        """:class:`int`: The flag bits of the archive member."""
        return self._header.Flags

    @property
    def compress_type(self) -> int:
        """:class:`int`: The compression type of the archive member."""
        return self._header.Method


# see https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-dosdatetimetofiletime
def dostime_to_timetuple(dostime) -> DateTime:
    """Convert a RAR archive member DOS time to a Python time tuple."""
    date = dostime >> 16 & 0xFFFF
    time = dostime & 0xFFFF
    day = date & 0x1F
    month = (date >> 5) & 0xF
    year = 1980 + (date >> 9)
    second = 2 * (time & 0x1F)
    minute = (time >> 5) & 0x3F
    hour = time >> 11
    return (year, month, day, hour, minute, second)
