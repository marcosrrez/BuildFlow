from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.project import Project, Phase
from backend.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectRead, ProjectDetail,
    PhaseCreate, PhaseRead,
)

router = APIRouter()


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.post("/projects", response_model=ProjectRead, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects/{project_id}", response_model=ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.put("/projects/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(project, key, val)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    db.delete(project)
    db.commit()


@router.get("/projects/{project_id}/phases", response_model=list[PhaseRead])
def list_phases(project_id: int, db: Session = Depends(get_db)):
    return db.query(Phase).filter(Phase.project_id == project_id).order_by(Phase.sort_order).all()


@router.post("/projects/{project_id}/phases", response_model=PhaseRead, status_code=201)
def create_phase(project_id: int, data: PhaseCreate, db: Session = Depends(get_db)):
    phase = Phase(project_id=project_id, **data.model_dump())
    db.add(phase)
    db.commit()
    db.refresh(phase)
    return phase
