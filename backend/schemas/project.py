from datetime import date, datetime
from pydantic import BaseModel


class PhaseBase(BaseModel):
    name: str
    sort_order: int = 0
    start_date: date | None = None
    end_date: date | None = None
    status: str = "not_started"


class PhaseCreate(PhaseBase):
    pass


class PhaseRead(PhaseBase):
    id: int
    project_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    name: str
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    lot_number: str | None = None
    total_budget: float = 0
    start_date: date | None = None
    target_end_date: date | None = None
    status: str = "active"
    notes: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    lot_number: str | None = None
    total_budget: float | None = None
    start_date: date | None = None
    target_end_date: date | None = None
    actual_end_date: date | None = None
    status: str | None = None
    notes: str | None = None


class ProjectRead(ProjectBase):
    id: int
    actual_end_date: date | None = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ProjectDetail(ProjectRead):
    phases: list[PhaseRead] = []
