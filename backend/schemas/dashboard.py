from pydantic import BaseModel


class BudgetSummaryCard(BaseModel):
    total_budget: float
    total_spent: float
    total_committed: float
    variance: float
    variance_percent: float
    status: str  # on_track, at_risk, critical


class ScheduleSummaryCard(BaseModel):
    total_activities: int
    completed_activities: int
    percent_complete: float
    critical_count: int
    days_remaining: int
    status: str


class AlertItem(BaseModel):
    module: str
    severity: str  # critical, warning, info
    message: str
    entity_type: str
    entity_id: int | None = None


class DeadlineItem(BaseModel):
    module: str
    description: str
    due_date: str
    days_until: int
    entity_type: str
    entity_id: int | None = None


class ActivityFeedItem(BaseModel):
    module: str
    action: str
    description: str
    created_at: str


class WeatherData(BaseModel):
    temp: float | None = None
    condition: str | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    icon: str | None = None


class DashboardSummary(BaseModel):
    project_name: str
    project_status: str
    budget: BudgetSummaryCard
    schedule: ScheduleSummaryCard
    alerts: list[AlertItem]
    deadlines: list[DeadlineItem]
    recent_activity: list[ActivityFeedItem]
    weather: WeatherData | None = None
