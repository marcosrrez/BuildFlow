from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.permit import Permit, PermitDocument, Inspection, PermitFee
from backend.schemas.permit import (
    PermitCreate, PermitUpdate, PermitRead, PermitDetail,
    PermitDocumentCreate, PermitDocumentRead,
    InspectionCreate, InspectionUpdate, InspectionRead,
    PermitFeeCreate, PermitFeeUpdate, PermitFeeRead,
)

router = APIRouter()


@router.get("/projects/{project_id}/permits", response_model=list[PermitRead])
def list_permits(project_id: int, db: Session = Depends(get_db)):
    return db.query(Permit).filter(Permit.project_id == project_id).all()


@router.post("/projects/{project_id}/permits", response_model=PermitRead, status_code=201)
def create_permit(project_id: int, data: PermitCreate, db: Session = Depends(get_db)):
    permit = Permit(project_id=project_id, **data.model_dump())
    db.add(permit)
    db.commit()
    db.refresh(permit)
    return permit


@router.get("/projects/{project_id}/permits/{permit_id}", response_model=PermitDetail)
def get_permit(project_id: int, permit_id: int, db: Session = Depends(get_db)):
    permit = db.query(Permit).filter(Permit.id == permit_id, Permit.project_id == project_id).first()
    if not permit:
        raise HTTPException(404, "Permit not found")
    return permit


@router.put("/projects/{project_id}/permits/{permit_id}", response_model=PermitRead)
def update_permit(project_id: int, permit_id: int, data: PermitUpdate, db: Session = Depends(get_db)):
    permit = db.query(Permit).filter(Permit.id == permit_id, Permit.project_id == project_id).first()
    if not permit:
        raise HTTPException(404, "Permit not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(permit, key, val)
    db.commit()
    db.refresh(permit)
    return permit


@router.delete("/projects/{project_id}/permits/{permit_id}", status_code=204)
def delete_permit(project_id: int, permit_id: int, db: Session = Depends(get_db)):
    permit = db.query(Permit).filter(Permit.id == permit_id, Permit.project_id == project_id).first()
    if not permit:
        raise HTTPException(404, "Permit not found")
    db.delete(permit)
    db.commit()


@router.get("/projects/{project_id}/permits/{permit_id}/documents", response_model=list[PermitDocumentRead])
def list_permit_docs(project_id: int, permit_id: int, db: Session = Depends(get_db)):
    return db.query(PermitDocument).filter(PermitDocument.permit_id == permit_id).all()


@router.post("/projects/{project_id}/permits/{permit_id}/documents", response_model=PermitDocumentRead, status_code=201)
def add_permit_doc(project_id: int, permit_id: int, data: PermitDocumentCreate, db: Session = Depends(get_db)):
    doc = PermitDocument(permit_id=permit_id, **data.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/projects/{project_id}/permits/{permit_id}/inspections", response_model=list[InspectionRead])
def list_inspections(project_id: int, permit_id: int, db: Session = Depends(get_db)):
    return db.query(Inspection).filter(Inspection.permit_id == permit_id).all()


@router.post("/projects/{project_id}/permits/{permit_id}/inspections", response_model=InspectionRead, status_code=201)
def schedule_inspection(project_id: int, permit_id: int, data: InspectionCreate, db: Session = Depends(get_db)):
    insp = Inspection(permit_id=permit_id, project_id=project_id, **data.model_dump())
    db.add(insp)
    db.commit()
    db.refresh(insp)
    return insp


@router.delete("/projects/{project_id}/permits/{permit_id}/inspections/{insp_id}", status_code=204)
def delete_inspection(project_id: int, permit_id: int, insp_id: int, db: Session = Depends(get_db)):
    insp = db.query(Inspection).filter(Inspection.id == insp_id, Inspection.permit_id == permit_id).first()
    if not insp:
        raise HTTPException(404, "Inspection not found")
    db.delete(insp)
    db.commit()


@router.put("/projects/{project_id}/permits/{permit_id}/inspections/{insp_id}", response_model=InspectionRead)
def update_inspection(project_id: int, permit_id: int, insp_id: int, data: InspectionUpdate, db: Session = Depends(get_db)):
    insp = db.query(Inspection).filter(Inspection.id == insp_id, Inspection.permit_id == permit_id).first()
    if not insp:
        raise HTTPException(404, "Inspection not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(insp, key, val)
    db.commit()
    db.refresh(insp)
    return insp


@router.get("/projects/{project_id}/permits/{permit_id}/fees", response_model=list[PermitFeeRead])
def list_fees(project_id: int, permit_id: int, db: Session = Depends(get_db)):
    return db.query(PermitFee).filter(PermitFee.permit_id == permit_id).all()


@router.post("/projects/{project_id}/permits/{permit_id}/fees", response_model=PermitFeeRead, status_code=201)
def add_fee(project_id: int, permit_id: int, data: PermitFeeCreate, db: Session = Depends(get_db)):
    fee = PermitFee(permit_id=permit_id, **data.model_dump())
    db.add(fee)
    db.commit()
    db.refresh(fee)
    return fee


@router.put("/projects/{project_id}/permits/{permit_id}/fees/{fee_id}", response_model=PermitFeeRead)
def update_fee(project_id: int, permit_id: int, fee_id: int, data: PermitFeeUpdate, db: Session = Depends(get_db)):
    fee = db.query(PermitFee).filter(PermitFee.id == fee_id, PermitFee.permit_id == permit_id).first()
    if not fee:
        raise HTTPException(404, "Fee not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(fee, key, val)
    db.commit()
    db.refresh(fee)
    return fee


@router.delete("/projects/{project_id}/permits/{permit_id}/fees/{fee_id}", status_code=204)
def delete_fee(project_id: int, permit_id: int, fee_id: int, db: Session = Depends(get_db)):
    fee = db.query(PermitFee).filter(PermitFee.id == fee_id, PermitFee.permit_id == permit_id).first()
    if not fee:
        raise HTTPException(404, "Fee not found")
    db.delete(fee)
    db.commit()


@router.get("/projects/{project_id}/permits/alerts")
def permit_alerts(project_id: int, db: Session = Depends(get_db)):
    today = date.today()
    alerts = []
    permits = db.query(Permit).filter(Permit.project_id == project_id).all()
    for p in permits:
        if p.expiry_date:
            days_until = (p.expiry_date - today).days
            if days_until <= 30:
                severity = "critical" if days_until <= 7 else "warning"
                alerts.append({
                    "permit_id": p.id, "permit_type": p.permit_type,
                    "message": f"Permit expires in {days_until} days",
                    "severity": severity, "days_until": days_until,
                })
    inspections = db.query(Inspection).filter(
        Inspection.project_id == project_id, Inspection.result.is_(None)
    ).all()
    for i in inspections:
        if i.scheduled_date:
            days_until = (i.scheduled_date - today).days
            if days_until <= 7:
                alerts.append({
                    "permit_id": i.permit_id, "inspection_id": i.id,
                    "message": f"{i.inspection_type} inspection in {days_until} days",
                    "severity": "info" if days_until > 1 else "warning",
                    "days_until": days_until,
                })
    return alerts
