from DirectoryEntryInfo import DirectoryEntryInfo


class DirectoryEntity:
    def __init__(self, entries_list: list):
        self.entries_list = entries_list

    def get_subdirectories_entries(self) -> list[DirectoryEntryInfo]:
        return self.get_sublist_by_rule(lambda e: e.attribute.is_directory)

    def get_subfiles_entries(self) -> list[DirectoryEntryInfo]:
        return self.get_sublist_by_rule(lambda e: not e.attribute.is_directory)

    def get_sublist_by_rule(self, rule) -> list[DirectoryEntryInfo]:
        elements = []
        for entry in self.entries_list:
            if rule(entry):
                elements.append(entry)
        return elements

    def merge(self, other_directory_entity: 'DirectoryEntity'):
        return DirectoryEntity(self.entries_list +
                               other_directory_entity.entries_list)
