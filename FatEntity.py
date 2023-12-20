from FileHandler import FileHandler


class FatEntity:
    def __init__(self, file_handler: FileHandler):
        self.file_handler = file_handler
        #фрагментатор, внесение ошибок
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
