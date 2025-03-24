from app.schemas.division import DivisionSchema
from app.schemas.card import BusinessCardSchema
from app.infra.database.knowledge.models import Division, BusinessCard


def division_to_division_schema(division: Division) -> DivisionSchema:
    return DivisionSchema.model_validate(division)


def card_to_card_schema(card: BusinessCard) -> BusinessCardSchema:
    return BusinessCardSchema(
        id=card.id,
        name=card.name,
        description=card.description,
        materials=[m.external_id for m in card.materials],
    )
