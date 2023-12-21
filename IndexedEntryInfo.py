from DirectoryEntryInfo import DirectoryEntryInfo


class IndexedEntryInfo:
    def __init__(self, 
                 directory_entry_entity: DirectoryEntryInfo,
                 cur_cluster: int,
                 last_cluster: int or None,
                 is_directory: bool):
        self.directory_entry_info = directory_entry_entity
        self.cur_cluster = cur_cluster
        self.last_cluster = last_cluster
        self.is_directory = is_directory
