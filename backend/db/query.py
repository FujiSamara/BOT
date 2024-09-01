import logging
from typing import Callable, Optional, Type
import typing
from sqlalchemy import BinaryExpression, Select, and_, or_, desc, select
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import InstrumentedAttribute
from pydantic import BaseModel
import db.schemas as schemas
import db.models as models
from db.database import Base


class QueryBuilder:
    """Helper for building composite query."""

    name = "|QUERYBUILDER|"

    logger = logging.getLogger("uvicorn.error")

    def __init__(self, initial_query: Query):
        """
        :param initial_query: Initially generated query for table `model_type` by `Session`.
        """
        entities = [item["entity"] for item in initial_query.column_descriptions]

        if not len(entities) == 1:
            self.logger.warning(
                f"{self.name} Requested query building with not one entity"
            )

        self.query = initial_query
        self._model_type = entities[0]

        # Schema to model dict
        self._schema_to_model: dict[Type[BaseModel], Type[Base]] = {
            schemas.WorkerSchema: models.Worker,
            schemas.DepartmentSchema: models.Department,
            schemas.ExpenditureSchema: models.Expenditure,
            schemas.BidSchema: models.Bid,
            schemas.PostSchema: models.Post,
            schemas.BudgetRecordSchema: models.BudgetRecord,
        }

        # Model to schema dict
        self._model_to_schema: dict[Type[Base], Type[BaseModel]] = {
            self._schema_to_model[schema]: schema for schema in self._schema_to_model
        }

        # Order by builders.
        self._order_by_builders: dict[
            BaseModel, Callable[[InstrumentedAttribute[any], bool], Query]
        ] = {
            schemas.WorkerSchema: self._order_by_worker,
            schemas.DepartmentSchema: self._order_by_department,
            schemas.ExpenditureSchema: self._order_by_expenditure,
        }

        # Search builders.
        self._search_builders: dict[
            BaseModel,
            Callable[[str], Select],
        ] = {
            schemas.WorkerSchema: self._search_by_worker,
            schemas.DepartmentSchema: self._search_by_department,
        }

    def apply(self, query_schema: schemas.QuerySchema):
        """
        Applies `query_schema` to query.

        **Instructions**:
        1) Order by
        2) Search by
        3) Date by
        """
        if query_schema.date_query:
            self._apply_date(query_schema.date_query)

        self._apply_search(query_schema.search_query)

        if query_schema.order_by_query:
            self._apply_order_by(query_schema.order_by_query)

    def _get_schema_column_type(
        self, schema_type: Type[BaseModel], column_name: str
    ) -> Type:
        column_model_hint = typing.get_type_hints(schema_type)[column_name]

        column_model_type = None
        if typing.get_origin(column_model_hint) == typing.Union:
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
            self.query = builder(column, is_desc)
        # If column is simple type.
        elif not issubclass(column_type, BaseModel):
            if is_desc:
                column = desc(column)
            self.query = self.query.order_by(column)
        # If column is schema with non implemented order by.
        else:
            self.logger.warning(
                f"{self.name} Attempt to order by non implemented method, column type: {column_type}"
            )

    def _order_by_worker(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Query:
        columns = [models.Worker.l_name, models.Worker.f_name, models.Worker.o_name]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.query.join(column).order_by(*columns)

    def _order_by_department(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Query:
        columns = [models.Department.name]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.query.join(column).order_by(*columns)

    def _order_by_expenditure(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Query:
        columns = [models.Expenditure.name, models.Expenditure.chapter]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.query.join(column).order_by(*columns)

    # endregion

    # region Search
    def _apply_search(
        self,
        search_schemas: list[schemas.SearchSchema],
    ):
        """
        Applies `search_schemas`.
        """
        search_clause = self._get_search_clause(self._model_type, search_schemas)
        if search_clause is not None:
            self.query = self.query.filter(search_clause)

    def _get_search_clause(
        self,
        model_type: Type[Base],
        search_schemas: list[schemas.SearchSchema],
    ) -> Optional[BinaryExpression[bool]]:
        """Generates recursive search clause."""
        search_clauses: list[BinaryExpression[bool]] = []
        schema_type = self._model_to_schema[model_type]

        for search_schema in search_schemas:
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

                # Builds select for schema table.
                cur_level_select = builder(term)

                if len(search_schema.dependencies) > 0:
                    column_model_type = self._schema_to_model[column_type]
                    dependency_clause = self._get_search_clause(
                        column_model_type, search_schema.dependencies
                    )
                    if dependency_clause is not None:
                        cur_level_select = cur_level_select.filter(dependency_clause)

                # Filters by entry from column table.
                search_clause = column.in_(cur_level_select)

            # If column is simple type.
            elif not issubclass(column_type, BaseModel):
                column: InstrumentedAttribute[any] = getattr(model_type, column_name)
                search_clause = column.ilike(f"%{term}%")
            # If column is schema with non implemented search.
            else:
                self.logger.warning(
                    f"{self.name} Attempt to search non implemented method, column type: {column_type}"
                )
                continue

            search_clauses.append(search_clause)

        return or_(*search_clauses) if len(search_clauses) > 0 else None

    def _search_by_worker(self, term: str) -> Select:
        if not term:
            return select(models.Worker.id)

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
        if not term:
            return select(models.Department.id)

        search_columns = [models.Department.name]

        search_clauses = []

        for search_column in search_columns:
            search_clauses.append(search_column.ilike(f"%{term}%"))

        return select(models.Department.id).filter(or_(*search_clauses))

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

        self.query = self.query.filter(and_(column <= end, column >= start))

    # endregion
