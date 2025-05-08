from app.schemas.dish import (
    DishSchema,
    DishModifierSchema,
    DishMaterialsDTO,
    DishModifierGroupSchema,
)
from app.infra.database.dish.models import TTKProduct


def product_to_dish_schema(dish: TTKProduct, *, materials_count=0) -> DishSchema:
    return DishSchema(
        id=dish.id,
        title=dish.title,
        description=dish.description,
        image=dish.image,
        materials_count=materials_count,
    )


def modifier_to_modifier_schema(modifier: dict) -> DishModifierSchema:
    return DishModifierSchema.model_validate(modifier)


def materials_to_materials_dto(
    materials: list[int], video: int | None
) -> DishMaterialsDTO:
    return DishMaterialsDTO(materials=materials, video=video)


def modifier_group_to_modifier_group_schema(group) -> DishModifierGroupSchema:
    title = group["title"]
    modifier_dict: dict = group["modifiers"]
    return DishModifierGroupSchema(
        title=title,
        modifiers=[
            DishModifierSchema.model_validate(modifier)
            for modifier in modifier_dict.values()
        ],
    )
