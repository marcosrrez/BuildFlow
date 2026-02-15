from datetime import date, datetime
from pydantic import BaseModel


class BudgetCategoryBase(BaseModel):
    name: str
    code: str
    budgeted_amount: float = 0
    sort_order: int = 0


class BudgetCategoryCreate(BudgetCategoryBase):
    pass


class BudgetCategoryRead(BudgetCategoryBase):
    id: int
    project_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


class BudgetItemBase(BaseModel):
    category_id: int
    item_code: str
    description: str
    original_budget: float = 0
    current_budget: float = 0
    committed_cost: float = 0
    actual_cost: float = 0
    forecast_cost: float = 0
    percent_complete: float = 0
    notes: str | None = None


class BudgetItemCreate(BudgetItemBase):
    pass


class BudgetItemUpdate(BaseModel):
    category_id: int | None = None
    item_code: str | None = None
    description: str | None = None
    original_budget: float | None = None
    current_budget: float | None = None
    committed_cost: float | None = None
    actual_cost: float | None = None
    forecast_cost: float | None = None
    percent_complete: float | None = None
    notes: str | None = None


class BudgetItemRead(BudgetItemBase):
    id: int
    project_id: int
    bids: list[BidRead] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class BidBase(BaseModel):
    contractor_name: str
    amount: float
    is_selected: bool = False
    notes: str | None = None


class BidCreate(BidBase):
    budget_item_id: int


class BidUpdate(BaseModel):
    contractor_name: str | None = None
    amount: float | None = None
    is_selected: bool | None = None
    notes: str | None = None


class BidRead(BidBase):
    id: int
    budget_item_id: int
    project_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


class CostEntryBase(BaseModel):
    entry_date: date
    amount: float
    entry_type: str
    vendor: str | None = None
    invoice_number: str | None = None
    description: str | None = None


class CostEntryCreate(CostEntryBase):
    pass


class CostEntryRead(CostEntryBase):
    id: int
    budget_item_id: int
    project_id: int
    receipt_path: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ChangeOrderBase(BaseModel):
    co_number: str
    title: str
    description: str | None = None
    change_type: str
    cost_impact: float = 0
    time_impact_days: int = 0
    status: str = "draft"
    requested_by: str | None = None
    requested_date: date | None = None


class ChangeOrderCreate(ChangeOrderBase):
    pass


class ChangeOrderUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    change_type: str | None = None
    cost_impact: float | None = None
    time_impact_days: int | None = None
    status: str | None = None
    approved_date: date | None = None


class ChangeOrderRead(ChangeOrderBase):
    id: int
    project_id: int
    approved_date: date | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class BudgetSummary(BaseModel):
    total_budget: float
    total_committed: float
    total_actual: float
    total_forecast: float
    variance: float
    variance_percent: float
    categories: list[dict]


class CostSuggestionRead(BaseModel):
    label: str
    amount: float
    type: str
    description_options: list[str]
    rationale: str
