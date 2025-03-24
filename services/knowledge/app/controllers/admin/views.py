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

    form_columns = [models.Division.name, models.Division.path]

    column_details_list = column_list


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


class DishVisionView(ModelView, model=models.DishDivision):
    can_export = False
    can_edit = True
    can_delete = True
    can_create = True
    name_plural = "Бизнес карты"
    name = "Карта"

    column_list = [
        models.DishDivision.id,
        models.DishDivision.dish_id,
        models.DishDivision.division_id,
    ]

    form_columns = [
        models.DishDivision.dish_id,
        models.DishDivision.division_id,
    ]

    column_details_list = column_list
