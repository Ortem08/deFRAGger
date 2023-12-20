from FileHandler import FileHandler
from FatType import FatType

class FatEntity:
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler

        # Инструкция перехода на программу загрузки
        self.BS_jmpBoot = file_handler.read_int(3)
        # Аббревиатура операционной системы
        self.BS_OEMName = file_handler.read_int(8)
        # Число байтов в секторе - 512, 1024, 2048, 4096
        self.BPB_BytsPerSec = file_handler.read_int(2)
        # Число секторов в кластере
        self.BPB_SecPerClus = file_handler.read_int(1)
        # Размер системной области (включая этот сектор)
        self.BPB_ResvdSecCnt = file_handler.read_int(2)
        # Количество таблиц FAT на диске
        self.BPB_NumFATs = file_handler.read_int(1)
        # Для FAT16 - число 32-б элементов корневой директории. Для FAT32 - 0
        self.BPB_RootEntCnt = file_handler.read_int(2)
        # Кол-во секторов на диске (старое)
        self.BPB_TotSec16 = file_handler.read_int(2)
        # чето скучное
        self.BPB_Media = file_handler.read_int(1)
        # Кол-во секторов одного FAT для FAT16, для FAT32 - 0
        self.BPB_FATSz16 = file_handler.read_int(2)
        # какойто трек
        self.BPB_SecPerTrk = file_handler.read_int(2)
        # головы
        self.BPB_NumHeads = file_handler.read_int(2)
        # чето спрятанное
        self.BPB_HiddSec = file_handler.read_int(4)
        # Кол-во секторов на диске (новое)
        self.BPB_TotSec32 = file_handler.read_int(4)

        # Кол-во секторов одного FAT для FAT32, для FAT16 - 0
        self.BPB_FATSz32 = self.read_FATSz32()

        FATSz = self.BPB_FATSz16 if self.BPB_FATSz16 != 0 \
            else self.BPB_FATSz32


        #Количество секторов, занимаемых корневой директорией
        self._RootDirSectorsCnt = ((self.BPB_RootEntCnt * 32) + (self.BPB_BytsPerSec - 1)) // self.BPB_BytsPerSec

        # Начало дата сектора, первый сектор второго кластера
        self.first_data_sector = self.BPB_ResvdSecCnt + self._RootDirSectorsCnt + (self.BPB_NumFATs * FATSz)

        self.clusters_count = self._get_count_of_clusters()
        self.fat_type = self._get_fat_type()

        if self.fat_type == FatType.fat16:
            self._parse_fat16_structure(file_handler)
        else:
            self._parse_fat32_structure(file_handler)

        self.first_root_dir_sec = self._get_first_root_dir_sec()


    def read_FATSz32(self):
        FATSz32 = 0
        if self.BPB_RootEntCnt == 0:
            FATSz32 = self.file_handler.read_int(4)
            # Сохраняем целостность данных
            self.file_handler.pointer -= 4
            self.file_handler.file.seek(self.file_handler.pointer)
        return FATSz32

    def _parse_fat16_structure(self, file_handler: FileHandler):
        # Тип - int 0x13. 0x00 для дискет, 0x80 для жёстких дисков. Системная переменная
        self.BS_DrvNum = file_handler.read_int(1)
        # Используется Windows NT
        self.BS_Reserved1 = file_handler.read_int(1)
        # Байт подписи, который указывает, есть ли в загрузочном секторе следующие три поля
        self.BS_bootSig = file_handler.read_int(1)
        self.BS_VolID = file_handler.read_int(4)
        self.BS_VolLab = file_handler.read_int(11)
        self.BS_FilSysType = file_handler.read_int(8)

    def _parse_fat32_structure(self, file_handler: FileHandler):
        self.BPB_FATSz32 = file_handler.read_int(4)
        self.BPB_ExtFlags = file_handler.read_int(2)
        self.BPB_FSVer = file_handler.read_int(2)
        # Номер первого кластера корневой директории
        self.BPB_RootClus = file_handler.read_int(4)
        self.BPB_FSInfo = file_handler.read_int(2)
        self.BPB_BkBootSec = file_handler.read_int(2)
        self.BPB_Reserved = file_handler.read_int(12)
        self.BS_DrvNum = file_handler.read_int(1)
        self.BS_Reserved1 = file_handler.read_int(1)
        self.BS_BootSig = file_handler.read_int(1)
        self.BS_VolID = file_handler.read_int(4)
        self.BS_VolLab = file_handler.read_int(11)
        self.BS_FilSysType = file_handler.read_int(8)

    def _get_first_root_dir_sec(self):
        if self.fat_type == FatType.fat32:
            return (self.first_data_sector + (
                        self.BPB_RootClus - 2) * self.BPB_SecPerClus) * self.BPB_BytsPerSec
        else:
            return (self.BPB_ResvdSecCnt + (
                        self.BPB_NumFATs * self.BPB_FATSz16)) * self.BPB_BytsPerSec

    def _get_count_of_clusters(self):
        if self.BPB_TotSec16 != 0:
            tot_sec = self.BPB_TotSec16
        else:
            tot_sec = self.BPB_TotSec32

        data_sec = tot_sec - self.first_data_sector

        return data_sec // self.BPB_SecPerClus

    def _get_fat_type(self):
        if self.clusters_count <= 0:
            raise ValueError("Incorrect Image. Count of clusters: " + str(
                self.clusters_count))
        elif self.clusters_count < 65525:
            fat_type = FatType.fat16
        else:
            fat_type = FatType.fat32
        return fat_type

    def get_count_entries_in_dir_cluster(self):
        return self.BPB_BytsPerSec * self.BPB_SecPerClus // 32

    def get_bytes_per_cluster(self):
        return self.BPB_BytsPerSec * self.BPB_SecPerClus

    @classmethod
    def get_in_bytes(cls, value: int):
        return int.to_bytes(value, (value.bit_length() + 7) // 8, 'little')

    @classmethod
    def get_in_hex(cls, value: int):
        val = FatEntity.get_in_bytes(value).hex()
        return val if val != '' else '0'


