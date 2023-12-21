from DirectoryEntity import DirectoryEntity
from DirectoryEntryInfo import DirectoryEntryInfo
from DirectoryParser import DirectoryParser
from FatType import FatType
from IndexedEntryInfo import IndexedEntryInfo


class FatIndexer:
    def __init__(self, directory_parser: DirectoryParser):
        self.directory_parser = directory_parser
        self.fat_entity = directory_parser.fat_entity
        self.indexed_table = {}
        self.index_table()

    def get_full_indexed_table(self) -> dict[int: list[IndexedEntryInfo]]:
        return self.indexed_table

    def get_correct_indexed_table(self) -> dict[int: IndexedEntryInfo]:
        result = {}
        for i in self.indexed_table:
            result[i] = self.indexed_table[i][0]
        return result

    def index_table(self):
        if self.fat_entity.fat_type == FatType.fat16:
            root_directory = self.directory_parser.get_fat16_root_directory_entity()
        else:
            root_directory = self.index_and_get_directory(
                self.fat_entity.BPB_RootClus,
                DirectoryEntryInfo('\\', None, self.fat_entity.BPB_RootClus, -1)
            )

        stack = [root_directory]
        while len(stack) != 0:
            current_directory = stack.pop()

            if current_directory is None:
                print(stack)

            for subfile_entry in current_directory.get_subfiles_entries():
                self.index_whole_file(subfile_entry.first_cluster_number, subfile_entry)

            for subdirectory_entry in current_directory.get_subdirectories_entries():
                if subdirectory_entry.name.strip() != '.' and subdirectory_entry.name.strip() != '..':
                    subdirectory = self.index_and_get_directory(subdirectory_entry.first_cluster_number, subdirectory_entry)
                    if subdirectory is not None:
                        stack.append(subdirectory)

    def index_and_get_directory(self, first_directory_cluster_number: int, directory_entry: DirectoryEntryInfo) -> DirectoryEntity:
        """
        Получение полной информации о директории, и индексировании этой директории
        :param first_directory_cluster_number: номер первого кластера директории в таблице FAT
        :param directory_entry: информация о записи в директории
        :return: DirectoryEntity
        """
        fat_cluster_value = first_directory_cluster_number
        last_cluster = None
        directory_entity = None
        while True:
            new_directory_entity = self.directory_parser.get_directory_entity_in_one_cluster(fat_cluster_value,
                                                                                             self.fat_entity.get_entries_count_in_directory_cluster())
            if self.index_cluster(first_directory_cluster_number,
                                  last_cluster,
                                  directory_entry,
                                  True):
                break

            if directory_entity is None:
                directory_entity = new_directory_entity
            else:
                directory_entity = directory_entity.merge(new_directory_entity)

            last_cluster = fat_cluster_value
            fat_cluster_value = self.directory_parser.fat_handler.get_cluster_value_in_main_fat(fat_cluster_value)
            if self.directory_parser.fat_handler.is_final_cluster(fat_cluster_value):
                break

        return directory_entity

    def index_whole_file(self, first_cluster_number: int, directory_entry: DirectoryEntryInfo) -> None:
        """
        Индексирование всего файла
        :param first_cluster_number: номер первого кластера файла
        :param directory_entry: информация о записи в директории
        :return: None
        """
        fat_cluster_value = first_cluster_number
        last_cluster = None
        while True:
            if self.index_cluster(fat_cluster_value, last_cluster, directory_entry, False):
                break
            last_cluster = fat_cluster_value
            fat_cluster_value = self.directory_parser.fat_handler.get_cluster_value_in_main_fat(fat_cluster_value)
            if self.directory_parser.fat_handler.is_final_cluster(fat_cluster_value):
                break

    def index_cluster(self,
                      cluster_number: int,
                      last_cluster: int or None,
                      directory_entry: DirectoryEntryInfo,
                      is_directory: bool) -> bool:
        """
        Индексирование кластера
        :param cluster_number: номер кластера
        :param directory_entry: информация о записи в директории
        :param is_directory: является ли кластер частью директории
        :return: True, если требуется завершить дальнейшее индексирование файла, False - в противном случае
        """
        if cluster_number not in self.indexed_table:
            self.indexed_table[cluster_number] = []

        has_loop = False

        for indexed_entry in self.indexed_table[cluster_number]:
            if indexed_entry.directory_entry_info.name == directory_entry.name:
                has_loop = True

        self.indexed_table[cluster_number].append(IndexedEntryInfo(directory_entry, cluster_number, last_cluster, is_directory))

        is_next_cluster_bad = False
        fat_handler = self.directory_parser.fat_handler

        if fat_handler.is_bad_cluster(fat_handler.get_cluster_value_in_main_fat(cluster_number)):
            is_next_cluster_bad = True

        return has_loop or is_next_cluster_bad
