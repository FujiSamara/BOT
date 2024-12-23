from io import BytesIO
from typing import Callable, Type
import typing
from abc import ABC
from sqlalchemy import (
    BinaryExpression,
    Result,
    Select,
    and_,
    or_,
    desc,
    select,
    func,
    cast,
    String,
)
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.infra.logging import logger
import app.infra.database.models as models
from app.infra.database.database import Base

from app import schemas

from app.contracts.clients import XlSXExporter


class Builder(ABC):
    """Base class for sqlalchemy based builder.

    - Note:
    Builder works inside session only.
    """

    name = "|BUILDER|"

    logger = logger

    def __init__(self, initial_select: Select, session: Session):
        """
        :param initial_query: Initially generated query for table `model_type` by `Session`.
        """
        entities = [
            item["entity"]
            for item in initial_select.column_descriptions
            if item["entity"] is not None and issubclass(item["entity"], Base)
        ]

        if not len(entities) == 1:
            for entity in entities:
                if entities[0] != entity:
                    self._warning("Requested query building with not one entity")
                    break

        self.select = initial_select
        self.session = session
        self._model_type = entities[0]

        # Schema to model dict
        self._schema_to_model: dict[Type[schemas.BaseSchema], Type[Base]] = {
            schemas.WorkerSchema: models.Worker,
            schemas.DepartmentSchema: models.Department,
            schemas.ExpenditureSchema: models.Expenditure,
            schemas.BidSchema: models.Bid,
            schemas.PostSchema: models.Post,
            schemas.BudgetRecordSchema: models.BudgetRecord,
            schemas.WorkTimeSchema: models.WorkTime,
        }

        # Model to schema dict
        self._model_to_schema: dict[Type[Base], Type[schemas.BaseSchema]] = {
            self._schema_to_model[schema]: schema for schema in self._schema_to_model
        }

    def all(self) -> list[schemas.BaseSchema]:
        """Returns all entries in database with `self.query`."""
        schema_type = self._model_to_schema[self._model_type]
        rows = self.session.execute(self.select).scalars().all()
        return [schema_type.model_validate(model) for model in rows]

    def count(self) -> int:
        """Returns count of all entries in database with `self.query`."""
        res: Result = self.session.execute(
            select(func.count()).select_from(self.select)
        )
        return res.scalar()

    def _warning(self, msg: str):
        """Logs `msg`."""
        self.logger.warning(f"{self.name} {msg}")

    def export(self, exporter: XlSXExporter) -> BytesIO:
        """Generates xlsx file with data from `Builder.all`.

        :return: Generated xlsx file in `BytesIO` representation.
        """
        data = self.all()
        return exporter.export(data)


class QueryBuilder(Builder):
    """Helper for building composite query.

    Important:
    1) Searching can applying for field inherit `schemas.BaseSchema` and simple field.
    Filtering can applying any field (`str`, `int`, etc...),
    but filtering can applying any deep query, for example `Dog.owner.name`.
    2) Searching supports groups, different groups handles by `or_` statement,
    terms inside group handles by `_and` statement.
    Filtering also supports groups, but  different groups handles by `and_` statement,
    terms inside group handles by `_or` statement.
    3) Searching use `ilike('%term%')` syntax.
    Filtering use `column == value` syntax.
    4) Order by can work with up level field (not Dog.owner.name, only Dow.owner).
    5) Order by can applying for field inherit `schemas.BaseSchema` and simple field.
    """

    name = "|QUERYBUILDER|"

    def __init__(self, initial_select: Select, session: Session):
        """
        :param initial_query: Initially generated query for table `model_type` by `Session`.
        """
        super().__init__(initial_select, session)

        # Order by builders.
        self._order_by_builders: dict[
            schemas.BaseSchema, Callable[[InstrumentedAttribute[any], bool], Select]
        ] = {
            schemas.WorkerSchema: self._order_by_worker,
            schemas.DepartmentSchema: self._order_by_department,
            schemas.ExpenditureSchema: self._order_by_expenditure,
        }

        # Search builders.
        self._search_builders: dict[
            schemas.BaseSchema,
            Callable[[str], Select],
        ] = {
            schemas.WorkerSchema: self._search_by_worker,
            schemas.DepartmentSchema: self._search_by_department,
            schemas.ExpenditureSchema: self._search_by_expenditure,
        }

    def apply(self, query_schema: schemas.QuerySchema):
        """
        Applies `query_schema` to query.

        **Instructions**:
        1) Date by
        2) Filter by
        3) Search by
        4) Order by
        """
        if query_schema.date_query:
            self._apply_date(query_schema.date_query)

        self._apply_filter(query_schema.filter_query)

        self._apply_search(query_schema.search_query)

        if query_schema.order_by_query:
            self._apply_order_by(query_schema.order_by_query)

    def _get_schema_column_type(
        self, schema_type: Type[schemas.BaseSchema], column_name: str
    ) -> Type:
        column_model_hint = typing.get_type_hints(schema_type)[column_name]

        column_model_type = None
        type_args = typing.get_args(column_model_hint)
        if len(type_args) > 0:
            column_model_type = typing.get_args(column_model_hint)[0]
        else:
            column_model_type = column_model_hint

        return column_model_type

    # region Order by
    def _apply_order_by(self, order_by_schema: schemas.OrderBySchema):
        """
        Applies `order_by_schema`.
        """
        column_name = order_by_schema.column
        is_desc = order_by_schema.desc
        model_type = self._model_type
        schema_type = self._model_to_schema[model_type]

        column_type = self._get_schema_column_type(schema_type, column_name)
        column = getattr(model_type, column_name)

        # If column is pydantic schema.
        if column_type in self._order_by_builders:
            builder = self._order_by_builders[column_type]
            self.select = builder(column, is_desc)
        # If column is simple type.
        elif not issubclass(column_type, schemas.BaseSchema):
            if is_desc:
                column = desc(column)
            self.select = self.select.order_by(column)
        # If column is schema with non implemented order by.
        else:
            self._warning(
                f"Attempt to order by non implemented method, column type: {column_type}"
            )

    def _order_by_worker(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Select:
        columns = [models.Worker.l_name, models.Worker.f_name, models.Worker.o_name]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.select.join(column).order_by(*columns)

    def _order_by_department(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Select:
        columns = [models.Department.name]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.select.join(column).order_by(*columns)

    def _order_by_expenditure(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Select:
        columns = [models.Expenditure.name, models.Expenditure.chapter]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.select.join(column).order_by(*columns)

    # endregion

    # region Search
    def _apply_search(
        self,
        search_query: list[schemas.SearchSchema],
    ):
        """
        Applies `search_query`.
        """
        search_clause = self._get_search_clause(self._model_type, search_query)
        if search_clause is not None:
            self.select = self.select.filter(search_clause)

    def _get_search_clause(
        self,
        model_type: Type[Base],
        search_schemas: list[schemas.SearchSchema],
    ) -> BinaryExpression[bool] | None:
        """Generates recursive search clause."""
        schema_type = self._model_to_schema[model_type]

        # Dict for all groups in current level.
        groups: dict[int, list[schemas.SearchSchema]] = {-1: []}
        for search_schema in search_schemas:
            for group in search_schema.groups:
                if group in groups:
                    groups[group].append(search_schema)
                else:
                    groups[group] = [search_schema]

            if len(search_schema.groups) == 0:
                groups[-1].append(search_schema)

        # Calcs clause for every group
        group_clauses = []
        for group_id in groups:
            group = groups[group_id]
            inside_group_clauses: list[BinaryExpression[bool]] = []

            for search_schema in group:
                column_name = search_schema.column
                term = search_schema.term

                search_clause: BinaryExpression[bool] = None

                # Type inference
                column_type = self._get_schema_column_type(schema_type, column_name)

                # If column is pydantic schema.
                if column_type in self._search_builders:
                    column: InstrumentedAttribute[any] = getattr(
                        model_type, column_name + "_id"
                    )
                    builder = self._search_builders[column_type]
                    column_model_type = self._schema_to_model[column_type]

                    # Builds select for schema table.
                    cur_level_select = (
                        builder(term) if term else select(column_model_type.id)
                    )

                    if len(search_schema.dependencies) > 0:
                        dependency_clause = self._get_search_clause(
                            column_model_type, search_schema.dependencies
                        )
                        if dependency_clause is not None:
                            cur_level_select = cur_level_select.filter(
                                dependency_clause
                            )

                    # Filters by entry from column table.
                    search_clause = column.in_(cur_level_select)

                # If column is simple type.
                elif not issubclass(column_type, schemas.BaseSchema):
                    column: InstrumentedAttribute[any] = getattr(
                        model_type, column_name
                    )

                    if issubclass(column_type, str):
                        search_clause = column.ilike(f"%{term}%")
                    else:
                        search_clause = cast(column, String).ilike(f"%{term}%")
                # If column is schema with non implemented search.
                else:
                    self._warning(
                        f"Attempt to search non implemented method, column type: {column_type}"
                    )
                    continue

                inside_group_clauses.append(search_clause)

            if len(inside_group_clauses) > 0:
                group_clause: BinaryExpression[bool]
                # Group -1 is default group.
                if group_id != -1:
                    group_clause = and_(*inside_group_clauses)
                else:
                    group_clause = or_(*inside_group_clauses)

                group_clauses.append(group_clause)

        return or_(*group_clauses) if len(group_clauses) > 0 else None

    def _search_by_worker(self, term: str) -> Select:
        search_columns = [
            models.Worker.l_name,
            models.Worker.f_name,
            models.Worker.o_name,
        ]

        search_clauses = []

        for search_column in search_columns:
            search_clauses.append(search_column.ilike(f"%{term}%"))

        return select(models.Worker.id).filter(or_(*search_clauses))

    def _search_by_department(self, term: str) -> Select:
        search_columns = [models.Department.name]

        search_clauses = []

        for search_column in search_columns:
            search_clauses.append(search_column.ilike(f"%{term}%"))

        return select(models.Department.id).filter(or_(*search_clauses))

    def _search_by_expenditure(self, term: str) -> Select:
        search_columns = [models.Expenditure.name, models.Expenditure.chapter]

        search_clauses = []

        for search_column in search_columns:
            search_clauses.append(search_column.ilike(f"%{term}%"))

        return select(models.Expenditure.id).filter(or_(*search_clauses))

    # endregion

    # region Date
    def _apply_date(self, date_query: schemas.DateSchema):
        """
        Applies `date_query`.
        """
        column_name = date_query.column
        start = date_query.start
        end = date_query.end
        model_type = self._model_type

        column = getattr(model_type, column_name)

        self.select = self.select.filter(and_(column <= end, column >= start))

    # endregion

    # region Filter by
    def _apply_filter(
        self,
        filter_query: list[schemas.FilterSchema],
    ):
        """
        Applies `filter_query`.
        """
        filter_clause = self._get_filter_clause(self._model_type, filter_query)
        if filter_clause is not None:
            self.select = self.select.filter(filter_clause)

    def _get_filter_clause(
        self,
        model_type: Type[Base],
        filter_schemas: list[schemas.FilterSchema],
    ):
        schema_type = self._model_to_schema[model_type]

        # Dict for all groups in current level.
        groups: dict[int, list[schemas.SearchSchema]] = {-1: []}
        for filter_schema in filter_schemas:
            for group in filter_schema.groups:
                if group in groups:
                    groups[group].append(filter_schema)
                else:
                    groups[group] = [filter_schema]

            if len(filter_schema.groups) == 0:
                groups[-1].append(filter_schema)

        # Calcs clause for every group
        group_clauses = []
        for group_id in groups:
            group = groups[group_id]
            inside_group_clauses: list[BinaryExpression[bool]] = []

            for filter_schema in group:
                column_name = filter_schema.column
                value = filter_schema.value

                filter_clause: BinaryExpression[bool] = None

                # Type inference
                column_type = self._get_schema_column_type(schema_type, column_name)

                # If column is pydantic schema.
                if issubclass(column_type, schemas.BaseSchema):
                    column: InstrumentedAttribute[any] = getattr(
                        model_type, column_name + "_id"
                    )

                    if len(filter_schema.dependencies) > 0:
                        column_model_type = self._schema_to_model[column_type]
                        cur_level_select = select(column_model_type.id)

                        dependency_clause = self._get_filter_clause(
                            column_model_type, filter_schema.dependencies
                        )
                        if dependency_clause is not None:
                            cur_level_select = cur_level_select.filter(
                                dependency_clause
                            )
                    else:
                        self._warning(
                            f"Attempt to filter with non simple type, column type: {column_type}"
                        )
                        continue

                    # Filters by entry from column table.
                    filter_clause = column.in_(cur_level_select)

                # If column is simple type.
                else:
                    column: InstrumentedAttribute[any] = getattr(
                        model_type, column_name
                    )
                    filter_clause = column == value

                inside_group_clauses.append(filter_clause)

            if len(inside_group_clauses) > 0:
                group_clause: BinaryExpression[bool]
                # Group -1 is default group.
                if group_id != -1:
                    group_clause = or_(*inside_group_clauses)
                else:
                    group_clause = and_(*inside_group_clauses)

                group_clauses.append(group_clause)

        return and_(*group_clauses) if len(group_clauses) > 0 else None

    # endregion
