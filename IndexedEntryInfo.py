from DirectoryEntryInfo import DirectoryEntryInfo


class IndexedEntryInfo:
    def __init__(self, dir_entry_info: DirectoryEntryInfo, cur_clus: int, last_clus: int or None, is_directory: bool):
        self.dir_entry_info = dir_entry_info
        self.cur_clus = cur_clus
        self.last_clus = last_clus
        self.is_directory = is_directory
