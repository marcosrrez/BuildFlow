"""Smart Notification Service — proactive alerts across all modules."""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.models.project import Project
from backend.models.budget import BudgetItem
from backend.models.schedule import Activity, Milestone
from backend.models.permit import Permit, Inspection
from backend.models.punchlist import PunchItem
from backend.models.subcontractor import Subcontractor, SubcontractorPayment, LienWaiver
from backend.schemas.notifications import Notification, NotificationList


def generate_notifications(db: Session, project_id: int) -> NotificationList:
    """Generate all project notifications by scanning across modules."""
    notifications: list[Notification] = []
    today = date.today()
    counter = 0

    def _add(category: str, severity: str, title: str, message: str, action_url: str | None = None):
        nonlocal counter
        counter += 1
        notifications.append(Notification(
            id=f"N-{counter:04d}",
            category=category,
            severity=severity,
            title=title,
            message=message,
            action_url=action_url,
        ))

    # --- Budget alerts ---
    items = db.query(BudgetItem).filter(BudgetItem.project_id == project_id).all()
    total_budget = sum(i.current_budget for i in items)
    total_spent = sum(i.actual_cost for i in items)

    if total_budget > 0 and total_spent / total_budget > 0.90:
        pct = round(total_spent / total_budget * 100, 1)
        _add("budget", "critical", "Budget Nearly Exhausted",
             f"You've spent {pct}% of your total ${total_budget:,.0f} budget.",
             "/budget")

    over_budget = [i for i in items if i.current_budget > 0 and i.actual_cost > i.current_budget]
    for item in over_budget:
        over_amt = item.actual_cost - item.current_budget
        _add("budget", "critical", f"Over Budget: {item.description}",
             f"{item.item_code} is ${over_amt:,.0f} over its ${item.current_budget:,.0f} budget.",
             "/budget")

    at_risk = [i for i in items
               if i.current_budget > 0 and i.forecast_cost > 0
               and i.forecast_cost > i.current_budget * 1.10
               and i not in over_budget]
    for item in at_risk[:3]:
        _add("budget", "warning", f"Budget Risk: {item.description}",
             f"Forecast ${item.forecast_cost:,.0f} exceeds budget ${item.current_budget:,.0f}.",
             "/budget")

    # --- Schedule alerts ---
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    overdue_acts = [a for a in activities
                    if a.planned_finish and a.planned_finish < today
                    and a.status not in ("completed",)]
    for act in overdue_acts[:3]:
        days_late = (today - act.planned_finish).days
        _add("schedule", "critical" if days_late > 7 else "warning",
             f"Overdue: {act.name}",
             f"Activity {act.activity_code} is {days_late} days past its planned finish.",
             "/schedule")

    # Critical path activities starting soon
    critical_soon = [a for a in activities
                     if a.is_critical and a.planned_start
                     and 0 <= (a.planned_start - today).days <= 7
                     and a.status not in ("completed", "in_progress")]
    for act in critical_soon:
        days_until = (act.planned_start - today).days
        _add("schedule", "warning", f"Critical Path Starting: {act.name}",
             f"{act.activity_code} starts in {days_until} days. Ensure resources are ready.",
             "/schedule")

    # --- Permit alerts ---
    permits = db.query(Permit).filter(Permit.project_id == project_id).all()
    for permit in permits:
        if permit.expiry_date:
            days_until = (permit.expiry_date - today).days
            if days_until < 0:
                _add("permits", "critical", f"Expired: {permit.permit_type} Permit",
                     f"Permit expired {abs(days_until)} days ago. Renew immediately.",
                     "/permits")
            elif days_until <= 30:
                _add("permits", "warning", f"Expiring: {permit.permit_type} Permit",
                     f"Permit expires in {days_until} days ({permit.expiry_date}).",
                     "/permits")

    # Upcoming inspections
    inspections = db.query(Inspection).filter(
        Inspection.project_id == project_id,
        Inspection.scheduled_date >= today,
        Inspection.scheduled_date <= today + timedelta(days=7),
        Inspection.result.is_(None),
    ).all()
    for insp in inspections:
        days_until = (insp.scheduled_date - today).days
        _add("permits", "info", f"Inspection: {insp.inspection_type}",
             f"Scheduled in {days_until} days ({insp.scheduled_date}).",
             "/permits")

    # --- Punch list alerts ---
    overdue_punch = db.query(PunchItem).filter(
        PunchItem.project_id == project_id,
        PunchItem.due_date < today,
        PunchItem.status.notin_(["Verified", "Completed"]),
    ).all()
    if overdue_punch:
        _add("punchlist", "warning", f"{len(overdue_punch)} Overdue Punch Items",
             "Items past their due date need attention.",
             "/punchlist")

    stale_punch = db.query(PunchItem).filter(
        PunchItem.project_id == project_id,
        PunchItem.status == "Open",
    ).all()
    old_items = [p for p in stale_punch if p.created_at and (today - p.created_at.date()).days > 14]
    if old_items:
        _add("punchlist", "info", f"{len(old_items)} Punch Items Open > 14 Days",
             "Consider following up with assigned trades.",
             "/punchlist")

    # --- Subcontractor alerts ---
    subs = db.query(Subcontractor).filter(Subcontractor.project_id == project_id).all()
    for sub in subs:
        if sub.insurance_expiry:
            try:
                exp_date = sub.insurance_expiry if isinstance(sub.insurance_expiry, date) else date.fromisoformat(str(sub.insurance_expiry))
                days_until = (exp_date - today).days
                if days_until < 0:
                    _add("subcontractors", "critical",
                         f"Insurance Expired: {sub.company_name}",
                         f"Insurance expired {abs(days_until)} days ago. Stop work until renewed.",
                         "/subcontractors")
                elif days_until <= 30:
                    _add("subcontractors", "warning",
                         f"Insurance Expiring: {sub.company_name}",
                         f"Insurance expires in {days_until} days.",
                         "/subcontractors")
            except (ValueError, TypeError):
                pass

        # Check for missing lien waivers
        payments = db.query(SubcontractorPayment).filter(
            SubcontractorPayment.subcontractor_id == sub.id,
            SubcontractorPayment.paid_date.isnot(None),
        ).all()
        paid_ids = {p.id for p in payments}
        waivers = db.query(LienWaiver).filter(LienWaiver.payment_id.in_(paid_ids)).all() if paid_ids else []
        waiver_payment_ids = {w.payment_id for w in waivers}
        missing = [p for p in payments if p.id not in waiver_payment_ids]
        if missing:
            _add("subcontractors", "warning",
                 f"Missing Waivers: {sub.company_name}",
                 f"{len(missing)} payments without lien waivers.",
                 "/subcontractors")

    # Sort: critical first, then warning, then info
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    notifications.sort(key=lambda n: severity_order.get(n.severity, 3))

    return NotificationList(
        total=len(notifications),
        critical_count=sum(1 for n in notifications if n.severity == "critical"),
        warning_count=sum(1 for n in notifications if n.severity == "warning"),
        info_count=sum(1 for n in notifications if n.severity == "info"),
        notifications=notifications,
    )
