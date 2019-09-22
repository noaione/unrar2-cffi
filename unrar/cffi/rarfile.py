import io
from collections import OrderedDict
from .unrarlib import RarArchive, BadRarFile

def is_rarfile(filename):
    """Return true if file is a valid RAR file."""
    try:
        with RarArchive.open_for_metadata(filename):        
            return True
    except:
        return False

class RarFile(object):
    def __init__(self, filename):
        """Load RAR archive file with mode read only "r"."""
        self.filename = filename
        self.filenames = []
        self.infos = OrderedDict()
        
        with RarArchive.open_for_metadata(filename) as rar:
            for header in rar.iterate_headers():
                self.infos[header.FileNameW] = RarInfo(header)
                self.filenames.append(header.FileNameW)
                header.skip()

    def namelist(self):
        return self.filenames

    def open(self, member):
        with RarArchive.open_for_processing(self.filename) as rar:
            for header in rar.iterate_headers():
                if header.FileNameW == member:
                    callback = InMemoryCollector()
                    header.test(callback)
                    return callback.bytes_io
                header.skip()

    def read(self, member):
        return self.open(member).read()
    
    def testrar(self):
        with RarArchive.open_for_processing(self.filename) as rar:
            for header in rar.iterate_headers():
                try:
                    header.test()
                except BadRarFile:
                    return header.FileNameW
    
    def infolist(self):
        return list(self.infos.values())

    def getinfo(self, filename):
        return self.infos[filename]

class InMemoryCollector:
    def __init__(self):
        self._data = b''
    def __call__(self, chunk):              
        self._data += chunk

    @property
    def bytes_io(self):
        return io.BytesIO(self._data)
    

class RarInfo(object):
    """Class with attributes describing each member in the RAR archive."""
    def __init__(self, header):
        """Initialize a RarInfo object with a member header data."""
        self.filename = header.FileNameW
        self.date_time = dostime_to_timetuple(header.FileTime)
        self.compress_size = header.PackSize + (header.PackSizeHigh << 32)
        self.file_size = header.UnpSize + (header.UnpSizeHigh << 32)
        self.create_system = header.HostOS
        self.extract_version = header.UnpVer
        self.CRC = header.FileCRC
        self.flag_bits = header.Flags
        self.compress_type = header.Method

# see https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-dosdatetimetofiletime
def dostime_to_timetuple(dostime):
    """Convert a RAR archive member DOS time to a Python time tuple."""
    date = dostime >> 16 & 0xffff
    time = dostime & 0xffff   
    day = date & 0x1f
    month = (date >> 5) & 0xf
    year = 1980 + (date >> 9)
    second = 2 * (time & 0x1f)
    minute = (time >> 5) & 0x3f
    hour = time >> 11
    return (year, month, day, hour, minute, second)