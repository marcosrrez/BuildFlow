from datetime import date, datetime
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    phase_id: Mapped[int | None] = mapped_column(ForeignKey("phases.id"))
    activity_code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    early_start: Mapped[int] = mapped_column(Integer, default=0)
    early_finish: Mapped[int] = mapped_column(Integer, default=0)
    late_start: Mapped[int] = mapped_column(Integer, default=0)
    late_finish: Mapped[int] = mapped_column(Integer, default=0)
    total_float: Mapped[int] = mapped_column(Integer, default=0)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="not_started")
    percent_complete: Mapped[float] = mapped_column(Float, default=0)
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_finish: Mapped[date | None] = mapped_column(Date)
    actual_start: Mapped[date | None] = mapped_column(Date)
    actual_finish: Mapped[date | None] = mapped_column(Date)
    assigned_to: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    dependencies: Mapped[list["ActivityDependency"]] = relationship(
        back_populates="activity", foreign_keys="ActivityDependency.activity_id", cascade="all, delete-orphan"
    )


class ActivityDependency(Base):
    __tablename__ = "activity_dependencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)
    predecessor_id: Mapped[int] = mapped_column(ForeignKey("activities.id"), nullable=False)
    dependency_type: Mapped[str] = mapped_column(String(5), default="FS")
    lag_days: Mapped[int] = mapped_column(Integer, default=0)

    activity: Mapped["Activity"] = relationship(foreign_keys=[activity_id], back_populates="dependencies")
    predecessor: Mapped["Activity"] = relationship(foreign_keys=[predecessor_id])


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    target_date: Mapped[date | None] = mapped_column(Date)
    actual_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="upcoming")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Decision(Base):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    activity_id: Mapped[int | None] = mapped_column(ForeignKey("activities.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, decided
    choice_made: Mapped[str | None] = mapped_column(String(500))
    impact_level: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    knowledge_term: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime)

    activity: Mapped["Activity"] = relationship()
