from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import requests
from backend.database import get_db
from backend.config import settings
from backend.models.project import Project
from backend.models.budget import BudgetItem
from backend.models.schedule import Activity, Milestone
from backend.models.permit import Permit, Inspection
from backend.models.punchlist import PunchItem
from backend.models.subcontractor import SubcontractorPayment
from backend.models.activity_log import ActivityLog
from backend.schemas.dashboard import (
    DashboardSummary, BudgetSummaryCard, ScheduleSummaryCard,
    AlertItem, DeadlineItem, ActivityFeedItem, WeatherData,
)
from backend.schemas.analytics import KPIResult
from backend.schemas.notifications import NotificationList
from backend.services.analytics import run_kpi_analysis
from backend.services.notifications import generate_notifications

router = APIRouter()


def _get_weather() -> WeatherData | None:
    if not settings.weather_api_key:
        return None
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={settings.project_location_lat}&lon={settings.project_location_lon}&appid={settings.weather_api_key}&units=imperial"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            d = r.json()
            return WeatherData(
                temp=d["main"]["temp"],
                condition=d["weather"][0]["description"] if d.get("weather") else None,
                humidity=d["main"].get("humidity"),
                wind_speed=d["wind"].get("speed"),
                icon=d["weather"][0].get("icon") if d.get("weather") else None,
            )
    except Exception:
        pass
    return None


@router.get("/projects/{project_id}/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")

    # Budget
    items = db.query(BudgetItem).filter(BudgetItem.project_id == project_id).all()
    total_budget = sum(i.current_budget for i in items) or project.total_budget
    total_spent = sum(i.actual_cost for i in items)
    total_committed = sum(i.committed_cost for i in items)
    total_forecast = sum(i.forecast_cost for i in items)
    variance = total_budget - total_forecast
    variance_pct = (variance / total_budget * 100) if total_budget else 0
    budget_status = "on_track" if variance_pct > -5 else ("at_risk" if variance_pct > -15 else "critical")
    budget_card = BudgetSummaryCard(
        total_budget=total_budget, total_spent=total_spent, total_committed=total_committed,
        variance=variance, variance_percent=round(variance_pct, 2), status=budget_status,
    )

    # Schedule
    acts = db.query(Activity).filter(Activity.project_id == project_id).all()
    total_acts = len(acts)
    completed_acts = sum(1 for a in acts if a.status == "completed")
    pct_complete = round(completed_acts / total_acts * 100, 1) if total_acts else 0
    critical_count = sum(1 for a in acts if a.is_critical)
    days_remaining = (project.target_end_date - date.today()).days if project.target_end_date else 0
    sched_status = "on_track" if pct_complete >= 0 else "at_risk"
    schedule_card = ScheduleSummaryCard(
        total_activities=total_acts, completed_activities=completed_acts,
        percent_complete=pct_complete, critical_count=critical_count,
        days_remaining=max(days_remaining, 0), status=sched_status,
    )

    # Alerts
    alerts: list[AlertItem] = []
    today = date.today()
    overdue_punch = db.query(PunchItem).filter(
        PunchItem.project_id == project_id,
        PunchItem.due_date < today,
        PunchItem.status.notin_(["Verified", "Completed"]),
    ).count()
    if overdue_punch:
        alerts.append(AlertItem(module="punchlist", severity="warning",
                                message=f"{overdue_punch} overdue punch items", entity_type="punch_item"))

    over_budget = [i for i in items if i.current_budget > 0 and i.actual_cost > i.current_budget]
    if over_budget:
        alerts.append(AlertItem(module="budget", severity="critical",
                                message=f"{len(over_budget)} budget items over budget", entity_type="budget_item"))

    expiring = db.query(Permit).filter(
        Permit.project_id == project_id,
        Permit.expiry_date.isnot(None),
        Permit.expiry_date <= today + timedelta(days=30),
    ).count()
    if expiring:
        alerts.append(AlertItem(module="permits", severity="warning",
                                message=f"{expiring} permits expiring within 30 days", entity_type="permit"))

    # Deadlines
    deadlines: list[DeadlineItem] = []
    upcoming_insp = db.query(Inspection).filter(
        Inspection.project_id == project_id,
        Inspection.scheduled_date >= today,
        Inspection.scheduled_date <= today + timedelta(days=14),
        Inspection.result.is_(None),
    ).all()
    for insp in upcoming_insp:
        days_until = (insp.scheduled_date - today).days
        deadlines.append(DeadlineItem(
            module="permits", description=f"{insp.inspection_type} inspection",
            due_date=str(insp.scheduled_date), days_until=days_until,
            entity_type="inspection", entity_id=insp.id,
        ))

    upcoming_ms = db.query(Milestone).filter(
        Milestone.project_id == project_id,
        Milestone.target_date >= today,
        Milestone.target_date <= today + timedelta(days=14),
        Milestone.status == "upcoming",
    ).all()
    for ms in upcoming_ms:
        days_until = (ms.target_date - today).days
        deadlines.append(DeadlineItem(
            module="schedule", description=ms.name,
            due_date=str(ms.target_date), days_until=days_until,
            entity_type="milestone", entity_id=ms.id,
        ))

    deadlines.sort(key=lambda x: x.days_until)

    # Recent activity
    logs = db.query(ActivityLog).filter(ActivityLog.project_id == project_id).order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()
    recent = [
        ActivityFeedItem(
            module=log.module, action=log.action,
            description=log.description or "", created_at=str(log.created_at),
        )
        for log in logs
    ]

    weather = _get_weather()

    return DashboardSummary(
        project_name=project.name, project_status=project.status,
        budget=budget_card, schedule=schedule_card,
        alerts=alerts, deadlines=deadlines,
        recent_activity=recent, weather=weather,
    )


@router.get("/projects/{project_id}/dashboard/weather")
def get_weather(project_id: int):
    w = _get_weather()
    if not w:
        return {"message": "Weather API not configured. Set WEATHER_API_KEY in .env"}
    return w


@router.get("/projects/{project_id}/dashboard/kpis", response_model=KPIResult)
def get_kpis(project_id: int, db: Session = Depends(get_db)):
    return run_kpi_analysis(db, project_id)


@router.get("/projects/{project_id}/notifications", response_model=NotificationList)
def get_notifications(project_id: int, db: Session = Depends(get_db)):
    return generate_notifications(db, project_id)
