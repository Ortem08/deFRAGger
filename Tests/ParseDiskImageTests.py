import pytest

import FatParser
from FatType import FatType
from FileHandler import FileHandler


class TestParseDiskImage:
    def test_fat16_recognition(self):
        io_manager = FileHandler('../Images/fat16_test.vhd')
        file_system = FatParser.parse_fat(io_manager)
        assert file_system.get_type_of_fat() == FatType.fat16
