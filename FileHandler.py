class FileHandler:
    def __init__(self, filename):
        self.file = None
        self.pointer = 0
        self.open(filename)

    def open(self, filename):
        self.file = open(filename, 'rb')

    def close(self):
        self.file.close()

    def skip(self, count: int):
        self.file.seek(self.file.tell() + count)

    def read_bytes(self, count: int) -> bytes:
        self.pointer += count
        result = self.file.read(count)
        return result

    def read_ints(self, count: int) -> [int]:
        file_bytes = self.read_bytes(count)
        result = int.from_bytes(file_bytes, 'little')
        return result
