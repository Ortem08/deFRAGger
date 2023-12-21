import argparse
from random import Random
from sys import stderr

from FileHandler import FileHandler
from FatExtensions import get_info_about_fragmentation
from DirectoryParser import DirectoryParser
from FatParser import parse_fat
from Defragger import Defragger
from ErrorHandler import ErrorHandler
from ErrorCreator import ErrorCreator
from FileSystem import FileSystem
from Fragger import Fragger


def error_handler(file_system: FileSystem, error_handler: ErrorHandler):
    if len(error_handler.different_clusters) != 0:
        print("Таблицы FAT различаются", file=stderr)
        fat_nums = [i for i in range(file_system.get_fat_handler().fat_entity.BPB_NumFATs)]
        correct_fat = -1
        while correct_fat == -1:
            print(f"Выберете номер правильной таблицы FAT ({fat_nums}): ", end='')
            correct_fat = int(input())

        error_handler.repair_differences_fats(correct_fat)
        print("Таблицы исправлены", file=stderr)
        file_system.fat_handler.file_handler.close()
        raise SystemExit

    if len(error_handler.looped_files) != 0:
        print("Некоторые файлы зациклены: " + str([i.directory_entry_info.name for i in error_handler.looped_files]), file=stderr)

        error_handler.repair_looped_files()
        error_handler.clear_fat_table(file_system.get_indexed_fat_table())

        print("Зацикленные файлы удалены: " + str(error_handler.unused_clusters), file=stderr)
        file_system.fat_handler.file_handler.close()
        raise SystemExit

    if len(error_handler.intersecting_files) != 0:
        list_files = []
        for intersecting_files in error_handler.intersecting_files:
            all_files = ', '.join(list(map(lambda x: x.directory_entry_info.name, intersecting_files)))
            list_files.append(f'{intersecting_files[0].cur_cluster}: [{all_files}]')

        print("Некоторые файлы пересекаются: " + ', '.join(list_files), file=stderr)

        error_handler.repair_intersecting_files()
        error_handler.clear_fat_table(file_system.get_indexed_fat_table())

        print("Пересекающиеся файлы удалены: " +
              str(error_handler.unused_clusters), file=stderr)
        file_system.fat_handler.file_handler.close()
        raise SystemExit

    error_handler.clear_fat_table(file_system.get_indexed_fat_table())
    if len(error_handler.unused_clusters) != 0:
        print("Были удалены кластеры, не принадлежащие ни одному файлу: " + str(error_handler.unused_clusters),file=stderr)


def main(parsed_args):
    file_handler = FileHandler(parsed_args.path)

    file_system_of_image = parse_fat(file_handler)
    print(file_system_of_image.get_name_type_of_fat(), end='\n')

    error_handler(file_system_of_image, file_system_of_image.get_error_handler())

    if parsed_args.type_action == 'fragmentation':
        print(f'Fragmentation (BEFORE): ~{int(get_info_about_fragmentation(file_system_of_image.get_fat_handler()))}%')
        fragger = Fragger(file_system_of_image, file_handler, Random())
        fragger.fragmentate(1000)

    elif parsed_args.type_action == 'defragmentation':
        defragger = Defragger(file_system_of_image, file_handler)
        defragger.defragmentation()

    elif parsed_args.type_action == 'error_fat_table':
        error = ErrorCreator(DirectoryParser(file_system_of_image.get_fat_handler()), file_system_of_image)
        error.make_error_in_fat_table(parsed_args.fat_num)

    elif parsed_args.type_action == 'error_looped_file':
        error = ErrorCreator(DirectoryParser(file_system_of_image.get_fat_handler()), file_system_of_image)
        try:
            error.make_looped_file(parsed_args.folder)
        except ValueError as ex:
            print(ex.args[0], file=stderr)

    elif parsed_args.type_action == 'error_intersected_files':
        error = ErrorCreator(DirectoryParser(file_system_of_image.get_fat_handler()), file_system_of_image)
        try:
            error.make_intersecting_files(parsed_args.folder)
        except ValueError as error:
            print(error.args[0], file=stderr)

    print()
    print(f'Fragmentation: ~{int(get_info_about_fragmentation(file_system_of_image.get_fat_handler()))}%')

    file_handler.close()


class Argument:
    def __init__(self, path: str, type_action: str):
        self.path = path
        self.type_action = type_action


if __name__ == '__main__':
    args = Argument('Images/fat16_test.vhd', 'fragmentation')
    main(args)
    # parser = argparse.ArgumentParser()
    # parser.add_argument("path")
    # parser.add_argument("type_action", choices=["fragmentation",
    #                                             "defragmentation",
    #                                             "error_fat_table",
    #                                             "error_looped_file",
    #                                             "error_intersecting_files"])
    # parser.add_argument("-f", "--folder", type=str)
    # parser.add_argument("-n", "--fat_num", type=int)
    # parsed_args = parser.parse_args()
    # main(parsed_args)

