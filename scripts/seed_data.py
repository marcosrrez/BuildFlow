"""Seed BuildFlow with a sample home build project."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import date, timedelta
from backend.database import Base, engine, SessionLocal
import backend.models  # noqa: F401
from backend.models.project import Project, Phase
from backend.models.budget import BudgetCategory, BudgetItem
from backend.models.schedule import Activity, ActivityDependency, Milestone
from backend.models.permit import Permit, Inspection
from backend.models.punchlist import PunchList
from backend.models.subcontractor import Subcontractor
from backend.models.document import DocumentCategory

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Project
today = date.today()
project = Project(
    name="123 Oakwood Drive - New Home",
    address="123 Oakwood Drive",
    city="Austin",
    state="TX",
    zip_code="78745",
    lot_number="Lot 42",
    total_budget=425000,
    start_date=today,
    target_end_date=today + timedelta(days=270),
    status="active",
    notes="3BR/2.5BA single-family residence, 2400 sqft",
)
db.add(project)
db.flush()
pid = project.id

# Phases
phases_data = [
    ("Pre-Construction", 0), ("Site Work", 1), ("Foundation", 2),
    ("Framing", 3), ("Rough-In", 4), ("Exterior", 5),
    ("Interior Finishes", 6), ("Landscaping", 7), ("Closeout", 8),
]
for name, order in phases_data:
    db.add(Phase(project_id=pid, name=name, sort_order=order))

# Budget Categories
cats = [
    ("01-SITE", "Site Work", 25000), ("02-FOUND", "Foundation", 35000),
    ("03-FRAME", "Framing", 55000), ("04-ROOF", "Roofing", 18000),
    ("05-PLUMB", "Plumbing", 28000), ("06-ELEC", "Electrical", 24000),
    ("07-HVAC", "HVAC", 22000), ("08-INSUL", "Insulation", 8000),
    ("09-DRYWL", "Drywall", 18000), ("10-FLOOR", "Flooring", 22000),
    ("11-PAINT", "Painting", 12000), ("12-FIXT", "Fixtures & Appliances", 35000),
    ("13-LAND", "Landscaping", 15000), ("14-PERMIT", "Permits & Fees", 12000),
    ("15-CONTG", "Contingency", 42500),
]
cat_ids = {}
for i, (code, name, amt) in enumerate(cats):
    c = BudgetCategory(project_id=pid, code=code, name=name, budgeted_amount=amt, sort_order=i)
    db.add(c)
    db.flush()
    cat_ids[code] = c.id

# Sample budget items
items = [
    ("01-SITE", "SITE-001", "Clearing & grading", 8000),
    ("01-SITE", "SITE-002", "Driveway gravel", 5000),
    ("01-SITE", "SITE-003", "Temporary utilities", 3500),
    ("02-FOUND", "FOUND-001", "Excavation", 12000),
    ("02-FOUND", "FOUND-002", "Footings & walls", 18000),
    ("02-FOUND", "FOUND-003", "Waterproofing & backfill", 5000),
    ("03-FRAME", "FRAME-001", "Lumber package", 32000),
    ("03-FRAME", "FRAME-002", "Framing labor", 20000),
    ("04-ROOF", "ROOF-001", "Roofing materials & labor", 18000),
    ("05-PLUMB", "PLUMB-001", "Rough plumbing", 16000),
    ("05-PLUMB", "PLUMB-002", "Finish plumbing & fixtures", 12000),
    ("06-ELEC", "ELEC-001", "Rough electrical", 14000),
    ("06-ELEC", "ELEC-002", "Finish electrical & fixtures", 10000),
    ("07-HVAC", "HVAC-001", "HVAC system install", 22000),
]
for code, icode, desc, amt in items:
    db.add(BudgetItem(
        category_id=cat_ids[code], project_id=pid,
        item_code=icode, description=desc,
        original_budget=amt, current_budget=amt,
    ))

# Permits
permits = [
    ("building", "City of Austin Building Dept"),
    ("electrical", "City of Austin Building Dept"),
    ("plumbing", "City of Austin Building Dept"),
    ("mechanical", "City of Austin Building Dept"),
]
for ptype, juris in permits:
    p = Permit(project_id=pid, permit_type=ptype, jurisdiction=juris, status="draft")
    db.add(p)

# Milestones
milestones = [
    ("Permits Approved", today + timedelta(days=14)),
    ("Foundation Complete", today + timedelta(days=45)),
    ("Framing Complete", today + timedelta(days=85)),
    ("Dry-In (Roof & Windows)", today + timedelta(days=100)),
    ("Rough-In Complete", today + timedelta(days=130)),
    ("Drywall Complete", today + timedelta(days=160)),
    ("Final Inspection", today + timedelta(days=250)),
    ("Certificate of Occupancy", today + timedelta(days=260)),
]
for name, tdate in milestones:
    db.add(Milestone(project_id=pid, name=name, target_date=tdate))

# Punch List
db.add(PunchList(project_id=pid, name="Main Punch List", status="Active"))

# Subcontractors
subs = [
    ("Hill Country Excavating", "Mike Torres", "Excavation", 25000, "512-555-0101"),
    ("Solid Rock Foundations", "Jim Baker", "Concrete", 35000, "512-555-0102"),
    ("Austin Frame Masters", "Carlos Reyes", "Framing", 55000, "512-555-0103"),
    ("Lone Star Roofing", "Dan Smith", "Roofing", 18000, "512-555-0104"),
    ("Central TX Plumbing", "Sarah Chen", "Plumbing", 28000, "512-555-0105"),
    ("Spark Electric", "Tom Davis", "Electrical", 24000, "512-555-0106"),
    ("Cool Breeze HVAC", "Amy Wilson", "HVAC", 22000, "512-555-0107"),
    ("Perfect Finish Drywall", "Pedro Martinez", "Drywall", 18000, "512-555-0108"),
    ("Pro Painters LLC", "Lisa Brown", "Painting", 12000, "512-555-0109"),
    ("Texas Floor Co", "Mark Johnson", "Flooring", 22000, "512-555-0110"),
]
for company, contact, trade, amt, phone in subs:
    db.add(Subcontractor(
        project_id=pid, company_name=company, contact_name=contact,
        trade=trade, contract_amount=amt, phone=phone,
        retention_percent=0.10, status="active",
    ))

# Document categories
doc_cats = ["Contracts", "Permits", "Plans & Drawings", "Specifications",
            "Insurance", "Warranties", "Lien Waivers", "Photos", "Reports"]
for i, name in enumerate(doc_cats):
    db.add(DocumentCategory(project_id=pid, name=name, sort_order=i))

db.commit()
pname = project.name
db.close()
print(f"Seeded project '{pname}' (ID: {pid}) with:")
print(f"  - {len(phases_data)} phases")
print(f"  - {len(cats)} budget categories, {len(items)} budget items")
print(f"  - {len(permits)} permits")
print(f"  - {len(milestones)} milestones")
print(f"  - {len(subs)} subcontractors")
print(f"  - {len(doc_cats)} document categories")
print("Ready to go!")
