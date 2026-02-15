from datetime import date, datetime
from sqlalchemy import Integer, String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base


class BudgetCategory(Base):
    __tablename__ = "budget_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    budgeted_amount: Mapped[float] = mapped_column(Float, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["BudgetItem"]] = relationship(back_populates="category", cascade="all, delete-orphan")


class BudgetItem(Base):
    __tablename__ = "budget_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("budget_categories.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    item_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    original_budget: Mapped[float] = mapped_column(Float, default=0)
    current_budget: Mapped[float] = mapped_column(Float, default=0)
    committed_cost: Mapped[float] = mapped_column(Float, default=0)
    actual_cost: Mapped[float] = mapped_column(Float, default=0)
    forecast_cost: Mapped[float] = mapped_column(Float, default=0)
    percent_complete: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category: Mapped["BudgetCategory"] = relationship(back_populates="items")
    cost_entries: Mapped[list["CostEntry"]] = relationship(back_populates="budget_item", cascade="all, delete-orphan")
    bids: Mapped[list["Bid"]] = relationship(back_populates="budget_item", cascade="all, delete-orphan")


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_item_id: Mapped[int] = mapped_column(ForeignKey("budget_items.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    contractor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    is_selected: Mapped[bool] = mapped_column(Integer, default=0)  # SQLite handles bool as 0/1
    notes: Mapped[str | None] = mapped_column(Text)
    proposal_path: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    budget_item: Mapped["BudgetItem"] = relationship(back_populates="bids")


class CostEntry(Base):
    __tablename__ = "cost_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_item_id: Mapped[int] = mapped_column(ForeignKey("budget_items.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    entry_type: Mapped[str] = mapped_column(String(20), nullable=False)
    vendor: Mapped[str | None] = mapped_column(String(200))
    invoice_number: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    receipt_path: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    budget_item: Mapped["BudgetItem"] = relationship(back_populates="cost_entries")


class ChangeOrder(Base):
    __tablename__ = "change_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    co_number: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)
    cost_impact: Mapped[float] = mapped_column(Float, default=0)
    time_impact_days: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    requested_by: Mapped[str | None] = mapped_column(String(100))
    requested_date: Mapped[date | None] = mapped_column(Date)
    approved_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
