from datetime import date, datetime
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class PunchList(Base):
    __tablename__ = "punch_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    walk_date: Mapped[date | None] = mapped_column(Date)
    attendees: Mapped[str | None] = mapped_column(Text)
    area: Mapped[str | None] = mapped_column(String(200))
    list_type: Mapped[str] = mapped_column(String(20), default="Punch")
    status: Mapped[str] = mapped_column(String(20), default="Active")
    created_by: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["PunchItem"]] = relationship(back_populates="punch_list", cascade="all, delete-orphan")


class PunchItem(Base):
    __tablename__ = "punch_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    punch_list_id: Mapped[int] = mapped_column(ForeignKey("punch_lists.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    building: Mapped[str | None] = mapped_column(String(100))
    floor: Mapped[str | None] = mapped_column(String(50))
    room: Mapped[str | None] = mapped_column(String(100))
    trade: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="Medium")
    status: Mapped[str] = mapped_column(String(30), default="Open")
    assigned_to: Mapped[str | None] = mapped_column(String(200))
    assigned_date: Mapped[date | None] = mapped_column(Date)
    due_date: Mapped[date | None] = mapped_column(Date)
    photo_before_path: Mapped[str | None] = mapped_column(String(500))
    photo_after_path: Mapped[str | None] = mapped_column(String(500))
    spec_reference: Mapped[str | None] = mapped_column(String(200))
    completed_by: Mapped[str | None] = mapped_column(String(200))
    completed_date: Mapped[date | None] = mapped_column(Date)
    completion_notes: Mapped[str | None] = mapped_column(Text)
    verified_by: Mapped[str | None] = mapped_column(String(200))
    verified_date: Mapped[date | None] = mapped_column(Date)
    verification_notes: Mapped[str | None] = mapped_column(Text)
    back_charge: Mapped[bool] = mapped_column(Boolean, default=False)
    back_charge_amount: Mapped[float] = mapped_column(Float, default=0)
    back_charge_ref: Mapped[str | None] = mapped_column(String(100))
    created_by: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    punch_list: Mapped["PunchList"] = relationship(back_populates="items")
