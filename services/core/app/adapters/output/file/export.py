from datetime import datetime
from io import BytesIO
from xlsxwriter import Workbook

from app.contracts.clients import XlSXExporter
from app.schemas import SchemaT
from app import schemas
from app.infra.config import settings
from app.infra.database import models
from app.adapters.bot.kb import approval_status_dict


class XlSXWriterExporter(XlSXExporter):
    def export(self, data: list[SchemaT]) -> BytesIO:
        result = BytesIO()
        workbook = Workbook(result)
        worksheet = workbook.add_worksheet()

        headers: list[str] = []
        rows_width: list[int] = []

        for field_name in SchemaT.model_fields:
            if field_name not in self._exclude_columns:
                width = len(field_name)
                if field_name in self._aliases:
                    width = max(width, len(self._aliases[field_name]))
                rows_width.append(width)
                headers.append(field_name)

        worksheet.write_row(
            0,
            0,
            [
                self._aliases[header] if header in self._aliases else header
                for header in headers
            ],
        )  # Writes headers

        for index, elem in enumerate(data):
            vals = []
            for name_index, name in enumerate(headers):
                val = getattr(elem, name)
                formatted = self._format(val, name)
                vals.append(formatted)
                if len(formatted) > rows_width[name_index]:
                    rows_width[name_index] = len(formatted)

            worksheet.write_row(index + 1, 0, vals)  # Index + 1 (header row)

        # Sets columns width
        for index, row_width in enumerate(rows_width):
            worksheet.set_column(index, index, row_width)

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
