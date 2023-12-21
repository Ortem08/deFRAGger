from FileSystem import FileSystem
from FileHandler import FileHandler
from ClusterExchanger import ClusterExchanger


class Defragger:
    def __init__(self, file_system: FileSystem, file_handler: FileHandler):
        self.file_system = file_system
        self.file_handler = file_handler
        self.cluster_exchanger = ClusterExchanger(file_system.get_indexed_fat_table(), file_system.get_fat_handler(), file_handler)

    def defragmentation(self):
        all_directories_entries_list = self.file_system.get_all_directory_entries_set()
        fat_handler = self.file_system.get_fat_handler()
        indexed_table = self.file_system.get_indexed_fat_table()

        current_cluster = 2

        for directory_entries in all_directories_entries_list:
            if directory_entries.name == '\\':
                continue

            current_file_cluster = directory_entries.first_cluster_number

            while True:
                if current_cluster in indexed_table and indexed_table[current_cluster].directory_entry_info.name == '\\' or\
                   fat_handler.is_bad_cluster(fat_handler.get_cluster_value_in_main_fat(current_cluster)):

                    current_cluster += 1
                    continue

                self.cluster_exchanger.exchange_clusters(current_cluster, current_file_cluster)
                next_clus = fat_handler.get_cluster_value_in_main_fat(current_cluster)

                if fat_handler.is_final_cluster(next_clus):
                    current_cluster += 1
                    break
                else:
                    current_file_cluster = next_clus

                current_cluster += 1
