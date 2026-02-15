from datetime import date, datetime
from pydantic import BaseModel


class PermitBase(BaseModel):
    permit_type: str
    permit_number: str | None = None
    jurisdiction: str | None = None
    status: str = "draft"
    application_date: date | None = None
    issued_date: date | None = None
    expiry_date: date | None = None
    description: str | None = None
    project_value: float = 0
    applicant_name: str | None = None


class PermitCreate(PermitBase):
    pass


class PermitUpdate(BaseModel):
    permit_type: str | None = None
    permit_number: str | None = None
    jurisdiction: str | None = None
    status: str | None = None
    application_date: date | None = None
    issued_date: date | None = None
    expiry_date: date | None = None
    description: str | None = None
    project_value: float | None = None
    applicant_name: str | None = None


class PermitRead(PermitBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class PermitDocumentBase(BaseModel):
    document_type: str
    description: str | None = None
    is_required: bool = True


class PermitDocumentCreate(PermitDocumentBase):
    pass


class PermitDocumentRead(PermitDocumentBase):
    id: int
    permit_id: int
    file_path: str | None = None
    submitted_date: date | None = None
    status: str = "pending"
    version: int = 1
    reviewer_notes: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class InspectionBase(BaseModel):
    inspection_type: str
    scheduled_date: date | None = None


class InspectionCreate(InspectionBase):
    pass


class InspectionUpdate(BaseModel):
    scheduled_date: date | None = None
    completed_date: date | None = None
    inspector_name: str | None = None
    result: str | None = None
    notes: str | None = None
    corrections: str | None = None


class InspectionRead(InspectionBase):
    id: int
    permit_id: int
    project_id: int
    completed_date: date | None = None
    inspector_name: str | None = None
    result: str | None = None
    notes: str | None = None
    corrections: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class PermitFeeBase(BaseModel):
    fee_type: str
    amount: float
    due_date: date | None = None


class PermitFeeCreate(PermitFeeBase):
    pass


class PermitFeeUpdate(BaseModel):
    paid_date: date | None = None
    receipt_number: str | None = None


class PermitFeeRead(PermitFeeBase):
    id: int
    permit_id: int
    paid_date: date | None = None
    receipt_number: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}


class PermitDetail(PermitRead):
    documents: list[PermitDocumentRead] = []
    inspections: list[InspectionRead] = []
    fees: list[PermitFeeRead] = []
