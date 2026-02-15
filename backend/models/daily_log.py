from datetime import date, datetime
from sqlalchemy import Integer, String, Float, Date, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class DailyLog(Base):
    __tablename__ = "daily_logs"
    __table_args__ = (UniqueConstraint("project_id", "log_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    report_number: Mapped[str | None] = mapped_column(String(20))
    weather_temp: Mapped[float | None] = mapped_column(Float)
    weather_condition: Mapped[str | None] = mapped_column(String(50))
    weather_wind: Mapped[float | None] = mapped_column(Float)
    weather_humidity: Mapped[float | None] = mapped_column(Float)
    weather_impact: Mapped[str | None] = mapped_column(String(20))
    work_summary: Mapped[str | None] = mapped_column(Text)
    work_planned: Mapped[str | None] = mapped_column(Text)
    issues: Mapped[str | None] = mapped_column(Text)
    safety_incidents: Mapped[int] = mapped_column(Integer, default=0)
    safety_notes: Mapped[str | None] = mapped_column(Text)
    prepared_by: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    crew_entries: Mapped[list["DailyLogCrew"]] = relationship(back_populates="daily_log", cascade="all, delete-orphan")
    work_items: Mapped[list["DailyLogWorkItem"]] = relationship(back_populates="daily_log", cascade="all, delete-orphan")
    photos: Mapped[list["DailyLogPhoto"]] = relationship(back_populates="daily_log", cascade="all, delete-orphan")


class DailyLogCrew(Base):
    __tablename__ = "daily_log_crew"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    daily_log_id: Mapped[int] = mapped_column(ForeignKey("daily_logs.id"), nullable=False)
    trade: Mapped[str] = mapped_column(String(50), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(200))
    headcount: Mapped[int] = mapped_column(Integer, default=0)
    hours_worked: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    daily_log: Mapped["DailyLog"] = relationship(back_populates="crew_entries")


class DailyLogWorkItem(Base):
    __tablename__ = "daily_log_work_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    daily_log_id: Mapped[int] = mapped_column(ForeignKey("daily_logs.id"), nullable=False)
    trade: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="completed")
    notes: Mapped[str | None] = mapped_column(Text)

    daily_log: Mapped["DailyLog"] = relationship(back_populates="work_items")


class DailyLogPhoto(Base):
    __tablename__ = "daily_log_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    daily_log_id: Mapped[int] = mapped_column(ForeignKey("daily_logs.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    daily_log: Mapped["DailyLog"] = relationship(back_populates="photos")
