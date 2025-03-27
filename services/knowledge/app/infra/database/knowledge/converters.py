from app.schemas.division import DivisionSchema, SubdivisionSchema, DivisionType
from app.schemas.card import BusinessCardSchema
from app.infra.database.knowledge.models import Division, BusinessCard


def division_to_division_schema(division: Division) -> DivisionSchema:
    return DivisionSchema.model_validate(division)


def division_to_subdivision_schema(
    division: Division, *, subdivisions_count: int, files_count: int
) -> SubdivisionSchema:
    return SubdivisionSchema(
        id=division.id,
        name=division.name,
        path=division.path,
        type=DivisionType.division,
        subdivisions_count=subdivisions_count,
        files_count=files_count,
    )


def card_to_card_schema(card: BusinessCard) -> BusinessCardSchema:
    return BusinessCardSchema(
        id=card.id,
        name=card.name,
        description=card.description,
        materials=[m.external_id for m in card.materials],
    )
