from datetime import date, datetime
from pydantic import BaseModel


class CrewEntryBase(BaseModel):
    trade: str
    company_name: str | None = None
    headcount: int = 0
    hours_worked: float = 0
    notes: str | None = None


class CrewEntryCreate(CrewEntryBase):
    pass


class CrewEntryRead(CrewEntryBase):
    id: int
    daily_log_id: int
    model_config = {"from_attributes": True}


class WorkItemBase(BaseModel):
    trade: str | None = None
    description: str
    status: str = "completed"
    notes: str | None = None


class WorkItemCreate(WorkItemBase):
    pass


class WorkItemRead(WorkItemBase):
    id: int
    daily_log_id: int
    model_config = {"from_attributes": True}


class LogPhotoRead(BaseModel):
    id: int
    daily_log_id: int
    file_path: str
    caption: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class DailyLogBase(BaseModel):
    log_date: date
    report_number: str | None = None
    weather_temp: float | None = None
    weather_condition: str | None = None
    weather_wind: float | None = None
    weather_humidity: float | None = None
    weather_impact: str | None = None
    work_summary: str | None = None
    work_planned: str | None = None
    issues: str | None = None
    safety_incidents: int = 0
    safety_notes: str | None = None
    prepared_by: str | None = None


class DailyLogCreate(DailyLogBase):
    crew_entries: list[CrewEntryCreate] = []
    work_items: list[WorkItemCreate] = []


class DailyLogUpdate(BaseModel):
    weather_temp: float | None = None
    weather_condition: str | None = None
    weather_wind: float | None = None
    weather_humidity: float | None = None
    weather_impact: str | None = None
    work_summary: str | None = None
    work_planned: str | None = None
    issues: str | None = None
    safety_incidents: int | None = None
    safety_notes: str | None = None
    prepared_by: str | None = None


class DailyLogRead(DailyLogBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class DailyLogDetail(DailyLogRead):
    crew_entries: list[CrewEntryRead] = []
    work_items: list[WorkItemRead] = []
    photos: list[LogPhotoRead] = []
