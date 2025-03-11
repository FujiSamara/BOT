from sqladmin import ModelView

import app.infra.database.models as models


class FileView(ModelView, model=models.File):
    can_export = False
    can_edit = True
    can_delete = True
    can_create = False
    name_plural = "Files"

    column_list = [
        models.File.id,
        models.File.name,
        models.File.ext,
        models.File.key,
        models.File.bucket,
        models.File.size,
        models.File.created,
        models.File.confirmed,
    ]

    form_columns = [models.File.confirmed]

    column_details_list = column_list
