from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.schedule import Activity, ActivityDependency, Milestone
from backend.schemas.schedule import (
    ActivityCreate, ActivityUpdate, ActivityRead,
    DependencyCreate,
    MilestoneCreate, MilestoneUpdate, MilestoneRead,
    DelayImpactRequest, CriticalPathResult,
)
from backend.schemas.analytics import WeatherImpactResult
from backend.services.analytics import run_weather_impact

router = APIRouter()


def _recalc_critical_path(project_id: int, db: Session) -> dict:
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    deps = db.query(ActivityDependency).join(Activity, Activity.id == ActivityDependency.activity_id).filter(
        Activity.project_id == project_id
    ).all()

    act_map = {a.id: a for a in activities}
    pred_map: dict[int, list[int]] = {a.id: [] for a in activities}
    for d in deps:
        pred_map[d.activity_id].append(d.predecessor_id)

    # Forward pass
    for a in activities:
        a.early_start = 0
        a.early_finish = a.duration_days
    changed = True
    while changed:
        changed = False
        for a in activities:
            for pid in pred_map[a.id]:
                p = act_map.get(pid)
                if p and p.early_finish > a.early_start:
                    a.early_start = p.early_finish
                    a.early_finish = a.early_start + a.duration_days
                    changed = True

    project_duration = max((a.early_finish for a in activities), default=0)

    # Backward pass
    for a in activities:
        a.late_finish = project_duration
        a.late_start = a.late_finish - a.duration_days
    changed = True
    while changed:
        changed = False
        for a in activities:
            succ_ids = [s.id for s in activities if a.id in pred_map[s.id]]
            for sid in succ_ids:
                s = act_map[sid]
                if s.late_start < a.late_finish:
                    a.late_finish = s.late_start
                    a.late_start = a.late_finish - a.duration_days
                    changed = True

    critical_path = []
    near_critical = []
    for a in activities:
        a.total_float = a.late_start - a.early_start
        a.is_critical = a.total_float == 0
        if a.is_critical:
            critical_path.append(a.activity_code)
        elif a.total_float <= 5:
            near_critical.append(a.activity_code)

    db.commit()
    return {
        "critical_path": critical_path,
        "project_duration": project_duration,
        "near_critical": near_critical,
    }


def _activity_to_read(a: Activity, db: Session) -> dict:
    deps = db.query(ActivityDependency).filter(ActivityDependency.activity_id == a.id).all()
    d = {c.name: getattr(a, c.name) for c in a.__table__.columns}
    d["predecessor_ids"] = [dep.predecessor_id for dep in deps]
    return d


@router.get("/projects/{project_id}/schedule/activities", response_model=list[ActivityRead])
def list_activities(project_id: int, db: Session = Depends(get_db)):
    acts = db.query(Activity).filter(Activity.project_id == project_id).order_by(Activity.sort_order).all()
    return [_activity_to_read(a, db) for a in acts]


@router.post("/projects/{project_id}/schedule/activities", response_model=ActivityRead, status_code=201)
def create_activity(project_id: int, data: ActivityCreate, db: Session = Depends(get_db)):
    d = data.model_dump(exclude={"predecessor_ids"})
    act = Activity(project_id=project_id, **d)
    db.add(act)
    db.flush()
    for pid in data.predecessor_ids:
        dep = ActivityDependency(activity_id=act.id, predecessor_id=pid)
        db.add(dep)
    db.commit()
    db.refresh(act)
    _recalc_critical_path(project_id, db)
    return _activity_to_read(act, db)


@router.put("/projects/{project_id}/schedule/activities/{act_id}", response_model=ActivityRead)
def update_activity(project_id: int, act_id: int, data: ActivityUpdate, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == act_id, Activity.project_id == project_id).first()
    if not act:
        raise HTTPException(404, "Activity not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(act, key, val)
    db.commit()
    _recalc_critical_path(project_id, db)
    db.refresh(act)
    return _activity_to_read(act, db)


@router.delete("/projects/{project_id}/schedule/activities/{act_id}", status_code=204)
def delete_activity(project_id: int, act_id: int, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == act_id, Activity.project_id == project_id).first()
    if not act:
        raise HTTPException(404, "Activity not found")
    db.query(ActivityDependency).filter(
        (ActivityDependency.activity_id == act_id) | (ActivityDependency.predecessor_id == act_id)
    ).delete()
    db.delete(act)
    db.commit()


@router.post("/projects/{project_id}/schedule/activities/{act_id}/dependencies", status_code=201)
def add_dependency(project_id: int, act_id: int, data: DependencyCreate, db: Session = Depends(get_db)):
    dep = ActivityDependency(activity_id=act_id, predecessor_id=data.predecessor_id,
                             dependency_type=data.dependency_type, lag_days=data.lag_days)
    db.add(dep)
    db.commit()
    _recalc_critical_path(project_id, db)
    return {"status": "ok"}


@router.get("/projects/{project_id}/schedule/critical-path", response_model=CriticalPathResult)
def get_critical_path(project_id: int, db: Session = Depends(get_db)):
    result = _recalc_critical_path(project_id, db)
    acts = db.query(Activity).filter(Activity.project_id == project_id).order_by(Activity.sort_order).all()
    return CriticalPathResult(
        critical_path=result["critical_path"],
        project_duration=result["project_duration"],
        activities=[_activity_to_read(a, db) for a in acts],
        near_critical=result["near_critical"],
    )


@router.post("/projects/{project_id}/schedule/delay-impact")
def analyze_delay(project_id: int, data: DelayImpactRequest, db: Session = Depends(get_db)):
    act = db.query(Activity).filter(Activity.id == data.activity_id, Activity.project_id == project_id).first()
    if not act:
        raise HTTPException(404, "Activity not found")
    original_duration = _recalc_critical_path(project_id, db)["project_duration"]
    impact = max(0, data.delay_days - act.total_float)
    return {
        "activity": act.name,
        "is_critical": act.is_critical,
        "total_float": act.total_float,
        "delay_days": data.delay_days,
        "project_impact_days": impact,
        "original_duration": original_duration,
        "new_duration": original_duration + impact,
    }


@router.get("/projects/{project_id}/schedule/milestones", response_model=list[MilestoneRead])
def list_milestones(project_id: int, db: Session = Depends(get_db)):
    return db.query(Milestone).filter(Milestone.project_id == project_id).order_by(Milestone.target_date).all()


@router.post("/projects/{project_id}/schedule/milestones", response_model=MilestoneRead, status_code=201)
def create_milestone(project_id: int, data: MilestoneCreate, db: Session = Depends(get_db)):
    m = Milestone(project_id=project_id, **data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/projects/{project_id}/schedule/milestones/{ms_id}", response_model=MilestoneRead)
def update_milestone(project_id: int, ms_id: int, data: MilestoneUpdate, db: Session = Depends(get_db)):
    m = db.query(Milestone).filter(Milestone.id == ms_id, Milestone.project_id == project_id).first()
    if not m:
        raise HTTPException(404, "Milestone not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(m, key, val)
    db.commit()
    db.refresh(m)
    return m


@router.delete("/projects/{project_id}/schedule/milestones/{ms_id}", status_code=204)
def delete_milestone(project_id: int, ms_id: int, db: Session = Depends(get_db)):
    m = db.query(Milestone).filter(Milestone.id == ms_id, Milestone.project_id == project_id).first()
    if not m:
        raise HTTPException(404, "Milestone not found")
    db.delete(m)
    db.commit()


HOME_BUILD_TEMPLATE = [
    ("A010", "Site Survey & Permits", 14, []),
    ("A020", "Site Clearing & Grading", 7, ["A010"]),
    ("A030", "Foundation Excavation", 5, ["A020"]),
    ("A040", "Foundation Footings", 5, ["A030"]),
    ("A050", "Foundation Walls & Waterproofing", 10, ["A040"]),
    ("A060", "Backfill & Compaction", 3, ["A050"]),
    ("A070", "Slab on Grade / Basement Floor", 5, ["A060"]),
    ("A080", "Rough Framing - Walls", 14, ["A070"]),
    ("A090", "Rough Framing - Roof", 10, ["A080"]),
    ("A100", "Windows & Exterior Doors", 5, ["A090"]),
    ("A110", "Roofing", 7, ["A090"]),
    ("A120", "Exterior Siding / Masonry", 14, ["A100", "A110"]),
    ("A130", "Rough Plumbing", 7, ["A080"]),
    ("A140", "Rough Electrical", 7, ["A080"]),
    ("A150", "Rough HVAC", 7, ["A080"]),
    ("A160", "Insulation", 5, ["A130", "A140", "A150"]),
    ("A170", "Drywall Hang & Finish", 14, ["A160"]),
    ("A180", "Interior Painting", 10, ["A170"]),
    ("A190", "Cabinets & Countertops", 7, ["A180"]),
    ("A200", "Finish Plumbing", 5, ["A190"]),
    ("A210", "Finish Electrical", 5, ["A190"]),
    ("A220", "Flooring", 10, ["A180"]),
    ("A230", "Trim & Doors", 7, ["A220"]),
    ("A240", "Final HVAC", 3, ["A210"]),
    ("A250", "Landscaping & Grading", 10, ["A120"]),
    ("A260", "Driveway & Walkways", 5, ["A250"]),
    ("A270", "Final Inspections", 5, ["A200", "A210", "A230", "A240", "A260"]),
    ("A280", "Punch List & Closeout", 10, ["A270"]),
]


@router.post("/projects/{project_id}/schedule/template", status_code=201)
def load_template(project_id: int, db: Session = Depends(get_db)):
    code_to_id: dict[str, int] = {}
    for code, name, dur, preds in HOME_BUILD_TEMPLATE:
        act = Activity(project_id=project_id, activity_code=code, name=name, duration_days=dur,
                       sort_order=int(code[1:]))
        db.add(act)
        db.flush()
        code_to_id[code] = act.id

    for code, _, _, preds in HOME_BUILD_TEMPLATE:
        for pred_code in preds:
            dep = ActivityDependency(activity_id=code_to_id[code], predecessor_id=code_to_id[pred_code])
            db.add(dep)

    db.commit()
    _recalc_critical_path(project_id, db)
    return {"status": "ok", "activities_created": len(HOME_BUILD_TEMPLATE)}


@router.get("/projects/{project_id}/schedule/weather-impact", response_model=WeatherImpactResult)
def weather_impact(project_id: int, db: Session = Depends(get_db)):
    return run_weather_impact(db, project_id)
