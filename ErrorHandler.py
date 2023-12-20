import random

import ImageTools

from FatHandler import FatHandler
from IndexedEntryInfo import IndexedEntryInfo


class ErrorHandler:
    def __init__(self, fat_handler: FatHandler):
        self.fat_handler = fat_handler
        self.different_clusters = []
        self.looped_files = []
        self.intersecting_files = []
        self.unused_clusters = []
        self.indexed_files_to_delete = set()

    def check_differences_in_fats(self):
        info = self.fat_handler.fat_entity
        for i in range(info.count_of_clusters):
            value_in_first_fat = self.fat_handler.get_cluster_value_in_fat(i, 0)
            for j in range(info.BPB_NumFATs):
                if value_in_first_fat != self.fat_handler.get_cluster_value_in_fat(i, j):
                    self.different_clusters.append(i)

        return len(self.different_clusters) != 0

    def is_looped_or_intersecting_files(self, indexed_table: dict[int, list[IndexedEntryInfo]]) -> bool:
        for ind in indexed_table:
            list_values = indexed_table[ind]
            if len(list_values) == 1:
                continue

            directory = {}
            for entity in list_values:
                if entity.dir_entry_info.name in directory:
                    self.looped_files.append(entity)
                else:
                    directory[entity.dir_entry_info.name] = entity

            if len(directory):
                self.intersecting_files.append(list(directory.values()))

        return len(self.looped_files) != 0 or len(self.looped_files) != 0

    def clear_fat_table(self, indexed_table: dict) -> bool:
        fat_entity = self.fat_handler.fat_entity
        unused_clusters = []
        for i in range(2, fat_entity.count_of_clusters):
            if (self.fat_handler.get_cluster_value_in_main_fat(i) != 0 and i not in indexed_table) or \
                    self.is_cluster_of_file_to_delete(i, indexed_table):
                self.fat_handler.write_cluster_value_in_all_tables(0, i)
                unused_clusters.append(i)
        self.unused_clusters = unused_clusters

        return len(self.unused_clusters) != 0

    def is_cluster_of_file_to_delete(self, cluster_number: int, indexed_table: dict) -> bool:
        if cluster_number not in indexed_table:
            return False
        if type(indexed_table[cluster_number]) == list:
            for entry in indexed_table[cluster_number]:
                if entry.dir_entry_info.name in self.indexed_files_to_delete:
                    return True
            return False
        else:
            return indexed_table[cluster_number].dir_entry_info.name in self.indexed_files_to_delete

    def repair_differences_fats(self, correct_table_number: int) -> None:
        for cluster in self.different_clusters:
            correct_value = self.fat_handler.get_cluster_value_in_fat(cluster, correct_table_number)
            for fat_number in range(self.fat_handler.fat_entity.BPB_NumFATs):
                if fat_number == correct_table_number:
                    continue
                self.fat_handler.write_cluster_value_in_fat(correct_value,
                                                            cluster,
                                                            fat_number)
        self.different_clusters = []

    def repair_looped_files(self) -> None:
        dir_parser = ImageTools.DirectoryParser(self.fat_handler)
        for entry in self.looped_files:
            dir_parser.delete_entry_in_directory(entry.dir_entry_info.entry_point)
            self.indexed_files_to_delete.add(entry.dir_entry_info.name)

        self.looped_files = []

    def repair_intersecting_files(self) -> None:
        directory_parser = ImageTools.DirectoryParser(self.fat_handler)
        for entries_list in self.intersecting_files:
            for entry in entries_list:
                directory_parser.delete_entry_in_directory(entry.dir_entry_info.entry_point)
                self.indexed_files_to_delete.add(entry.dir_entry_info.name)

        self.intersecting_files = []
