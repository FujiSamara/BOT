from abc import ABC, abstractmethod
from io import BytesIO
from typing import Callable, TypeAlias

from app.schemas import BaseSchema


FormatValue: TypeAlias = Callable[[any], str]


class XlSXExporter(ABC):
    """Helper for building xlsx sheets."""

    def __init__(
        self,
        field_formatters: dict[str, FormatValue] = {},
        exclude_columns: list[str] = [],
        aliases: dict[str, str] = {},
    ):
        """
        :param field_formatters: Special formatters for fields
        (**column_name**=**formatter**). Overrides default type formatters.
        :param exclude_columns: Column names for exclude from worksheet.
        :param aliases: Aliases for column headers (**column_name**=**alias**).
        """
        self._field_formatters = field_formatters
        self._exclude_columns = exclude_columns
        self._aliases = aliases

    @abstractmethod
    def export(self, data: list[BaseSchema]) -> BytesIO:
        """Generates xlsx file.

        :return: Generated xlsx file in `BytesIO` representation.
        """
