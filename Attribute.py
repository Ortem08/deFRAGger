class Attribute:
    def __init__(self,
                 is_archive: bool,
                 is_directory: bool,
                 is_volume: bool,
                 is_system: bool,
                 is_hidden: bool,
                 is_read_only: bool):
        self.is_archive = is_archive
        self.is_directory = is_directory
        self.is_volume_id = is_volume
        self.is_system = is_system
        self.is_hidden = is_hidden
        self.is_read_only = is_read_only

    def is_long_name(self) -> bool:
        return (self.is_read_only
                and self.is_hidden
                and self.is_system
                and self.is_volume_id
                and not self.is_directory
                and not self.is_archive)

    def is_directory(self) -> bool:
        return self.is_directory

    @staticmethod
    def attribute_parser(attribute: int or None) -> 'Attribute' or None:
        if attribute is None:
            return attribute

        return Attribute(attribute & 0x20 == 32,
                         attribute & 0x10 == 16,
                         attribute & 0x08 == 8,
                         attribute & 0x04 == 4,
                         attribute & 0x02 == 2,
                         attribute & 0x01 == 1)
