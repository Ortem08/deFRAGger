class DirectoryEntryLongNameInfo:
    """
    Получение информации о записи в директории являющаяся частью длинного имени
    """
    def __init__(self,
                 value: int,
                 name1: bytes,
                 check_sum: int,
                 name2: bytes,
                 name3: bytes):
        self.value = value
        self.names = [name1, name2, name3]
        self.check_sum = check_sum

    def get_full_name(self):
        return b''.join(self.names).decode('utf-16')
