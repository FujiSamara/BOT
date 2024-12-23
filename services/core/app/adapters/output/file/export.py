from datetime import datetime
from io import BytesIO
from typing import Generator, Type
from xlsxwriter import Workbook

from app.contracts.clients import XlSXExporter, FormatValue
from app import schemas
from app.infra.config import settings
from app.infra.database import models
from app.adapters.bot.kb import approval_status_dict


class XlSXWriterExporter(XlSXExporter):
    def __init__(self, field_formatters, exclude_columns, aliases):
        super().__init__(field_formatters, exclude_columns, aliases)

        self._type_formatters: dict[Type, FormatValue] = {
            schemas.WorkerSchema: self._format_worker,
            schemas.DepartmentSchema: self._format_department,
            schemas.ExpenditureSchema: self._format_expenditure,
            datetime: self._format_datetime,
            models.ApprovalStatus: self._format_approval_status,
            schemas.PostSchema: self._format_post,
            float: self._format_float,
        }

    def _get_headers(
        self, rows: list[schemas.BaseSchema | dict], dumped: bool = False
    ) -> list[str]:
        result = []
        row = rows[0]

        if not dumped:
            row = row.model_fields

        for field_name in row:
            if field_name not in self._exclude_columns:
                result.append(field_name)

        return result

    def _format_rows(
        self,
        rows: list[schemas.BaseSchema | dict],
        headers: list[str],
        dumped: bool = False,
    ) -> Generator[list[str], None, None]:
        result = []
        for elem in rows:
            vals = []
            for name in headers:
                val = elem[name] if dumped else getattr(elem, name)
                formatted = self._format(val, name)
                vals.append(formatted)

            yield vals

        return result

    def export(
        self, rows: list[schemas.BaseSchema], with_dump: bool = False
    ) -> BytesIO:
        result = BytesIO()
        workbook = Workbook(result)
        worksheet = workbook.add_worksheet()

        if len(rows) == 0:
            workbook.close()
            result.seek(0)
            return result

        data = [row.model_dump() for row in rows] if with_dump else rows

        headers: list[str] = self._get_headers(data, with_dump)
        rows_width: list[int] = []

        for field_name in headers:
            width = len(field_name)
            if field_name in self._aliases:
                width = max(width, len(self._aliases[field_name]))
            rows_width.append(width)

        worksheet.write_row(
            0,
            0,
            [
                self._aliases[header] if header in self._aliases else header
                for header in headers
            ],
        )  # Writes headers

        formatted_data = self._format_rows(data, headers, with_dump)

        for index, row in enumerate(formatted_data):
            for name_index in range(len(headers)):
                if len(row[name_index]) > rows_width[name_index]:
                    rows_width[name_index] = len(row[name_index])

            worksheet.write_row(index + 1, 0, row)  # Index + 1 (header row)

        # Sets columns width
        for index, row_width in enumerate(rows_width):
            worksheet.set_column(index, index, row_width + 2)

        workbook.close()
        result.seek(0)

        return result

    def _format(self, value: any, column_name: str) -> str:
        """Formats `value`, used exist formatter for each type."""
        formatter = None

        if type(value) in self._type_formatters:
            formatter = self._type_formatters[type(value)]

        if column_name in self._field_formatters:
            formatter = self._field_formatters[column_name]

        return formatter(value) if formatter else str(value)

    def _format_worker(self, value: schemas.WorkerSchema) -> str:
        return f"{value.l_name} {value.f_name} {value.o_name}"

    def _format_department(self, value: schemas.DepartmentSchema) -> str:
        return f"{value.name}"

    def _format_expenditure(self, value: schemas.ExpenditureSchema) -> str:
        return f"{value.name}"

    def _format_datetime(self, value: datetime) -> str:
        return value.strftime(settings.date_format)

    def _format_approval_status(self, value: models.ApprovalStatus) -> str:
        return approval_status_dict[value]

    def _format_post(self, value: schemas.PostSchema) -> str:
        return value.name

    def _format_float(self, value: float) -> str:
        return str(round(value, 2))
