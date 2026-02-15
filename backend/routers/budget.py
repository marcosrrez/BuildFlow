from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.budget import BudgetCategory, BudgetItem, CostEntry, ChangeOrder, Bid
from backend.schemas.budget import (
    BudgetCategoryCreate, BudgetCategoryRead,
    BudgetItemCreate, BudgetItemUpdate, BudgetItemRead,
    BidCreate, BidUpdate, BidRead,
    CostEntryCreate, CostEntryRead,
    ChangeOrderCreate, ChangeOrderUpdate, ChangeOrderRead,
    BudgetSummary, CostSuggestionRead
)
from backend.schemas.analytics import BudgetVarianceResult, CashFlowResult
from backend.services.analytics import run_budget_variance, run_cash_flow_forecast
from backend.services.costs import CostService

router = APIRouter()


@router.get("/projects/{project_id}/budget/suggest", response_model=list[CostSuggestionRead])
def suggest_budget(project_id: int, category_id: int, db: Session = Depends(get_db)):
    from backend.models.project import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    
    cat = db.query(BudgetCategory).filter(BudgetCategory.id == category_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
        
    return CostService.get_suggestions(cat.code, state=project.state, city=project.city)


@router.get("/projects/{project_id}/budget/summary", response_model=BudgetSummary)
def budget_summary(project_id: int, db: Session = Depends(get_db)):
    from backend.models.project import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    items = db.query(BudgetItem).filter(BudgetItem.project_id == project_id).all()
    total_budget = sum(i.current_budget for i in items) or (project.total_budget if project else 0)
    total_committed = sum(i.committed_cost for i in items)
    total_actual = sum(i.actual_cost for i in items)
    total_forecast = sum(i.forecast_cost for i in items)
    variance = total_budget - total_forecast
    variance_pct = (variance / total_budget * 100) if total_budget else 0

    cats = db.query(BudgetCategory).filter(BudgetCategory.project_id == project_id).order_by(BudgetCategory.sort_order).all()
    cat_data = []
    for c in cats:
        c_items = [i for i in items if i.category_id == c.id]
        cat_data.append({
            "id": c.id, "name": c.name, "code": c.code,
            "budgeted": c.budgeted_amount,
            "committed": sum(i.committed_cost for i in c_items),
            "actual": sum(i.actual_cost for i in c_items),
            "forecast": sum(i.forecast_cost for i in c_items),
        })

    return BudgetSummary(
        total_budget=total_budget, total_committed=total_committed,
        total_actual=total_actual, total_forecast=total_forecast,
        variance=variance, variance_percent=round(variance_pct, 2),
        categories=cat_data,
    )


@router.get("/projects/{project_id}/budget/categories", response_model=list[BudgetCategoryRead])
def list_categories(project_id: int, db: Session = Depends(get_db)):
    return db.query(BudgetCategory).filter(BudgetCategory.project_id == project_id).order_by(BudgetCategory.sort_order).all()


@router.post("/projects/{project_id}/budget/categories", response_model=BudgetCategoryRead, status_code=201)
def create_category(project_id: int, data: BudgetCategoryCreate, db: Session = Depends(get_db)):
    cat = BudgetCategory(project_id=project_id, **data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/projects/{project_id}/budget/categories/{cat_id}", status_code=204)
def delete_category(project_id: int, cat_id: int, db: Session = Depends(get_db)):
    cat = db.query(BudgetCategory).filter(BudgetCategory.id == cat_id, BudgetCategory.project_id == project_id).first()
    if not cat:
        raise HTTPException(404, "Budget category not found")
    db.delete(cat)
    db.commit()


@router.get("/projects/{project_id}/budget/items", response_model=list[BudgetItemRead])
def list_items(project_id: int, category_id: int | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(BudgetItem).filter(BudgetItem.project_id == project_id)
    if category_id:
        q = q.filter(BudgetItem.category_id == category_id)
    return q.all()


@router.post("/projects/{project_id}/budget/items", response_model=BudgetItemRead, status_code=201)
def create_item(project_id: int, data: BudgetItemCreate, db: Session = Depends(get_db)):
    item = BudgetItem(project_id=project_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/projects/{project_id}/budget/items/{item_id}", response_model=BudgetItemRead)
def update_item(project_id: int, item_id: int, data: BudgetItemUpdate, db: Session = Depends(get_db)):
    item = db.query(BudgetItem).filter(BudgetItem.id == item_id, BudgetItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Budget item not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(item, key, val)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/projects/{project_id}/budget/items/{item_id}", status_code=204)
def delete_item(project_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.query(BudgetItem).filter(BudgetItem.id == item_id, BudgetItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Budget item not found")
    db.delete(item)
    db.commit()


@router.post("/projects/{project_id}/budget/items/{item_id}/costs", response_model=CostEntryRead, status_code=201)
def add_cost_entry(project_id: int, item_id: int, data: CostEntryCreate, db: Session = Depends(get_db)):
    item = db.query(BudgetItem).filter(BudgetItem.id == item_id, BudgetItem.project_id == project_id).first()
    if not item:
        raise HTTPException(404, "Budget item not found")
    entry = CostEntry(budget_item_id=item_id, project_id=project_id, **data.model_dump())
    db.add(entry)
    if data.entry_type == "actual":
        item.actual_cost += data.amount
    elif data.entry_type == "committed":
        item.committed_cost += data.amount
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/projects/{project_id}/budget/change-orders", response_model=list[ChangeOrderRead])
def list_change_orders(project_id: int, db: Session = Depends(get_db)):
    return db.query(ChangeOrder).filter(ChangeOrder.project_id == project_id).all()


@router.post("/projects/{project_id}/budget/change-orders", response_model=ChangeOrderRead, status_code=201)
def create_change_order(project_id: int, data: ChangeOrderCreate, db: Session = Depends(get_db)):
    co = ChangeOrder(project_id=project_id, **data.model_dump())
    db.add(co)
    db.commit()
    db.refresh(co)
    return co


@router.put("/projects/{project_id}/budget/change-orders/{co_id}", response_model=ChangeOrderRead)
def update_change_order(project_id: int, co_id: int, data: ChangeOrderUpdate, db: Session = Depends(get_db)):
    co = db.query(ChangeOrder).filter(ChangeOrder.id == co_id, ChangeOrder.project_id == project_id).first()
    if not co:
        raise HTTPException(404, "Change order not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(co, key, val)
    db.commit()
    db.refresh(co)
    return co


@router.delete("/projects/{project_id}/budget/change-orders/{co_id}", status_code=204)
def delete_change_order(project_id: int, co_id: int, db: Session = Depends(get_db)):
    co = db.query(ChangeOrder).filter(ChangeOrder.id == co_id, ChangeOrder.project_id == project_id).first()
    if not co:
        raise HTTPException(404, "Change order not found")
    db.delete(co)
    db.commit()


@router.get("/projects/{project_id}/budget/variance-analysis", response_model=BudgetVarianceResult)
def budget_variance_analysis(project_id: int, db: Session = Depends(get_db)):
    return run_budget_variance(db, project_id)


@router.get("/projects/{project_id}/budget/cashflow-forecast", response_model=CashFlowResult)
def cashflow_forecast(project_id: int, db: Session = Depends(get_db)):
    return run_cash_flow_forecast(db, project_id)


# Bid Management (Bid Leveling)
@router.get("/projects/{project_id}/budget/items/{item_id}/bids", response_model=list[BidRead])
def list_bids(project_id: int, item_id: int, db: Session = Depends(get_db)):
    return db.query(Bid).filter(Bid.project_id == project_id, Bid.budget_item_id == item_id).all()


@router.post("/projects/{project_id}/budget/items/{item_id}/bids", response_model=BidRead, status_code=201)
def create_bid(project_id: int, item_id: int, data: BidCreate, db: Session = Depends(get_db)):
    bid = Bid(project_id=project_id, **data.model_dump())
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return bid


@router.put("/projects/{project_id}/budget/bids/{bid_id}", response_model=BidRead)
def update_bid(project_id: int, bid_id: int, data: BidUpdate, db: Session = Depends(get_db)):
    bid = db.query(Bid).filter(Bid.id == bid_id, Bid.project_id == project_id).first()
    if not bid:
        raise HTTPException(404, "Bid not found")
    
    # If this bid is being selected, unselect others for this item
    update_data = data.model_dump(exclude_unset=True)
    if update_data.get("is_selected"):
        db.query(Bid).filter(Bid.budget_item_id == bid.budget_item_id).update({"is_selected": False})
        
    for key, val in update_data.items():
        setattr(bid, key, val)
    db.commit()
    db.refresh(bid)
    return bid


@router.delete("/projects/{project_id}/budget/bids/{bid_id}", status_code=204)
def delete_bid(project_id: int, bid_id: int, db: Session = Depends(get_db)):
    bid = db.query(Bid).filter(Bid.id == bid_id, Bid.project_id == project_id).first()
    if not bid:
        raise HTTPException(404, "Bid not found")
    db.delete(bid)
    db.commit()
