from FatEntity import FatEntity
from FatType import FatType
from FatTypeExtensions import FatTypeExtensions
from FileHandler import FileHandler


class FatHandler:
    VALUE_MASK_FAT32 = 0x0FFFFFFF
    MINIMAL_END_CLUSTER_FAT16 = 0xFFF8
    MINIMAL_END_CLUSTER_FAT32 = 0x0FFFFFF8
    BAD_CLUSTER_FAT16 = 0xFFF7
    BAD_CLUSTER_FAT32 = 0x0FFFFFF7
    LENGTH_CLUSTER_FAT16 = 2
    LENGTH_CLUSTER_FAT32 = 4
    END_CLUSTER_IN_WIN_FAT_16 = 0xFFFF
    END_CLUSTER_IN_WIN_FAT_32 = 0x0FFFFFFF

    def __init__(self, fat_entity: FatEntity, file_handler: FileHandler):
        self.fat_type = fat_entity.fat_type
        self.fat_entity = fat_entity
        self.file_handler = file_handler

        if self.fat_type == FatType.fat16:
            self.end_cluster = FatHandler.MINIMAL_END_CLUSTER_FAT16
            self.bad_cluster = FatHandler.BAD_CLUSTER_FAT16
        else:
            self.end_cluster = FatHandler.MINIMAL_END_CLUSTER_FAT32
            self.bad_cluster = FatHandler.BAD_CLUSTER_FAT32

    def get_cluster_entry_in_fat(self, cluster: int, table_number: int) -> int:
        if self.fat_entity.BPB_FATSz16 != 0:
            fat_sz = self.fat_entity.BPB_FATSz16
        else:
            fat_sz = self.fat_entity.BPB_FATSz32

        if self.fat_type == FatType.fat16:
            fat_offset = cluster * FatHandler.LENGTH_CLUSTER_FAT16
        else:
            fat_offset = cluster * FatHandler.LENGTH_CLUSTER_FAT32

        result = ((self.fat_entity.BPB_ResvdSecCnt + table_number * fat_sz)
                  * self.fat_entity.BPB_BytsPerSec + fat_offset)

        return result

    def get_cluster_entry_in_data(self, cluster: int) -> int:
        first_sector = (self.fat_entity.first_data_sector +
                        (cluster - 2) * self.fat_entity.BPB_SecPerClus)
        entry = first_sector * self.fat_entity.BPB_BytsPerSec
        return entry

    def get_cluster_value_in_fat(self, cluster_number: int, table_number: int) -> int:
        entry = self.get_cluster_entry_in_fat(cluster_number, table_number)
        self.file_handler.seek(entry)
        fat_cluster = self.file_handler.read_int(FatTypeExtensions.fat_entry_length[self.fat_type])

        if self.fat_type == FatType.fat32:
            fat_cluster = fat_cluster & FatHandler.VALUE_MASK_FAT32

        return fat_cluster

    def get_cluster_value_in_main_fat(self, n: int) -> int:
        return self.get_cluster_value_in_fat(n, 0)

    def is_end_cluster(self, fat_cluster_value: int) -> bool:
        return fat_cluster_value >= self.end_cluster

    def is_bad_cluster(self, fat_cluster_value: int) -> bool:
        return fat_cluster_value == self.bad_cluster

    def write_cluster_value_in_all_tables(self, value: int, cluster: int) -> None:
        for i in range(self.fat_entity.BPB_NumFATs):
            self.write_cluster_value_in_fat(value, cluster, i)

    def write_cluster_value_in_fat(self, value: int, cluster: int, fat_number: int) -> None:
        entry = self.get_cluster_entry_in_fat(cluster, fat_number)
        length = self.LENGTH_CLUSTER_FAT16 if \
            self.fat_entity.fat_type == FatType.fat16 else \
            self.LENGTH_CLUSTER_FAT32
        self.file_handler.seek(entry)
        self.file_handler.write_int(value, length)

    def get_cluster_value_in_data(self, cluster: int) -> bytes:
        entry = self.get_cluster_entry_in_data(cluster)
        bytes_len = self.fat_entity.get_bytes_per_cluster()

        self.file_handler.seek(entry)
        return self.file_handler.read_bytes(bytes_len)

    def write_cluster_value_in_data(
            self,
            value: bytes,
            cluster: int) -> None:

        entry = self.get_cluster_entry_in_data(cluster)

        self.file_handler.seek(entry)
        self.file_handler.write_bytes(value)
