import logging
from typing import Callable, Optional, Type
import typing
from sqlalchemy import BinaryExpression, or_, and_, desc, select
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import InstrumentedAttribute
from pydantic import BaseModel
from db.models import Department, Expenditure, Worker
from db.schemas import (
    DepartmentSchema,
    ExpenditureSchema,
    OrderBySchema,
    QuerySchema,
    SearchSchema,
    WorkerSchema,
)
from db.database import Base


class QueryBuilder:
    """Helper for building composite query."""

    logger = logging.getLogger("uvicorn.error")

    def __init__(
        self, initial_query: Query, model_type: Type[Base], schema_type: Type[BaseModel]
    ):
        """
        :param initial_query: Initially generated query for table `model_type` by `Session`.
        :param model_type: Type of table required.
        :param schema_type: Type of table schema required.
        """
        self.query = initial_query
        self._model_type = model_type
        self._schema_type = schema_type

        # Order by builders.
        self._order_by_builders: dict[
            BaseModel, Callable[[InstrumentedAttribute[any], bool], Query]
        ] = {
            WorkerSchema: self._order_by_worker,
            DepartmentSchema: self._order_by_department,
            ExpenditureSchema: self._order_by_expenditure,
        }

        # Search builders.
        self._search_builders: dict[
            BaseModel,
            Callable[[InstrumentedAttribute[any], str], BinaryExpression[bool]],
        ] = {WorkerSchema: self._search_by_worker}

    def apply(self, query_schema: QuerySchema):
        """
        Applies `query_schema` to query.

        **Instructions**:
        1) Order by
        2) Search by
        """
        self._apply_search(query_schema.search_query)

        if query_schema.order_by_query:
            self._apply_order_by(query_schema.order_by_query)

    def _get_column_type(self, column_name: str) -> Type:
        column_model_hint = typing.get_type_hints(self._schema_type)[column_name]

        column_model_type = None
        if typing.get_origin(column_model_hint) == typing.Union:
            column_model_type = typing.get_args(column_model_hint)[0]
        else:
            column_model_type = column_model_hint

        return column_model_type

    # region Order by.
    def _apply_order_by(self, order_by_schema: OrderBySchema):
        """
        Applies `order_by_schema`.
        """
        column_name = order_by_schema.column
        is_desc = order_by_schema.desc
        model_type = self._model_type

        column_model_type = self._get_column_type(column_name)
        column = getattr(model_type, column_name)

        if column_model_type in self._order_by_builders:
            builder = self._order_by_builders[column_model_type]
            self.query = builder(column, is_desc)
        elif not issubclass(column_model_type, BaseModel):
            if is_desc:
                column = desc(column)
            self.query = self.query.order_by(column)
        else:
            self.logger.warning(
                f"Attempt to order by non implemented method, column type: {column_model_type}"
            )

    def _order_by_worker(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Query:
        columns = [Worker.l_name, Worker.f_name, Worker.o_name]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.query.join(column).order_by(*columns)

    def _order_by_department(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Query:
        columns = [Department.name]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.query.join(column).order_by(*columns)

    def _order_by_expenditure(
        self, column: InstrumentedAttribute[any], is_desc: bool = False
    ) -> Query:
        columns = [Expenditure.name, Expenditure.chapter]
        if is_desc:
            columns = [desc(w_column) for w_column in columns]
        return self.query.join(column).order_by(*columns)

    # endregion

    # region Search
    def _apply_search(self, search_schemas: list[SearchSchema]):
        """
        Applies `search_schemas`.
        """
        search_clause = self._get_search_clause(search_schemas)
        if search_clause is not None:
            self.query = self.query.filter(search_clause)

    def _get_search_clause(
        self, search_schemas: list[SearchSchema]
    ) -> Optional[BinaryExpression[bool]]:
        model_type = self._model_type

        search_clauses: list[BinaryExpression[bool]] = []

        for search_schema in search_schemas:
            column_name = search_schema.column
            term = search_schema.term

            search_clause: BinaryExpression[bool] = None

            # Type inference
            column_model_type = self._get_column_type(column_name)

            if column_model_type in self._search_builders:
                column: InstrumentedAttribute[any] = getattr(
                    model_type, column_name + "_id"
                )
                builder = self._search_builders[column_model_type]
                search_clause = builder(column, term)
            elif not issubclass(column_model_type, BaseModel):
                column: InstrumentedAttribute[any] = getattr(model_type, column_name)
                search_clause = column.ilike(f"%{term}%")
            else:
                self.logger.warning(
                    f"Attempt to search non implemented method, column type: {column_model_type}"
                )
                continue

            if len(search_schema.dependencies) > 0:
                dependency_clause = self._get_search_clause(search_schema.dependencies)
                if dependency_clause:
                    search_clause = and_(search_clause, dependency_clause)

            search_clauses.append(search_clause)

        return or_(*search_clauses) if len(search_clauses) > 0 else None

    def _search_by_worker(
        self, column: InstrumentedAttribute[any], term: str
    ) -> BinaryExpression[bool]:
        search_columns = [Worker.l_name, Worker.f_name, Worker.o_name]

        search_clauses = []

        for search_column in search_columns:
            search_clauses.append(search_column.ilike(f"%{term}%"))

        return column.in_(select(Worker.id).filter(or_(*search_clauses)))

    # endregion
