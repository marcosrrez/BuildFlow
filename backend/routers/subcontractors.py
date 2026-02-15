from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.subcontractor import Subcontractor, SubcontractorPayment, LienWaiver
from backend.schemas.subcontractor import (
    SubcontractorCreate, SubcontractorUpdate, SubcontractorRead,
    PaymentCreate, PaymentUpdate, PaymentRead,
    LienWaiverCreate, LienWaiverRead,
)
from backend.schemas.analytics import PaymentAnalysisResult
from backend.services.analytics import run_payment_analysis

router = APIRouter()


def _enrich_sub(sub: Subcontractor, db: Session) -> dict:
    payments = db.query(SubcontractorPayment).filter(SubcontractorPayment.subcontractor_id == sub.id).all()
    total_paid = sum(p.net_amount for p in payments if p.paid_date)
    total_retention = sum(p.retention_held for p in payments)
    balance = sub.contract_amount - total_paid - total_retention
    d = {c.name: getattr(sub, c.name) for c in sub.__table__.columns}
    d["total_paid"] = total_paid
    d["total_retention"] = total_retention
    d["balance_remaining"] = balance
    return d


@router.get("/projects/{project_id}/subcontractors", response_model=list[SubcontractorRead])
def list_subs(project_id: int, db: Session = Depends(get_db)):
    subs = db.query(Subcontractor).filter(Subcontractor.project_id == project_id).all()
    return [_enrich_sub(s, db) for s in subs]


@router.get("/projects/{project_id}/subcontractors/payment-analysis", response_model=PaymentAnalysisResult)
def payment_analysis(project_id: int, db: Session = Depends(get_db)):
    return run_payment_analysis(db, project_id)


@router.post("/projects/{project_id}/subcontractors", response_model=SubcontractorRead, status_code=201)
def create_sub(project_id: int, data: SubcontractorCreate, db: Session = Depends(get_db)):
    sub = Subcontractor(project_id=project_id, **data.model_dump())
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return _enrich_sub(sub, db)


@router.get("/projects/{project_id}/subcontractors/{sub_id}", response_model=SubcontractorRead)
def get_sub(project_id: int, sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(Subcontractor).filter(Subcontractor.id == sub_id, Subcontractor.project_id == project_id).first()
    if not sub:
        raise HTTPException(404, "Subcontractor not found")
    return _enrich_sub(sub, db)


@router.put("/projects/{project_id}/subcontractors/{sub_id}", response_model=SubcontractorRead)
def update_sub(project_id: int, sub_id: int, data: SubcontractorUpdate, db: Session = Depends(get_db)):
    sub = db.query(Subcontractor).filter(Subcontractor.id == sub_id, Subcontractor.project_id == project_id).first()
    if not sub:
        raise HTTPException(404, "Subcontractor not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(sub, key, val)
    db.commit()
    db.refresh(sub)
    return _enrich_sub(sub, db)


@router.delete("/projects/{project_id}/subcontractors/{sub_id}", status_code=204)
def delete_sub(project_id: int, sub_id: int, db: Session = Depends(get_db)):
    sub = db.query(Subcontractor).filter(Subcontractor.id == sub_id, Subcontractor.project_id == project_id).first()
    if not sub:
        raise HTTPException(404, "Subcontractor not found")
    db.delete(sub)
    db.commit()


@router.get("/projects/{project_id}/subcontractors/{sub_id}/payments", response_model=list[PaymentRead])
def list_payments(project_id: int, sub_id: int, db: Session = Depends(get_db)):
    return db.query(SubcontractorPayment).filter(SubcontractorPayment.subcontractor_id == sub_id).order_by(SubcontractorPayment.created_at.desc()).all()


@router.post("/projects/{project_id}/subcontractors/{sub_id}/payments", response_model=PaymentRead, status_code=201)
def create_payment(project_id: int, sub_id: int, data: PaymentCreate, db: Session = Depends(get_db)):
    pmt = SubcontractorPayment(subcontractor_id=sub_id, project_id=project_id, **data.model_dump())
    db.add(pmt)
    db.commit()
    db.refresh(pmt)
    return pmt


@router.put("/projects/{project_id}/subcontractors/{sub_id}/payments/{pmt_id}", response_model=PaymentRead)
def update_payment(project_id: int, sub_id: int, pmt_id: int, data: PaymentUpdate, db: Session = Depends(get_db)):
    pmt = db.query(SubcontractorPayment).filter(SubcontractorPayment.id == pmt_id, SubcontractorPayment.subcontractor_id == sub_id).first()
    if not pmt:
        raise HTTPException(404, "Payment not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(pmt, key, val)
    db.commit()
    db.refresh(pmt)
    return pmt


@router.delete("/projects/{project_id}/subcontractors/{sub_id}/payments/{pmt_id}", status_code=204)
def delete_payment(project_id: int, sub_id: int, pmt_id: int, db: Session = Depends(get_db)):
    pmt = db.query(SubcontractorPayment).filter(SubcontractorPayment.id == pmt_id, SubcontractorPayment.subcontractor_id == sub_id).first()
    if not pmt:
        raise HTTPException(404, "Payment not found")
    db.delete(pmt)
    db.commit()


@router.post("/projects/{project_id}/subcontractors/{sub_id}/payments/{pmt_id}/waiver", response_model=LienWaiverRead, status_code=201)
def add_waiver(project_id: int, sub_id: int, pmt_id: int, data: LienWaiverCreate, db: Session = Depends(get_db)):
    waiver = LienWaiver(payment_id=pmt_id, **data.model_dump())
    db.add(waiver)
    db.commit()
    db.refresh(waiver)
    return waiver


@router.get("/projects/{project_id}/subcontractors/missing-waivers")
def missing_waivers(project_id: int, db: Session = Depends(get_db)):
    payments = db.query(SubcontractorPayment).filter(
        SubcontractorPayment.project_id == project_id,
        SubcontractorPayment.paid_date.isnot(None),
    ).all()
    missing = []
    for p in payments:
        waiver = db.query(LienWaiver).filter(LienWaiver.payment_id == p.id).first()
        if not waiver:
            sub = db.query(Subcontractor).filter(Subcontractor.id == p.subcontractor_id).first()
            missing.append({
                "subcontractor_id": p.subcontractor_id,
                "subcontractor_name": sub.company_name if sub else "Unknown",
                "payment_id": p.id,
                "invoice_number": p.invoice_number,
                "amount": p.net_amount,
                "paid_date": str(p.paid_date) if p.paid_date else None,
            })
    return missing
