from datetime import date, datetime
from sqlalchemy import Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class Subcontractor(Base):
    __tablename__ = "subcontractors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(30))
    trade: Mapped[str] = mapped_column(String(50), nullable=False)
    license_number: Mapped[str | None] = mapped_column(String(50))
    insurance_expiry: Mapped[date | None] = mapped_column(Date)
    contract_amount: Mapped[float] = mapped_column(Float, default=0)
    retention_percent: Mapped[float] = mapped_column(Float, default=0.10)
    contract_start: Mapped[date | None] = mapped_column(Date)
    contract_end: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="active")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payments: Mapped[list["SubcontractorPayment"]] = relationship(back_populates="subcontractor", cascade="all, delete-orphan")


class SubcontractorPayment(Base):
    __tablename__ = "subcontractor_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subcontractor_id: Mapped[int] = mapped_column(ForeignKey("subcontractors.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    invoice_number: Mapped[str | None] = mapped_column(String(50))
    invoice_date: Mapped[date | None] = mapped_column(Date)
    gross_amount: Mapped[float] = mapped_column(Float, nullable=False)
    retention_held: Mapped[float] = mapped_column(Float, default=0)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="invoiced")
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    paid_date: Mapped[date | None] = mapped_column(Date)
    check_number: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subcontractor: Mapped["Subcontractor"] = relationship(back_populates="payments")
    lien_waiver: Mapped["LienWaiver | None"] = relationship(back_populates="payment", uselist=False, cascade="all, delete-orphan")


class LienWaiver(Base):
    __tablename__ = "lien_waivers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("subcontractor_payments.id"), nullable=False)
    waiver_type: Mapped[str] = mapped_column(String(30), nullable=False)
    through_date: Mapped[date | None] = mapped_column(Date)
    amount: Mapped[float | None] = mapped_column(Float)
    received_date: Mapped[date | None] = mapped_column(Date)
    file_path: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    payment: Mapped["SubcontractorPayment"] = relationship(back_populates="lien_waiver")
