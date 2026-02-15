from datetime import date, datetime
from pydantic import BaseModel


class SubcontractorBase(BaseModel):
    company_name: str
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    trade: str
    license_number: str | None = None
    insurance_expiry: date | None = None
    contract_amount: float = 0
    retention_percent: float = 0.10
    contract_start: date | None = None
    contract_end: date | None = None
    status: str = "active"
    notes: str | None = None


class SubcontractorCreate(SubcontractorBase):
    pass


class SubcontractorUpdate(BaseModel):
    company_name: str | None = None
    contact_name: str | None = None
    email: str | None = None
    phone: str | None = None
    trade: str | None = None
    license_number: str | None = None
    insurance_expiry: date | None = None
    contract_amount: float | None = None
    retention_percent: float | None = None
    contract_start: date | None = None
    contract_end: date | None = None
    status: str | None = None
    notes: str | None = None


class SubcontractorRead(SubcontractorBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    total_paid: float = 0
    total_retention: float = 0
    balance_remaining: float = 0
    model_config = {"from_attributes": True}


class PaymentBase(BaseModel):
    invoice_number: str | None = None
    invoice_date: date | None = None
    gross_amount: float
    retention_held: float = 0
    net_amount: float
    status: str = "invoiced"
    scheduled_date: date | None = None
    notes: str | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    status: str | None = None
    paid_date: date | None = None
    check_number: str | None = None
    notes: str | None = None


class PaymentRead(PaymentBase):
    id: int
    subcontractor_id: int
    project_id: int
    paid_date: date | None = None
    check_number: str | None = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class LienWaiverBase(BaseModel):
    waiver_type: str
    through_date: date | None = None
    amount: float | None = None


class LienWaiverCreate(LienWaiverBase):
    pass


class LienWaiverRead(LienWaiverBase):
    id: int
    payment_id: int
    received_date: date | None = None
    file_path: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}
