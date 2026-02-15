from datetime import date, datetime
from pydantic import BaseModel


class ActivityBase(BaseModel):
    activity_code: str
    name: str
    duration_days: int
    phase_id: int | None = None
    status: str = "not_started"
    percent_complete: float = 0
    planned_start: date | None = None
    planned_finish: date | None = None
    assigned_to: str | None = None
    notes: str | None = None
    sort_order: int = 0


class ActivityCreate(ActivityBase):
    predecessor_ids: list[int] = []


class ActivityUpdate(BaseModel):
    activity_code: str | None = None
    name: str | None = None
    duration_days: int | None = None
    phase_id: int | None = None
    status: str | None = None
    percent_complete: float | None = None
    planned_start: date | None = None
    planned_finish: date | None = None
    actual_start: date | None = None
    actual_finish: date | None = None
    assigned_to: str | None = None
    notes: str | None = None


class ActivityRead(ActivityBase):
    id: int
    project_id: int
    early_start: int = 0
    early_finish: int = 0
    late_start: int = 0
    late_finish: int = 0
    total_float: int = 0
    is_critical: bool = False
    actual_start: date | None = None
    actual_finish: date | None = None
    created_at: datetime
    updated_at: datetime
    predecessor_ids: list[int] = []
    model_config = {"from_attributes": True}


class DependencyCreate(BaseModel):
    predecessor_id: int
    dependency_type: str = "FS"
    lag_days: int = 0


class MilestoneBase(BaseModel):
    name: str
    target_date: date | None = None
    status: str = "upcoming"
    notes: str | None = None


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(BaseModel):
    name: str | None = None
    target_date: date | None = None
    actual_date: date | None = None
    status: str | None = None
    notes: str | None = None


class MilestoneRead(MilestoneBase):
    id: int
    project_id: int
    actual_date: date | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class DecisionBase(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    status: str = "pending"
    choice_made: str | None = None
    impact_level: str = "medium"
    knowledge_term: str | None = None
    activity_id: int | None = None


class DecisionCreate(DecisionBase):
    pass


class DecisionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    status: str | None = None
    choice_made: str | None = None
    impact_level: str | None = None
    knowledge_term: str | None = None
    activity_id: int | None = None
    decided_at: datetime | None = None


class DecisionRead(DecisionBase):
    id: int
    project_id: int
    created_at: datetime
    decided_at: datetime | None = None
    model_config = {"from_attributes": True}


class DelayImpactRequest(BaseModel):
    activity_id: int
    delay_days: int


class CriticalPathResult(BaseModel):
    critical_path: list[str]
    project_duration: int
    activities: list[ActivityRead]
    near_critical: list[str]
