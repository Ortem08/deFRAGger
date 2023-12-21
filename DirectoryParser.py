from Attribute import Attribute
from DirectoryEntity import DirectoryEntity
from DirectoryEntryInfo import DirectoryEntryInfo
from DirectoryEntryLongNameInfo import DirectoryEntryLongNameInfo
from FatHandler import FatHandler


class DirectoryParser:
    EMPTY_RECORD = 0xe5
    END_OF_RECORDS = 0x00
    ENTRY_SIZE = 32

    def __init__(self, fat_handler: FatHandler):
        self.file_handler = fat_handler.file_handler
        self.fat_handler = fat_handler
        self.fat_entity = fat_handler.fat_entity

    def get_directory_entity(self, directory_entry_cluster_number: int) -> DirectoryEntity:
        current_fat_pointer = directory_entry_cluster_number
        directory_entity = None

        while True:
            new_directory_entity = self.get_directory_entity_in_one_cluster(
                current_fat_pointer,
                self.fat_entity.get_entries_count_in_directory_cluster()
            )

            if directory_entity is None:
                directory_entity = new_directory_entity
            else:
                directory_entity = directory_entity.merge(new_directory_entity)
            current_fat_pointer = self.fat_handler.get_cluster_value_in_main_fat(current_fat_pointer)
            if self.fat_handler.is_final_cluster(current_fat_pointer):
                break

        return directory_entity

    def get_fat16_root_directory_entity(self) -> DirectoryEntity:
        """
        Получение информации о корневой директории FAT 16
        :return: DirectoryInfo
        """
        return self._get_dir_info_in_one_cluster(self.fat_entity.first_root_dir_sec, self.fat_entity.BPB_RootEntCnt)

    def get_directory_entity_in_one_cluster(self, directory_cluster_number: int, max_entries_number: int) -> DirectoryEntity:
        entry_point = self.fat_handler.get_cluster_entry_in_data(directory_cluster_number)
        return self._get_dir_info_in_one_cluster(entry_point, max_entries_number)

    def _get_dir_info_in_one_cluster(self,
                                     directory_entry_pointer: int,
                                     max_entries_number: int) -> DirectoryEntity:
        current_pointer = directory_entry_pointer

        entries_with_long_name = {}
        entries = []

        for i in range(max_entries_number):
            entry = self.parse_entry(current_pointer)

            self.file_handler.seek(current_pointer)
            type_entry = self.file_handler.read_int(1)

            current_pointer = current_pointer + DirectoryParser.ENTRY_SIZE

            if type_entry == DirectoryParser.EMPTY_RECORD:
                continue
            elif type_entry == DirectoryParser.END_OF_RECORDS:
                break

            if isinstance(entry, DirectoryEntryInfo):
                if len(entries_with_long_name) != 0:
                    keys = [e.value for e in entries_with_long_name.values()]
                    keys.sort()

                    entry.name = ''.join([entries_with_long_name[v].get_full_name() for v in keys])
                    cut = entry.name.find('\x00')
                    if cut != -1:
                        entry.name = entry.name[:cut]

                    entries_with_long_name = {}
                else:
                    print(entry.name)
                    entry.name = entry.name.decode()
                entries.append(entry)
            else:
                entries_with_long_name[entry.value] = entry

        return DirectoryEntity(entries)

    def parse_entry(self, input_recording_point: int) -> DirectoryEntryInfo or DirectoryEntryLongNameInfo:
        self.file_handler.seek(input_recording_point + 11)
        attribute = Attribute.attribute_parser(self.file_handler.read_int(1))

        self.file_handler.seek(input_recording_point)
        if attribute.is_long_name():
            Ord = self.file_handler.read_int(1)
            Name1 = self.file_handler.read_bytes(10)
            self.file_handler.skip(2)
            Chksum = self.file_handler.read_int(1)
            Name2 = self.file_handler.read_bytes(12)
            self.file_handler.skip(2)
            Name3 = self.file_handler.read_bytes(4)
            return DirectoryEntryLongNameInfo(Ord, Name1, Chksum, Name2, Name3)
        else:
            name = self.file_handler.read_bytes(11)
            attribute = self.file_handler.read_int(1)
            self.file_handler.skip(8)
            FstClusHI = self.file_handler.read_int(2)
            self.file_handler.skip(4)
            FstClusLO = self.file_handler.read_int(2)
            self.file_handler.skip(4)
            return DirectoryEntryInfo(name,
                                      attribute,
                                      ((FstClusHI << 16) + FstClusLO if FstClusHI != 0 else FstClusLO),
                                      input_recording_point)

    def find_empty_entry_in_directory(self, directory_entry_point: int) -> int or None:
        current_point = directory_entry_point

        for i in range(self.fat_entity.get_entries_count_in_directory_cluster()):
            self.file_handler.seek(current_point)
            type_entry = self.file_handler.read_int(1)

            if type_entry == DirectoryParser.EMPTY_RECORD or type_entry == DirectoryParser.END_OF_RECORDS:
                return current_point

            current_point += DirectoryParser.ENTRY_SIZE

        return None

    def create_entry_in_directory(self, entry_point: int, name: str, attribute: int, first_cluster: int) -> None:
        if len(name) > 11:
            name = name[:11]
        elif len(name) < 11:
            name = '{:<11}'.format(name)
        name = name.upper()

        self.file_handler.seek(entry_point)
        self.file_handler.write_bytes(name.encode())
        self.file_handler.write_int(attribute, 1)
        self.file_handler.seek(entry_point + 20)
        self.file_handler.write_int(first_cluster >> 16, 2)
        self.file_handler.seek(entry_point + 26)
        self.file_handler.write_int(first_cluster & 0xFFFF, 2)
        self.file_handler.write_int(1, 4)

    def delete_entry_in_directory(self, entry_point: int) -> None:
        """
        Удаляет запись в директории
        :param entry_point: входная точка записи
        :return: None
        """
        self.file_handler.seek(entry_point)
        self.file_handler.write_int(self.EMPTY_RECORD, 1)
