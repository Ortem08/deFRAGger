from Attribute import Attribute


class DirectoryEntryInfo:
    def __init__(self, name,
                 attribute: int or None,
                 first_cluster_number: int,
                 entry_point: int):
        self.name = name
        self.attribute = Attribute.attribute_parser(attribute)
        self.first_cluster_number = first_cluster_number
        self.entry_point = entry_point
