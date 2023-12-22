import random

import FatExtensions
from DirectoryParser import DirectoryParser
from FatHandler import FatHandler
from FatType import FatType
from FileSystem import FileSystem


class ErrorCreator:
    def __init__(self, directory_parser: DirectoryParser, file_system: FileSystem):
        self.directory_parser = directory_parser
        self.file_system = file_system
        self.fat_entity = directory_parser.fat_handler.fat_entity
        self.fat_handler = self.directory_parser.fat_handler

        self.end_clus_val = (FatHandler.END_CLUSTER_IN_WIN_FAT_16 if
                             self.fat_entity.fat_type == FatType.fat16 else
                             FatHandler.END_CLUSTER_IN_WIN_FAT_32)

    def make_error_in_fat_table(self, fat_number: int):
        cluster_number = random.randint(0, self.fat_entity.clusters_count)
        value = self.fat_handler.get_cluster_value_in_fat(cluster_number, fat_number)
        self.fat_handler.write_cluster_value_in_fat(value + 1, cluster_number, fat_number)

    def make_looped_file(self, name_dir: str):
        empty_entry_point = self.get_free_entry_point_in_directory(name_dir)

        free_clusters = FatExtensions.find_empty_clusters(3, self.fat_entity, self.file_system.get_indexed_fat_table())

        self.directory_parser.create_entry_in_directory(empty_entry_point, 'ERRORLOOP  ', 0x00, free_clusters[0])

        for i in range(len(free_clusters)):
            if i == len(free_clusters) - 1:
                self.fat_handler.write_cluster_value_in_all_tables(free_clusters[0], free_clusters[i])
            else:
                self.fat_handler.write_cluster_value_in_all_tables(free_clusters[i + 1], free_clusters[i])

    def make_intersecting_files(self, name_dir: str):
        empty_entry_point = self.get_free_entry_point_in_directory(name_dir)
        free_clusters = FatExtensions.find_empty_clusters(3, self.fat_entity, self.file_system.get_indexed_fat_table())

        self.directory_parser.create_entry_in_directory(empty_entry_point, 'ERRINTERSEC', 0x00, free_clusters[0])

        for i in range(len(free_clusters)):
            if i == len(free_clusters) - 1:
                self.fat_handler.write_cluster_value_in_all_tables(self.end_clus_val, free_clusters[i])
            else:
                self.fat_handler.write_cluster_value_in_all_tables(free_clusters[i + 1], free_clusters[i])

        empty_entry_point = self.get_free_entry_point_in_directory(name_dir)
        new_free_clusters = FatExtensions.find_empty_clusters(1, self.fat_entity, self.file_system.get_indexed_fat_table())

        self.directory_parser.create_entry_in_directory(empty_entry_point, 'ERRINTERS 2', 0x00, new_free_clusters[0])
        self.fat_handler.write_cluster_value_in_all_tables(free_clusters[1], new_free_clusters[0])

    def get_free_entry_point_in_directory(self, name_dir: str):
        if name_dir == '\\':
            dir_entry_point = self.file_system.get_fat_handler().fat_entity.first_root_dir_sec
        else:
            set_of_files = self.file_system.get_all_directory_entries_set()

            for dir_entry_info in set_of_files:
                if dir_entry_info.name.strip() == name_dir.strip() and dir_entry_info.attribute.is_directory:
                    dir_entry_point = self.fat_handler.get_cluster_entry_in_data(dir_entry_info.first_cluster_number)
                    break
            else:
                raise ValueError(f"Directory \"{name_dir}\" does not exist")

        empty_entry_point = self.directory_parser.find_empty_entry_in_directory(dir_entry_point)

        if empty_entry_point is None:
            raise ValueError(f'No free entries in directory "{name_dir}"')

        return empty_entry_point