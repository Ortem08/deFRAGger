import pytest
from FileHandler import FileHandler


class FileHandlerTests:
    def test_read_bytes(self):
        io_manager = FileHandler('test_io_manager')
        result = io_manager.read_bytes(1)
        assert b'5' == result

    def test_read_int(self):
        io_manager = FileHandler('test_io_manager')
        result = io_manager.read_int(1)
        assert 53 == result

    def test_jump_back_with_correct_value(self):
        io_manager = FileHandler('test_io_manager')
        io_manager.read_bytes(1)
        io_manager.jump_back(1)
        assert io_manager.pointer == 0
