from pydantic import BaseModel


class Notification(BaseModel):
    id: str
    category: str  # budget, schedule, permits, punchlist, subcontractors, weather
    severity: str  # critical, warning, info
    title: str
    message: str
    action_url: str | None = None


class NotificationList(BaseModel):
    total: int
    critical_count: int
    warning_count: int
    info_count: int
    notifications: list[Notification]
