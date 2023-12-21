class FileHandler:
    def __init__(self, filename):
        self.file = None
        self.pointer = 0
        self.open(filename)

    def __del__(self):
        self.file.close()

    def open(self, filename):
        self.file = open(filename, 'rb+')

    def close(self):
        self.file.close()

    def skip(self, count: int):
        self.file.seek(self.file.tell() + count)

    def seek(self, position: int):
        self.pointer = position
        self.file.seek(position)

    def read_bytes(self, count: int) -> bytes:
        self.pointer += count
        result = self.file.read(count)
        return result

    def read_int(self, count: int) -> int:
        file_bytes = self.read_bytes(count)
        result = int.from_bytes(file_bytes, 'little')
        return result

    def write_int(self, value: int, length: int):
        self.pointer += length
        self.file.write(int.to_bytes(value, length, 'little'))

    def write_bytes(self, value: bytes):
        self.pointer += len(value)
        self.file.write(value)
