from dataclasses import dataclass


@dataclass
class DuplicateOptions:

    columns: list
    keep: str = "first"
    case_sensitive: bool = True
    ignore_whitespace: bool = False

@dataclass
class MissingValueOptions:

    columns: list
    action: str
    method: str | None = None
    value: object = None


class DataCleaner:

    def clean_missing(self, dataframe, options):
        pass

    def find_duplicates(self, dataframe, options):
        pass

    def remove_duplicates(self, dataframe, options):
        pass