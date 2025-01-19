from sqladmin.forms import ModelConverter, converts
from sqladmin.fields import (
    SelectField,
)
from sqlalchemy.orm import ColumnProperty
import enum
from typing import Dict, Any
from wtforms import validators, BooleanField
from wtforms.fields.core import UnboundField

from app.infra.database.converters import (
    approval_status_technical_request_dict,
    scope_decode_dict,
    worker_status_dict,
    gender_decode_dict,
)
from app.infra.database.models import (
    ApprovalStatus,
    FujiScope,
    WorkerStatus,
    Gender,
)


class TechnicalRequestConverter(ModelConverter):
    @converts("Enum")
    def conv_enum(
        self, model: type, prop: ColumnProperty, kwargs: Dict[str, Any]
    ) -> UnboundField:
        available_choices = [
            (e, approval_status_technical_request_dict[getattr(ApprovalStatus, e)])
            for e in prop.columns[0].type.enums
        ]
        accepted_values = [choice[0] for choice in available_choices]

        if prop.columns[0].nullable:
            kwargs["allow_blank"] = True
            accepted_values.append(None)
            filters = kwargs.get("filters", [])
            filters.append(lambda x: x or None)
            kwargs["filters"] = filters

        kwargs["choices"] = available_choices
        kwargs.setdefault("validators", [])
        kwargs["validators"].append(validators.AnyOf(accepted_values))
        kwargs["coerce"] = lambda v: v.name if isinstance(v, enum.Enum) else str(v)
        return SelectField(**kwargs)


class PostScopeConverter(ModelConverter):
    @converts("Enum")
    def conv_enum(
        self, model: type, prop: ColumnProperty, kwargs: Dict[str, Any]
    ) -> UnboundField:
        available_choices = [
            (e, scope_decode_dict[getattr(FujiScope, e)])
            for e in prop.columns[0].type.enums
        ]
        accepted_values = [choice[0] for choice in available_choices]

        if prop.columns[0].nullable:
            kwargs["allow_blank"] = True
            accepted_values.append(None)
            filters = kwargs.get("filters", [])
            filters.append(lambda x: x or None)
            kwargs["filters"] = filters

        kwargs["choices"] = available_choices
        kwargs.setdefault("validators", [])
        kwargs["validators"].append(validators.AnyOf(accepted_values))
        kwargs["coerce"] = lambda v: v.name if isinstance(v, enum.Enum) else str(v)
        return SelectField(**kwargs)


class WorkerConverter(ModelConverter):
    @converts("Enum")
    def conv_enum(
        self, model: type, prop: ColumnProperty, kwargs: Dict[str, Any]
    ) -> UnboundField:
        match prop.columns[0].name:
            case "state":
                available_choices = [
                    (e, worker_status_dict[getattr(WorkerStatus, e)])
                    for e in prop.columns[0].type.enums
                ]
            case "gender":
                available_choices = [
                    (e, gender_decode_dict[getattr(Gender, e)])
                    for e in prop.columns[0].type.enums
                ]
            case _:
                available_choices = [(e, e) for e in prop.columns[0].type.enums]

        accepted_values = [choice[0] for choice in available_choices]

        if prop.columns[0].nullable:
            kwargs["allow_blank"] = True
            accepted_values.append(None)
            filters = kwargs.get("filters", [])
            filters.append(lambda x: x or None)
            kwargs["filters"] = filters

        kwargs["choices"] = available_choices
        kwargs.setdefault("validators", [])
        kwargs["validators"].append(validators.AnyOf(accepted_values))
        kwargs["coerce"] = lambda v: v.name if isinstance(v, enum.Enum) else str(v)
        return SelectField(**kwargs)

    @converts("Boolean", "dialects.mssql.base.BIT")
    def conv_boolean(
        self, model: type, prop: ColumnProperty, kwargs: Dict[str, Any]
    ) -> UnboundField:
        if not prop.columns[0].nullable:
            kwargs.setdefault("render_kw", {})
            kwargs["render_kw"]["class"] = "form-check-input"
            return BooleanField(**kwargs)

        kwargs["allow_blank"] = True
        kwargs["choices"] = [(True, "Да"), (False, "Нет")]
        kwargs["coerce"] = lambda v: str(v) == "True"
        return SelectField(**kwargs)
