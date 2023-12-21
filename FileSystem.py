from DirectoryEntryInfo import DirectoryEntryInfo
from ErrorHandler import ErrorHandler
from FatEntity import FatEntity
from FatHandler import FatHandler
from FatType import FatType
from FatTypeExtensions import FatTypeExtensions
from IndexedEntryInfo import IndexedEntryInfo


class FileSystem:
    def __init__(self,
                 fat_entity: FatEntity,
                 fat_handler: FatHandler,
                 indexed_table: dict,
                 error_handler: ErrorHandler):
        self.fat_type = fat_entity.fat_type
        self.fat_entity = fat_entity
        self.fat_handler = fat_handler
        self.indexed_table = indexed_table
        self.error_handler = error_handler

    def get_type_of_fat(self) -> FatType:
        return self.fat_type

    def get_name_type_of_fat(self) -> str:
        return FatTypeExtensions.name_by_type[self.fat_type]

    def get_fat_handler(self) -> FatHandler:
        return self.fat_handler

    def get_indexed_fat_table(self) -> dict[int, IndexedEntryInfo]:
        return self.indexed_table

    def get_all_directory_entries_set(self) -> set[DirectoryEntryInfo]:
        return set(map(lambda x: x.directory_entry_info, self.indexed_table.values()))

    def get_error_handler(self) -> ErrorHandler:
        return self.error_handler
