from datetime import date, datetime
from pydantic import BaseModel


class PunchListBase(BaseModel):
    name: str
    walk_date: date | None = None
    attendees: str | None = None
    area: str | None = None
    list_type: str = "Punch"
    status: str = "Active"
    created_by: str | None = None


class PunchListCreate(PunchListBase):
    pass


class PunchListRead(PunchListBase):
    id: int
    project_id: int
    created_at: datetime
    item_count: int = 0
    open_count: int = 0
    model_config = {"from_attributes": True}


class PunchItemBase(BaseModel):
    description: str
    location: str
    building: str | None = None
    floor: str | None = None
    room: str | None = None
    trade: str
    priority: str = "Medium"
    assigned_to: str | None = None
    due_date: date | None = None
    spec_reference: str | None = None


class PunchItemCreate(PunchItemBase):
    punch_list_id: int


class PunchItemUpdate(BaseModel):
    description: str | None = None
    location: str | None = None
    building: str | None = None
    floor: str | None = None
    room: str | None = None
    trade: str | None = None
    priority: str | None = None
    status: str | None = None
    assigned_to: str | None = None
    due_date: date | None = None


class PunchItemRead(PunchItemBase):
    id: int
    punch_list_id: int
    project_id: int
    status: str = "Open"
    assigned_date: date | None = None
    photo_before_path: str | None = None
    photo_after_path: str | None = None
    completed_by: str | None = None
    completed_date: date | None = None
    completion_notes: str | None = None
    verified_by: str | None = None
    verified_date: date | None = None
    verification_notes: str | None = None
    back_charge: bool = False
    back_charge_amount: float = 0
    back_charge_ref: str | None = None
    created_by: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class PunchItemComplete(BaseModel):
    completed_by: str
    completion_notes: str | None = None


class PunchItemVerify(BaseModel):
    verified_by: str
    verification_notes: str | None = None
    accepted: bool = True


class PunchItemBackCharge(BaseModel):
    amount: float
    reference: str | None = None


class PunchListStats(BaseModel):
    total: int
    open: int
    in_progress: int
    completed: int
    verified: int
    rejected: int
    completion_rate: float
    by_trade: dict[str, int]
    by_priority: dict[str, int]
    overdue: int
