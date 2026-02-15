from datetime import date, datetime
from sqlalchemy import Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Permit(Base):
    __tablename__ = "permits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    permit_type: Mapped[str] = mapped_column(String(30), nullable=False)
    permit_number: Mapped[str | None] = mapped_column(String(50))
    jurisdiction: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="draft")
    application_date: Mapped[date | None] = mapped_column(Date)
    issued_date: Mapped[date | None] = mapped_column(Date)
    expiry_date: Mapped[date | None] = mapped_column(Date)
    description: Mapped[str | None] = mapped_column(Text)
    project_value: Mapped[float] = mapped_column(Float, default=0)
    applicant_name: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents: Mapped[list["PermitDocument"]] = relationship(back_populates="permit", cascade="all, delete-orphan")
    inspections: Mapped[list["Inspection"]] = relationship(back_populates="permit", cascade="all, delete-orphan")
    fees: Mapped[list["PermitFee"]] = relationship(back_populates="permit", cascade="all, delete-orphan")


class PermitDocument(Base):
    __tablename__ = "permit_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(ForeignKey("permits.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    file_path: Mapped[str | None] = mapped_column(String(500))
    submitted_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    version: Mapped[int] = mapped_column(Integer, default=1)
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    permit: Mapped["Permit"] = relationship(back_populates="documents")


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(ForeignKey("permits.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    inspection_type: Mapped[str] = mapped_column(String(100), nullable=False)
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    completed_date: Mapped[date | None] = mapped_column(Date)
    inspector_name: Mapped[str | None] = mapped_column(String(200))
    result: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    corrections: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    permit: Mapped["Permit"] = relationship(back_populates="inspections")


class PermitFee(Base):
    __tablename__ = "permit_fees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permit_id: Mapped[int] = mapped_column(ForeignKey("permits.id"), nullable=False)
    fee_type: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date)
    paid_date: Mapped[date | None] = mapped_column(Date)
    receipt_number: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    permit: Mapped["Permit"] = relationship(back_populates="fees")
