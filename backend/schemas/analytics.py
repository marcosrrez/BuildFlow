from pydantic import BaseModel


class VarianceItemResult(BaseModel):
    item_code: str
    description: str
    original_budget: float
    current_budget: float
    committed_cost: float
    actual_cost: float
    forecast_cost: float
    percent_complete: float
    variance_amount: float
    variance_percent: float
    status: str  # under_budget, on_budget, over_budget, critical


class BudgetVarianceResult(BaseModel):
    project_name: str
    total_original_budget: float
    total_current_budget: float
    total_actual: float
    total_forecast: float
    total_variance: float
    total_variance_percent: float
    overall_status: str
    items: list[VarianceItemResult]
    critical_items: list[VarianceItemResult]
    over_budget_items: list[VarianceItemResult]


class CashFlowPeriodResult(BaseModel):
    period_label: str
    planned_spend: float
    actual_spend: float
    cumulative_planned: float
    cumulative_actual: float


class CashFlowResult(BaseModel):
    project_name: str
    total_budget: float
    total_spent: float
    periods: list[CashFlowPeriodResult]


class KPIMetricResult(BaseModel):
    name: str
    category: str
    current_value: float
    target_value: float
    unit: str
    status: str  # on_track, at_risk, critical
    description: str = ""


class KPIResult(BaseModel):
    project_name: str
    schedule_kpis: list[KPIMetricResult]
    cost_kpis: list[KPIMetricResult]
    quality_kpis: list[KPIMetricResult]


class WeatherImpactActivity(BaseModel):
    activity_code: str
    activity_name: str
    risk_level: str  # low, medium, high
    concerns: list[str]


class WeatherImpactResult(BaseModel):
    project_name: str
    assessment_date: str
    outdoor_activities_at_risk: list[WeatherImpactActivity]
    recommendations: list[str]


class PaymentAnalysisSubResult(BaseModel):
    company_name: str
    trade: str
    contract_amount: float
    total_paid: float
    total_retention: float
    balance_remaining: float
    percent_paid: float
    missing_waivers: int


class PaymentAnalysisResult(BaseModel):
    project_name: str
    total_contracted: float
    total_paid: float
    total_retention: float
    total_balance: float
    subcontractors: list[PaymentAnalysisSubResult]
