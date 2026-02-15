from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.punchlist import PunchList, PunchItem
from backend.schemas.punchlist import (
    PunchListCreate, PunchListRead,
    PunchItemCreate, PunchItemUpdate, PunchItemRead,
    PunchItemComplete, PunchItemVerify, PunchItemBackCharge,
    PunchListStats,
)

router = APIRouter()


@router.get("/projects/{project_id}/punchlist/lists", response_model=list[PunchListRead])
def list_punch_lists(project_id: int, db: Session = Depends(get_db)):
    lists = db.query(PunchList).filter(PunchList.project_id == project_id).all()
    result = []
    for pl in lists:
        total = db.query(func.count(PunchItem.id)).filter(PunchItem.punch_list_id == pl.id).scalar()
        open_count = db.query(func.count(PunchItem.id)).filter(
            PunchItem.punch_list_id == pl.id, PunchItem.status.in_(["Open", "Assigned", "In Progress"])
        ).scalar()
        d = {c.name: getattr(pl, c.name) for c in pl.__table__.columns}
        d["item_count"] = total
        d["open_count"] = open_count
        result.append(d)
    return result


@router.post("/projects/{project_id}/punchlist/lists", response_model=PunchListRead, status_code=201)
def create_punch_list(project_id: int, data: PunchListCreate, db: Session = Depends(get_db)):
    pl = PunchList(project_id=project_id, **data.model_dump())
    db.add(pl)
    db.commit()
    db.refresh(pl)
    d = {c.name: getattr(pl, c.name) for c in pl.__table__.columns}
    d["item_count"] = 0
    d["open_count"] = 0
    return d


@router.get("/projects/{project_id}/punchlist/items", response_model=list[PunchItemRead])
def list_punch_items(
    project_id: int,
    trade: str | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(PunchItem).filter(PunchItem.project_id == project_id)
    if trade:
        q = q.filter(PunchItem.trade == trade)
    if status:
        q = q.filter(PunchItem.status == status)
    if priority:
        q = q.filter(PunchItem.priority == priority)
    return q.order_by(PunchItem.created_at.desc()).all()


@router.post("/projects/{project_id}/punchlist/items", response_model=PunchItemRead, status_code=201)
def create_punch_item(project_id: int, data: PunchItemCreate, db: Session = Depends(get_db)):
    item = PunchItem(project_id=project_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/projects/{project_id}/punchlist/items/{item_id}", response_model=PunchItemRead)
def get_punch_item(project_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.query(PunchItem).filter(PunchItem.id == item_id, PunchItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Punch item not found")
    return item


@router.delete("/projects/{project_id}/punchlist/lists/{list_id}", status_code=204)
def delete_punch_list(project_id: int, list_id: int, db: Session = Depends(get_db)):
    pl = db.query(PunchList).filter(PunchList.id == list_id, PunchList.project_id == project_id).first()
    if not pl:
        raise HTTPException(404, "Punch list not found")
    db.delete(pl)
    db.commit()


@router.delete("/projects/{project_id}/punchlist/items/{item_id}", status_code=204)
def delete_punch_item(project_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.query(PunchItem).filter(PunchItem.id == item_id, PunchItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Punch item not found")
    db.delete(item)
    db.commit()


@router.put("/projects/{project_id}/punchlist/items/{item_id}", response_model=PunchItemRead)
def update_punch_item(project_id: int, item_id: int, data: PunchItemUpdate, db: Session = Depends(get_db)):
    item = db.query(PunchItem).filter(PunchItem.id == item_id, PunchItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Punch item not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(item, key, val)
    if data.assigned_to and not item.assigned_date:
        item.assigned_date = date.today()
        if item.status == "Open":
            item.status = "Assigned"
    db.commit()
    db.refresh(item)
    return item


@router.post("/projects/{project_id}/punchlist/items/{item_id}/complete", response_model=PunchItemRead)
def complete_punch_item(project_id: int, item_id: int, data: PunchItemComplete, db: Session = Depends(get_db)):
    item = db.query(PunchItem).filter(PunchItem.id == item_id, PunchItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Punch item not found")
    item.status = "Completed"
    item.completed_by = data.completed_by
    item.completed_date = date.today()
    item.completion_notes = data.completion_notes
    db.commit()
    db.refresh(item)
    return item


@router.post("/projects/{project_id}/punchlist/items/{item_id}/verify", response_model=PunchItemRead)
def verify_punch_item(project_id: int, item_id: int, data: PunchItemVerify, db: Session = Depends(get_db)):
    item = db.query(PunchItem).filter(PunchItem.id == item_id, PunchItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Punch item not found")
    item.verified_by = data.verified_by
    item.verified_date = date.today()
    item.verification_notes = data.verification_notes
    item.status = "Verified" if data.accepted else "Rejected"
    db.commit()
    db.refresh(item)
    return item


@router.post("/projects/{project_id}/punchlist/items/{item_id}/back-charge", response_model=PunchItemRead)
def add_back_charge(project_id: int, item_id: int, data: PunchItemBackCharge, db: Session = Depends(get_db)):
    item = db.query(PunchItem).filter(PunchItem.id == item_id, PunchItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Punch item not found")
    item.back_charge = True
    item.back_charge_amount = data.amount
    item.back_charge_ref = data.reference
    db.commit()
    db.refresh(item)
    return item


@router.get("/projects/{project_id}/punchlist/statistics", response_model=PunchListStats)
def punch_statistics(project_id: int, db: Session = Depends(get_db)):
    items = db.query(PunchItem).filter(PunchItem.project_id == project_id).all()
    total = len(items)
    by_status = {}
    by_trade: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    overdue = 0
    today = date.today()
    for i in items:
        by_status[i.status] = by_status.get(i.status, 0) + 1
        by_trade[i.trade] = by_trade.get(i.trade, 0) + 1
        by_priority[i.priority] = by_priority.get(i.priority, 0) + 1
        if i.due_date and i.due_date < today and i.status not in ("Verified", "Completed"):
            overdue += 1
    done = by_status.get("Verified", 0) + by_status.get("Completed", 0)
    return PunchListStats(
        total=total,
        open=by_status.get("Open", 0),
        in_progress=by_status.get("In Progress", 0) + by_status.get("Assigned", 0),
        completed=by_status.get("Completed", 0),
        verified=by_status.get("Verified", 0),
        rejected=by_status.get("Rejected", 0),
        completion_rate=round(done / total * 100, 1) if total else 0,
        by_trade=by_trade,
        by_priority=by_priority,
        overdue=overdue,
    )
