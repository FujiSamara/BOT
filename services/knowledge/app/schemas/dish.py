from common.schemas.base import BaseSchema
from common.schemas.file import FileLinkSchema


class DishSchema(BaseSchema):
    id: int
    title: str
    description: str
    image: str
    materials_count: int = 0


class IngredientSchema(BaseSchema):
    id: int
    title: str
    amount: float


class DishModifierGroupSchema(BaseSchema):
    title: str
    modifiers: list["DishModifierSchema"]


class DishModifierSchema(BaseSchema):
    id: int
    title: str
    ingredients: list[IngredientSchema]


class DishMaterialsDTO(BaseSchema):
    video: int | None
    materials: list[int]


class DishMaterialsSchema(BaseSchema):
    video: FileLinkSchema | None
    materials: list[FileLinkSchema]


class DishUpdateSchema(BaseSchema):
    video: int | None
