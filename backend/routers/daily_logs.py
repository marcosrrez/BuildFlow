from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.daily_log import DailyLog, DailyLogCrew, DailyLogWorkItem, DailyLogPhoto
from backend.schemas.daily_log import (
    DailyLogCreate, DailyLogUpdate, DailyLogRead, DailyLogDetail,
    CrewEntryCreate, CrewEntryRead,
    WorkItemCreate, WorkItemRead,
)
from backend.utils.file_storage import save_upload

router = APIRouter()


@router.get("/projects/{project_id}/daily-logs", response_model=list[DailyLogRead])
def list_logs(project_id: int, db: Session = Depends(get_db)):
    return db.query(DailyLog).filter(DailyLog.project_id == project_id).order_by(DailyLog.log_date.desc()).all()


@router.post("/projects/{project_id}/daily-logs", response_model=DailyLogDetail, status_code=201)
def create_log(project_id: int, data: DailyLogCreate, db: Session = Depends(get_db)):
    d = data.model_dump(exclude={"crew_entries", "work_items"})
    log = DailyLog(project_id=project_id, **d)
    db.add(log)
    db.flush()
    for crew in data.crew_entries:
        db.add(DailyLogCrew(daily_log_id=log.id, **crew.model_dump()))
    for wi in data.work_items:
        db.add(DailyLogWorkItem(daily_log_id=log.id, **wi.model_dump()))
    db.commit()
    db.refresh(log)
    return log


@router.get("/projects/{project_id}/daily-logs/{log_id}", response_model=DailyLogDetail)
def get_log(project_id: int, log_id: int, db: Session = Depends(get_db)):
    log = db.query(DailyLog).filter(DailyLog.id == log_id, DailyLog.project_id == project_id).first()
    if not log:
        raise HTTPException(404, "Daily log not found")
    return log


@router.put("/projects/{project_id}/daily-logs/{log_id}", response_model=DailyLogRead)
def update_log(project_id: int, log_id: int, data: DailyLogUpdate, db: Session = Depends(get_db)):
    log = db.query(DailyLog).filter(DailyLog.id == log_id, DailyLog.project_id == project_id).first()
    if not log:
        raise HTTPException(404, "Daily log not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(log, key, val)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/projects/{project_id}/daily-logs/{log_id}", status_code=204)
def delete_log(project_id: int, log_id: int, db: Session = Depends(get_db)):
    log = db.query(DailyLog).filter(DailyLog.id == log_id, DailyLog.project_id == project_id).first()
    if not log:
        raise HTTPException(404, "Daily log not found")
    db.delete(log)
    db.commit()


@router.post("/projects/{project_id}/daily-logs/{log_id}/crew", response_model=CrewEntryRead, status_code=201)
def add_crew(project_id: int, log_id: int, data: CrewEntryCreate, db: Session = Depends(get_db)):
    entry = DailyLogCrew(daily_log_id=log_id, **data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/projects/{project_id}/daily-logs/{log_id}/work-items", response_model=WorkItemRead, status_code=201)
def add_work_item(project_id: int, log_id: int, data: WorkItemCreate, db: Session = Depends(get_db)):
    wi = DailyLogWorkItem(daily_log_id=log_id, **data.model_dump())
    db.add(wi)
    db.commit()
    db.refresh(wi)
    return wi


@router.post("/projects/{project_id}/daily-logs/{log_id}/photos", status_code=201)
async def add_photo(project_id: int, log_id: int, file: UploadFile = File(...), caption: str = "", db: Session = Depends(get_db)):
    contents = await file.read()
    path = save_upload(contents, file.filename or "photo.jpg", "photos")
    photo = DailyLogPhoto(daily_log_id=log_id, file_path=path, caption=caption)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return {"id": photo.id, "file_path": photo.file_path, "caption": photo.caption}
