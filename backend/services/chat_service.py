"""AI Chat Service — Claude-powered project-aware assistant."""

import anthropic
from sqlalchemy.orm import Session
from backend.config import settings
from backend.models.project import Project
from backend.models.budget import BudgetItem
from backend.models.schedule import Activity, Milestone
from backend.models.permit import Permit
from backend.models.punchlist import PunchItem
from backend.models.subcontractor import Subcontractor
from datetime import date, timedelta


def _gather_project_context(db: Session, project_id: int) -> str:
    """Build a context string with current project data for Claude."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return "No project found."

    # Budget summary
    items = db.query(BudgetItem).filter(BudgetItem.project_id == project_id).all()
    total_budget = sum(i.current_budget for i in items)
    total_spent = sum(i.actual_cost for i in items)
    total_committed = sum(i.committed_cost for i in items)
    total_forecast = sum(i.forecast_cost for i in items)
    variance = total_budget - total_forecast
    over_budget_items = [i for i in items if i.actual_cost > i.current_budget and i.current_budget > 0]

    # Schedule summary
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    total_acts = len(activities)
    completed_acts = sum(1 for a in activities if a.status == "completed")
    critical_acts = [a for a in activities if a.is_critical and a.status != "completed"]
    in_progress = [a for a in activities if a.status == "in_progress"]

    # Milestones
    milestones = db.query(Milestone).filter(Milestone.project_id == project_id).all()
    upcoming_ms = [m for m in milestones if m.target_date and m.target_date >= date.today() and m.status != "completed"]

    # Permits
    permits = db.query(Permit).filter(Permit.project_id == project_id).all()

    # Punch items
    punch_items = db.query(PunchItem).filter(
        PunchItem.project_id == project_id,
        PunchItem.status.notin_(["Verified", "Completed"]),
    ).all()

    # Subcontractors
    subs = db.query(Subcontractor).filter(Subcontractor.project_id == project_id).all()

    days_remaining = (project.target_end_date - date.today()).days if project.target_end_date else 0

    ctx = f"""PROJECT: {project.name}
Address: {project.address or 'N/A'}, {project.city or ''}, {project.state or ''}
Status: {project.status}
Start: {project.start_date}, Target End: {project.target_end_date}
Days Remaining: {max(days_remaining, 0)}

BUDGET:
- Total Budget: ${total_budget:,.0f}
- Total Spent: ${total_spent:,.0f}
- Total Committed: ${total_committed:,.0f}
- Total Forecast: ${total_forecast:,.0f}
- Variance: ${variance:,.0f} ({variance/total_budget*100:.1f}% of budget)
"""
    if over_budget_items:
        ctx += "- OVER BUDGET ITEMS:\n"
        for i in over_budget_items:
            ctx += f"  - {i.item_code} {i.description}: budget ${i.current_budget:,.0f}, actual ${i.actual_cost:,.0f}\n"

    ctx += f"""
SCHEDULE:
- Total Activities: {total_acts}, Completed: {completed_acts} ({completed_acts/total_acts*100:.0f}% complete)
- Critical Path Items (incomplete): {len(critical_acts)}
- Currently In Progress: {len(in_progress)}
"""
    if in_progress:
        for a in in_progress[:5]:
            ctx += f"  - {a.activity_code} {a.name} ({a.percent_complete}% done)\n"

    if upcoming_ms:
        ctx += "\nUPCOMING MILESTONES:\n"
        for m in sorted(upcoming_ms, key=lambda x: x.target_date)[:5]:
            days = (m.target_date - date.today()).days
            ctx += f"  - {m.name}: {m.target_date} ({days} days away)\n"

    ctx += f"\nPERMITS: {len(permits)} total\n"
    for p in permits:
        ctx += f"  - {p.permit_type}: {p.status}\n"

    ctx += f"\nOPEN PUNCH ITEMS: {len(punch_items)}\n"
    if punch_items:
        for pi in punch_items[:5]:
            ctx += f"  - [{pi.priority}] {pi.description} ({pi.trade}, {pi.status})\n"

    ctx += f"\nSUBCONTRACTORS: {len(subs)} active\n"
    for s in subs[:5]:
        ctx += f"  - {s.company_name} ({s.trade}): contract ${s.contract_amount:,.0f}\n"

    return ctx


async def chat(db: Session, project_id: int, user_message: str,
               history: list[dict]) -> str:
    """Send a message to Claude with project context."""
    if not settings.anthropic_api_key:
        return ("The AI assistant is not configured yet. "
                "Please set ANTHROPIC_API_KEY in your .env file to enable chat.")

    context = _gather_project_context(db, project_id)

    system_prompt = f"""You are BuildFlow AI, an intelligent construction project assistant for a homeowner who is acting as their own general contractor. You have access to their project data below.

Answer questions clearly and concisely. Focus on actionable advice. When referencing numbers, use the data provided. If asked about something not in the data, say so honestly.

Be encouraging but realistic. Flag risks when you see them. Use construction terminology but explain it simply.

CURRENT PROJECT DATA:
{context}"""

    # Build messages from history + new message
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )

    return response.content[0].text
