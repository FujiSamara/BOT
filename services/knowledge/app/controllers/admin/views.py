from sqladmin import ModelView

from app.infra.database.knowledge import models


class DivisionView(ModelView, model=models.Division):
    can_export = False
    can_edit = True
    can_delete = True
    can_create = True
    name_plural = "Разделы"
    name = "Раздел"

    column_list = [
        models.Division.id,
        models.Division.name,
        models.Division.path,
    ]

    form_columns = [models.Division.path]

    column_details_list = column_list

    def on_model_change(self, data, model, is_created, request):
        path_end = data["path"].split("/")[-1]
        data["name"] = path_end
        return super().on_model_change(data, model, is_created, request)


class BusinessCardView(ModelView, model=models.BusinessCard):
    can_export = False
    can_edit = True
    can_delete = True
    can_create = True
    name_plural = "Бизнес карты"
    name = "Карта"

    column_list = [
        models.BusinessCard.id,
        models.BusinessCard.name,
        models.BusinessCard.description,
        models.BusinessCard.division,
    ]

    form_columns = [
        models.BusinessCard.name,
        models.BusinessCard.division,
        models.BusinessCard.description,
    ]

    column_details_list = column_list

    form_ajax_refs = {
        "division": {
            "fields": ("name",),
            "order_by": "id",
        },
    }


class DishDisionView(ModelView, model=models.DishDivision):
    can_export = False
    can_edit = True
    can_delete = True
    can_create = True

    column_list = [
        models.DishDivision.id,
        models.DishDivision.dish_id,
        models.DishDivision.division_id,
    ]

    form_columns = [
        models.DishDivision.dish_id,
        models.DishDivision.division,
    ]

    column_details_list = column_list
