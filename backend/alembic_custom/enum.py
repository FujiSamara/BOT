from alembic import op
import sqlalchemy as sa


def update_enum(old: tuple[str], new: tuple[str], name: str, table: str, column: str):
    """Updates enum."""
    old_type = sa.Enum(*old, name=name)
    new_type = sa.Enum(*new, name=name)
    tmp_type = sa.Enum(*new, name=f"_{name}")

    if len(old) > len(new):
        sa_column = sa.Column(column, old_type, nullable=False)
        tcr = sa.sql.table(table, sa_column)
        for record in old:
            if record not in new:
                op.execute(
                    tcr.update().where(tcr.c[column] == record).values({column: new[0]})
                )

    tmp_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        f"ALTER TABLE {table} ALTER COLUMN {column} TYPE _{name}"
        f" USING {column}::text::_{name}"
    )
    old_type.drop(op.get_bind(), checkfirst=False)
    new_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        f"ALTER TABLE {table} ALTER COLUMN {column} TYPE {name}"
        f" USING {column}::text::{name}"
    )
    tmp_type.drop(op.get_bind(), checkfirst=False)


def delete_enum(name: str):
    """Deletes enum."""
    sa.Enum(name=name).drop(op.get_bind(), checkfirst=False)
