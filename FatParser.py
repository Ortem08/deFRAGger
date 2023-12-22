from DirectoryParser import DirectoryParser
from FatHandler import FatHandler
from FatIndexer import FatIndexer
from FileSystem import FileSystem
from FileHandler import FileHandler
from ErrorHandler import ErrorHandler
from FatEntity import FatEntity


def parse_fat(file_handler: FileHandler):
    far_entity = FatEntity(file_handler)

    fat_handler = FatHandler(far_entity, file_handler)
    error_handler = ErrorHandler(fat_handler)
    directory_parser = DirectoryParser(fat_handler)

    if error_handler.check_differences_in_fats():
        return FileSystem(far_entity,
                          fat_handler,
                          {},
                          error_handler)

    fat_index = FatIndexer(directory_parser)
    full_indexed_fat_table = fat_index.get_full_indexed_table()

    if error_handler.is_looped_or_intersecting_files(full_indexed_fat_table):
        return FileSystem(far_entity,
                          fat_handler,
                          full_indexed_fat_table,
                          error_handler)

    correct_indexed_fat_table = fat_index.get_correct_indexed_table()

    file_system = FileSystem(far_entity,
                             fat_handler,
                             correct_indexed_fat_table,
                             error_handler)

    return file_system
