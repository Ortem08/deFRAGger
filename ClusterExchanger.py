from DirectoryParser import DirectoryParser
from FatHandler import FatHandler
from FileHandler import FileHandler
from IndexedEntryInfo import IndexedEntryInfo


class ClusterExchanger:
    def __init__(self,
                 indexed_table: dict,
                 fat_handler: FatHandler,
                 file_handler: FileHandler):
        self.indexed_table = indexed_table
        self.fat_handler = fat_handler
        self.file_handler = file_handler
        self.fat_entity = fat_handler.fat_entity

    def exchange_clusters(self,
                          first_cluster_number: int,
                          second_cluster_number: int) -> None:
        if first_cluster_number == second_cluster_number:
            return

        first_value_in_fat = \
            (self.fat_handler
             .get_cluster_value_in_main_fat(first_cluster_number))
        second_value_in_fat = (
            self.fat_handler
            .get_cluster_value_in_main_fat(second_cluster_number))

        # меняем значения во всех FATs
        self.exchange_values_in_fats(first_cluster_number,
                                     second_cluster_number)

        # меняем значение в предыдущих кластерах
        first_indexed_entry_info = (self
                                    .get_indexed_entry(first_cluster_number))
        second_indexed_entry_info = (self
                                     .get_indexed_entry(second_cluster_number))
        self.change_all_references(second_cluster_number,
                                   first_value_in_fat,
                                   first_indexed_entry_info)
        self.change_all_references(first_cluster_number,
                                   second_value_in_fat,
                                   second_indexed_entry_info)

        # меняем записи в индексированной таблице
        self.exchange_value_in_indexed_table(first_cluster_number,
                                             second_cluster_number)

        # меняем записи в области данных
        self.exchange_clusters_in_data(first_cluster_number,
                                       second_cluster_number)

        # сохраняем правильность хранения файлов в директории
        directory_parser = DirectoryParser(self.fat_handler)
        cnt_entries = (directory_parser.fat_handler.fat_entity
                       .get_entries_count_in_directory_cluster())
        for i in [first_cluster_number, second_cluster_number]:
            if i in self.indexed_table and self.indexed_table[i].is_directory:
                directory_info = \
                    (directory_parser
                     .get_directory_entity_in_one_cluster(i, cnt_entries))
                for entry in directory_info.entries_list:
                    if entry.name.strip() == '.' or entry.name.strip() == '..':
                        continue
                    cluster_number = entry.first_cluster_number
                    directory_entry_info = (self.indexed_table[cluster_number]
                                            .directory_entry_info)
                    directory_entry_info.entry_point = entry.entry_point

    def exchange_value_in_indexed_table(self,
                                        first_cluster: int,
                                        second_cluster: int):
        if (first_cluster in self.indexed_table
                and second_cluster in self.indexed_table):
            first_indexed_entry_info = self.indexed_table[first_cluster]
            self.indexed_table[first_cluster].cur_cluster = second_cluster
            self.indexed_table[second_cluster].cur_cluster = first_cluster

            self.indexed_table[first_cluster] = (
                self.indexed_table)[second_cluster]
            self.indexed_table[second_cluster] = first_indexed_entry_info

        elif (first_cluster not in self.indexed_table
              and second_cluster in self.indexed_table):
            self._swap_ind_tab_fat_val_with_zero(second_cluster, first_cluster)

        elif (second_cluster not in self.indexed_table
              and first_cluster in self.indexed_table):
            self._swap_ind_tab_fat_val_with_zero(first_cluster, second_cluster)

    def _swap_ind_tab_fat_val_with_zero(self,
                                        clus_without_zero: int,
                                        clus_with_zero):
        self.indexed_table[clus_without_zero].cur_cluster = clus_with_zero
        self.indexed_table[clus_with_zero] = (
            self.indexed_table)[clus_without_zero]
        self.indexed_table.pop(clus_without_zero)

    def exchange_values_in_fats(self,
                                first_cluster: int,
                                second_cluster: int) -> None:
        value_first_in_fat = (self.fat_handler
                              .get_cluster_value_in_main_fat(first_cluster))
        value_second_in_fat = (self.fat_handler
                               .get_cluster_value_in_main_fat(second_cluster))
        self.fat_handler.write_cluster_value_in_all_tables(value_second_in_fat,
                                                           first_cluster)
        self.fat_handler.write_cluster_value_in_all_tables(value_first_in_fat,
                                                           second_cluster)

    def exchange_clusters_in_data(self,
                                  first_cluster: int,
                                  second_cluster: int) -> None:
        first_val_in_data = (self.fat_handler
                             .get_cluster_value_in_data(first_cluster))
        second_val_in_data = (self.fat_handler
                              .get_cluster_value_in_data(second_cluster))
        self.fat_handler.write_cluster_value_in_data(first_val_in_data,
                                                     second_cluster)
        self.fat_handler.write_cluster_value_in_data(second_val_in_data,
                                                     first_cluster)

    def change_all_references(self,
                              new_value: int,
                              next_value_for_cur_clus: int,
                              indexed_entry_info_of_ch_clus: IndexedEntryInfo
                                                             or None) -> None:
        if indexed_entry_info_of_ch_clus is not None:
            last_cluster = indexed_entry_info_of_ch_clus.last_cluster
            cur_value_in_fat = self.fat_handler.get_cluster_value_in_main_fat(
                indexed_entry_info_of_ch_clus.cur_cluster)

            if last_cluster is None:
                (self
                 .write_first_cluster_in_directory_entry(
                    new_value,
                    indexed_entry_info_of_ch_clus
                    .directory_entry_info
                    .entry_point))
                indexed_entry_info_of_ch_clus.directory_entry_info\
                    .first_cluster_number = new_value
            elif indexed_entry_info_of_ch_clus.cur_cluster == cur_value_in_fat:
                (self.fat_handler
                 .write_cluster_value_in_all_tables(
                    new_value,
                    indexed_entry_info_of_ch_clus
                    .cur_cluster))
                indexed_entry_info_of_ch_clus.last_cluster = (
                    indexed_entry_info_of_ch_clus.cur_cluster)
            else:
                (self.fat_handler
                 .write_cluster_value_in_all_tables(new_value,
                                                    last_cluster))

            if (not self.fat_handler.is_final_cluster(
                    next_value_for_cur_clus)
                    and next_value_for_cur_clus != new_value):
                self.indexed_table[
                    next_value_for_cur_clus].last_cluster = new_value

    def write_first_cluster_in_directory_entry(self,
                                               value: int,
                                               directory_entry_point: int)\
            -> None:
        first_clus_hi = value >> 16
        first_clus_lo = value & 0xFFFF

        self.file_handler.seek(directory_entry_point + 20)
        self.file_handler.write_int(first_clus_hi, 2)

        self.file_handler.seek(directory_entry_point + 26)
        self.file_handler.write_int(first_clus_lo, 2)

    def get_indexed_entry(self,
                          cluster_number: int) -> IndexedEntryInfo or None:
        if cluster_number in self.indexed_table:
            return self.indexed_table[cluster_number]
        return None
