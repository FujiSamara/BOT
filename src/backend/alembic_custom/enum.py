from alembic import op
import sqlalchemy as sa


def update_enum(
    old: tuple[str],
    new: tuple[str],
    name: str,
    table_columns: dict[str, list],
):
    """Updates enum."""
    old_type = sa.Enum(*old, name=name)
    new_type = sa.Enum(*new, name=name)
    tmp_type = sa.Enum(*new, name=f"_{name}")

    # Createss temp type with new fields.
    tmp_type.create(op.get_bind(), checkfirst=False)

    # Temprorary changes old type to temp type
    for table in table_columns:
        for column in table_columns[table]:
            op.execute(
                f"ALTER TABLE {table} ALTER COLUMN {column} TYPE _{name}"
                f" USING {column}::text::_{name}"
            )

    # Deletes old type and create new type
    old_type.drop(op.get_bind(), checkfirst=False)
    new_type.create(op.get_bind(), checkfirst=False)

    # Changes temp type to new type
    for table in table_columns:
        for column in table_columns[table]:
            op.execute(
                f"ALTER TABLE {table} ALTER COLUMN {column} TYPE {name}"
                f" USING {column}::text::{name}"
            )

    # Deletes temp type
    tmp_type.drop(op.get_bind(), checkfirst=False)


def delete_enum(name: str):
    """Deletes enum."""
    sa.Enum(name=name).drop(op.get_bind(), checkfirst=False)
