from common.schemas.base import BaseSchema


class ReceptSchema(BaseSchema):
    pass


class DishSchema(BaseSchema):
    id: int
    name: str


class DishOutSchema(DishSchema):
    pass


# TODO: schemas for dish
