from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.accounting.models.dimensions import (
    BusinessLine,
    CostCenter,
    Department,
    DimensionDefinition,
    GeographicRegion,
    Project,
    ReserveDimension9,
    ReserveDimension10,
)
from app.modules.accounting.models.entities import Branch, LegalEntity

DIMENSION_MODEL_MAP = {
    "cost_centers": CostCenter,
    "departments": Department,
    "projects": Project,
    "geographic_regions": GeographicRegion,
    "business_lines": BusinessLine,
    "reserve_dimension_9_values": ReserveDimension9,
    "reserve_dimension_10_values": ReserveDimension10,
}


def create_simple_entity(db: Session, model_cls, **kwargs):
    obj = model_cls(**kwargs)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_dimension_definitions(db: Session) -> list[DimensionDefinition]:
    return list(db.scalars(select(DimensionDefinition).order_by(DimensionDefinition.sort_order.asc())))


def create_legal_entity(db: Session, *, code: str, name: str, is_active: bool) -> LegalEntity:
    return create_simple_entity(db, LegalEntity, code=code, name=name, is_active=is_active)


def create_branch(db: Session, *, legal_entity_id: int, code: str, name: str, is_active: bool) -> Branch:
    return create_simple_entity(
        db,
        Branch,
        legal_entity_id=legal_entity_id,
        code=code,
        name=name,
        is_active=is_active,
    )
