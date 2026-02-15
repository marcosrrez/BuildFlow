"""Analytics service — bridges DDC skills to the database layer."""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.models.project import Project
from backend.models.budget import BudgetCategory, BudgetItem
from backend.models.schedule import Activity
from backend.models.permit import Permit, Inspection
from backend.models.punchlist import PunchItem
from backend.models.subcontractor import Subcontractor, SubcontractorPayment, LienWaiver
from backend.schemas.analytics import (
    VarianceItemResult, BudgetVarianceResult,
    CashFlowPeriodResult, CashFlowResult,
    KPIMetricResult, KPIResult,
    WeatherImpactActivity, WeatherImpactResult,
    PaymentAnalysisSubResult, PaymentAnalysisResult,
)


def run_budget_variance(db: Session, project_id: int) -> BudgetVarianceResult:
    """Run budget variance analysis using DDC BudgetVarianceAnalyzer logic."""
    project = db.query(Project).filter(Project.id == project_id).first()
    items = db.query(BudgetItem).filter(BudgetItem.project_id == project_id).all()

    result_items = []
    for item in items:
        forecast = item.forecast_cost if item.forecast_cost > 0 else item.current_budget
        variance_amt = item.current_budget - forecast
        variance_pct = (variance_amt / item.current_budget * 100) if item.current_budget else 0

        if variance_pct > 5:
            status = "under_budget"
        elif variance_pct >= -5:
            status = "on_budget"
        elif variance_pct >= -15:
            status = "over_budget"
        else:
            status = "critical"

        result_items.append(VarianceItemResult(
            item_code=item.item_code,
            description=item.description,
            original_budget=item.original_budget,
            current_budget=item.current_budget,
            committed_cost=item.committed_cost,
            actual_cost=item.actual_cost,
            forecast_cost=forecast,
            percent_complete=item.percent_complete,
            variance_amount=round(variance_amt, 2),
            variance_percent=round(variance_pct, 2),
            status=status,
        ))

    total_original = sum(i.original_budget for i in items)
    total_current = sum(i.current_budget for i in items)
    total_actual = sum(i.actual_cost for i in items)
    total_forecast = sum(i.forecast_cost if i.forecast_cost > 0 else i.current_budget for i in items)
    total_var = total_current - total_forecast
    total_var_pct = (total_var / total_current * 100) if total_current else 0

    if total_var_pct > 5:
        overall = "under_budget"
    elif total_var_pct >= -5:
        overall = "on_budget"
    elif total_var_pct >= -15:
        overall = "over_budget"
    else:
        overall = "critical"

    return BudgetVarianceResult(
        project_name=project.name if project else "",
        total_original_budget=total_original,
        total_current_budget=total_current,
        total_actual=total_actual,
        total_forecast=total_forecast,
        total_variance=round(total_var, 2),
        total_variance_percent=round(total_var_pct, 2),
        overall_status=overall,
        items=result_items,
        critical_items=[i for i in result_items if i.status == "critical"],
        over_budget_items=[i for i in result_items if i.status in ("over_budget", "critical")],
    )


def run_cash_flow_forecast(db: Session, project_id: int) -> CashFlowResult:
    """Generate monthly cash flow forecast (planned vs actual S-curve)."""
    project = db.query(Project).filter(Project.id == project_id).first()
    items = db.query(BudgetItem).filter(BudgetItem.project_id == project_id).all()

    total_budget = sum(i.current_budget for i in items)
    total_spent = sum(i.actual_cost for i in items)

    # Build monthly periods from project start to end
    start = project.start_date if project and project.start_date else date.today()
    end = project.target_end_date if project and project.target_end_date else start + timedelta(days=270)
    months = max(1, (end.year - start.year) * 12 + (end.month - start.month) + 1)

    # Distribute budget linearly across months (S-curve approximation)
    monthly_planned = total_budget / months if months > 0 else 0

    # For actual spend, distribute it evenly across elapsed months
    today = date.today()
    elapsed_months = max(1, (today.year - start.year) * 12 + (today.month - start.month) + 1)
    monthly_actual = total_spent / elapsed_months if elapsed_months > 0 else 0

    periods = []
    cum_planned = 0.0
    cum_actual = 0.0
    current = date(start.year, start.month, 1)

    for i in range(months):
        cum_planned += monthly_planned
        is_past = current <= today
        if is_past and i < elapsed_months:
            cum_actual += monthly_actual
        period_actual = monthly_actual if (is_past and i < elapsed_months) else 0

        periods.append(CashFlowPeriodResult(
            period_label=current.strftime("%b %Y"),
            planned_spend=round(monthly_planned, 2),
            actual_spend=round(period_actual, 2),
            cumulative_planned=round(cum_planned, 2),
            cumulative_actual=round(cum_actual, 2),
        ))

        # Advance month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    return CashFlowResult(
        project_name=project.name if project else "",
        total_budget=total_budget,
        total_spent=total_spent,
        periods=periods,
    )


def run_kpi_analysis(db: Session, project_id: int) -> KPIResult:
    """Calculate project KPIs using DDC ProjectKPIDashboard logic."""
    project = db.query(Project).filter(Project.id == project_id).first()
    items = db.query(BudgetItem).filter(BudgetItem.project_id == project_id).all()
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    inspections = db.query(Inspection).filter(Inspection.project_id == project_id).all()
    punch_items = db.query(PunchItem).filter(PunchItem.project_id == project_id).all()

    # Schedule KPIs
    total_acts = len(activities)
    completed_acts = sum(1 for a in activities if a.status == "completed")
    spi = completed_acts / total_acts if total_acts > 0 else 0
    spi_status = "on_track" if spi >= 0.95 else ("at_risk" if spi >= 0.85 else "critical")
    pct_complete = round(completed_acts / total_acts * 100, 1) if total_acts > 0 else 0

    schedule_kpis = [
        KPIMetricResult(
            name="Schedule Performance Index (SPI)",
            category="schedule", current_value=round(spi, 2), target_value=1.0,
            unit="ratio", status=spi_status,
            description="SPI = Completed Activities / Total Activities"
        ),
        KPIMetricResult(
            name="Percent Complete",
            category="schedule", current_value=pct_complete, target_value=100,
            unit="%", status=spi_status,
        ),
    ]

    # Cost KPIs
    total_budget = sum(i.current_budget for i in items)
    total_actual = sum(i.actual_cost for i in items)
    earned_value = sum(i.current_budget * (i.percent_complete / 100) for i in items)
    cpi = earned_value / total_actual if total_actual > 0 else 1.0
    cpi_status = "on_track" if cpi >= 0.95 else ("at_risk" if cpi >= 0.85 else "critical")
    budget_used = round(total_actual / total_budget * 100, 1) if total_budget > 0 else 0

    cost_kpis = [
        KPIMetricResult(
            name="Cost Performance Index (CPI)",
            category="cost", current_value=round(cpi, 2), target_value=1.0,
            unit="ratio", status=cpi_status,
            description="CPI = Earned Value / Actual Cost"
        ),
        KPIMetricResult(
            name="Budget Utilization",
            category="cost", current_value=budget_used, target_value=100,
            unit="%", status=cpi_status,
        ),
    ]

    # Quality KPIs
    completed_insp = [i for i in inspections if i.result is not None]
    total_insp = len(completed_insp)
    passed_insp = sum(1 for i in completed_insp if i.result == "pass")
    fpy = passed_insp / total_insp if total_insp > 0 else 1.0
    fpy_status = "on_track" if fpy >= 0.98 else ("at_risk" if fpy >= 0.95 else "critical")
    if total_insp == 0:
        fpy_status = "on_track"  # No data yet, don't flag as critical

    total_punch = len(punch_items)
    resolved_punch = sum(1 for p in punch_items if p.status in ("Verified", "Completed"))
    rework_rate = round((total_punch - resolved_punch) / max(total_punch, 1) * 100, 1) if total_punch > 0 else 0

    quality_kpis = [
        KPIMetricResult(
            name="First Pass Yield (FPY)",
            category="quality", current_value=round(fpy * 100, 1), target_value=98,
            unit="%", status=fpy_status,
            description="Inspection pass rate on first attempt"
        ),
        KPIMetricResult(
            name="Rework Rate",
            category="quality", current_value=rework_rate, target_value=2,
            unit="%", status=fpy_status,
        ),
    ]

    return KPIResult(
        project_name=project.name if project else "",
        schedule_kpis=schedule_kpis,
        cost_kpis=cost_kpis,
        quality_kpis=quality_kpis,
    )


def run_weather_impact(db: Session, project_id: int) -> WeatherImpactResult:
    """Assess weather impact on outdoor activities."""
    project = db.query(Project).filter(Project.id == project_id).first()
    activities = db.query(Activity).filter(
        Activity.project_id == project_id,
        Activity.status.notin_(["completed"]),
    ).all()

    # Outdoor activity types that are weather-sensitive
    outdoor_keywords = {"site", "excavat", "foundation", "concrete", "roof", "exterior",
                        "landscap", "grade", "pour", "masonry", "paving"}

    at_risk = []
    recommendations = []

    for act in activities:
        name_lower = act.name.lower()
        is_outdoor = any(kw in name_lower for kw in outdoor_keywords)
        if not is_outdoor:
            continue

        concerns = []
        risk = "low"

        if "concrete" in name_lower or "pour" in name_lower or "foundation" in name_lower:
            concerns.append("Concrete requires dry conditions and temps above 40F")
            risk = "medium"
        if "roof" in name_lower:
            concerns.append("Roofing unsafe in rain or high winds (>25mph)")
            risk = "medium"
        if "excavat" in name_lower or "grade" in name_lower:
            concerns.append("Earthwork affected by heavy rain and frost")
            risk = "medium"
        if "exterior" in name_lower or "masonry" in name_lower:
            concerns.append("Exterior work delayed by precipitation")
            risk = "low"
        if "landscap" in name_lower:
            concerns.append("Planting affected by extreme temps and frost")
            risk = "low"

        if not concerns:
            concerns.append("General outdoor activity - weather sensitive")

        at_risk.append(WeatherImpactActivity(
            activity_code=act.activity_code,
            activity_name=act.name,
            risk_level=risk,
            concerns=concerns,
        ))

    if at_risk:
        recommendations.append("Monitor weather forecasts daily for outdoor activities")
        recommendations.append("Have contingency plans for rain delays on critical-path items")
        recommendations.append("Schedule concrete pours during dry weather windows")
        if any(a.risk_level == "high" for a in at_risk):
            recommendations.append("Consider weather insurance for high-risk activities")

    return WeatherImpactResult(
        project_name=project.name if project else "",
        assessment_date=str(date.today()),
        outdoor_activities_at_risk=at_risk,
        recommendations=recommendations,
    )


def run_payment_analysis(db: Session, project_id: int) -> PaymentAnalysisResult:
    """Analyze subcontractor payment status using DDC SubcontractorPaymentTracker logic."""
    project = db.query(Project).filter(Project.id == project_id).first()
    subs = db.query(Subcontractor).filter(Subcontractor.project_id == project_id).all()

    sub_results = []
    total_contracted = 0
    total_paid = 0
    total_retention = 0
    total_balance = 0

    for sub in subs:
        payments = db.query(SubcontractorPayment).filter(
            SubcontractorPayment.subcontractor_id == sub.id
        ).all()
        paid_ids = {p.id for p in payments}
        waivers = db.query(LienWaiver).filter(
            LienWaiver.payment_id.in_(paid_ids)
        ).all() if paid_ids else []

        paid = sum(p.net_amount for p in payments if p.paid_date)
        retention = sum(p.retention_held for p in payments)
        balance = sub.contract_amount - paid - retention
        pct_paid = round(paid / sub.contract_amount * 100, 1) if sub.contract_amount else 0

        # Count payments that should have waivers but don't
        paid_payments = [p for p in payments if p.paid_date]
        waiver_payment_ids = {w.payment_id for w in waivers}
        missing = sum(1 for p in paid_payments if p.id not in waiver_payment_ids)

        sub_results.append(PaymentAnalysisSubResult(
            company_name=sub.company_name,
            trade=sub.trade,
            contract_amount=sub.contract_amount,
            total_paid=paid,
            total_retention=retention,
            balance_remaining=balance,
            percent_paid=pct_paid,
            missing_waivers=missing,
        ))

        total_contracted += sub.contract_amount
        total_paid += paid
        total_retention += retention
        total_balance += balance

    return PaymentAnalysisResult(
        project_name=project.name if project else "",
        total_contracted=total_contracted,
        total_paid=total_paid,
        total_retention=total_retention,
        total_balance=total_balance,
        subcontractors=sub_results,
    )
