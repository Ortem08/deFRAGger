class DirectoryEntryInfo:
    def __init__(self, name: str, attr: int or None, first_cluster_num: int, entry_point: int):
        self.name = name
        self.attr = attribute_parser(attr)
        self.first_cluster_num = first_cluster_num
        self.entry_point = entry_point
