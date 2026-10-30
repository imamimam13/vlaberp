# BUNDLE BACKEND CODEBASE VLAB-ERP ENTERPRISE (FASTAPI & SQLALCHEMY)



---
# FILE: backend/app/main.py
---
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal, init_db_schema
from backend.app.routers import auth, simulation, vendors, crm, manufacturing, accounting, hr, inventory, tenants
from backend.app.routers import settings as settings_router
from backend.app.seed import seed_database
from backend.app.services.tenant_service import seed_multi_tenants

# Create DB tables & sync schema
init_db_schema()

# Auto seed database on startup if empty
seed_database()

# Ensure multi-tenant companies exist
startup_db = SessionLocal()
try:
    seed_multi_tenants(startup_db)
finally:
    startup_db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Virtual Lab & Simulation Platform for Enterprise Resource Planning",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(simulation.router, prefix=settings.API_V1_STR)
app.include_router(vendors.router, prefix=settings.API_V1_STR)
app.include_router(crm.router, prefix=settings.API_V1_STR)
app.include_router(manufacturing.router, prefix=settings.API_V1_STR)
app.include_router(accounting.router, prefix=settings.API_V1_STR)
app.include_router(hr.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(tenants.router, prefix=settings.API_V1_STR)
app.include_router(settings_router.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "platform": "VLab-ERP: Virtual Lab & Business Simulation Engine",
        "status": "operational",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    db = SessionLocal()
    try:
        from backend.app.models.models import Company, User, Product, Vendor
        co_count = db.query(Company).count()
        usr_count = db.query(User).count()
        prod_count = db.query(Product).count()
        ven_count = db.query(Vendor).count()
        return {
            "status": "healthy",
            "database": "connected",
            "db_path": str(settings.DATABASE_URL),
            "stats": {
                "companies": co_count,
                "users": usr_count,
                "products": prod_count,
                "vendors": ven_count
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "error",
            "detail": str(e)
        }
    finally:
        db.close()


```


---
# FILE: backend/app/database.py
---
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db_schema():
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            res = conn.execute(text("PRAGMA table_info(class_sessions)")).fetchall()
            col_names = [r[1] for r in res]
            if "academic_term" not in col_names:
                conn.execute(text("ALTER TABLE class_sessions ADD COLUMN academic_term VARCHAR(50) DEFAULT 'Semester Ganjil 2026/2027'"))
            if "department" not in col_names:
                conn.execute(text("ALTER TABLE class_sessions ADD COLUMN department VARCHAR(100) DEFAULT 'S1 Manajemen & Akuntansi Bisnis Digital FEB'"))
            if "description" not in col_names:
                conn.execute(text("ALTER TABLE class_sessions ADD COLUMN description TEXT"))
            conn.commit()
        except Exception as e:
            print(f"Schema sync notice: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```


---
# FILE: backend/app/config.py
---
```python
import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve repository root directory to ensure absolute database persistence
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = ROOT_DIR / "vlaberp.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "VLab-ERP: Virtual Lab & Business Simulation Platform"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "vlab-erp-super-secret-key-for-university-simulation-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

    class Config:
        case_sensitive = True

settings = Settings()

```


---
# FILE: backend/app/models/models.py
---
```python
import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role = Column(String(20), default="MAHASISWA")  # ADMIN, DOSEN, MAHASISWA
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    assigned_classes = relationship("ClassSessionLecturer", back_populates="user", cascade="all, delete-orphan")

class ClassSession(Base):
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    lecturer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    academic_term = Column(String(50), default="Semester Ganjil 2026/2027")
    department = Column(String(100), default="S1 Manajemen & Akuntansi Bisnis Digital FEB")
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # active, archived
    progression_mode = Column(String(30), default="problem_based")  # problem_based, turn_based
    current_round = Column(Integer, default=1)
    total_rounds = Column(Integer, default=12)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    companies = relationship("Company", back_populates="session", cascade="all, delete-orphan")
    team_lecturers = relationship("ClassSessionLecturer", back_populates="session", cascade="all, delete-orphan")

class ClassSessionLecturer(Base):
    __tablename__ = "class_session_lecturers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_title = Column(String(100), default="Dosen Pengampu")  # Koordinator, Pemasaran, SDM, Keuangan, Operasional
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ClassSession", back_populates="team_lecturers")
    user = relationship("User", back_populates="assigned_classes")

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=False)
    name = Column(String(100), nullable=False)
    industry = Column(String(50), default="Manufaktur Elektronik Smart Device")
    team_leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    initial_capital = Column(Float, default=500000000.0)
    current_cash = Column(Float, default=500000000.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ClassSession", back_populates="companies")
    sim_state = relationship("SimulationState", back_populates="company", uselist=False, cascade="all, delete-orphan")
    slider_config = relationship("SimulationSlider", back_populates="company", uselist=False, cascade="all, delete-orphan")

class SimulationState(Base):
    __tablename__ = "simulation_states"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False)
    current_round = Column(Integer, default=1)
    period_name = Column(String(50), default="Bulan 1 (Januari)")
    cash = Column(Float, default=500000000.0)
    revenue = Column(Float, default=0.0)
    expenses = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    csat_score = Column(Float, default=85.0)  # 0 - 100
    worker_morale = Column(Float, default=90.0)  # 0 - 100
    machine_health = Column(Float, default=95.0)  # 0 - 100
    supplier_health = Column(Float, default=90.0)  # 0 - 100
    overall_score = Column(Float, default=0.0)
    is_strike_active = Column(Boolean, default=False)
    strike_reason = Column(String(200), nullable=True)
    active_case_title = Column(String(200), nullable=True)
    active_case_description = Column(Text, nullable=True)

    company = relationship("Company", back_populates="sim_state")

class SimulationSlider(Base):
    __tablename__ = "simulation_sliders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=True)
    is_company_override = Column(Boolean, default=False)
    supply_disruption = Column(Float, default=20.0)      # 0 - 100%
    machine_breakdown_risk = Column(Float, default=15.0) # 0 - 100%
    market_volatility = Column(Float, default=30.0)      # 0 - 100%
    labor_strike_risk = Column(Float, default=10.0)      # 0 - 100%
    bad_debt_risk = Column(Float, default=15.0)          # 0 - 100%
    competitor_price_war = Column(Float, default=25.0)   # 0 - 100%

    company = relationship("Company", back_populates="slider_config")

class ScenarioCase(Base):
    __tablename__ = "scenario_cases"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    code = Column(String(50), index=True)
    stage_order = Column(Integer, default=1)
    title = Column(String(200), nullable=False)
    category = Column(String(50), default="general")  # procurement, production, crm, accounting, hr
    description = Column(Text, nullable=False)
    trigger_hint = Column(Text, nullable=True)
    solvable_workflow = Column(Text, nullable=False)
    resolution_criteria = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, active, resolved, failed
    round_introduced = Column(Integer, default=1)
    resolution_score = Column(Float, default=0.0)
    grade = Column(String(5), default="A")
    step_scores = Column(Text, nullable=True)  # JSON string of step breakdown
    fact_sheet_data = Column(Text, nullable=True)  # JSON string of pedagogical factsheet
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50), default="Komponen Presisi & Bahan Baku")
    lead_time_days = Column(Integer, default=5)
    fulfillment_rate = Column(Float, default=95.0)  # Completion rate %
    on_time_rate = Column(Float, default=92.0)      # Ketaatan %
    defect_rate = Column(Float, default=1.5)        # % cacat bahan mentah
    price_multiplier = Column(Float, default=1.0)   # 1.0 = standard
    min_order_qty = Column(Integer, default=10)
    credit_terms_days = Column(Integer, default=30)
    notes = Column(Text, nullable=True)

    metrics = relationship("VendorMetricHistory", back_populates="vendor", cascade="all, delete-orphan")

class VendorMetricHistory(Base):
    __tablename__ = "vendor_metric_histories"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    period_label = Column(String(50), nullable=False)  # e.g. "Bulan -3", "Bulan -2"
    fulfillment_rate = Column(Float, default=95.0)
    on_time_rate = Column(Float, default=90.0)
    defect_rate = Column(Float, default=2.0)
    price_index = Column(Float, default=100.0)

    vendor = relationship("Vendor", back_populates="metrics")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    sku = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    product_type = Column(String(30), default="raw_material")  # raw_material, wip, finished_good
    uom = Column(String(20), default="pcs")
    cost_price = Column(Float, default=0.0)
    list_price = Column(Float, default=0.0)
    current_stock = Column(Float, default=0.0)
    min_safety_stock = Column(Float, default=20.0)

class BillOfMaterials(Base):
    __tablename__ = "bill_of_materials"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    finished_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(100), nullable=False)
    version = Column(String(20), default="v1.0")
    is_active = Column(Boolean, default=True)

    items = relationship("BOMItem", back_populates="bom", cascade="all, delete-orphan")

class BOMItem(Base):
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, index=True)
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    raw_product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_required = Column(Float, default=1.0)

    bom = relationship("BillOfMaterials", back_populates="items")

class WorkCenter(Base):
    __tablename__ = "work_centers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    capacity_units_per_hour = Column(Float, default=25.0)
    hourly_cost = Column(Float, default=150000.0)
    failure_rate = Column(Float, default=5.0)  # % breakdown probability
    status = Column(String(20), default="operational")  # operational, breakdown, maintenance

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    code = Column(String(50), nullable=False)
    bom_id = Column(Integer, ForeignKey("bill_of_materials.id"), nullable=False)
    work_center_id = Column(Integer, ForeignKey("work_centers.id"), nullable=False)
    qty_to_produce = Column(Integer, default=50)
    qty_produced = Column(Integer, default=0)
    scrap_qty = Column(Integer, default=0)
    status = Column(String(20), default="draft")  # draft, in_progress, completed, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class CRMLead(Base):
    __tablename__ = "crm_leads"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(150), nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=True)
    stage = Column(String(30), default="new")  # new, qualified, proposition, won, lost
    expected_revenue = Column(Float, default=50000000.0)
    probability = Column(Float, default=30.0)  # %
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    credit_rating = Column(String(20), default="medium_risk")  # low_risk, medium_risk, high_risk
    csat_score = Column(Float, default=85.0)
    notes = Column(Text, nullable=True)
    is_complaint = Column(Boolean, default=False)
    complaint_details = Column(Text, nullable=True)
    resolution_action = Column(String(100), nullable=True)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    credit_limit = Column(Float, default=100000000.0)
    credit_rating = Column(String(20), default="low_risk")
    payment_terms_days = Column(Integer, default=30)
    csat_score = Column(Float, default=85.0)

class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    code = Column(String(50), nullable=False)
    total_amount = Column(Float, default=0.0)
    payment_terms = Column(String(50), default="Tempo 30 Hari")
    status = Column(String(20), default="draft")  # draft, confirmed, delivered, invoiced, paid, defaulted
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("SalesOrderItem", back_populates="order", cascade="all, delete-orphan")

class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"

    id = Column(Integer, primary_key=True, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)

    order = relationship("SalesOrder", back_populates="items")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    code = Column(String(50), nullable=False)
    total_amount = Column(Float, default=0.0)
    status = Column(String(20), default="draft")  # draft, sent, received, billed, paid
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("PurchaseOrderItem", back_populates="po", cascade="all, delete-orphan")

class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=10)
    unit_price = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)

    po = relationship("PurchaseOrder", back_populates="items")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    account_type = Column(String(30), nullable=False)  # asset, liability, equity, revenue, expense
    balance = Column(Float, default=0.0)

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    entry_number = Column(String(50), nullable=False)
    entry_date = Column(DateTime, default=datetime.datetime.utcnow)
    reference = Column(String(100), nullable=True)
    memo = Column(String(255), nullable=True)
    is_posted = Column(Boolean, default=True)

    items = relationship("JournalItem", back_populates="entry", cascade="all, delete-orphan")

class JournalItem(Base):
    __tablename__ = "journal_items"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)

    entry = relationship("JournalEntry", back_populates="items")

class DepartmentBudget(Base):
    __tablename__ = "department_budgets"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    department = Column(String(50), nullable=False)  # marketing, production, procurement, hr, r&d
    allocated_amount = Column(Float, default=50000000.0)
    spent_amount = Column(Float, default=0.0)
    period_name = Column(String(50), default="Q1")

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(50), default="Produksi")
    role = Column(String(50), default="Operator Mesin")
    monthly_salary = Column(Float, default=5000000.0)
    morale_score = Column(Float, default=90.0)    # 0 - 100
    fatigue_score = Column(Float, default=20.0)   # 0 - 100
    status = Column(String(20), default="active")  # active, on_strike, resigned

class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String(100), nullable=False)
    channel = Column(String(50), default="Digital Social Ads")
    budget = Column(Float, default=20000000.0)
    spent = Column(Float, default=0.0)
    leads_generated = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    status = Column(String(20), default="active")

class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class CompanyStoryEvent(Base):
    __tablename__ = "company_story_events"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, default=1)
    period_name = Column(String(50), default="Bulan 1 (Januari)")
    domain = Column(String(50), default="general")  # purchasing, manufacturing, crm, hr, accounting
    event_type = Column(String(50), default="scenario_branch")  # scenario_branch, ripple_consequence, black_swan, living_event
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    decision_taken = Column(String(200), nullable=True)
    ripple_summary = Column(Text, nullable=True)  # JSON string of multi-department ripples
    document_data = Column(Text, nullable=True)   # JSON string of generated official document
    created_at = Column(DateTime, default=datetime.datetime.utcnow)



```


---
# FILE: backend/app/schemas/schemas.py
---
```python
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# Token & Auth
class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    full_name: str
    role: str
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    group_label: Optional[str] = None
    session_id: Optional[int] = None

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: str
    password: str
    role: str = "MAHASISWA"
    company_id: Optional[int] = None
    session_id: Optional[int] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[int] = None
    session_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# Simulation State & Sliders
class SimulationSliderUpdate(BaseModel):
    supply_disruption: float
    machine_breakdown_risk: float
    market_volatility: float
    labor_strike_risk: float
    bad_debt_risk: float
    competitor_price_war: float

class SimulationSliderOut(BaseModel):
    id: int
    company_id: Optional[int] = None
    session_id: Optional[int] = None
    supply_disruption: float
    machine_breakdown_risk: float
    market_volatility: float
    labor_strike_risk: float
    bad_debt_risk: float
    competitor_price_war: float

    class Config:
        from_attributes = True

class SimulationStateOut(BaseModel):
    id: int
    company_id: int
    current_round: int
    period_name: str
    cash: float
    revenue: float
    expenses: float
    net_profit: float
    csat_score: float
    worker_morale: float
    machine_health: float
    supplier_health: float
    overall_score: float
    is_strike_active: bool
    strike_reason: Optional[str] = None
    active_case_title: Optional[str] = None
    active_case_description: Optional[str] = None

    class Config:
        from_attributes = True

# Case / Solvable Missions
class ScenarioCaseOut(BaseModel):
    id: int
    code: str
    stage_order: int
    title: str
    category: str
    description: str
    trigger_hint: Optional[str] = None
    solvable_workflow: str
    resolution_criteria: str
    status: str
    round_introduced: int
    resolution_score: float
    grade: Optional[str] = "A"
    step_scores: Optional[str] = None
    fact_sheet_data: Optional[str] = None

    class Config:
        from_attributes = True

class SolveCaseRequest(BaseModel):
    action_taken: str
    notes: Optional[str] = None

# Vendor & Historical Metrics
class VendorMetricOut(BaseModel):
    period_label: str
    fulfillment_rate: float
    on_time_rate: float
    defect_rate: float
    price_index: float

    class Config:
        from_attributes = True

class VendorOut(BaseModel):
    id: int
    company_id: int
    name: str
    category: str
    lead_time_days: int
    fulfillment_rate: float
    on_time_rate: float
    defect_rate: float
    price_multiplier: float
    min_order_qty: int
    credit_terms_days: int
    notes: Optional[str] = None
    metrics: List[VendorMetricOut] = []

    class Config:
        from_attributes = True

# Products
class ProductOut(BaseModel):
    id: int
    company_id: int
    sku: str
    name: str
    product_type: str
    uom: str
    cost_price: float
    list_price: float
    current_stock: float
    min_safety_stock: float

    class Config:
        from_attributes = True

# CRM
class CRMLeadOut(BaseModel):
    id: int
    company_id: int
    title: str
    customer_name: str
    customer_email: Optional[str] = None
    stage: str
    expected_revenue: float
    probability: float
    priority: str
    credit_rating: str
    csat_score: float
    notes: Optional[str] = None
    is_complaint: bool
    complaint_details: Optional[str] = None
    resolution_action: Optional[str] = None

    class Config:
        from_attributes = True

class CRMLeadUpdate(BaseModel):
    stage: Optional[str] = None
    priority: Optional[str] = None
    resolution_action: Optional[str] = None
    notes: Optional[str] = None

# Manufacturing
class WorkCenterOut(BaseModel):
    id: int
    code: str
    name: str
    capacity_units_per_hour: float
    hourly_cost: float
    failure_rate: float
    status: str

    class Config:
        from_attributes = True

class WorkOrderOut(BaseModel):
    id: int
    code: str
    bom_id: int
    work_center_id: int
    qty_to_produce: int
    qty_produced: int
    scrap_qty: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CreateWorkOrder(BaseModel):
    bom_id: int
    work_center_id: int
    qty_to_produce: int

# Accounting & Budgeting
class AccountOut(BaseModel):
    id: int
    code: str
    name: str
    account_type: str
    balance: float

    class Config:
        from_attributes = True

class DepartmentBudgetOut(BaseModel):
    id: int
    department: str
    allocated_amount: float
    spent_amount: float
    period_name: str

    class Config:
        from_attributes = True

# HR
class EmployeeOut(BaseModel):
    id: int
    name: str
    department: str
    role: str
    monthly_salary: float
    morale_score: float
    fatigue_score: float
    status: str

    class Config:
        from_attributes = True

class ResolveStrikeRequest(BaseModel):
    wage_increase_percentage: float = 0.0
    bonus_per_worker: float = 0.0
    overtime_restriction_hours: int = 40
    notes: Optional[str] = None

# Class Session & Lecturer Team Schemas
class LecturerAssignment(BaseModel):
    user_id: int
    role_title: str = "Dosen Pengampu"
    is_primary: bool = False

class ClassSessionLecturerOut(BaseModel):
    id: int
    user_id: int
    username: str
    full_name: str
    email: str
    role_title: str
    is_primary: bool

class ClassSessionCreate(BaseModel):
    name: str
    code: str
    academic_term: Optional[str] = "Semester Ganjil 2026/2027"
    department: Optional[str] = "S1 Manajemen & Akuntansi Bisnis Digital FEB"
    description: Optional[str] = None
    progression_mode: str = "problem_based"
    total_rounds: int = 12
    lecturers: Optional[List[LecturerAssignment]] = []
    auto_provision_groups: Optional[int] = 0
    initial_capital: Optional[float] = 500000000.0

class ClassSessionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    academic_term: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progression_mode: Optional[str] = None
    total_rounds: Optional[int] = None
    lecturers: Optional[List[LecturerAssignment]] = None

class ClassSessionCloneRequest(BaseModel):
    new_name: str
    new_code: str
    academic_term: Optional[str] = None
    department: Optional[str] = None
    clone_companies: bool = True
    differentiate_cases: bool = True

```


---
# FILE: backend/app/seed.py
---
```python
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from backend.app.database import engine, Base, SessionLocal
from backend.app.models.models import (
    User, ClassSession, ClassSessionLecturer, Company, SimulationState, SimulationSlider, ScenarioCase,
    Vendor, VendorMetricHistory, Product, BillOfMaterials, BOMItem,
    WorkCenter, CRMLead, Customer, Account, JournalEntry, JournalItem,
    DepartmentBudget, Employee, MarketingCampaign
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def ensure_team_lecturers(db: Session):
    """Ensures all class sessions have their multidisciplinary team teaching lecturers mapped."""
    sessions = db.query(ClassSession).all()
    dosen_lead = db.query(User).filter(User.username == "dosen").first()
    dosen_mkt = db.query(User).filter(User.username == "dosen.marketing").first()
    dosen_sdm = db.query(User).filter(User.username == "dosen.sdm").first()
    dosen_fin = db.query(User).filter(User.username == "dosen.keuangan").first()

    for s in sessions:
        count = db.query(ClassSessionLecturer).filter(ClassSessionLecturer.session_id == s.id).count()
        if count == 0:
            if dosen_lead:
                db.add(ClassSessionLecturer(session_id=s.id, user_id=dosen_lead.id, role_title="Koordinator Matakuliah & Pengampu Utama", is_primary=True))
            if dosen_mkt:
                db.add(ClassSessionLecturer(session_id=s.id, user_id=dosen_mkt.id, role_title="Dosen Bidang Pemasaran & CRM", is_primary=False))
            if dosen_sdm:
                db.add(ClassSessionLecturer(session_id=s.id, user_id=dosen_sdm.id, role_title="Dosen Bidang SDM & Organisasi", is_primary=False))
            if dosen_fin:
                db.add(ClassSessionLecturer(session_id=s.id, user_id=dosen_fin.id, role_title="Dosen Bidang Keuangan & Akuntansi", is_primary=False))
    db.commit()

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if already seeded
    if db.query(User).filter(User.username == "admin").first():
        ensure_team_lecturers(db)
        print("Database already seeded. Team lecturers verified.")
        db.close()
        return

    print("Seeding initial data...")

    # 1. Users
    admin = User(
        username="admin",
        email="admin@vlaberp.ac.id",
        full_name="System Administrator FEB",
        hashed_password=get_password_hash("admin123"),
        role="ADMIN"
    )
    dosen = User(
        username="dosen",
        email="dosen@vlaberp.ac.id",
        full_name="Tim Dosen Pengampu FEB",
        hashed_password=get_password_hash("dosen123"),
        role="DOSEN"
    )
    dosen_mkt = User(
        username="dosen.marketing",
        email="maya.indah@vlaberp.ac.id",
        full_name="Dr. Maya Indah, S.E., M.M. (Dosen Pemasaran FEB)",
        hashed_password=get_password_hash("dosen123"),
        role="DOSEN"
    )
    dosen_sdm = User(
        username="dosen.sdm",
        email="bambang.prakoso@vlaberp.ac.id",
        full_name="Drs. Bambang Prakoso, M.Psi., M.M. (Dosen SDM FEB)",
        hashed_password=get_password_hash("dosen123"),
        role="DOSEN"
    )
    dosen_fin = User(
        username="dosen.keuangan",
        email="budi.santoso@vlaberp.ac.id",
        full_name="Dr. Ir. Budi Santoso, S.E., Ak., M.Ak. (Dosen Keuangan FEB)",
        hashed_password=get_password_hash("dosen123"),
        role="DOSEN"
    )
    mahasiswa = User(
        username="mahasiswa",
        email="kelompok1.a@mahasiswa.vlaberp.ac.id",
        full_name="Kelompok 1 (Kelas FEB A)",
        hashed_password=get_password_hash("mhs123"),
        role="MAHASISWA"
    )
    mahasiswa_b = User(
        username="mahasiswa_b",
        email="kelompok1.b@mahasiswa.vlaberp.ac.id",
        full_name="Kelompok 1 (Kelas FEB B)",
        hashed_password=get_password_hash("mhs123"),
        role="MAHASISWA"
    )
    db.add_all([admin, dosen, dosen_mkt, dosen_sdm, dosen_fin, mahasiswa, mahasiswa_b])
    db.commit()
    db.refresh(dosen)
    db.refresh(dosen_mkt)
    db.refresh(dosen_sdm)
    db.refresh(dosen_fin)
    db.refresh(mahasiswa)
    db.refresh(mahasiswa_b)

    # 2. Class Sessions (FEB-A and FEB-B)
    session_a = ClassSession(
        name="Praktikum ERP & Simulasi Bisnis - Kelas FEB A",
        code="ERP-FEB-A",
        academic_term="Semester Ganjil 2026/2027",
        department="S1 Manajemen & Bisnis Digital FEB",
        lecturer_id=dosen.id,
        progression_mode="problem_based",
        current_round=1,
        total_rounds=12
    )
    session_b = ClassSession(
        name="Praktikum ERP & Simulasi Bisnis - Kelas FEB B",
        code="ERP-FEB-B",
        academic_term="Semester Ganjil 2026/2027",
        department="S1 Akuntansi & Keuangan FEB",
        lecturer_id=dosen.id,
        progression_mode="problem_based",
        current_round=1,
        total_rounds=12
    )
    db.add_all([session_a, session_b])
    db.commit()
    db.refresh(session_a)
    db.refresh(session_b)
    session = session_a

    # Seed Team Lecturers for Session A and B
    ensure_team_lecturers(db)

    # 3. Company
    company = Company(
        session_id=session.id,
        name="PT Inovasi Cipta Mandiri",
        industry="Manufaktur Perangkat Cerdas (Smart Devices)",
        team_leader_id=mahasiswa.id,
        initial_capital=500000000.0,
        current_cash=500000000.0
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    # 4. Simulation State & Sliders
    sim_state = SimulationState(
        company_id=company.id,
        current_round=1,
        period_name="Bulan 1 (Januari)",
        cash=500000000.0,
        revenue=45000000.0,
        expenses=25000000.0,
        net_profit=20000000.0,
        csat_score=88.5,
        worker_morale=92.0,
        machine_health=95.0,
        supplier_health=91.0,
        overall_score=0.0,
        is_strike_active=False,
        active_case_title="Tahap 1: Due Diligence Vendor & Kesiapan Produksi",
        active_case_description="Kelompok diminta melakukan evaluasi kinerja 4 vendor bahan baku. Teliti grafik ketaatan dan defect rate sebelum menerbitkan PO."
    )
    slider = SimulationSlider(
        company_id=company.id,
        session_id=session.id,
        is_company_override=False,
        supply_disruption=25.0,
        machine_breakdown_risk=15.0,
        market_volatility=30.0,
        labor_strike_risk=10.0,
        bad_debt_risk=15.0,
        competitor_price_war=20.0
    )
    db.add_all([sim_state, slider])
    db.commit()

    # 5. Solvable Scenario Cases (Misi Bertahap)
    cases = [
        ScenarioCase(
            session_id=session.id,
            company_id=company.id,
            code="CASE-01",
            stage_order=1,
            title="Misi 1: Evaluasi Vendor & Pencegahan Bottleneck Bahan Baku",
            category="procurement",
            description="Lini produksi Smartwatch membutuhkan pasokan baterai dan chipset yang konsisten. Ada 4 vendor yang tersedia dengan profil berbeda. Hindari vendor dengan defect rate tinggi yang berisiko merusak mesin di pabrik.",
            trigger_hint="Periksa grafik Completion Rate & Defect History pada menu Pengadaan/Vendor.",
            solvable_workflow="1. Buka modul Vendor/Purchasing -> Bandingkan chart 4 vendor.\n2. Buat Purchase Order (PO) ke vendor terpercaya dengan defect rate < 2%.\n3. Pertahankan safety stock minimal 50 unit.",
            resolution_criteria="PO diterbitkan ke vendor berkualitas, safety stock bahan baku terpenuhi.",
            status="active",
            round_introduced=1,
            resolution_score=0.0,
            grade="-",
            step_scores=None,
            fact_sheet_data=None
        ),
        ScenarioCase(
            session_id=session.id,
            company_id=company.id,
            code="CASE-02",
            stage_order=2,
            title="Misi 2: Penanganan Krisis Keluhan Pelanggan VIP di CRM",
            category="crm",
            description="Klien penting (CV Megah Sentosa) melaporkan 15 unit Smartwatch mengalami layar bergaris dari batch pengiriman sebelumnya dan mengancam memutus kontrak tahunan senilai Rp 150.000.000.",
            trigger_hint="Buka tiket keluhan bernotifikasi Urgent di modul CRM.",
            solvable_workflow="1. Buka modul CRM -> Cari tiket keluhan CV Megah Sentosa.\n2. Pilih tindakan penyelesaian: 'Ganti Unit Baru + Voucher Diskon 10%'.\n3. Terbitkan Credit Note di Akuntansi untuk mencatat retur barang.",
            resolution_criteria="Tiket keluhan terselesaikan, CSAT pulih di atas 80%.",
            status="pending",
            round_introduced=2,
            resolution_score=0.0,
            grade="-",
            step_scores=None,
            fact_sheet_data=None
        ),
        ScenarioCase(
            session_id=session.id,
            company_id=company.id,
            code="CASE-03",
            stage_order=3,
            title="Misi 3: Manajemen Likuiditas Kas & Pencegahan Mogok Kerja Buruh",
            category="hr",
            description="Terjadi penundaan pembayaran dari salah satu pelanggan retail. Jika saldo kas operasional tidak diamankan, pembayaran gaji operator pabrik akan terlambat dan memicu ancaman mogok kerja serikat buruh.",
            trigger_hint="Pantau rasio kas dan indikator Moral Pekerja di modul HR.",
            solvable_workflow="1. Buka modul Akuntansi -> Kurangi pengeluaran promosi non-esensial.\n2. Di modul HR -> Setujui paket uang lembur proporsional.\n3. Pastikan gaji dibayarkan tepat waktu.",
            resolution_criteria="Gaji terbayar, indikator moral buruh di atas 85%, mogok kerja dihindari.",
            status="pending",
            round_introduced=3,
            resolution_score=0.0,
            grade="-",
            step_scores=None,
            fact_sheet_data=None
        )
    ]
    db.add_all(cases)
    db.commit()

    # 6. Realistic Vendors with Historical Charts
    v1 = Vendor(
        company_id=company.id,
        name="PT Surya Logam Presisi",
        category="Casing Aluminium & Mekanikal Presisi",
        lead_time_days=4,
        fulfillment_rate=98.5,
        on_time_rate=97.0,
        defect_rate=0.4,
        price_multiplier=1.20,
        min_order_qty=20,
        credit_terms_days=30,
        notes="Supplier grade-1 terakreditasi ISO. Harga sedikit premium namun kualitas konsisten tanpa komplain."
    )
    v2 = Vendor(
        company_id=company.id,
        name="Apex Micro Components Ltd",
        category="Microcontroller MCU & Sensor Semikonduktor",
        lead_time_days=6,
        fulfillment_rate=94.0,
        on_time_rate=93.0,
        defect_rate=1.2,
        price_multiplier=1.10,
        min_order_qty=30,
        credit_terms_days=30,
        notes="Pemasok semikonduktor internasional. Ketaatan jadwal stabil, kapasitas pasokan besar."
    )
    v3 = Vendor(
        company_id=company.id,
        name="CV Mitra Bahari Sentosa",
        category="Baterai & Komponen Elektrik Grosir",
        lead_time_days=10,
        fulfillment_rate=78.0,
        on_time_rate=74.0,
        defect_rate=8.8,
        price_multiplier=0.72,
        min_order_qty=10,
        credit_terms_days=14,
        notes="Harga sangat miring (diskon 28%). Namun defect rate tinggi dan sering terlambat dari jadwal."
    )
    v4 = Vendor(
        company_id=company.id,
        name="PT Mandiri Cipta Display",
        category="Panel Layar AMOLED 1.4 Inch",
        lead_time_days=5,
        fulfillment_rate=91.0,
        on_time_rate=89.0,
        defect_rate=1.8,
        price_multiplier=1.00,
        min_order_qty=15,
        credit_terms_days=60,
        notes="Menyediakan termin pembayaran fleksibel tempo 60 hari. Sangat bersahabat untuk cashflow."
    )
    db.add_all([v1, v2, v3, v4])
    db.commit()
    db.refresh(v1)
    db.refresh(v2)
    db.refresh(v3)
    db.refresh(v4)

    # Historical Metrics for Charts (Bulan -4 s/d Bulan -1)
    histories = [
        # V1
        VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -3", fulfillment_rate=99.0, on_time_rate=98.0, defect_rate=0.3, price_index=120.0),
        VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -2", fulfillment_rate=98.0, on_time_rate=96.5, defect_rate=0.5, price_index=120.0),
        VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -1", fulfillment_rate=98.5, on_time_rate=97.0, defect_rate=0.4, price_index=122.0),
        # V2
        VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -3", fulfillment_rate=95.0, on_time_rate=94.0, defect_rate=1.1, price_index=110.0),
        VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -2", fulfillment_rate=93.5, on_time_rate=92.0, defect_rate=1.3, price_index=110.0),
        VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -1", fulfillment_rate=94.0, on_time_rate=93.0, defect_rate=1.2, price_index=112.0),
        # V3 (High risk)
        VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -3", fulfillment_rate=82.0, on_time_rate=79.0, defect_rate=7.5, price_index=75.0),
        VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -2", fulfillment_rate=75.0, on_time_rate=71.0, defect_rate=9.2, price_index=70.0),
        VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -1", fulfillment_rate=78.0, on_time_rate=74.0, defect_rate=8.8, price_index=72.0),
        # V4
        VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -3", fulfillment_rate=92.0, on_time_rate=90.0, defect_rate=1.6, price_index=100.0),
        VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -2", fulfillment_rate=90.0, on_time_rate=88.0, defect_rate=2.0, price_index=100.0),
        VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -1", fulfillment_rate=91.0, on_time_rate=89.0, defect_rate=1.8, price_index=102.0),
    ]
    db.add_all(histories)
    db.commit()

    # 7. Products & BOM
    p_mcu = Product(company_id=company.id, sku="RAW-MCU-01", name="Chipset Microcontroller MCU-X", product_type="raw_material", cost_price=75000.0, list_price=0.0, current_stock=120.0, min_safety_stock=40.0)
    p_screen = Product(company_id=company.id, sku="RAW-DSP-01", name="Layar AMOLED 1.4 Inch", product_type="raw_material", cost_price=60000.0, list_price=0.0, current_stock=110.0, min_safety_stock=40.0)
    p_bat = Product(company_id=company.id, sku="RAW-BAT-01", name="Baterai Li-Po 450mAh", product_type="raw_material", cost_price=35000.0, list_price=0.0, current_stock=130.0, min_safety_stock=50.0)
    p_case = Product(company_id=company.id, sku="RAW-CAS-01", name="Casing Aluminium CNC", product_type="raw_material", cost_price=40000.0, list_price=0.0, current_stock=90.0, min_safety_stock=30.0)
    p_smartwatch = Product(company_id=company.id, sku="FNG-SW-01", name="Smartwatch VLab Pro 1 (Waterproof)", product_type="finished_good", cost_price=210000.0, list_price=550000.0, current_stock=45.0, min_safety_stock=20.0)

    db.add_all([p_mcu, p_screen, p_bat, p_case, p_smartwatch])
    db.commit()
    db.refresh(p_smartwatch)
    db.refresh(p_mcu)
    db.refresh(p_screen)
    db.refresh(p_bat)
    db.refresh(p_case)

    # BOM
    bom = BillOfMaterials(company_id=company.id, finished_product_id=p_smartwatch.id, name="BOM Standar Smartwatch VLab Pro 1", version="v1.0")
    db.add(bom)
    db.commit()
    db.refresh(bom)

    bom_items = [
        BOMItem(bom_id=bom.id, raw_product_id=p_mcu.id, quantity_required=1.0),
        BOMItem(bom_id=bom.id, raw_product_id=p_screen.id, quantity_required=1.0),
        BOMItem(bom_id=bom.id, raw_product_id=p_bat.id, quantity_required=1.0),
        BOMItem(bom_id=bom.id, raw_product_id=p_case.id, quantity_required=1.0),
    ]
    db.add_all(bom_items)
    db.commit()

    # 8. Work Centers
    wc1 = WorkCenter(company_id=company.id, code="WC-SMT-01", name="Lini Perakitan Elektronik SMT", capacity_units_per_hour=30.0, hourly_cost=180000.0, failure_rate=4.0, status="operational")
    wc2 = WorkCenter(company_id=company.id, code="WC-QC-02", name="Lini Finishing & QC Packaging", capacity_units_per_hour=40.0, hourly_cost=140000.0, failure_rate=2.0, status="operational")
    db.add_all([wc1, wc2])
    db.commit()

    # 9. CRM Leads & Customer Complaints
    leads = [
        CRMLead(
            company_id=company.id,
            title="Pengadaan 120 Unit Smartwatch Korporat",
            customer_name="PT Multi Integra Nusantara",
            customer_email="procurement@multi-integra.co.id",
            stage="proposition",
            expected_revenue=66000000.0,
            probability=75.0,
            priority="high",
            credit_rating="low_risk",
            csat_score=90.0,
            notes="Prospek korporasi untuk program kesehatan karyawan. Menunggu proposal final."
        ),
        CRMLead(
            company_id=company.id,
            title="Tender Perangkat Smart Band Daerah",
            customer_name="Dinas Pemuda & Olahraga Prov. Jabar",
            customer_email="kontak@dispora-jabar.go.id",
            stage="qualified",
            expected_revenue=137500000.0,
            probability=45.0,
            priority="medium",
            credit_rating="low_risk",
            csat_score=85.0,
            notes="Tender terbuka untuk 250 unit perangkat pelacak kebugaran."
        ),
        CRMLead(
            company_id=company.id,
            title="[URGENT KELUHAN] Retur Batch #08 Layar Bergaris",
            customer_name="CV Megah Sentosa",
            customer_email="direktur@megahsentosa.id",
            stage="qualified",
            expected_revenue=150000000.0,
            probability=20.0,
            priority="urgent",
            credit_rating="medium_risk",
            csat_score=35.0,
            is_complaint=True,
            complaint_details="15 unit dari pengiriman kemarin mengalami layar flicker & garis hitam. Akun VIP mengancam memutus kontrak jika tidak ada solusi hari ini!",
            notes="Kasus kritis yang harus segera diselesaikan di Misi 2."
        )
    ]
    db.add_all(leads)
    db.commit()

    # 10. Accounts & Initial Balances
    accounts = [
        Account(company_id=company.id, code="1010", name="Kas & Rekening Bank", account_type="asset", balance=500000000.0),
        Account(company_id=company.id, code="1020", name="Piutang Usaha (AR)", account_type="asset", balance=45000000.0),
        Account(company_id=company.id, code="1030", name="Persediaan Bahan Baku", account_type="asset", balance=45000000.0),
        Account(company_id=company.id, code="1040", name="Persediaan Barang Jadi", account_type="asset", balance=24750000.0),
        Account(company_id=company.id, code="2010", name="Utang Usaha (AP)", account_type="liability", balance=15000000.0),
        Account(company_id=company.id, code="3010", name="Modal Disetor Mahasiswa", account_type="equity", balance=500000000.0),
        Account(company_id=company.id, code="4010", name="Pendapatan Penjualan", account_type="revenue", balance=45000000.0),
        Account(company_id=company.id, code="5010", name="Harga Pokok Penjualan (HPP)", account_type="expense", balance=18900000.0),
        Account(company_id=company.id, code="6010", name="Beban Gaji Karyawan", account_type="expense", balance=25000000.0),
        Account(company_id=company.id, code="6020", name="Beban Pemasaran & Iklan", account_type="expense", balance=10000000.0),
    ]
    db.add_all(accounts)
    db.commit()

    # 11. Department Budgets
    budgets = [
        DepartmentBudget(company_id=company.id, department="Produksi & Manufaktur", allocated_amount=120000000.0, spent_amount=25000000.0, period_name="Bulan 1"),
        DepartmentBudget(company_id=company.id, department="Pengadaan / Purchasing", allocated_amount=150000000.0, spent_amount=35000000.0, period_name="Bulan 1"),
        DepartmentBudget(company_id=company.id, department="Pemasaran / Marketing", allocated_amount=40000000.0, spent_amount=10000000.0, period_name="Bulan 1"),
        DepartmentBudget(company_id=company.id, department="Human Resources (HR)", allocated_amount=60000000.0, spent_amount=25000000.0, period_name="Bulan 1"),
    ]
    db.add_all(budgets)
    db.commit()

    # 12. Employees
    employees = [
        Employee(company_id=company.id, name="Ahmad Fauzi", department="Produksi", role="Kepala Lini Perakitan", monthly_salary=7500000.0, morale_score=92.0, fatigue_score=25.0, status="active"),
        Employee(company_id=company.id, name="Siti Rahma", department="Produksi", role="Operator SMT Mesin 1", monthly_salary=5200000.0, morale_score=90.0, fatigue_score=30.0, status="active"),
        Employee(company_id=company.id, name="Bambang Wijaya", department="Produksi", role="Operator SMT Mesin 2", monthly_salary=5200000.0, morale_score=88.0, fatigue_score=32.0, status="active"),
        Employee(company_id=company.id, name="Dewi Lestari", department="Quality Control", role="Spesialis Inspeksi QC", monthly_salary=6000000.0, morale_score=94.0, fatigue_score=20.0, status="active"),
        Employee(company_id=company.id, name="Rian Pratama", department="Sales & CRM", role="Key Account Executive", monthly_salary=6500000.0, morale_score=91.0, fatigue_score=22.0, status="active"),
    ]
    db.add_all(employees)
    db.commit()

    # 13. Provision Company & Rolling Initial Data for Kelas FEB B
    from backend.app.services.tenant_service import provision_company_data, roll_session_cases
    company_b = Company(
        session_id=session_b.id,
        name="PT Sinergi Prima Nusantara",
        industry="Manufaktur & Distribusi Perangkat Cerdas FEB",
        team_leader_id=mahasiswa_b.id,
        initial_capital=500000000.0,
        current_cash=500000000.0
    )
    db.add(company_b)
    db.commit()
    db.refresh(company_b)
    provision_company_data(db, company_b, session_b)

    # Initial Rolling: Kelas FEB A (Pemasaran Duluan), Kelas FEB B (Keuangan Duluan)
    roll_session_cases(db, session_a.id, "marketing_first")
    roll_session_cases(db, session_b.id, "finance_first")

    print("Seeding completed successfully for FEB A & FEB B!")
    db.close()

if __name__ == "__main__":
    seed_database()

```


---
# FILE: backend/app/routers/auth.py
---
```python
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models.models import User, Company, ClassSession
from backend.app.schemas.schemas import Token, UserLogin, UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau kata sandi tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    company = db.query(Company).filter(Company.team_leader_id == user.id).first()
    if not company and user.role == "MAHASISWA":
        # Fallback to match by username prefix/suffix or order
        if "1" in user.username:
            company = db.query(Company).filter(Company.id == 1).first()
        elif "2" in user.username:
            company = db.query(Company).filter(Company.id == 2).first()
        elif "3" in user.username:
            company = db.query(Company).filter(Company.id == 3).first()
        elif "4" in user.username:
            company = db.query(Company).filter(Company.id == 4).first()
        else:
            company = db.query(Company).first()

    company_id = company.id if company else None
    company_name = company.name if company else None
    group_label = f"Kelompok {company.id}" if company else None
    session_id = company.session_id if company else None

    # If lecturer, find their session
    if user.role in ["DOSEN", "ADMIN"]:
        session = db.query(ClassSession).filter(ClassSession.lecturer_id == user.id).first()
        if not session:
            session = db.query(ClassSession).first()
        if session:
            session_id = session.id
            first_co = db.query(Company).filter(Company.session_id == session.id).first()
            if first_co:
                company_id = first_co.id
                company_name = first_co.name
                group_label = "Supervisi Seluruh Kelompok"

    access_token = create_access_token(data={"sub": user.username, "role": user.role, "id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "company_id": company_id,
        "company_name": company_name,
        "group_label": group_label,
        "session_id": session_id
    }

@router.get("/me", response_model=UserOut)
def get_me(db: Session = Depends(get_db)):
    # Default to first user or demo user
    user = db.query(User).first()
    return user

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.role, User.id).all()
    result = []
    for u in users:
        company = db.query(Company).filter(Company.team_leader_id == u.id).first()
        session = db.query(ClassSession).filter(ClassSession.lecturer_id == u.id).first()
        if not session and company and company.session_id:
            session = db.query(ClassSession).filter(ClassSession.id == company.session_id).first()

        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "company_id": company.id if company else None,
            "company_name": company.name if company else None,
            "group_label": f"Kelompok {company.id}" if company else None,
            "session_id": session.id if session else None,
            "session_name": session.name if session else None,
            "session_code": session.code if session else None
        })
    return result

@router.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    
    # Check username uniqueness if changed
    if payload.username and payload.username.strip() != user.username:
        new_username = payload.username.strip()
        existing = db.query(User).filter(User.username == new_username).first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=400, detail=f"Username '{new_username}' sudah digunakan oleh akun lain")
        user.username = new_username
        if not payload.email:
            user.email = f"{new_username}@vlab.edu"

    if payload.full_name and payload.full_name.strip():
        user.full_name = payload.full_name.strip()

    if payload.email and payload.email.strip():
        user.email = payload.email.strip()

    if payload.role and payload.role.strip():
        user.role = payload.role.strip()

    # If password is provided, hash with bcrypt
    if payload.password and len(payload.password.strip()) > 0:
        user.hashed_password = get_password_hash(payload.password.strip())

    # Handle tenant/company linking
    if payload.company_id is not None:
        # Unlink existing companies where this user was leader
        db.query(Company).filter(Company.team_leader_id == user.id).update({"team_leader_id": None})
        if payload.company_id > 0:
            target_co = db.query(Company).filter(Company.id == payload.company_id).first()
            if target_co:
                target_co.team_leader_id = user.id

    # Handle class session linking for DOSEN
    if payload.session_id is not None and user.role == "DOSEN":
        if payload.session_id > 0:
            target_sess = db.query(ClassSession).filter(ClassSession.id == payload.session_id).first()
            if target_sess:
                target_sess.lecturer_id = user.id

    db.commit()
    db.refresh(user)

    return {
        "message": f"Akun '{user.username}' ({user.full_name}) berhasil diperbarui!",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "email": user.email
        }
    }

@router.post("/users")
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username.strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Username '{payload.username.strip()}' sudah terdaftar")
    
    hashed = get_password_hash(payload.password.strip())
    new_user = User(
        username=payload.username.strip(),
        email=payload.email.strip() if payload.email else f"{payload.username.strip()}@vlab.edu",
        full_name=payload.full_name.strip(),
        hashed_password=hashed,
        role=payload.role.strip() if payload.role else "MAHASISWA"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Link tenant company if provided
    if payload.company_id and payload.company_id > 0:
        target_co = db.query(Company).filter(Company.id == payload.company_id).first()
        if target_co:
            target_co.team_leader_id = new_user.id
            db.commit()

    # Link class session if provided and role is DOSEN
    if payload.session_id and payload.session_id > 0 and new_user.role == "DOSEN":
        target_sess = db.query(ClassSession).filter(ClassSession.id == payload.session_id).first()
        if target_sess:
            target_sess.lecturer_id = new_user.id
            db.commit()

    return {
        "message": f"Akun baru '{new_user.username}' berhasil dibuat!",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "role": new_user.role
        }
    }

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    
    if user.role == "ADMIN":
        admin_count = db.query(User).filter(User.role == "ADMIN").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Tidak dapat menghapus satu-satunya akun Administrator")

    username = user.username
    # Safely unlink any foreign keys first
    db.query(Company).filter(Company.team_leader_id == user_id).update({"team_leader_id": None})
    db.query(ClassSession).filter(ClassSession.lecturer_id == user_id).update({"lecturer_id": None})
    db.commit()

    db.delete(user)
    db.commit()
    return {"message": f"Akun '{username}' berhasil dihapus."}

from pydantic import BaseModel
from typing import List

class BatchResetPasswordPayload(BaseModel):
    user_ids: List[int]
    new_password: str

@router.post("/users/batch-reset-password")
def batch_reset_password(payload: BatchResetPasswordPayload, db: Session = Depends(get_db)):
    if not payload.user_ids:
        raise HTTPException(status_code=400, detail="Pilih minimal satu akun pengguna")
    if not payload.new_password or len(payload.new_password.strip()) < 4:
        raise HTTPException(status_code=400, detail="Password baru minimal 4 karakter")

    hashed = get_password_hash(payload.new_password.strip())
    users = db.query(User).filter(User.id.in_(payload.user_ids)).all()
    count = 0
    for u in users:
        u.hashed_password = hashed
        count += 1
    db.commit()
    return {"message": f"Berhasil mereset password untuk {count} akun ke '{payload.new_password}'!"}


```


---
# FILE: backend/app/routers/tenants.py
---
```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import ClassSession, Company, User, ClassSessionLecturer, SimulationSlider
from backend.app.schemas.schemas import (
    ClassSessionCreate, ClassSessionUpdate, ClassSessionCloneRequest,
    LecturerAssignment
)
from backend.app.services.tenant_service import (
    provision_company_data, reset_company_data, batch_generate_tenants,
    differentiate_tenant_cases
)

router = APIRouter(prefix="/simulation", tags=["tenants"])

class CreateCompanyRequest(BaseModel):
    session_id: int
    name: str
    group_name: Optional[str] = None
    industry: str = "Manufaktur Elektronik Smart Device"
    initial_capital: float = 500000000.0

@router.get("/dosen-list")
def get_dosen_list(db: Session = Depends(get_db)):
    dosens = db.query(User).filter(User.role.in_(["DOSEN", "ADMIN"])).order_by(User.id).all()
    results = []
    for d in dosens:
        class_count = db.query(ClassSessionLecturer).filter(ClassSessionLecturer.user_id == d.id).count()
        if class_count == 0:
            class_count = db.query(ClassSession).filter(ClassSession.lecturer_id == d.id).count()
        results.append({
            "id": d.id,
            "username": d.username,
            "full_name": d.full_name,
            "email": d.email,
            "role": d.role,
            "assigned_class_count": class_count
        })
    return results

@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(ClassSession).order_by(ClassSession.id).all()
    results = []
    for s in sessions:
        team_lecturers_records = db.query(ClassSessionLecturer).filter(ClassSessionLecturer.session_id == s.id).all()
        team_list = []
        for l in team_lecturers_records:
            u = db.query(User).filter(User.id == l.user_id).first()
            if u:
                team_list.append({
                    "id": l.id,
                    "user_id": u.id,
                    "username": u.username,
                    "full_name": u.full_name,
                    "email": u.email,
                    "role_title": l.role_title,
                    "is_primary": l.is_primary
                })
        
        # Fallback primary lecturer if team_list is empty
        if not team_list and s.lecturer_id:
            u = db.query(User).filter(User.id == s.lecturer_id).first()
            if u:
                team_list.append({
                    "id": 0,
                    "user_id": u.id,
                    "username": u.username,
                    "full_name": u.full_name,
                    "email": u.email,
                    "role_title": "Dosen Pengampu Utama",
                    "is_primary": True
                })
        
        company_count = db.query(Company).filter(Company.session_id == s.id).count()
        
        primary_lecturer = next((l for l in team_list if l["is_primary"]), None) or (team_list[0] if team_list else None)
        lecturer_name_display = primary_lecturer["full_name"] if primary_lecturer else "Tim Dosen Pengampu FEB"
        if len(team_list) > 1:
            lecturer_name_display += f" & Tim ({len(team_list)} Dosen)"

        results.append({
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "academic_term": s.academic_term or "Semester Ganjil 2026/2027",
            "department": s.department or "S1 Manajemen & Akuntansi Bisnis Digital FEB",
            "description": s.description or "",
            "lecturer_id": s.lecturer_id,
            "lecturer_name": lecturer_name_display,
            "team_lecturers": team_list,
            "progression_mode": s.progression_mode,
            "current_round": s.current_round,
            "total_rounds": s.total_rounds,
            "status": s.status or "active",
            "company_count": company_count
        })
    return results

@router.post("/sessions")
def create_session(payload: ClassSessionCreate, db: Session = Depends(get_db)):
    code_clean = payload.code.strip().upper()
    existing = db.query(ClassSession).filter(ClassSession.code == code_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Sesi kelas dengan kode '{code_clean}' sudah terdaftar.")
    
    primary_id = None
    if payload.lecturers:
        primary = next((l for l in payload.lecturers if l.is_primary), payload.lecturers[0])
        primary_id = primary.user_id
    else:
        dosen = db.query(User).filter(User.role == "DOSEN").first()
        if dosen:
            primary_id = dosen.id

    session = ClassSession(
        name=payload.name.strip(),
        code=code_clean,
        academic_term=payload.academic_term or "Semester Ganjil 2026/2027",
        department=payload.department or "S1 Manajemen & Akuntansi Bisnis Digital FEB",
        description=payload.description or "",
        lecturer_id=primary_id,
        progression_mode=payload.progression_mode or "problem_based",
        current_round=1,
        total_rounds=payload.total_rounds or 12,
        status="active"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Assign team lecturers
    if payload.lecturers:
        for item in payload.lecturers:
            lecturer_rec = ClassSessionLecturer(
                session_id=session.id,
                user_id=item.user_id,
                role_title=item.role_title or "Dosen Pengampu",
                is_primary=item.is_primary
            )
            db.add(lecturer_rec)
        db.commit()
    elif primary_id:
        lecturer_rec = ClassSessionLecturer(
            session_id=session.id,
            user_id=primary_id,
            role_title="Koordinator Matakuliah & Pengampu Utama",
            is_primary=True
        )
        db.add(lecturer_rec)
        db.commit()

    # Create default simulation slider config for the session
    session_slider = SimulationSlider(
        session_id=session.id,
        is_company_override=False,
        supply_disruption=20.0,
        machine_breakdown_risk=15.0,
        market_volatility=30.0,
        labor_strike_risk=10.0,
        bad_debt_risk=15.0,
        competitor_price_war=25.0
    )
    db.add(session_slider)
    db.commit()

    # Optional Auto Provisioning Groups
    provisioned_msg = ""
    if payload.auto_provision_groups and payload.auto_provision_groups > 0:
        batch_generate_tenants(
            db,
            session_id=session.id,
            target_count=min(payload.auto_provision_groups, 12),
            initial_capital=payload.initial_capital or 500000000.0,
            differentiate_cases=True
        )
        provisioned_msg = f" dan berhasil menyiapkan {payload.auto_provision_groups} entitas kelompok perusahaan praktikan!"

    return {
        "status": "success",
        "message": f"Sesi kelas '{session.name}' ({session.code}) berhasil dibuat{provisioned_msg}",
        "session_id": session.id
    }

@router.put("/sessions/{session_id}")
def update_session(session_id: int, payload: ClassSessionUpdate, db: Session = Depends(get_db)):
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesi kelas tidak ditemukan.")

    if payload.code and payload.code.strip().upper() != session.code:
        code_check = db.query(ClassSession).filter(
            ClassSession.code == payload.code.strip().upper(),
            ClassSession.id != session_id
        ).first()
        if code_check:
            raise HTTPException(status_code=400, detail=f"Kode sesi '{payload.code.strip().upper()}' sudah digunakan oleh kelas lain.")
        session.code = payload.code.strip().upper()

    if payload.name is not None:
        session.name = payload.name.strip()
    if payload.academic_term is not None:
        session.academic_term = payload.academic_term.strip()
    if payload.department is not None:
        session.department = payload.department.strip()
    if payload.description is not None:
        session.description = payload.description.strip()
    if payload.status is not None:
        session.status = payload.status
    if payload.progression_mode is not None:
        session.progression_mode = payload.progression_mode
    if payload.total_rounds is not None:
        session.total_rounds = payload.total_rounds

    if payload.lecturers is not None:
        db.query(ClassSessionLecturer).filter(ClassSessionLecturer.session_id == session_id).delete()
        primary_id = None
        for item in payload.lecturers:
            lecturer_rec = ClassSessionLecturer(
                session_id=session.id,
                user_id=item.user_id,
                role_title=item.role_title or "Dosen Pengampu",
                is_primary=item.is_primary
            )
            db.add(lecturer_rec)
            if item.is_primary or primary_id is None:
                primary_id = item.user_id
        session.lecturer_id = primary_id

    db.commit()
    db.refresh(session)
    return {
        "status": "success",
        "message": f"Sesi kelas '{session.name}' ({session.code}) berhasil diperbarui!",
        "session_id": session.id
    }

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesi kelas tidak ditemukan.")

    total_sessions = db.query(ClassSession).count()
    if total_sessions <= 1:
        raise HTTPException(status_code=400, detail="Tidak dapat menghapus satu-satunya sesi kelas yang tersisa di sistem.")

    session_name = session.name
    session_code = session.code

    db.query(ClassSessionLecturer).filter(ClassSessionLecturer.session_id == session_id).delete()
    db.delete(session)
    db.commit()

    return {
        "status": "success",
        "message": f"Sesi kelas '{session_name}' ({session_code}) beserta seluruh data kelompoknya berhasil dihapus."
    }

@router.post("/sessions/{session_id}/clone")
def clone_session(session_id: int, payload: ClassSessionCloneRequest, db: Session = Depends(get_db)):
    source_session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not source_session:
        raise HTTPException(status_code=404, detail="Sesi kelas sumber tidak ditemukan.")

    new_code_clean = payload.new_code.strip().upper()
    existing = db.query(ClassSession).filter(ClassSession.code == new_code_clean).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Kode sesi '{new_code_clean}' sudah terdaftar.")

    new_session = ClassSession(
        name=payload.new_name.strip(),
        code=new_code_clean,
        academic_term=payload.academic_term or source_session.academic_term,
        department=payload.department or source_session.department,
        description=f"Duplikasi dari {source_session.name} ({source_session.code})",
        lecturer_id=source_session.lecturer_id,
        progression_mode=source_session.progression_mode,
        current_round=1,
        total_rounds=source_session.total_rounds,
        status="active"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Clone team lecturers
    source_lecturers = db.query(ClassSessionLecturer).filter(ClassSessionLecturer.session_id == source_session.id).all()
    for l in source_lecturers:
        new_l = ClassSessionLecturer(
            session_id=new_session.id,
            user_id=l.user_id,
            role_title=l.role_title,
            is_primary=l.is_primary
        )
        db.add(new_l)
    db.commit()

    # Clone slider config
    source_slider = db.query(SimulationSlider).filter(
        SimulationSlider.session_id == source_session.id,
        SimulationSlider.company_id == None
    ).first()
    new_slider = SimulationSlider(
        session_id=new_session.id,
        is_company_override=False,
        supply_disruption=source_slider.supply_disruption if source_slider else 20.0,
        machine_breakdown_risk=source_slider.machine_breakdown_risk if source_slider else 15.0,
        market_volatility=source_slider.market_volatility if source_slider else 30.0,
        labor_strike_risk=source_slider.labor_strike_risk if source_slider else 10.0,
        bad_debt_risk=source_slider.bad_debt_risk if source_slider else 15.0,
        competitor_price_war=source_slider.competitor_price_war if source_slider else 25.0
    )
    db.add(new_slider)
    db.commit()

    # Clone companies if requested
    if payload.clone_companies:
        source_companies = db.query(Company).filter(Company.session_id == source_session.id).all()
        target_count = len(source_companies) if len(source_companies) > 0 else 4
        batch_generate_tenants(
            db,
            session_id=new_session.id,
            target_count=target_count,
            initial_capital=500000000.0,
            differentiate_cases=payload.differentiate_cases
        )

    return {
        "status": "success",
        "message": f"Sesi kelas '{new_session.name}' ({new_session.code}) berhasil diduplikasi dari '{source_session.name}'!",
        "session_id": new_session.id
    }

class RollCasesRequest(BaseModel):
    sequence: str  # "marketing_first", "finance_first", "hr_first"

@router.post("/sessions/{session_id}/roll-cases")
def roll_cases(session_id: int, payload: RollCasesRequest, db: Session = Depends(get_db)):
    from backend.app.services.tenant_service import roll_session_cases
    success, message = roll_session_cases(db, session_id, payload.sequence)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {
        "status": "success",
        "message": message,
        "session_id": session_id,
        "sequence": payload.sequence
    }

@router.get("/companies")
def list_companies(session_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Company)
    if session_id:
        query = query.filter(Company.session_id == session_id)
    
    companies = query.all()
    results = []
    for idx, c in enumerate(companies):
        st = c.sim_state
        results.append({
            "id": c.id,
            "session_id": c.session_id,
            "name": c.name,
            "group_label": f"Kelompok {idx + 1}",
            "industry": c.industry,
            "initial_capital": c.initial_capital,
            "current_cash": st.cash if st else c.current_cash,
            "net_profit": st.net_profit if st else 0.0,
            "overall_score": st.overall_score if st else 0.0,
            "csat_score": st.csat_score if st else 85.0,
            "worker_morale": st.worker_morale if st else 90.0,
            "is_strike_active": st.is_strike_active if st else False,
            "active_case_title": st.active_case_title if st else "Misi 1: Evaluasi Vendor & Pencegahan Bottleneck Bahan Baku",
            "period_name": st.period_name if st else "Bulan 1 (Januari 2026)"
        })
    return results

@router.post("/companies")
def create_company(payload: CreateCompanyRequest, db: Session = Depends(get_db)):
    session = db.query(ClassSession).filter(ClassSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sesi kelas tidak ditemukan.")
    
    existing = db.query(Company).filter(
        Company.session_id == payload.session_id,
        Company.name == payload.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Perusahaan '{payload.name}' sudah ada di sesi ini.")

    company = Company(
        session_id=payload.session_id,
        name=payload.name,
        industry=payload.industry,
        initial_capital=payload.initial_capital,
        current_cash=payload.initial_capital
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    # Provision complete sandbox data for new tenant
    provision_company_data(db, company, session)

    return {
        "status": "success",
        "message": f"Tenant perusahaan '{company.name}' berhasil dibuat dan diprovisioning lengkap!",
        "company_id": company.id,
        "name": company.name
    }

@router.post("/companies/{company_id}/reset")
def reset_company(company_id: int, db: Session = Depends(get_db)):
    success = reset_company_data(db, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan.")
    return {
        "status": "success",
        "message": f"Sandbox perusahaan ID {company_id} berhasil di-reset ke kondisi awal master data."
    }

@router.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan.")
    
    total_companies = db.query(Company).count()
    if total_companies <= 1:
        raise HTTPException(status_code=400, detail="Tidak dapat menghapus satu-satunya perusahaan yang tersisa.")
    
    db.delete(company)
    db.commit()
    return {
        "status": "success",
        "message": f"Perusahaan '{company.name}' berhasil dihapus."
    }

class BatchGenerateRequest(BaseModel):
    session_id: int
    target_count: int = 4
    initial_capital: float = 500000000.0
    differentiate_cases: bool = True

@router.post("/companies/batch-generate")
def batch_generate(payload: BatchGenerateRequest, db: Session = Depends(get_db)):
    from backend.app.services.tenant_service import batch_generate_tenants
    res = batch_generate_tenants(
        db,
        session_id=payload.session_id,
        target_count=payload.target_count,
        initial_capital=payload.initial_capital,
        differentiate_cases=payload.differentiate_cases
    )
    return res

@router.post("/companies/{company_id}/randomize-cases")
def randomize_cases_for_company(company_id: int, db: Session = Depends(get_db)):
    from backend.app.services.tenant_service import differentiate_tenant_cases
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan.")
    
    success = differentiate_tenant_cases(db, company.id, company.id)
    if not success:
        raise HTTPException(status_code=500, detail="Gagal mengacak masalah kasus.")
    
    return {
        "status": "success",
        "message": f"Skenario masalah untuk '{company.name}' berhasil diperbarui dengan paket kasus diferensiasi baru!"
    }

@router.post("/differentiate-all-cases")
def differentiate_all_cases(session_id: Optional[int] = None, db: Session = Depends(get_db)):
    from backend.app.services.tenant_service import differentiate_tenant_cases
    query = db.query(Company)
    if session_id:
        query = query.filter(Company.session_id == session_id)
    companies = query.all()
    
    for idx, c in enumerate(companies):
        differentiate_tenant_cases(db, c.id, idx + 1)
        
    return {
        "status": "success",
        "message": f"Seluruh {len(companies)} entitas perusahaan kelompok berhasil diberikan paket skenario masalah yang unik dan berbeda-beda!",
        "affected_companies": len(companies)
    }


```


---
# FILE: backend/app/routers/simulation.py
---
```python
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import (
    SimulationState, SimulationSlider, ScenarioCase, Company, ClassSession,
    WorkCenter, Account, Employee, CRMLead, Product, PurchaseOrder, PurchaseOrderItem,
    Vendor, DepartmentBudget, SalesOrder, SalesOrderItem, WorkOrder,
    JournalEntry, JournalItem, Customer, MarketingCampaign, CompanyStoryEvent
)
from backend.app.schemas.schemas import (
    SimulationStateOut, SimulationSliderOut, SimulationSliderUpdate,
    ScenarioCaseOut, SolveCaseRequest
)
from backend.app.services.behavior_engine import (
    get_all_scenarios_matrix, get_scenario_by_id,
    calculate_action_ripples, execute_scenario_branch,
    run_smart_cfo_diagnostics, get_random_customer_temperament,
    get_union_leader_for_company, trigger_random_black_swan
)
from backend.app.services.tenant_service import (
    _apply_scenario_mutation, SCENARIO_INITIAL_MUTATIONS
)


router = APIRouter(prefix="/simulation", tags=["simulation"])

class CreateCaseRequest(BaseModel):
    session_id: int
    company_id: Optional[int] = None
    code: str
    stage_order: int
    title: str
    category: str
    description: str
    trigger_hint: Optional[str] = None
    solvable_workflow: str
    resolution_criteria: str

class UpdateCaseRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    trigger_hint: Optional[str] = None
    solvable_workflow: Optional[str] = None
    resolution_criteria: Optional[str] = None
    status: Optional[str] = None

# --- CRUD SCENARIO CASES (Dosen Management) ---
@router.post("/cases", response_model=ScenarioCaseOut)
def create_case(payload: CreateCaseRequest, db: Session = Depends(get_db)):
    new_case = ScenarioCase(
        session_id=payload.session_id,
        company_id=payload.company_id,
        code=payload.code,
        stage_order=payload.stage_order,
        title=payload.title,
        category=payload.category,
        description=payload.description,
        trigger_hint=payload.trigger_hint,
        solvable_workflow=payload.solvable_workflow,
        resolution_criteria=payload.resolution_criteria,
        status="pending",
        resolution_score=0.0
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

@router.put("/cases/{case_id}", response_model=ScenarioCaseOut)
def update_case(case_id: int, payload: UpdateCaseRequest, db: Session = Depends(get_db)):
    case = db.query(ScenarioCase).filter(ScenarioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    
    if payload.title is not None: case.title = payload.title
    if payload.category is not None: case.category = payload.category
    if payload.description is not None: case.description = payload.description
    if payload.trigger_hint is not None: case.trigger_hint = payload.trigger_hint
    if payload.solvable_workflow is not None: case.solvable_workflow = payload.solvable_workflow
    if payload.resolution_criteria is not None: case.resolution_criteria = payload.resolution_criteria
    if payload.status is not None: case.status = payload.status

    db.commit()
    db.refresh(case)
    return case

@router.delete("/cases/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(ScenarioCase).filter(ScenarioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    db.delete(case)
    db.commit()
    return {"status": "success", "message": f"Kasus {case.code} berhasil dihapus"}

# --- SIMULATION STATE & SLIDERS ---
@router.get("/state/{company_id}", response_model=SimulationStateOut)
def get_simulation_state(company_id: int, db: Session = Depends(get_db)):
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="Status simulasi perusahaan tidak ditemukan")
    return state

@router.get("/sliders/{company_id}", response_model=SimulationSliderOut)
def get_sliders(company_id: int, db: Session = Depends(get_db)):
    slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == company_id).first()
    if not slider:
        slider = SimulationSlider(company_id=company_id)
        db.add(slider)
        db.commit()
        db.refresh(slider)
    return slider

@router.put("/sliders/{company_id}", response_model=SimulationSliderOut)
def update_sliders(company_id: int, payload: SimulationSliderUpdate, db: Session = Depends(get_db)):
    slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == company_id).first()
    if not slider:
        slider = SimulationSlider(company_id=company_id)
        db.add(slider)
    
    slider.supply_disruption = payload.supply_disruption
    slider.machine_breakdown_risk = payload.machine_breakdown_risk
    slider.market_volatility = payload.market_volatility
    slider.labor_strike_risk = payload.labor_strike_risk
    slider.bad_debt_risk = payload.bad_debt_risk
    slider.competitor_price_war = payload.competitor_price_war
    slider.is_company_override = True

    # Adjust company metrics dynamically based on slider values
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if state:
        if payload.machine_breakdown_risk >= 60.0:
            wc = db.query(WorkCenter).filter(WorkCenter.company_id == company_id).first()
            if wc and wc.status == "operational":
                wc.status = "breakdown"
                state.machine_health = max(20.0, state.machine_health - 35.0)

        if payload.labor_strike_risk >= 70.0:
            state.is_strike_active = True
            state.strike_reason = "Tuntutan kenaikan upah lembur & UMR dari serikat buruh"
            state.worker_morale = max(25.0, state.worker_morale - 40.0)

    db.commit()
    db.refresh(slider)
    return slider

@router.put("/sliders/session/{session_id}")
def update_sliders_session(session_id: int, payload: SimulationSliderUpdate, db: Session = Depends(get_db)):
    companies = db.query(Company).filter(Company.session_id == session_id).all()
    if not companies:
        raise HTTPException(status_code=404, detail="Tidak ada perusahaan pada sesi kelas ini")

    for comp in companies:
        slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == comp.id).first()
        if not slider:
            slider = SimulationSlider(company_id=comp.id)
            db.add(slider)

        slider.supply_disruption = payload.supply_disruption
        slider.machine_breakdown_risk = payload.machine_breakdown_risk
        slider.market_volatility = payload.market_volatility
        slider.labor_strike_risk = payload.labor_strike_risk
        slider.bad_debt_risk = payload.bad_debt_risk
        slider.competitor_price_war = payload.competitor_price_war
        slider.is_company_override = True

        state = db.query(SimulationState).filter(SimulationState.company_id == comp.id).first()
        if state:
            if payload.machine_breakdown_risk >= 60.0:
                wc = db.query(WorkCenter).filter(WorkCenter.company_id == comp.id).first()
                if wc and wc.status == "operational":
                    wc.status = "breakdown"
                    state.machine_health = max(20.0, state.machine_health - 35.0)

            if payload.labor_strike_risk >= 70.0:
                state.is_strike_active = True
                state.strike_reason = "Tuntutan kenaikan upah lembur & UMR dari serikat buruh"
                state.worker_morale = max(25.0, state.worker_morale - 40.0)

    db.commit()
    return {
        "status": "success",
        "message": f"Parameter simulasi berhasil diterapkan serentak ke {len(companies)} kelompok pada sesi kelas {session_id}!",
        "affected_companies": len(companies)
    }


@router.get("/cases/{company_id}", response_model=List[ScenarioCaseOut])
def get_cases(company_id: int, db: Session = Depends(get_db)):
    return db.query(ScenarioCase).filter(
        (ScenarioCase.company_id == company_id) | (ScenarioCase.company_id == None)
    ).order_by(ScenarioCase.stage_order.asc()).all()

# --- DYNAMIC STEP-BY-STEP SCORING & FACT SHEET EVALUATOR (NO HARDCODING) ---
@router.post("/cases/{case_id}/solve")
def solve_case(case_id: int, payload: SolveCaseRequest, db: Session = Depends(get_db)):
    case = db.query(ScenarioCase).filter(ScenarioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    company_id = case.company_id
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    step_scores = []
    total_score = 0.0
    passed = True
    fact_sheet = {}

    # DYNAMIC EVALUATION PER MISSION CATEGORY
    cat = (case.category or "").lower()
    
    if cat in ["procurement", "purchasing", "scm"]:
        # 1. Check vendor selection from actual POs
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id).all()
        has_bad_vendor_po = False
        for po in pos:
            vendor = db.query(Vendor).filter(Vendor.id == po.vendor_id).first()
            if vendor and vendor.defect_rate > 5.0:
                has_bad_vendor_po = True

        # Step 1: Due Diligence
        s1_max = 30
        s1_score = 30 if len(pos) > 0 else 15
        step_scores.append({"step": "Due Diligence & Analisis Data Historis Vendor", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        # Step 2: Quality Supplier Selection (Defect < 2%)
        s2_max = 40
        s2_score = 15 if has_bad_vendor_po else 38
        step_scores.append({"step": "Pemilihan Pemasok Berkualitas Rendah Defect (< 2%)", "max_score": s2_max, "earned_score": s2_score, "status": "failed" if has_bad_vendor_po else "passed"})

        # Step 3: Stock Buffer Fulfillment
        raw_products = db.query(Product).filter(Product.company_id == company_id, Product.product_type == "raw_material").all()
        sufficient_stocks = [p for p in raw_products if p.current_stock >= p.min_safety_stock]
        stock_ratio = (len(sufficient_stocks) / len(raw_products)) if raw_products else 1.0
        s3_max = 30
        s3_score = int(30 * stock_ratio)
        step_scores.append({"step": "Pemenuhan Batas Minimum Safety Stock Gudang", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 20 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0) and not has_bad_vendor_po

        fact_sheet = {
            "root_cause": "Godaan harga murah menyembunyikan risiko cacat bahan baku tinggi yang dapat merusak mesin perakitan SMT.",
            "student_actions_taken": f"Menerbitkan {len(pos)} PO. Terpilih vendor cacat tinggi: {'Ya' if has_bad_vendor_po else 'Tidak'}. Safety stock tercapai: {int(stock_ratio*100)}%.",
            "why_evaluation": "Berhasil memilih vendor dengan kualifikasi andal dan menjaga kontinuitas persediaan." if passed else "Mahasiswa tergoda diskon vendor murah (CV Mitra Bahari) dengan tingkat cacat 8.8% yang memicu risiko gagal produksi.",
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Prioritaskan PT Surya Logam Presisi / Apex Micro Components (Zero Defect).\n2. Opsi Dual-Sourcing: 70% vendor grade-1 + 30% buffer suplier lokal.\n3. Pertahankan stok di atas safety stock minimal 40 unit.",
            "key_takeaway": "Total Cost of Ownership (TCO) jauh lebih penting daripada sekadar harga beli termurah di invoice."
        }

    elif cat in ["crm", "marketing", "sales"]:
        # Check complaint lead resolution
        complaints = db.query(CRMLead).filter(CRMLead.company_id == company_id, CRMLead.is_complaint == True).all()
        resolved_complaint = next((c for c in complaints if c.stage == "won" or c.resolution_action), None)
        complaint = resolved_complaint or (complaints[0] if complaints else None)
        
        is_replaced = complaint and complaint.stage == "won"
        csat_current = state.csat_score if state else 80.0

        s1_max = 30
        s1_score = 30 if complaint and complaint.resolution_action else 10
        step_scores.append({"step": "Kecepatan Respon & Penanganan Tiket Darurat Akun VIP", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        s2_max = 40
        s2_score = 40 if is_replaced else (20 if complaint and complaint.stage == "proposition" else 5)
        step_scores.append({"step": "Eksekusi Mitigasi Kompensasi yang Memuaskan Konsumen", "max_score": s2_max, "earned_score": s2_score, "status": "passed" if s2_score >= 30 else "failed"})

        s3_max = 30
        s3_score = int(min(30, (csat_current / 100.0) * 30))
        step_scores.append({"step": "Pemulihan Indeks CSAT & Penyelamatan Kontrak", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 22 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0)

        action_taken = complaint.resolution_action if complaint and complaint.resolution_action else "Belum ada tindakan mitigasi"
        if passed:
            if "Addendum Diskon" in action_taken:
                why_eval = "Keputusan Manajerial Brilian! Negosiasi mediasi direksi berhasil mempertahankan kontrak Rp 150M sekaligus mengamankan arus kas dan stok gudang tanpa pemotongan fisik."
            elif "Penggantian" in action_taken or "Ganti" in action_taken:
                why_eval = "SOP Customer-First Berhasil! Menjalankan penggantian 15 unit fisik mengembalikan kepercayaan penuh klien VIP dan menyelamatkan kontrak jangka panjang."
            elif "Servis" in action_taken or "Audit" in action_taken:
                why_eval = "Investigasi Pragmatis! Layanan teknisi lapangan menyelesaikan keluhan dan memberikan data forensik untuk menuntut ganti rugi ke vendor bahan baku cacat."
            else:
                why_eval = "Keluhan pelanggan VIP ditangani secara elegan sehingga loyalitas dan kontrak pulih."
        else:
            why_eval = "Penanganan keluhan lambat, gantung, atau tidak memberikan kompensasi riil sehingga klien memutus kontrak dan CSAT jatuh."

        fact_sheet = {
            "root_cause": "Lolosnya 15 unit Smartwatch berlayar cacat ke klien enterprise CV Megah Sentosa mengancam pembatalan kontrak Rp 150.000.000.",
            "student_actions_taken": f"Status tiket keluhan: {complaint.stage if complaint else 'N/A'}. Tindakan: {action_taken}.",
            "why_evaluation": why_eval,
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Opsi A: Ganti 15 Unit Fisik (SOP Standar, potong stok & HPP).\n2. Opsi B: Mediasi Direksi -> Addendum Diskon 15% (Hemat kas & aman stok).\n3. Opsi C: Mediasi Direksi -> Servis Lapangan & Audit Vendor Cacat.",
            "key_takeaway": "Retensi pelanggan enterprise memiliki banyak jalur solusi; manajer yang matang memilih trade-off terbaik antara kepuasan konsumen vs likuiditas kas operasional."
        }

    elif cat in ["accounting", "finance"]:
        # Finance & Bad debt mitigation
        cash = state.cash if state else 500000000.0
        budgets = db.query(DepartmentBudget).filter(DepartmentBudget.company_id == company_id).all()
        total_budget = sum(b.allocated_amount for b in budgets) if budgets else 370000000.0

        s1_max = 30
        s1_score = 30 if cash >= 200000000.0 else (18 if cash >= 100000000.0 else 5)
        step_scores.append({"step": "Pengamanan Likuiditas Kas di Atas Batas Kritis (Safety Cash Level)", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        s2_max = 40
        budget_controlled = total_budget <= 400000000.0
        s2_score = 38 if budget_controlled else 22
        step_scores.append({"step": "Rasionalisasi Pagu Anggaran Operasional Departemen", "max_score": s2_max, "earned_score": s2_score, "status": "passed" if s2_score >= 30 else "failed"})

        s3_max = 30
        s3_score = 28 if cash > 0 else 5
        step_scores.append({"step": "Mitigasi Risiko Piutang Macet & Keseimbangan Neraca", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 20 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0) and (cash >= 150000000.0)

        fact_sheet = {
            "root_cause": "Gagal bayar distributor retail mengancam likuiditas kas operasional perusahaan.",
            "student_actions_taken": f"Saldo Kas Saat Ini: Rp {cash:,.0f}. Total Plafon Anggaran: Rp {total_budget:,.0f}.",
            "why_evaluation": "Keberhasilan manajemen kas menjaga saldo di atas batas aman (Safety Cash Level) dan merasionalisasi anggaran." if passed else "Saldo kas jatuh mendekati titik nol akibat kelalaian dalam manajemen modal kerja dan mitigasi piutang macet.",
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Rasionalisasi pagu anggaran operasional non-kritis di modul Budgeting.\n2. Terapkan syarat pembayaran tunai / DP minimal untuk pesanan baru di CRM.\n3. Bentuk cadangan kerugian piutang di Akuntansi.",
            "key_takeaway": "Revenue is vanity, profit is sanity, cash is king. Likuiditas adalah oksigen keberlangsungan hidup entitas bisnis."
        }

    elif cat in ["hr", "sdm"]:
        # HR & Bipartite labor relations
        employees = db.query(Employee).filter(Employee.company_id == company_id).all()
        is_strike = state.is_strike_active if state else False
        morale_avg = sum(e.morale_score for e in employees) / len(employees) if employees else 90.0
        cash = state.cash if state else 500000000.0

        s1_max = 30
        s1_score = 30 if cash >= 50000000.0 else 10
        step_scores.append({"step": "Pengamanan Likuiditas Kas Operasional & Cadangan Gaji", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        s2_max = 40
        s2_score = 38 if not is_strike else 10
        step_scores.append({"step": "Penyelesaian Sengketa Hubungan Industrial Bipartit", "max_score": s2_max, "earned_score": s2_score, "status": "passed" if s2_score >= 25 else "failed"})

        s3_max = 30
        s3_score = int(min(30, (morale_avg / 100.0) * 30))
        step_scores.append({"step": "Pemulihan Moral Pekerja & Operasional Lini Pabrik", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 22 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0) and not is_strike

        fact_sheet = {
            "root_cause": "Arus kas menipis memicu keterlambatan pembayaran gaji, ditambah beban lembur memicu mogok kerja buruh pabrik.",
            "student_actions_taken": f"Saldo Kas: Rp {cash:,.0f}. Status Mogok: {'Aktif' if is_strike else 'Selesai'}. Rata-rata Moral Buruh: {morale_avg:.1f}%.",
            "why_evaluation": "Mampu mencapai kesepakatan bipartit damai dan menjaga kesinambungan lini produksi." if passed else "Gagal mengakhiri aksi mogok kerja, lini pabrik lumpuh dan beban biaya tetap terus membengkak.",
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Jalur Bipartit Kompromi: Setujui bonus produktivitas wajar di modul HR.\n2. Jalur Efisiensi: Realokasi pos non-esensial ke dana payroll.\n3. Nyalakan kembali lini perakitan pabrik.",
            "key_takeaway": "Likuiditas kas adalah darah perusahaan; terganggunya kas gaji berakibat langsung pada kelumpuhan operasional."
        }

    else:
        # MRP & Production operations
        work_centers = db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all()
        all_operational = all(wc.status == "operational" for wc in work_centers) if work_centers else True
        machine_health = state.machine_health if state else 95.0
        work_orders = db.query(WorkOrder).filter(WorkOrder.company_id == company_id).all()

        s1_max = 30
        s1_score = 30 if all_operational else 10
        step_scores.append({"step": "Kehandalan Stasiun Kerja & Pencegahan Downtime Pabrik", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        s2_max = 40
        s2_score = int(min(40, (machine_health / 100.0) * 40))
        step_scores.append({"step": "Pemeliharaan Mesin SMT & Penerapan Standar TPM", "max_score": s2_max, "earned_score": s2_score, "status": "passed" if s2_score >= 30 else "failed"})

        s3_max = 30
        s3_score = 28 if (len(work_orders) > 0 or all_operational) else 15
        step_scores.append({"step": "Realisasi Jadwal Produksi & Pengendalian Scrap", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 20 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0) and all_operational

        fact_sheet = {
            "root_cause": "Downtime stasiun perakitan dan tingginya scrap rate mengikis kapasitas pabrik.",
            "student_actions_taken": f"Kesehatan Mesin: {machine_health:.1f}%. Status Stasiun Kerja: {'Seluruhnya Operasional' if all_operational else 'Ada Kerusakan'}. Work Order Diterbitkan: {len(work_orders)}.",
            "why_evaluation": "Berhasil memelihara kehandalan mesin dan menjaga kesinambungan lini manufaktur." if passed else "Mesin perakitan mengalami kerusakan kritis dan belum dilakukan tindakan perbaikan darurat.",
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Eksekusi perbaikan/maintenance stasiun kerja di modul MRP.\n2. Kalibrasi toleransi resep BOM untuk meminimalkan scrap.\n3. Rilis Work Order penyesuaian kuantitas.",
            "key_takeaway": "Total Productive Maintenance (TPM) adalah kunci efisiensi pabrik dan kepuasan pelanggan."
        }

    # Grade calculation
    grade = "A+" if total_score >= 93 else ("A" if total_score >= 83 else ("B" if total_score >= 70 else ("C" if total_score >= 55 else "D")))

    case.resolution_score = total_score
    case.grade = grade
    case.step_scores = json.dumps(step_scores)
    case.fact_sheet_data = json.dumps(fact_sheet)
    case.status = "resolved" if passed else "failed"

    if state:
        all_cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).all()
        res_list = [c for c in all_cases if c.status == "resolved"]
        if res_list:
            state.overall_score = round(sum(c.resolution_score for c in res_list) / len(res_list), 1)
        else:
            state.overall_score = 0.0

    if passed and state:
        # Unlock next case
        next_case = db.query(ScenarioCase).filter(
            ScenarioCase.company_id == company_id,
            ScenarioCase.stage_order == case.stage_order + 1
        ).first()
        if next_case:
            next_case.status = "active"
            state.active_case_title = next_case.title
            state.active_case_description = next_case.description

    db.commit()
    return {
        "status": "success" if passed else "warning",
        "case_status": case.status,
        "total_score": total_score,
        "grade": grade,
        "step_scores": step_scores,
        "fact_sheet": fact_sheet,
        "message": f"Evaluasi Selesai! Skor: {total_score:.1f}/100 (Predikat: {grade}). {'Kasus Berhasil Dipecahkan!' if passed else 'Kasus Belum Berhasil. Tinjau Fact Sheet Problem Solving!'}"
    }

@router.post("/advance-round/{company_id}")
def advance_round(company_id: int, db: Session = Depends(get_db)):
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="Simulasi tidak ditemukan")
    
    slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == company_id).first()
    state.current_round += 1
    months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    month_idx = (state.current_round - 1) % 12
    state.period_name = f"Bulan {state.current_round} ({months[month_idx]})"

    monthly_sales = 55000000.0 * (1.0 - (slider.competitor_price_war / 200.0 if slider else 0.1))
    monthly_payroll = 30400000.0
    monthly_overhead = 12000000.0
    
    bad_debt_loss = 0.0
    if slider and slider.bad_debt_risk >= 40.0:
        bad_debt_loss = monthly_sales * (slider.bad_debt_risk / 200.0)
    
    monthly_net = monthly_sales - monthly_payroll - monthly_overhead - bad_debt_loss
    
    state.revenue += monthly_sales
    state.expenses += (monthly_payroll + monthly_overhead + bad_debt_loss)
    state.net_profit += monthly_net
    state.cash += monthly_net

    # CASCADE CHECKS:
    bankruptcy_alert = None
    if state.cash < 0:
        state.overall_score = max(5.0, state.overall_score - 35.0)
        bankruptcy_alert = "⚠️ PERUSAHAAN INSOLVENT: Saldo kas minus! Perusahaan berada di ambang kebangkrutan likuidasi!"

    strike_triggered = False
    if state.cash < monthly_payroll:
        state.worker_morale = max(10.0, state.worker_morale - 35.0)
        state.is_strike_active = True
        state.strike_reason = "Gagal bayar gaji karyawan akibat krisis likuiditas kas operasional!"
        strike_triggered = True

    cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1010").first()
    if cash_acc:
        cash_acc.balance = state.cash

    # ============================================================
    # CASCADING SCENARIO ENGINE
    # ============================================================
    cascade_event = None

    # Step 1: Evaluate currently ACTIVE ScenarioCase — penalise if unresolved
    active_cases = db.query(ScenarioCase).filter(
        ScenarioCase.company_id == company_id,
        ScenarioCase.status == "active"
    ).all()

    penalty_messages = []
    for ac in active_cases:
        cat = ac.category or ""
        if cat in ("mrp", "manufacturing"):
            state.machine_health = max(20.0, state.machine_health - 8.0)
            state.worker_morale = max(20.0, state.worker_morale - 5.0)
            for wc in db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all():
                if "SMT" in wc.code or "Perakitan" in wc.name:
                    wc.failure_rate = min(25.0, wc.failure_rate + 3.0)
            penalty_messages.append("⚙️ Mesin semakin aus (Kesehatan Mesin -8%), moral pekerja turun -5%")
        elif cat == "accounting":
            state.cash = max(0.0, state.cash - 15000000.0)
            state.overall_score = max(0.0, state.overall_score - 3.0)
            if cash_acc:
                cash_acc.balance = state.cash
            penalty_messages.append("💸 Denda keterlambatan akuntansi: Kas -Rp 15.000.000")
        elif cat == "crm":
            state.csat_score = max(10.0, state.csat_score - 8.0)
            state.overall_score = max(0.0, state.overall_score - 3.0)
            penalty_messages.append("📉 Keluhan pelanggan memburuk: CSAT -8%")
        elif cat == "hr":
            state.worker_morale = max(10.0, state.worker_morale - 10.0)
            if state.worker_morale < 40.0 and not state.is_strike_active:
                state.is_strike_active = True
                state.strike_reason = "Moral buruh kritis akibat misi SDM yang terbengkalai!"
                strike_triggered = True
            penalty_messages.append("👷 Moral buruh anjlok -10%, risiko mogok kerja meningkat!")
        elif cat == "purchasing":
            state.supplier_health = max(20.0, state.supplier_health - 8.0)
            penalty_messages.append("🚚 Relasi vendor memburuk: Supplier Health -8%")

    # Step 2: Activate next PENDING ScenarioCase (lowest stage_order)
    next_pending = db.query(ScenarioCase).filter(
        ScenarioCase.company_id == company_id,
        ScenarioCase.status == "pending"
    ).order_by(ScenarioCase.stage_order).first()

    new_mission_info = None
    if next_pending:
        next_pending.status = "active"
        next_pending.round_introduced = state.current_round

        cat = next_pending.category or ""
        # Apply specific scenario mutation if defined, otherwise fallback by category
        sc_code = next_pending.code or ""
        mutation = SCENARIO_INITIAL_MUTATIONS.get(sc_code)
        if mutation:
            _apply_scenario_mutation(state, mutation, db, company_id)
        else:
            if cat in ("mrp", "manufacturing"):
                state.machine_health = min(state.machine_health, 62.0)
                state.worker_morale = min(state.worker_morale, 68.0)
                state.is_strike_active = True
                state.strike_reason = "Mesin SMT korsleting inverter dan operator menuntut kenaikan upah lembur."
                for wc in db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all():
                    if "SMT" in wc.code or "Perakitan" in wc.name:
                        wc.status = "breakdown"
                        wc.failure_rate = min(20.0, wc.failure_rate + 5.0)
            elif cat == "accounting":
                bad_debt_hit = 25000000.0
                state.cash = max(0.0, state.cash - bad_debt_hit)
                if cash_acc:
                    cash_acc.balance = state.cash
            elif cat == "crm":
                state.csat_score = min(state.csat_score, 62.0)
            elif cat == "hr":
                state.worker_morale = min(state.worker_morale, 65.0)
                state.is_strike_active = True
                state.strike_reason = "Operator pabrik kelelahan lembur dan menuntut kenaikan upah."
            elif cat == "purchasing":
                state.supplier_health = min(state.supplier_health, 55.0)

        state.active_case_title = next_pending.title
        state.active_case_description = next_pending.description

        new_mission_info = {
            "id": next_pending.id,
            "code": next_pending.code,
            "title": next_pending.title,
            "category": cat,
            "description": next_pending.description,
            "stage_order": next_pending.stage_order,
        }

    # Step 3: Build cascade_event for frontend
    if penalty_messages or new_mission_info:
        module_map = {
            "mrp": "manufacturing", "manufacturing": "manufacturing",
            "accounting": "accounting", "crm": "crm",
            "hr": "hr", "purchasing": "purchasing"
        }
        cascade_module = None
        if new_mission_info:
            cascade_module = module_map.get(new_mission_info["category"], "missions")

        cascade_event = {
            "penalties_applied": penalty_messages,
            "new_mission": new_mission_info,
            "module": cascade_module,
        }

    db.commit()
    return {
        "status": "success",
        "current_round": state.current_round,
        "period_name": state.period_name,
        "net_profit_month": monthly_net,
        "current_cash": state.cash,
        "bad_debt_deducted": bad_debt_loss,
        "bankruptcy_alert": bankruptcy_alert,
        "strike_triggered": strike_triggered,
        "cascade_event": cascade_event,
    }


@router.get("/ending-report/{company_id}")
def get_ending_report(company_id: int, db: Session = Depends(get_db)):
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="Data simulasi tidak ditemukan")

    cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).all()
    resolved_cases = sum(1 for c in cases if c.status == "resolved")
    total_cases = len(cases)

    # Determine Ending Archetype (7 Multi-Ending Spectrum)
    if state.cash < 0:
        ending = {
            "code": "BANKRUPTCY",
            "badge": "PAILIT & LIKUIDASI",
            "badge_color": "bg-red-600 text-white",
            "title": "💀 KEBANGKRUTAN & LIKUIDASI ASET (Chapter 7 Bankruptcy)",
            "subtitle": "Kegagalan Manajemen Likuiditas Kas Operasional",
            "status": "FAILED",
            "verdict": "Perusahaan dinyatakan pailit oleh Pengadilan Niaga. Pembengkakan kompensasi yang tidak terkendali, piutang macet yang tak tertagih, dan saldo kas yang minus membuat perusahaan tidak mampu membayar kewajiban jangka pendek.",
            "autopsy": [
                f"Defisit Kas: Saldo kas tercatat minus Rp {abs(state.cash):,.0f}.",
                "Krisis Solvabilitas: Arus kas masuk tidak mampu menutup beban operasional dan HPP.",
                "Pelajaran Kunci: 'Cash is King' — Margin laba di atas kertas tidak berguna jika kas riil habis."
            ],
            "grade": "F"
        }
    elif state.is_strike_active or state.worker_morale < 45.0:
        ending = {
            "code": "STRIKE_SHUTDOWN",
            "badge": "MOGOK MASSAL",
            "badge_color": "bg-rose-700 text-white",
            "title": "🛑 KELUMPUHAN PABRIK AKIBAT MOGOK KERJA MASSAL",
            "subtitle": "Krisis Hubungan Industrial & Kegagalan Hak Buruh",
            "status": "FAILED",
            "verdict": "Lini perakitan manufaktur diduduki oleh serikat buruh. Kebijakan pemotongan sepihak atau keterlambatan gaji memicu pemogokan berkepanjangan. Mesin pabrik padam, pesanan klien terbengkalai, dan iklim kerja rusak total.",
            "autopsy": [
                f"Moral Pekerja Kritis: Indeks moral buruh berada di {state.worker_morale:.1f}% (Batas aman > 75%).",
                f"Alasan Pemogokan: {state.strike_reason or 'Kekecewaan buruh atas kompensasi dan beban kerja'}.",
                "Pelajaran Kunci: Keberlanjutan industri manufaktur bergantung pada keadilan kemitraan bipartit buruh-manajemen."
            ],
            "grade": "D"
        }
    elif state.csat_score < 45.0:
        ending = {
            "code": "REPUTATION_CRISIS",
            "badge": "SKANDAL MUTU",
            "badge_color": "bg-amber-600 text-white",
            "title": "📉 SKANDAL MUTU & BOIKOT KONSUMEN KORPORAT",
            "subtitle": "Keruntuhan Loyalitas Klien B2B Enterprise",
            "status": "FAILED",
            "verdict": "Akibat meremehkan komplain cacat produk dan memaksakan suku cadang bermutu rendah, CV Megah Sentosa dan jejaring klien korporat lainnya memutus seluruh kontrak pengadaan. Berita cacat produk viral di komunitas bisnis.",
            "autopsy": [
                f"Skor CSAT Jatuh: Indeks kepuasan konsumen hanya {state.csat_score:.1f}% (Batas aman > 70%).",
                "Kehilangan Pendapatan: Kontrak tahunan bernilai ratusan juta rupiah dibatalkan sepihak oleh klien.",
                "Pelajaran Kunci: Biaya retensi klien loyal jauh lebih murah daripada dampak boikot akibat cacat mutu produk."
            ],
            "grade": "D"
        }
    elif state.cash < 50000000.0 or state.overall_score < 60.0:
        ending = {
            "code": "ZOMBIE_CORP",
            "badge": "PERUSAHAAN ZOMBIE",
            "badge_color": "bg-slate-600 text-white",
            "title": "🏢 PERUSAHAAN ZOMBIE (Stagnant Survival Mode)",
            "subtitle": "Bertahan Hidup dengan Margin Tipis & Keterbatasan Modal",
            "status": "SURVIVED",
            "verdict": "Perusahaan berhasil lolos dari jurang kebangkrutan, namun terjebak dalam kondisi stagnan. Saldo kas pas-pasan, peralatan pabrik rentan mogok, dan perusahaan tidak memiliki kapasitas finansial untuk berekspansi.",
            "autopsy": [
                f"Saldo Kas Kritis: Tersisa Rp {state.cash:,.0f} (cadangan operasional sangat sempit).",
                f"Tingkat Penyelesaian Masalah: {resolved_cases}/{total_cases} misi terselesaikan.",
                "Pelajaran Kunci: Efisiensi reaktif hanya cukup untuk bertahan, dibutuhkan inovasi strategis terencana untuk tumbuh."
            ],
            "grade": "C"
        }
    elif state.cash < 150000000.0 or state.overall_score < 78.0:
        ending = {
            "code": "DEBT_RESTRUCTURING",
            "badge": "RESTRUKTURISASI UTANG",
            "badge_color": "bg-orange-600 text-white",
            "title": "🔄 RESTRUKTURISASI UTANG & TURNAROUND (Crisis Navigation)",
            "subtitle": "Manuver Penyelamatan Arus Kas Pasca-Disrupsi Makro",
            "status": "TURNAROUND",
            "verdict": "Perusahaan berhasil selamat dari rentetan disrupsi berkat manuver restrukturisasi utang dan pengetatan biaya operasional. Likuiditas mulai pulih meskipun beban kewajiban jangka panjang masih membayangi.",
            "autopsy": [
                f"Kas Pemulihan: Rp {state.cash:,.0f} dengan laba bersih Rp {state.net_profit:,.0f}.",
                f"Tingkat Resiliensi: Mampu menyerap goncangan pasar dan menyelesaikan {resolved_cases}/{total_cases} skenario.",
                "Pelajaran Kunci: Disiplin anggaran dan negosiasi perpanjangan tenor utang adalah kunci penyelamatan saat krisis likuiditas."
            ],
            "grade": "B-"
        }
    elif state.cash >= 350000000.0 and state.csat_score >= 90.0 and state.worker_morale >= 85.0 and resolved_cases == total_cases:
        ending = {
            "code": "UNICORN_LEADER",
            "badge": "MARKET LEADER",
            "badge_color": "bg-indigo-600 text-white",
            "title": "🏆 MARKET LEADER & UNICORN SCALE-UP (Operational Apex)",
            "subtitle": "Pencapaian Keunggulan Manajerial Paripurna Kelas Dunia",
            "status": "DISTINCTION",
            "verdict": "Pencapaian luar biasa! Perusahaan mendominasi industri berkat integrasi rantai pasok tangguh, lini perakitan nir-cacat (Zero Defect), kepuasan klien 90%+, dan neraca kas yang sangat sehat. Menjadi benchmark nasional!",
            "autopsy": [
                f"Kas Gemilang: Rp {state.cash:,.0f} dengan akumulasi laba bersih Rp {state.net_profit:,.0f}.",
                f"Harmoni Operasional: CSAT {state.csat_score:.1f}% • Moral Buruh {state.worker_morale:.1f}% • Mesin {state.machine_health:.1f}%.",
                f"Misi Tuntas: {resolved_cases}/{total_cases} tantangan industri dipecahkan dengan nilai prima.",
                "Pelajaran Kunci: Kolaborasi harmonis antara pengadaan, manufaktur, pemasaran, dan SDM adalah kunci kejayaan enterprise."
            ],
            "grade": "A+"
        }
    else:
        ending = {
            "code": "PRUDENT_PARTNER",
            "badge": "MITRA STRATEGIS",
            "badge_color": "bg-emerald-600 text-white",
            "title": "🛡️ MITRA STRATEGIS KORPORAT & BUMN (Prudent Enterprise)",
            "subtitle": "Ekosistem B2B Stabil dengan Pertumbuhan Berkelanjutan",
            "status": "PASSED",
            "verdict": "Manajemen mampu menerapkan negosiasi B2B yang matang dan menjaga kesinambungan neraca keuangan. Mediasi cerdas berhasil menyelamatkan kontrak tanpa mengorbankan likuiditas operasional dan hak pekerja.",
            "autopsy": [
                f"Kesehatan Finansial: Saldo kas Rp {state.cash:,.0f} dengan arus kas stabil.",
                f"Loyalitas Kemitraan: CSAT {state.csat_score:.1f}% • Moral Buruh {state.worker_morale:.1f}%.",
                f"Misi Berhasil: {resolved_cases}/{total_cases} kasus berhasil dimitigasi.",
                "Pelajaran Kunci: Kepemimpinan yang cermat dalam mitigasi risiko menghasilkan stabilitas bisnis jangka panjang."
            ],
            "grade": "A"
        }

    return {
        "company_id": company_id,
        "round": state.current_round,
        "period_name": state.period_name,
        "ending": ending,
        "metrics": {
            "cash": state.cash,
            "net_profit": state.net_profit,
            "revenue": state.revenue,
            "expenses": state.expenses,
            "csat_score": state.csat_score,
            "worker_morale": state.worker_morale,
            "machine_health": state.machine_health,
            "supplier_health": state.supplier_health,
            "overall_score": state.overall_score,
            "is_strike": state.is_strike_active,
            "resolved_cases": resolved_cases,
            "total_cases": total_cases
        }
    }

@router.get("/leaderboard/{session_id}")
def get_leaderboard(session_id: int, db: Session = Depends(get_db)):
    companies = db.query(Company).filter(Company.session_id == session_id).all()
    results = []
    for co in companies:
        st = co.sim_state
        sl = co.slider_config
        results.append({
            "company_id": co.id,
            "company_name": co.name,
            "overall_score": st.overall_score if st else 0.0,
            "cash": st.cash if st else 500000000.0,
            "net_profit": st.net_profit if st else 0.0,
            "csat_score": st.csat_score if st else 85.0,
            "worker_morale": st.worker_morale if st else 90.0,
            "machine_health": st.machine_health if st else 95.0,
            "supplier_health": st.supplier_health if st else 90.0,
            "is_strike": st.is_strike_active if st else False,
            "sliders": {
                "supply": sl.supply_disruption if sl else 20.0,
                "breakdown": sl.machine_breakdown_risk if sl else 15.0,
                "strike": sl.labor_strike_risk if sl else 10.0,
                "bad_debt": sl.bad_debt_risk if sl else 15.0,
            }
        })
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results

@router.post("/companies/{company_id}/reset-missions")
def reset_company_missions(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")

    # 1. Clean transactions generated by student
    sos = db.query(SalesOrder).filter(SalesOrder.company_id == company_id).all()
    for so in sos:
        db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == so.id).delete()
        db.delete(so)
    
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id).all()
    for po in pos:
        db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po.id).delete()
        db.delete(po)

    db.query(WorkOrder).filter(WorkOrder.company_id == company_id).delete()

    jes = db.query(JournalEntry).filter(JournalEntry.company_id == company_id).all()
    for je in jes:
        db.query(JournalItem).filter(JournalItem.journal_entry_id == je.id).delete()
        db.delete(je)

    # 2. Reset product stock to initial baseline
    products = db.query(Product).filter(Product.company_id == company_id).all()
    for p in products:
        if p.product_type == "raw_material":
            p.current_stock = 40.0
        elif p.product_type == "finished_good":
            p.current_stock = 25.0

    # 3. Reset scenario cases to initial pending/active
    cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).order_by(ScenarioCase.stage_order.asc()).all()
    for idx, c in enumerate(cases):
        if idx == 0:
            c.status = "active"
        else:
            c.status = "pending"
        c.resolution_score = 0.0
        c.grade = "-"
        c.step_scores = None
        c.fact_sheet_data = None

    # 4. Reset CRM Complaints to unresolved so student can mitigate it
    complaints = db.query(CRMLead).filter(CRMLead.company_id == company_id, CRMLead.is_complaint == True).all()
    for comp in complaints:
        comp.stage = "proposition"
        comp.resolution_action = None

    # 5. Reset cash and simulation state
    init_cash = company.initial_capital or 500000000.0
    company.current_cash = init_cash
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if state:
        state.cash = init_cash
        state.revenue = 0.0
        state.expenses = 0.0
        state.net_profit = 0.0
        state.csat_score = 88.0
        state.worker_morale = 92.0
        state.machine_health = 95.0
        state.is_strike_active = False
        state.strike_reason = None
        state.overall_score = 0.0
        if cases:
            state.active_case_title = cases[0].title
            state.active_case_description = cases[0].description

    # Reset account cash (1010)
    cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1010").first()
    if cash_acc:
        cash_acc.balance = init_cash

    db.commit()
    return {
        "status": "success",
        "message": f"Seluruh isian transaksi, stok gudang & skor misi untuk '{company.name}' berhasil di-reset ke kondisi awal!"
    }

@router.post("/reset-all-missions")
def reset_all_companies_missions(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    for co in companies:
        # Clean transactions
        sos = db.query(SalesOrder).filter(SalesOrder.company_id == co.id).all()
        for so in sos:
            db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == so.id).delete()
            db.delete(so)
        
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == co.id).all()
        for po in pos:
            db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po.id).delete()
            db.delete(po)

        db.query(WorkOrder).filter(WorkOrder.company_id == co.id).delete()

        jes = db.query(JournalEntry).filter(JournalEntry.company_id == co.id).all()
        for je in jes:
            db.query(JournalItem).filter(JournalItem.journal_entry_id == je.id).delete()
            db.delete(je)

        # Reset stock
        products = db.query(Product).filter(Product.company_id == co.id).all()
        for p in products:
            if p.product_type == "raw_material":
                p.current_stock = 40.0
            elif p.product_type == "finished_good":
                p.current_stock = 25.0

        # Reset cases
        cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == co.id).order_by(ScenarioCase.stage_order.asc()).all()
        for idx, c in enumerate(cases):
            if idx == 0:
                c.status = "active"
            else:
                c.status = "pending"
            c.resolution_score = 0.0
            c.grade = "-"
            c.step_scores = None
            c.fact_sheet_data = None
        
        # Reset complaints
        complaints = db.query(CRMLead).filter(CRMLead.company_id == co.id, CRMLead.is_complaint == True).all()
        for comp in complaints:
            comp.stage = "proposition"
            comp.resolution_action = None

        # Reset state & cash
        init_cash = co.initial_capital or 500000000.0
        co.current_cash = init_cash
        state = db.query(SimulationState).filter(SimulationState.company_id == co.id).first()
        if state:
            state.cash = init_cash
            state.revenue = 0.0
            state.expenses = 0.0
            state.net_profit = 0.0
            state.csat_score = 88.0
            state.worker_morale = 92.0
            state.machine_health = 95.0
            state.is_strike_active = False
            state.strike_reason = None
            state.overall_score = 0.0
            if cases:
                state.active_case_title = cases[0].title
                state.active_case_description = cases[0].description

        cash_acc = db.query(Account).filter(Account.company_id == co.id, Account.code == "1010").first()
        if cash_acc:
            cash_acc.balance = init_cash

    db.commit()
    return {
        "status": "success",
        "message": f"Seluruh isian transaksi & misi untuk {len(companies)} perusahaan berhasil di-reset ke kondisi awal!"
    }

@router.post("/cases/{case_id}/reset")
def reset_single_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(ScenarioCase).filter(ScenarioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    
    case.status = "active"
    case.resolution_score = 0.0
    case.grade = "-"
    case.step_scores = None
    case.fact_sheet_data = None

    cat = (case.category or "").lower()
    if cat in ["crm", "marketing", "sales"]:
        complaints = db.query(CRMLead).filter(CRMLead.company_id == case.company_id, CRMLead.is_complaint == True).all()
        for complaint in complaints:
            complaint.stage = "proposition"
            complaint.resolution_action = None
    elif cat in ["procurement", "purchasing", "scm"]:
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == case.company_id).all()
        for po in pos:
            db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po.id).delete()
            db.delete(po)

    db.commit()
    return {
        "status": "success",
        "message": f"Misi '{case.title}' berhasil di-reset ke status aktif tanpa jawaban tersimpan!"
    }


# =======================================================
# --- SMART PYTHON BRAIN: SCENARIO MATRIX & STORYLINE ---
# =======================================================

class ExecuteBranchRequest(BaseModel):
    scenario_id: str
    choice_id: str

class CalculateRippleRequest(BaseModel):
    company_id: int
    action_type: str
    action_payload: Optional[dict] = {}

@router.get("/scenarios/matrix")
def get_scenario_matrix():
    """
    Returns the full 20-scenario multi-domain matrix with branch options,
    rationale, ripple consequences, and formal document templates.
    """
    return {
        "total_scenarios": 20,
        "scenarios": get_all_scenarios_matrix()
    }

@router.get("/scenarios/{scenario_id}")
def get_scenario_detail(scenario_id: str):
    sc = get_scenario_by_id(scenario_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Skenario tidak ditemukan")
    return sc

@router.post("/scenarios/{company_id}/execute-branch")
def post_execute_scenario_branch(
    company_id: int,
    payload: ExecuteBranchRequest,
    db: Session = Depends(get_db)
):
    """
    Executes a branching decision for a specific company tenant, applying
    financial impacts, persisting story events, and generating formal business documents.
    """
    try:
        result = execute_scenario_branch(
            company_id=company_id,
            scenario_id=payload.scenario_id,
            choice_id=payload.choice_id,
            db=db
        )
        return {
            "status": "success",
            "message": f"Keputusan Cabang '{payload.choice_id}' untuk skenario '{payload.scenario_id}' berhasil dieksekusi!",
            "data": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal execution error: {str(e)}")

@router.get("/storyline/{company_id}")
def get_company_storyline(company_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the chronological story event log, branch choices made,
    generated documents, and cumulative consequences for a company.
    """
    events = (
        db.query(CompanyStoryEvent)
        .filter(CompanyStoryEvent.company_id == company_id)
        .order_by(CompanyStoryEvent.created_at.desc())
        .all()
    )
    story_list = []
    for ev in events:
        ripples = []
        if ev.ripple_summary:
            try:
                ripples = json.loads(ev.ripple_summary) if isinstance(ev.ripple_summary, str) else ev.ripple_summary
            except Exception:
                ripples = []
        doc = None
        if ev.document_data:
            try:
                doc = json.loads(ev.document_data) if isinstance(ev.document_data, str) else ev.document_data
            except Exception:
                doc = None

        story_list.append({
            "id": ev.id,
            "round_number": ev.round_number,
            "period_name": ev.period_name,
            "domain": ev.domain,
            "event_type": ev.event_type,
            "title": ev.title,
            "description": ev.description,
            "decision_taken": ev.decision_taken,
            "ripples": ripples,
            "document": doc,
            "created_at": ev.created_at.isoformat()
        })

    return {
        "company_id": company_id,
        "total_events": len(events),
        "events": story_list
    }

@router.get("/cfo-diagnostics/{company_id}")
def get_cfo_diagnostics(company_id: int, db: Session = Depends(get_db)):
    """
    Returns automated DuPont analysis, Altman Z-Score, Working Capital breakdown,
    and strategic recommendations for lecturers and student teams.
    """
    try:
        diagnostics = run_smart_cfo_diagnostics(company_id=company_id, db=db)
        return diagnostics
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CFO diagnostics computation error: {str(e)}")

@router.post("/ripples/calculate")
def post_calculate_ripples(
    payload: CalculateRippleRequest,
    db: Session = Depends(get_db)
):
    """
    Calculates multi-departmental domino impacts for standard ERP user actions.
    """
    try:
        ripples = calculate_action_ripples(
            company_id=payload.company_id,
            action_type=payload.action_type,
            action_payload=payload.action_payload or {},
            db=db
        )
        return ripples
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ripple calculation error: {str(e)}")


```


---
# FILE: backend/app/routers/crm.py
---
```python
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import (
    CRMLead, Customer, SalesOrder, SalesOrderItem, Product, SimulationState, ScenarioCase,
    Account, BillOfMaterials, BOMItem, WorkCenter, WorkOrder, Employee, JournalEntry, JournalItem, CompanyStoryEvent
)
from backend.app.schemas.schemas import CRMLeadOut, CRMLeadUpdate
from backend.app.services.behavior_engine import get_random_customer_temperament

router = APIRouter(prefix="/crm", tags=["crm"])

@router.post("/randomize-customer/{lead_id}")
def randomize_customer_temperament(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(CRMLead).filter(CRMLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead tidak ditemukan")

    persona = get_random_customer_temperament()
    lead.is_complaint = True
    lead.complaint_details = persona["dialog"]
    lead.priority = "urgent" if persona["type"] == "annoyingly_angry" else ("high" if persona["type"] == "shrewd_negotiator" else "medium")
    lead.notes = "Keluhan resmi diajukan melalui saluran prioritas. Menunggu tindak lanjut departemen layanan pelanggan."
    
    db.commit()
    db.refresh(lead)
    return {
        "status": "success",
        "lead_id": lead.id,
        "customer_name": lead.customer_name,
        "dialog": persona["dialog"]
    }

class ResolveComplaintRequest(BaseModel):
    action_type: str  # 'replace_with_discount', 'executive_meeting', 'ignore'
    notes: Optional[str] = None

class ConvertLeadToSORequest(BaseModel):
    lead_id: int
    product_id: int
    quantity: int
    payment_terms: str = "Tempo 30 Hari"

class CreateLeadRequest(BaseModel):
    company_id: int
    title: str
    customer_name: str
    customer_email: Optional[str] = None
    stage: str = "new"
    expected_revenue: float = 50000000.0
    probability: float = 30.0
    priority: str = "medium"
    credit_rating: str = "medium_risk"
    notes: Optional[str] = None

@router.get("/leads/{company_id}", response_model=List[CRMLeadOut])
def list_leads(company_id: int, db: Session = Depends(get_db)):
    return db.query(CRMLead).filter(CRMLead.company_id == company_id).all()

@router.post("/leads", response_model=CRMLeadOut)
def create_lead(payload: CreateLeadRequest, db: Session = Depends(get_db)):
    lead = CRMLead(
        company_id=payload.company_id,
        title=payload.title,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        stage=payload.stage,
        expected_revenue=payload.expected_revenue,
        probability=payload.probability,
        priority=payload.priority,
        credit_rating=payload.credit_rating,
        notes=payload.notes
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

@router.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(CRMLead).filter(CRMLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead tidak ditemukan")
    db.delete(lead)
    db.commit()
    return {"status": "success", "message": f"Lead '{lead.title}' berhasil dihapus"}

@router.patch("/leads/{lead_id}", response_model=CRMLeadOut)
def update_lead(lead_id: int, payload: CRMLeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(CRMLead).filter(CRMLead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead tidak ditemukan")

    if payload.stage is not None:
        lead.stage = payload.stage
        if payload.stage == "won":
            lead.probability = 100.0
        elif payload.stage == "lost":
            lead.probability = 0.0

    if payload.priority is not None:
        lead.priority = payload.priority
    if payload.resolution_action is not None:
        lead.resolution_action = payload.resolution_action
    if payload.notes is not None:
        lead.notes = payload.notes

    db.commit()
    db.refresh(lead)
    return lead

@router.post("/leads/{lead_id}/resolve-complaint")
def resolve_complaint(lead_id: int, payload: ResolveComplaintRequest, db: Session = Depends(get_db)):
    lead = db.query(CRMLead).filter(CRMLead.id == lead_id).first()
    if not lead or not lead.is_complaint:
        raise HTTPException(status_code=404, detail="Tiket keluhan tidak valid")

    state = db.query(SimulationState).filter(SimulationState.company_id == lead.company_id).first()
    finished_prod = db.query(Product).filter(
        Product.company_id == lead.company_id,
        Product.product_type == "finished_good"
    ).first()

    cascade_note = ""

    if payload.action_type == "replace_with_discount":
        lead.stage = "won"
        lead.csat_score = 92.0
        lead.resolution_action = "Penggantian 15 Unit Baru Gratis + Voucher Diskon 10%"
        if finished_prod:
            if finished_prod.current_stock >= 15:
                finished_prod.current_stock -= 15
                cascade_note = f"Stok barang jadi '{finished_prod.name}' dipotong 15 unit (sisa {finished_prod.current_stock})."
            else:
                cascade_note = f"PERINGATAN GUDANG: Stok barang jadi hanya {finished_prod.current_stock} unit! Segera terbitkan Work Order darurat di modul MRP."
        if state:
            state.csat_score = min(98.0, state.csat_score + 20.0)
            state.cash -= 3150000.0  # HPP penggantian 15 unit
        message = f"Keluhan berhasil diselesaikan! Klien puas dan kontrak Rp 150.000.000 terselamatkan. {cascade_note}"

    elif payload.action_type == "executive_meeting":
        lead.stage = "proposition"
        lead.csat_score = 75.0
        lead.resolution_action = "Dalam Proses Mediasi Tingkat Direksi (Menunggu Kesepakatan Final)"
        if state:
            state.csat_score = min(98.0, state.csat_score + 10.0)
        message = "Pertemuan mediasi terlaksana! Klien bersedia menunda pembatalan kontrak. Buka Notulensi Mediasi untuk memilih opsi kesepakatan akhir."

    elif payload.action_type == "mediation_discount_addendum":
        lead.stage = "won"
        lead.csat_score = 88.0
        lead.resolution_action = "Kesepakatan Mediasi: Addendum Diskon 15% pada Termin Berjalan (Tanpa Ganti Fisik)"
        if state:
            state.csat_score = min(98.0, state.csat_score + 16.0)
            # Kas tidak terpotong langsung, hanya margin future revenue yang disesuaikan
        message = "Kesepakatan Mediasi Tercapai! Addendum diskon 15% disetujui. Kas operasional utuh, stok gudang aman, dan kontrak Rp 150M terselamatkan!"

    elif payload.action_type == "mediation_emergency_replace":
        lead.stage = "won"
        lead.csat_score = 96.0
        lead.resolution_action = "Kesepakatan Mediasi: Penggantian 15 Unit Fisik Bergaransi Penuh dari Pabrik"
        if finished_prod:
            if finished_prod.current_stock >= 15:
                finished_prod.current_stock -= 15
                cascade_note = f"Stok gudang terpotong 15 unit (sisa: {finished_prod.current_stock})."
            else:
                cascade_note = f"PERINGATAN GUDANG: Stok hanya {finished_prod.current_stock} unit! Wajib rilis Work Order di modul MRP."
        if state:
            state.csat_score = min(98.0, state.csat_score + 22.0)
            state.cash -= 3150000.0
        message = f"Kesepakatan Mediasi Tercapai! Penggantian 15 unit bergaransi dieksekusi. Kepuasan klien pulih maksimal (CSAT 96%). {cascade_note}"

    elif payload.action_type == "mediation_qc_investigation":
        lead.stage = "won"
        lead.csat_score = 82.0
        lead.resolution_action = "Kesepakatan Mediasi: Servis Unit di Lokasi Klien & Forensik Defect Vendor"
        tech_service_cost = 1500000.0
        if state:
            state.csat_score = min(98.0, state.csat_score + 12.0)
            state.cash -= tech_service_cost
        message = f"Kesepakatan Mediasi Tercapai! Tim teknisi dikirim ke lokasi klien (Biaya Rp {tech_service_cost:,.0f}). Ditemukan cacat berasal dari batch vendor layar."

    else:
        lead.stage = "lost"
        lead.csat_score = 15.0
        lead.resolution_action = "Keluhan Diabaikan Tanpa Tindakan"
        if state:
            state.csat_score = max(10.0, state.csat_score - 35.0)
        message = "Keluhan diabaikan! Klien memutuskan kontrak tahunan Rp 150.000.000 dan reputasi perusahaan rusak di pasar korporat."

    # Auto-resolve matching CRM ScenarioCase for Problem-Based Learning
    if lead.stage == "won":
        crm_case = db.query(ScenarioCase).filter(
            ScenarioCase.company_id == lead.company_id,
            ScenarioCase.category.in_(["crm", "marketing", "sales"]),
            ScenarioCase.status.in_(["active", "pending"])
        ).first()

        if crm_case:
            if payload.action_type == "mediation_discount_addendum":
                score = 94.0
                grade = "A+"
                strategy_note = "Kesepakatan Mediasi Direksi: Addendum Diskon 15% (Kas & Stok Utuh)"
            elif payload.action_type == "mediation_emergency_replace":
                score = 96.0
                grade = "A+"
                strategy_note = "Kesepakatan Mediasi Direksi: Penggantian 15 Unit Fisik Bergaransi"
            elif payload.action_type == "mediation_qc_investigation":
                score = 90.0
                grade = "A"
                strategy_note = "Kesepakatan Mediasi Direksi: Tim Servis Lapangan & Forensik Cacat Vendor"
            else:
                score = 92.0
                grade = "A"
                strategy_note = "SOP Customer-First: Ganti Unit Baru + Voucher Diskon 10%"

            steps = [
                {"step": "Kecepatan Respon & Penanganan Tiket Darurat Akun VIP", "max_score": 30, "earned_score": 30, "status": "passed"},
                {"step": f"Eksekusi Strategis: {strategy_note}", "max_score": 40, "earned_score": 38 if score >= 90 else 34, "status": "passed"},
                {"step": "Penyelamatan Kontrak Dagang Rp 150M & Pemulihan CSAT", "max_score": 30, "earned_score": 26 if score >= 90 else 24, "status": "passed"}
            ]

            fact_sheet = {
                "root_cause": "Lolosnya unit layar cacat ke klien enterprise VIP CV Megah Sentosa mengancam pemutusan kontrak dagang Rp 150.000.000.",
                "student_actions_taken": f"Keputusan Terpilih: {strategy_note}. CSAT Pulih: {lead.csat_score}%.",
                "why_evaluation": "Keputusan Manajerial Brilian! Pilihan solusi terbukti menyelamatkan loyalitas klien enterprise dan memperkuat reputasi B2B.",
                "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Addendum Diskon 15% (Aman kas & stok).\n2. Penggantian Unit Fisik (Customer-First).\n3. Tim Servis Lapangan & Audit Vendor (Forensik Pragmatis).",
                "key_takeaway": "Retensi akun B2B memiliki beragam opsi kompensasi; eksekusi yang tanggap dan berkeadilan bagi klien adalah kunci sukses retensi enterprise."
            }

            crm_case.status = "resolved"
            crm_case.resolution_score = score
            crm_case.grade = grade
            crm_case.step_scores = json.dumps(steps)
            crm_case.fact_sheet_data = json.dumps(fact_sheet)

            # Unlock next mission in sequence
            next_case = db.query(ScenarioCase).filter(
                ScenarioCase.company_id == lead.company_id,
                ScenarioCase.stage_order == crm_case.stage_order + 1
            ).first()
            if next_case:
                next_case.status = "active"
                if state:
                    state.active_case_title = next_case.title
                    state.active_case_description = next_case.description

            if state:
                state.overall_score = min(100.0, state.overall_score + 5.0)

            message += f" 🎯 Misi Lab PBL '{crm_case.title}' otomatis dinyatakan Selesai (Skor: {score:.0f} • Predikat: {grade})!"

    # Log to Audit Trail
    from backend.app.models.models import CompanyStoryEvent
    round_num = state.current_round if state else 1
    crm_ripples = [
        {"dept": "CRM & Layanan Pelanggan", "icon": "👥", "impact": f"Keluhan {lead.customer_name} ditangani: {lead.resolution_action}. CSAT: {lead.csat_score}%."},
        {"dept": "Keuangan & Kas", "icon": "💰", "impact": f"Kompensasi penanganan: Kas tersesuaikan, valuasi kontrak Rp 150.000.000 terselamatkan."}
    ]
    if cascade_note:
        crm_ripples.append({"dept": "Pabrik & Gudang", "icon": "🏭", "impact": cascade_note})

    complaint_event = CompanyStoryEvent(
        company_id=lead.company_id,
        round_number=round_num,
        period_name=f"Bulan {round_num}",
        domain="crm",
        event_type="operational_transaction",
        title=f"Resolusi Tiket Keluhan Pelanggan — {lead.customer_name}",
        description=f"Departemen Layanan Pelanggan & CRM berhasil mengeksekusi tindakan penanganan: '{lead.resolution_action}'. {message}",
        decision_taken=lead.resolution_action,
        ripple_summary=json.dumps(crm_ripples),
        document_data=json.dumps({
            "doc_type": "COMPLAINT_SETTLEMENT",
            "customer": lead.customer_name,
            "action_taken": lead.resolution_action,
            "csat_score": lead.csat_score,
            "timestamp": "Baru Saja"
        })
    )
    db.add(complaint_event)

    db.commit()
    return {
        "status": "success",
        "lead_id": lead.id,
        "new_stage": lead.stage,
        "csat_score": lead.csat_score,
        "resolution_action": lead.resolution_action,
        "message": message
    }

@router.post("/convert-to-so")
def convert_lead_to_so(payload: ConvertLeadToSORequest, db: Session = Depends(get_db)):
    lead = db.query(CRMLead).filter(CRMLead.id == payload.lead_id).first()
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not lead or not product:
        raise HTTPException(status_code=404, detail="Lead atau produk tidak ditemukan")

    # Check credit risk warning
    warning = None
    if lead.credit_rating == "high_risk" and "Tempo" in payload.payment_terms:
        warning = "PERINGATAN: Klien memiliki risiko kredit tinggi. Memberikan tempo pembayaran tanpa DP berisiko gagal bayar (Bad Debt)!"

    # Customer record
    customer = db.query(Customer).filter(Customer.name == lead.customer_name).first()
    if not customer:
        customer = Customer(
            company_id=lead.company_id,
            name=lead.customer_name,
            email=lead.customer_email,
            credit_rating=lead.credit_rating,
            csat_score=lead.csat_score
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

    count = db.query(SalesOrder).filter(SalesOrder.company_id == lead.company_id).count() + 1
    code = f"SO/2026/{count:04d}"
    total = product.list_price * payload.quantity
    cogs_total = product.cost_price * payload.quantity

    so = SalesOrder(
        company_id=lead.company_id,
        customer_id=customer.id,
        code=code,
        total_amount=total,
        payment_terms=payload.payment_terms,
        status="confirmed"
    )
    db.add(so)
    db.commit()
    db.refresh(so)

    item = SalesOrderItem(
        sales_order_id=so.id,
        product_id=product.id,
        quantity=payload.quantity,
        unit_price=product.list_price,
        subtotal=total
    )
    db.add(item)

    # Lead marked won
    lead.stage = "won"
    lead.probability = 100.0

    state = db.query(SimulationState).filter(SimulationState.company_id == lead.company_id).first()
    round_num = state.current_round if state else 1
    period_label = f"Bulan {round_num}"

    # --- INVENTORY & PRODUCTION CASCADE ---
    initial_fg_stock = product.current_stock
    units_from_stock = 0
    deficit_qty = 0
    auto_wo_code = None
    consumed_raw_details = []

    if product.current_stock >= payload.quantity:
        product.current_stock -= payload.quantity
        units_from_stock = payload.quantity
    else:
        units_from_stock = product.current_stock
        deficit_qty = payload.quantity - product.current_stock
        product.current_stock = 0

    # Auto Work Order in MRP if deficit
    from backend.app.models.models import BillOfMaterials, BOMItem, WorkCenter, WorkOrder, Employee, JournalEntry, JournalItem, CompanyStoryEvent

    if deficit_qty > 0:
        bom = db.query(BillOfMaterials).filter(
            BillOfMaterials.company_id == lead.company_id,
            BillOfMaterials.finished_product_id == product.id
        ).first()
        if not bom:
            bom = db.query(BillOfMaterials).filter(BillOfMaterials.company_id == lead.company_id).first()

        wc = db.query(WorkCenter).filter(WorkCenter.company_id == lead.company_id).first()
        
        if bom and wc:
            # Deduct raw materials based on BOM
            for bom_item in bom.items:
                raw = db.query(Product).filter(Product.id == bom_item.raw_product_id).first()
                if raw:
                    needed_raw = bom_item.quantity_required * deficit_qty
                    raw.current_stock = max(0.0, raw.current_stock - needed_raw)
                    consumed_raw_details.append(f"{raw.name}: -{needed_raw:g} {raw.uom}")
                    # Reduce Raw Inventory balance in Accounting
                    raw_acc = db.query(Account).filter(Account.company_id == lead.company_id, Account.code == "1030").first()
                    if raw_acc:
                        raw_acc.balance = max(0.0, raw_acc.balance - (needed_raw * raw.cost_price))

            wo_count = db.query(WorkOrder).filter(WorkOrder.company_id == lead.company_id).count() + 1
            auto_wo_code = f"WO/AUTO/{wo_count:04d}"
            wo = WorkOrder(
                company_id=lead.company_id,
                bom_id=bom.id,
                work_center_id=wc.id,
                code=auto_wo_code,
                qty_to_produce=deficit_qty,
                qty_produced=deficit_qty,
                scrap_qty=0,
                status="completed"
            )
            db.add(wo)

            # Wear & tear on machine
            wc.failure_rate = min(25.0, wc.failure_rate + (deficit_qty * 0.04))
            if state:
                state.machine_health = max(10.0, state.machine_health - (deficit_qty * 0.06))

            # Fatigue & morale on HR
            factory_workers = db.query(Employee).filter(
                Employee.company_id == lead.company_id,
                Employee.department == "Produksi"
            ).all()
            for worker in factory_workers:
                worker.fatigue_score = min(100.0, worker.fatigue_score + (deficit_qty * 0.18))
                worker.morale_score = max(10.0, worker.morale_score - (deficit_qty * 0.08))

    # --- ACCOUNTING CASCADE & GENERAL LEDGER ---
    cash_acc = db.query(Account).filter(Account.company_id == lead.company_id, Account.code == "1010").first()
    ar_acc = db.query(Account).filter(Account.company_id == lead.company_id, Account.code == "1020").first()
    fg_acc = db.query(Account).filter(Account.company_id == lead.company_id, Account.code == "1040").first()
    rev_acc = db.query(Account).filter(Account.company_id == lead.company_id, Account.code == "4010").first()
    cogs_acc = db.query(Account).filter(Account.company_id == lead.company_id, Account.code == "5010").first()

    is_cash = "Tunai" in payload.payment_terms or "Cash" in payload.payment_terms
    je_count = db.query(JournalEntry).filter(JournalEntry.company_id == lead.company_id).count() + 1
    je = JournalEntry(
        company_id=lead.company_id,
        entry_number=f"JE/SO/{je_count:04d}",
        reference=code,
        memo=f"Pengakuan Penjualan & HPP {product.name} x {payload.quantity} unit ({customer.name})"
    )
    db.add(je)
    db.commit()
    db.refresh(je)

    # 1. Sales Recognition Entry
    if is_cash:
        if cash_acc:
            cash_acc.balance += total
            db.add(JournalItem(journal_entry_id=je.id, account_id=cash_acc.id, debit=total, credit=0.0))
    else:
        if ar_acc:
            ar_acc.balance += total
            db.add(JournalItem(journal_entry_id=je.id, account_id=ar_acc.id, debit=total, credit=0.0))

    if rev_acc:
        rev_acc.balance += total
        db.add(JournalItem(journal_entry_id=je.id, account_id=rev_acc.id, debit=0.0, credit=total))

    # 2. COGS & Inventory Entry
    if cogs_acc:
        cogs_acc.balance += cogs_total
        db.add(JournalItem(journal_entry_id=je.id, account_id=cogs_acc.id, debit=cogs_total, credit=0.0))
    if fg_acc:
        fg_acc.balance = max(0.0, fg_acc.balance - cogs_total)
        db.add(JournalItem(journal_entry_id=je.id, account_id=fg_acc.id, debit=0.0, credit=cogs_total))

    # Update Simulation State
    if state:
        state.revenue += total
        if is_cash:
            state.cash += total
        state.net_profit += (total - cogs_total)

    # --- CROSS-MODULE AUDIT TRAIL LOG (CompanyStoryEvent) ---
    ripples = [
        {
            "dept": "CRM & Sales",
            "icon": "👥",
            "impact": f"Sales Order {code} disahkan: {payload.quantity} unit {product.name} @ Rp {product.list_price:,.0f} (Total Rp {total:,.0f}, Termin: {payload.payment_terms})"
        },
        {
            "dept": "Keuangan & Akuntansi",
            "icon": "💰",
            "impact": f"Jurnal {je.entry_number}: {'Kas bertambah' if is_cash else 'Piutang Usaha (AR) bertambah'} Rp {total:,.0f}, Pendapatan +Rp {total:,.0f}, HPP +Rp {cogs_total:,.0f}"
        },
        {
            "dept": "Gudang & Logistik",
            "icon": "📦",
            "impact": f"Stok Barang Jadi dipotong {units_from_stock} unit (Sisa di rak: {product.current_stock} unit)."
        }
    ]

    if deficit_qty > 0:
        ripples.append({
            "dept": "Manufaktur & MRP",
            "icon": "🏭",
            "impact": f"Work Order Darurat #{auto_wo_code} terpicu otomatis untuk memproduksi defisit {deficit_qty} unit. Bahan baku terkonsumsi: {', '.join(consumed_raw_details)}."
        })
        ripples.append({
            "dept": "SDM & Pabrik",
            "icon": "👔",
            "impact": f"Lonjakan beban kerja manufaktur! Mesin terdepresiasi, kelelahan operator perakitan naik +{(deficit_qty * 0.18):.1f}%."
        })

    doc_data = {
        "doc_type": "SALES_ORDER",
        "doc_code": code,
        "customer": customer.name,
        "product": product.name,
        "quantity": payload.quantity,
        "unit_price": product.list_price,
        "total_amount": total,
        "payment_terms": payload.payment_terms,
        "journal_entry": je.entry_number,
        "auto_wo": auto_wo_code,
        "created_at": "Baru Saja"
    }

    story_ev = CompanyStoryEvent(
        company_id=lead.company_id,
        round_number=round_num,
        period_name=period_label,
        domain="crm",
        event_type="operational_transaction",
        title=f"Eksekusi Sales Order #{code} ({customer.name})",
        description=f"Perusahaan berhasil mengonversi prospek CRM menjadi Sales Order resmi #{code} senilai Rp {total:,.0f} ({payload.quantity} unit {product.name}). Transaksi memicu rantai otomasi lintas departemen (CRM ➔ MRP ➔ Akuntansi ➔ HR).",
        decision_taken=f"Penerbitan SO Termin: {payload.payment_terms}",
        ripple_summary=json.dumps(ripples),
        document_data=json.dumps(doc_data)
    )
    db.add(story_ev)

    db.commit()
    return {
        "status": "success",
        "so_code": code,
        "customer": customer.name,
        "total_amount": total,
        "warning": warning,
        "deficit_produced": deficit_qty,
        "auto_wo_code": auto_wo_code,
        "journal_entry": je.entry_number
    }

```


---
# FILE: backend/app/routers/vendors.py
---
```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import Vendor, VendorMetricHistory, PurchaseOrder, PurchaseOrderItem, Product, Account
from backend.app.schemas.schemas import VendorOut

router = APIRouter(prefix="/vendors", tags=["vendors"])

class CreatePORequest(BaseModel):
    vendor_id: int
    product_id: int
    quantity: int
    payment_method: str = "tempo"  # "tempo" (AP / Kredit) or "cash" (Kas Tunai)

class PayAPRequest(BaseModel):
    company_id: int
    amount: float

class CreateVendorRequest(BaseModel):
    company_id: int
    name: str
    category: str = "Komponen Presisi & Bahan Baku"
    lead_time_days: int = 5
    fulfillment_rate: float = 95.0
    on_time_rate: float = 90.0
    defect_rate: float = 1.5
    price_multiplier: float = 1.0
    min_order_qty: int = 10
    credit_terms_days: int = 30
    notes: Optional[str] = None

class UpdateVendorRequest(BaseModel):
    name: Optional[str] = None
    lead_time_days: Optional[int] = None
    price_multiplier: Optional[float] = None
    notes: Optional[str] = None

@router.get("/{company_id}", response_model=List[VendorOut])
def list_vendors(company_id: int, db: Session = Depends(get_db)):
    return db.query(Vendor).filter(Vendor.company_id == company_id).all()

@router.post("", response_model=VendorOut)
def create_vendor(payload: CreateVendorRequest, db: Session = Depends(get_db)):
    vendor = Vendor(
        company_id=payload.company_id,
        name=payload.name,
        category=payload.category,
        lead_time_days=payload.lead_time_days,
        fulfillment_rate=payload.fulfillment_rate,
        on_time_rate=payload.on_time_rate,
        defect_rate=payload.defect_rate,
        price_multiplier=payload.price_multiplier,
        min_order_qty=payload.min_order_qty,
        credit_terms_days=payload.credit_terms_days,
        notes=payload.notes
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

@router.put("/{vendor_id}", response_model=VendorOut)
def update_vendor(vendor_id: int, payload: UpdateVendorRequest, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor tidak ditemukan")
    if payload.name is not None: vendor.name = payload.name
    if payload.lead_time_days is not None: vendor.lead_time_days = payload.lead_time_days
    if payload.price_multiplier is not None: vendor.price_multiplier = payload.price_multiplier
    if payload.notes is not None: vendor.notes = payload.notes
    db.commit()
    db.refresh(vendor)
    return vendor

@router.delete("/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor tidak ditemukan")
    db.delete(vendor)
    db.commit()
    return {"status": "success", "message": f"Vendor '{vendor.name}' berhasil dihapus"}

@router.get("/detail/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor tidak ditemukan")
    return vendor

@router.post("/po/create")
def create_purchase_order(payload: CreatePORequest, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == payload.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor tidak ditemukan")

    # Match product for the vendor's company
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product or product.company_id != vendor.company_id:
        cat_lower = (vendor.category or "").lower()
        if "casing" in cat_lower or "aluminium" in cat_lower:
            product = db.query(Product).filter(Product.company_id == vendor.company_id, Product.name.ilike("%casing%")).first()
        elif "microcontroller" in cat_lower or "sensor" in cat_lower or "semikonduktor" in cat_lower:
            product = db.query(Product).filter(Product.company_id == vendor.company_id, Product.name.ilike("%chipset%")).first()
        elif "baterai" in cat_lower or "elektrik" in cat_lower:
            product = db.query(Product).filter(Product.company_id == vendor.company_id, Product.name.ilike("%baterai%")).first()
        elif "layar" in cat_lower or "amoled" in cat_lower or "display" in cat_lower:
            product = db.query(Product).filter(Product.company_id == vendor.company_id, Product.name.ilike("%layar%")).first()
        
        if not product:
            product = db.query(Product).filter(Product.company_id == vendor.company_id, Product.product_type == "raw_material").first()

    if not product:
        raise HTTPException(status_code=404, detail="Produk bahan baku tidak ditemukan untuk perusahaan ini")

    unit_cost = product.cost_price * vendor.price_multiplier
    total = unit_cost * payload.quantity

    from backend.app.models.models import JournalEntry, JournalItem, CompanyStoryEvent, SimulationState
    import json

    state = db.query(SimulationState).filter(SimulationState.company_id == vendor.company_id).first()
    round_num = state.current_round if state else 1

    is_cash = payload.payment_method in ["cash", "tunai"]

    if is_cash and state and state.cash < total:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo kas tidak mencukupi untuk pembelian tunai! Tersedia: Rp {state.cash:,.0f}, Butuh: Rp {total:,.0f}. Gunakan opsi pembayaran Tempo/Kredit."
        )

    # Generate PO Code
    count = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == vendor.company_id).count() + 1
    code = f"PO/{vendor.name[:3].upper()}/2026/{count:04d}"

    po = PurchaseOrder(
        company_id=vendor.company_id,
        vendor_id=vendor.id,
        code=code,
        total_amount=total,
        status="sent"
    )
    db.add(po)
    db.commit()
    db.refresh(po)

    po_item = PurchaseOrderItem(
        purchase_order_id=po.id,
        product_id=product.id,
        quantity=payload.quantity,
        unit_price=unit_cost,
        subtotal=total
    )
    db.add(po_item)

    # If vendor is very defect-prone (e.g. defect_rate > 5%), simulate received defect rate
    delivered_qty = payload.quantity
    defect_discarded = 0
    if vendor.defect_rate > 5.0:
        delivered_qty = int(payload.quantity * (1.0 - (vendor.defect_rate / 100.0)))
        defect_discarded = payload.quantity - delivered_qty

    product.current_stock += delivered_qty
    
    # Record Journal Entry in Accounting
    ap_acc = db.query(Account).filter(Account.company_id == vendor.company_id, Account.code == "2010").first()
    cash_acc = db.query(Account).filter(Account.company_id == vendor.company_id, Account.code == "1010").first()
    raw_inv_acc = db.query(Account).filter(Account.company_id == vendor.company_id, Account.code == "1030").first()

    if raw_inv_acc:
        raw_inv_acc.balance += total

    je_count = db.query(JournalEntry).filter(JournalEntry.company_id == vendor.company_id).count() + 1
    je = JournalEntry(
        company_id=vendor.company_id,
        entry_number=f"JE/PO/{je_count:04d}",
        reference=code,
        memo=f"Pembelian Bahan Baku {product.name} x {payload.quantity} unit ({vendor.name}) — {'Tunai' if is_cash else 'Tempo'}"
    )
    db.add(je)
    db.commit()
    db.refresh(je)

    if raw_inv_acc:
        db.add(JournalItem(journal_entry_id=je.id, account_id=raw_inv_acc.id, debit=total, credit=0.0))

    if is_cash:
        if cash_acc:
            cash_acc.balance = max(0.0, cash_acc.balance - total)
            db.add(JournalItem(journal_entry_id=je.id, account_id=cash_acc.id, debit=0.0, credit=total))
        if state:
            state.cash = max(0.0, state.cash - total)
    else:
        if ap_acc:
            ap_acc.balance += total
            db.add(JournalItem(journal_entry_id=je.id, account_id=ap_acc.id, debit=0.0, credit=total))

    # Update Department Budget Realization (Budget vs Actual)
    from backend.app.models.models import DepartmentBudget
    purchasing_budget = db.query(DepartmentBudget).filter(
        DepartmentBudget.company_id == vendor.company_id,
        (DepartmentBudget.department.ilike("%pengadaan%") | DepartmentBudget.department.ilike("%purchasing%"))
    ).first()
    if purchasing_budget:
        purchasing_budget.spent_amount += total

    ripples = [
        {
            "dept": "Pengadaan & SCM",
            "icon": "🛒",
            "impact": f"Purchase Order {code} terbit: {payload.quantity} unit {product.name} ke {vendor.name} (Total Rp {total:,.0f}, Metode: {'Tunai Langsung' if is_cash else f'Tempo {vendor.credit_terms_days} hari'})."
        },
        {
            "dept": "Gudang & QC",
            "icon": "📦",
            "impact": f"Bahan baku tiba: +{delivered_qty} unit masuk stok{' (Reject disortir: ' + str(defect_discarded) + ' unit)' if defect_discarded > 0 else ''}. Stok '{product.name}': {product.current_stock} unit."
        },
        {
            "dept": "Keuangan & Akuntansi",
            "icon": "💰",
            "impact": f"Jurnal {je.entry_number}: Persediaan Bahan Baku +Rp {total:,.0f}, {'Kas terpotong langsung' if is_cash else 'Utang Usaha (AP) bertambah'} Rp {total:,.0f}."
        }
    ]

    doc_data = {
        "doc_type": "PURCHASE_ORDER",
        "doc_code": code,
        "vendor": vendor.name,
        "product": product.name,
        "quantity_ordered": payload.quantity,
        "quantity_delivered": delivered_qty,
        "defect_discarded": defect_discarded,
        "total_cost": total,
        "payment_method": "Tunai / Cash" if is_cash else f"Tempo {vendor.credit_terms_days} Hari",
        "credit_terms_days": 0 if is_cash else vendor.credit_terms_days,
        "journal_entry": je.entry_number,
        "created_at": "Baru Saja"
    }

    story_ev = CompanyStoryEvent(
        company_id=vendor.company_id,
        round_number=round_num,
        period_name=f"Bulan {round_num}",
        domain="purchasing",
        event_type="operational_transaction",
        title=f"Penerbitan Purchase Order #{code} ({vendor.name})",
        description=f"Departemen Pengadaan (SCM) menerbitkan PO #{code} senilai Rp {total:,.0f} untuk pasokan {product.name}. Metode pembayaran: {'Tunai Langsung (Kas berkurang)' if is_cash else f'Tempo {vendor.credit_terms_days} Hari (Utang Usaha AP)'}. Diterima di gudang {delivered_qty} unit.",
        decision_taken=f"PO {vendor.name} ({payload.quantity} unit - {'Tunai' if is_cash else 'Tempo'})",
        ripple_summary=json.dumps(ripples),
        document_data=json.dumps(doc_data)
    )
    db.add(story_ev)

    db.commit()
    return {
        "status": "success",
        "code": code,
        "po_code": code,
        "vendor_name": vendor.name,
        "product_name": product.name,
        "quantity_ordered": payload.quantity,
        "quantity_delivered": delivered_qty,
        "delivered_qty": delivered_qty,
        "defect_discarded": defect_discarded,
        "total_amount": total,
        "total_cost": total,
        "payment_method": "cash" if is_cash else "tempo",
        "new_stock": product.current_stock,
        "journal_entry": je.entry_number,
        "cash_after": state.cash if state else 0.0
    }

@router.post("/ap/pay")
def pay_accounts_payable(payload: PayAPRequest, db: Session = Depends(get_db)):
    state = db.query(SimulationState).filter(SimulationState.company_id == payload.company_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="Data perusahaan tidak ditemukan")

    ap_acc = db.query(Account).filter(Account.company_id == payload.company_id, Account.code == "2010").first()
    cash_acc = db.query(Account).filter(Account.company_id == payload.company_id, Account.code == "1010").first()

    current_ap = ap_acc.balance if ap_acc else 0.0
    if current_ap <= 0:
        raise HTTPException(status_code=400, detail="Tidak ada saldo Utang Usaha (AP) yang perlu dilunasi saat ini.")

    pay_amount = min(payload.amount, current_ap)
    if state.cash < pay_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Saldo kas tidak mencukupi untuk pelunasan utang! Tersedia: Rp {state.cash:,.0f}, Butuh: Rp {pay_amount:,.0f}."
        )

    if ap_acc:
        ap_acc.balance = max(0.0, ap_acc.balance - pay_amount)
    if cash_acc:
        cash_acc.balance = max(0.0, cash_acc.balance - pay_amount)
    state.cash = max(0.0, state.cash - pay_amount)

    from backend.app.models.models import JournalEntry, JournalItem, CompanyStoryEvent
    import json

    # Journal Entry
    je_count = db.query(JournalEntry).filter(JournalEntry.company_id == payload.company_id).count() + 1
    je = JournalEntry(
        company_id=payload.company_id,
        entry_number=f"JE/PAY-AP/{je_count:04d}",
        memo=f"Pelunasan Utang Usaha (AP) ke Pemasok / Rekanan Vendor"
    )
    db.add(je)
    db.commit()
    db.refresh(je)

    if ap_acc:
        db.add(JournalItem(journal_entry_id=je.id, account_id=ap_acc.id, debit=pay_amount, credit=0.0))
    if cash_acc:
        db.add(JournalItem(journal_entry_id=je.id, account_id=cash_acc.id, debit=0.0, credit=pay_amount))

    # Audit Trail Story Event
    round_num = state.current_round if state else 1
    story_ev = CompanyStoryEvent(
        company_id=payload.company_id,
        round_number=round_num,
        period_name=f"Bulan {round_num}",
        domain="accounting",
        event_type="operational_transaction",
        title=f"Pelunasan Utang Usaha (AP) — Rp {pay_amount:,.0f}",
        description=f"Perusahaan melakukan pengeluaran kas pelunasan utang dagang (Disbursement) sebesar Rp {pay_amount:,.0f}. Saldo Utang Usaha (AP) berkurang menjadi Rp {ap_acc.balance if ap_acc else 0:,.0f}.",
        decision_taken="Pelunasan Utang Usaha",
        ripple_summary=json.dumps([
            {"dept": "Keuangan & Kas", "icon": "💰", "impact": f"Kas terpotong Rp {pay_amount:,.0f}. Sisa saldo kas: Rp {state.cash:,.0f}."},
            {"dept": "Akuntansi & Neraca", "icon": "📋", "impact": f"Kewajiban Utang Usaha (AP) berkurang Rp {pay_amount:,.0f}."}
        ]),
        document_data=json.dumps({
            "doc_type": "PAYMENT_RECEIPT",
            "title": "BUKTI PENGELUARAN KAS & PELUNASAN UTANG DAGANG",
            "recipient": "Rekanan Vendor Pemasok",
            "summary": f"Bukti Pelunasan Kewajiban Dagang:\n\n• Jumlah Dilunasi: Rp {pay_amount:,.0f}\n• Sisa Utang Usaha: Rp {ap_acc.balance if ap_acc else 0:,.0f}\n• Nomor Jurnal: {je.entry_number}\n\nKewajiban dagang telah diselesaikan dan neraca kas diperbarui.",
            "created_at": "Baru Saja"
        })
    )
    db.add(story_ev)
    db.commit()

    return {
        "status": "success",
        "message": f"Pelunasan utang usaha sebesar Rp {pay_amount:,.0f} berhasil! Saldo kas terpotong.",
        "paid_amount": pay_amount,
        "remaining_ap": ap_acc.balance if ap_acc else 0.0,
        "remaining_cash": state.cash
    }


```


---
# FILE: backend/app/routers/manufacturing.py
---
```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import WorkCenter, WorkOrder, BillOfMaterials, BOMItem, Product, SimulationState
from backend.app.schemas.schemas import WorkCenterOut, WorkOrderOut, CreateWorkOrder

router = APIRouter(prefix="/manufacturing", tags=["manufacturing"])

class RepairMachineRequest(BaseModel):
    work_center_id: int

@router.get("/workcenters/{company_id}", response_model=List[WorkCenterOut])
def list_workcenters(company_id: int, db: Session = Depends(get_db)):
    return db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all()

@router.get("/workorders/{company_id}", response_model=List[WorkOrderOut])
def list_workorders(company_id: int, db: Session = Depends(get_db)):
    return db.query(WorkOrder).filter(WorkOrder.company_id == company_id).all()

@router.post("/workorders/create")
def create_work_order(payload: CreateWorkOrder, db: Session = Depends(get_db)):
    bom = db.query(BillOfMaterials).filter(BillOfMaterials.id == payload.bom_id).first()
    wc = db.query(WorkCenter).filter(WorkCenter.id == payload.work_center_id).first()
    
    if not bom and wc:
        bom = db.query(BillOfMaterials).filter(BillOfMaterials.company_id == wc.company_id).first()
    elif not wc and bom:
        wc = db.query(WorkCenter).filter(WorkCenter.company_id == bom.company_id).first()
    elif not bom and not wc:
        bom = db.query(BillOfMaterials).first()
        if bom:
            wc = db.query(WorkCenter).filter(WorkCenter.company_id == bom.company_id).first()

    if not bom or not wc:
        raise HTTPException(status_code=404, detail="BOM atau Work Center tidak ditemukan")

    if wc.status == "breakdown":
        raise HTTPException(status_code=400, detail=f"Mesin di '{wc.name}' sedang rusak! Lakukan perbaikan terlebih dahulu.")

    # Check raw materials stock
    for item in bom.items:
        needed = item.quantity_required * payload.qty_to_produce
        raw = db.query(Product).filter(Product.id == item.raw_product_id).first()
        if not raw or raw.current_stock < needed:
            raise HTTPException(
                status_code=400,
                detail=f"Bahan baku '{raw.name if raw else 'Unknown'}' tidak cukup. Butuh {needed}, tersedia {raw.current_stock if raw else 0}."
            )

    # Consume raw materials & update Raw Inventory balance in Accounting
    from backend.app.models.models import Account, Employee, JournalEntry, JournalItem, CompanyStoryEvent
    import json

    state = db.query(SimulationState).filter(SimulationState.company_id == bom.company_id).first()
    round_num = state.current_round if state else 1

    total_raw_cost = 0.0
    consumed_raw_details = []
    for item in bom.items:
        needed = item.quantity_required * payload.qty_to_produce
        raw = db.query(Product).filter(Product.id == item.raw_product_id).first()
        if raw:
            raw.current_stock = max(0.0, raw.current_stock - needed)
            cost_chunk = needed * raw.cost_price
            total_raw_cost += cost_chunk
            consumed_raw_details.append(f"{raw.name}: -{needed:g} {raw.uom}")

    # Calculate defect and produced
    scrap = 0
    if wc.failure_rate > 3.0:
        scrap = int(payload.qty_to_produce * (wc.failure_rate / 100.0))
    produced = payload.qty_to_produce - scrap

    count = db.query(WorkOrder).filter(WorkOrder.company_id == bom.company_id).count() + 1
    code = f"WO/2026/{count:04d}"

    wo = WorkOrder(
        company_id=bom.company_id,
        bom_id=bom.id,
        work_center_id=wc.id,
        code=code,
        qty_to_produce=payload.qty_to_produce,
        qty_produced=produced,
        scrap_qty=scrap,
        status="completed"
    )
    db.add(wo)

    # Add finished good stock
    finished = db.query(Product).filter(Product.id == bom.finished_product_id).first()
    fg_value_added = 0.0
    if finished:
        finished.current_stock += produced
        fg_value_added = produced * finished.cost_price

    # Accounting update: Raw Inventory -> Finished Goods Inventory
    raw_acc = db.query(Account).filter(Account.company_id == bom.company_id, Account.code == "1030").first()
    fg_acc = db.query(Account).filter(Account.company_id == bom.company_id, Account.code == "1040").first()
    if raw_acc:
        raw_acc.balance = max(0.0, raw_acc.balance - total_raw_cost)
    if fg_acc:
        fg_acc.balance += fg_value_added

    # Update Department Budget Realization (Budget vs Actual)
    from backend.app.models.models import DepartmentBudget
    mfg_budget = db.query(DepartmentBudget).filter(
        DepartmentBudget.company_id == bom.company_id,
        (DepartmentBudget.department.ilike("%produksi%") | DepartmentBudget.department.ilike("%manufaktur%"))
    ).first()
    if mfg_budget:
        mfg_budget.spent_amount += total_raw_cost

    # Machine wear and operator fatigue
    wc.failure_rate = min(30.0, wc.failure_rate + (payload.qty_to_produce * 0.03))
    if state:
        state.machine_health = max(10.0, state.machine_health - (payload.qty_to_produce * 0.05))

    workers = db.query(Employee).filter(Employee.company_id == bom.company_id, Employee.department == "Produksi").all()
    for worker in workers:
        worker.fatigue_score = min(100.0, worker.fatigue_score + (payload.qty_to_produce * 0.12))
        worker.morale_score = max(10.0, worker.morale_score - (payload.qty_to_produce * 0.04))

    # Audit Trail Story Event
    ripples = [
        {
            "dept": "Manufaktur & MRP",
            "icon": "🏭",
            "impact": f"Work Order {code} selesai: {produced} unit {finished.name if finished else 'Barang Jadi'} berhasil dirakit (Scrap cacat: {scrap} unit)."
        },
        {
            "dept": "Gudang & Bahan Baku",
            "icon": "📦",
            "impact": f"Bahan baku terkonsumsi: {', '.join(consumed_raw_details)}. Stok barang jadi bertambah +{produced} unit."
        },
        {
            "dept": "Keuangan & Akuntansi",
            "icon": "💰",
            "impact": f"Perpindahan Persediaan: Bahan Baku -Rp {total_raw_cost:,.0f} ➔ Barang Jadi +Rp {fg_value_added:,.0f}."
        },
        {
            "dept": "SDM & Operator Pabrik",
            "icon": "👔",
            "impact": f"Beban mesin perakitan {wc.name} bertambah. Kelelahan operator lini SMT +{(payload.qty_to_produce * 0.12):.1f}%."
        }
    ]

    doc_data = {
        "doc_type": "WORK_ORDER",
        "doc_code": code,
        "work_center": wc.name,
        "product_produced": finished.name if finished else "Smartwatch",
        "qty_target": payload.qty_to_produce,
        "qty_produced": produced,
        "scrap_qty": scrap,
        "raw_cost": total_raw_cost,
        "created_at": "Baru Saja"
    }

    story_ev = CompanyStoryEvent(
        company_id=bom.company_id,
        round_number=round_num,
        period_name=f"Bulan {round_num}",
        domain="manufacturing",
        event_type="operational_transaction",
        title=f"Penyelesaian Work Order #{code} ({finished.name if finished else 'Barang Jadi'})",
        description=f"Lini produksi {wc.name} berhasil menyelesaikan Work Order #{code}. Sebanyak {produced} unit barang jadi siap jual telah masuk ke gudang logistik (Reject scrap: {scrap} unit).",
        decision_taken=f"Produksi WO {code} ({payload.qty_to_produce} unit)",
        ripple_summary=json.dumps(ripples),
        document_data=json.dumps(doc_data)
    )
    db.add(story_ev)

    db.commit()
    return {
        "status": "success",
        "wo_code": code,
        "product_name": finished.name if finished else "Smartwatch",
        "qty_produced": produced,
        "scrap_discarded": scrap,
        "new_finished_stock": finished.current_stock if finished else produced
    }

@router.post("/workcenters/repair")
def repair_workcenter(payload: RepairMachineRequest, db: Session = Depends(get_db)):
    wc = db.query(WorkCenter).filter(WorkCenter.id == payload.work_center_id).first()
    if not wc:
        raise HTTPException(status_code=404, detail="Work Center tidak ditemukan")

    from backend.app.models.models import Account, CompanyStoryEvent
    import json

    repair_cost = 7500000.0
    wc.status = "operational"
    wc.failure_rate = max(1.5, wc.failure_rate - 4.0)

    state = db.query(SimulationState).filter(SimulationState.company_id == wc.company_id).first()
    round_num = state.current_round if state else 1
    if state:
        state.cash = max(0.0, state.cash - repair_cost)
        state.machine_health = min(98.0, state.machine_health + 30.0)

    cash_acc = db.query(Account).filter(Account.company_id == wc.company_id, Account.code == "1010").first()
    if cash_acc:
        cash_acc.balance = max(0.0, cash_acc.balance - repair_cost)

    from backend.app.models.models import DepartmentBudget
    mfg_budget = db.query(DepartmentBudget).filter(
        DepartmentBudget.company_id == wc.company_id,
        (DepartmentBudget.department.ilike("%produksi%") | DepartmentBudget.department.ilike("%manufaktur%"))
    ).first()
    if mfg_budget:
        mfg_budget.spent_amount += repair_cost

    ripples = [
        {"dept": "Pabrik & Manufaktur", "icon": "🏭", "impact": f"Mesin '{wc.name}' selesai diservis. Tingkat kegagalan turun ke {wc.failure_rate:.1f}%."},
        {"dept": "Keuangan & Kas", "icon": "💰", "impact": f"Kas terpotong Rp {repair_cost:,.0f} untuk pemeliharaan preventif mesin."}
    ]

    story_ev = CompanyStoryEvent(
        company_id=wc.company_id,
        round_number=round_num,
        period_name=f"Bulan {round_num}",
        domain="manufacturing",
        event_type="operational_transaction",
        title=f"Pemeliharaan & Rekalibrasi Mesin — {wc.name}",
        description=f"Tim teknisi pabrik telah menyelesaikan overhaul dan rekalibrasi mesin {wc.name}. Keandalan operasional pulih dan risiko bottleneck teratasi.",
        decision_taken=f"Servis Mesin {wc.name}",
        ripple_summary=json.dumps(ripples),
        document_data=json.dumps({
            "doc_type": "MAINTENANCE_LOG",
            "work_center": wc.name,
            "cost": repair_cost,
            "status": "Operational",
            "date": "Baru Saja"
        })
    )
    db.add(story_ev)

    db.commit()
    return {
        "status": "success",
        "message": f"Mesin '{wc.name}' berhasil diperbaiki dan beroperasi normal!",
        "repair_cost": repair_cost,
        "machine_status": wc.status
    }

```


---
# FILE: backend/app/routers/accounting.py
---
```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import Account, DepartmentBudget, JournalEntry, SimulationState
from backend.app.schemas.schemas import AccountOut, DepartmentBudgetOut

router = APIRouter(prefix="/accounting", tags=["accounting"])

class CreateBudgetRequest(BaseModel):
    company_id: int
    department: str
    allocated_amount: float
    period_name: str = "Q1"

class UpdateBudgetRequest(BaseModel):
    allocated_amount: Optional[float] = None
    spent_amount: Optional[float] = None

@router.get("/accounts/{company_id}", response_model=List[AccountOut])
def list_accounts(company_id: int, db: Session = Depends(get_db)):
    return db.query(Account).filter(Account.company_id == company_id).all()

@router.get("/budgets/{company_id}", response_model=List[DepartmentBudgetOut])
def list_budgets(company_id: int, db: Session = Depends(get_db)):
    return db.query(DepartmentBudget).filter(DepartmentBudget.company_id == company_id).all()

@router.post("/budgets", response_model=DepartmentBudgetOut)
def create_budget(payload: CreateBudgetRequest, db: Session = Depends(get_db)):
    budget = DepartmentBudget(
        company_id=payload.company_id,
        department=payload.department,
        allocated_amount=payload.allocated_amount,
        spent_amount=0.0,
        period_name=payload.period_name
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

@router.put("/budgets/{budget_id}", response_model=DepartmentBudgetOut)
def update_budget(budget_id: int, payload: UpdateBudgetRequest, db: Session = Depends(get_db)):
    b = db.query(DepartmentBudget).filter(DepartmentBudget.id == budget_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Budget tidak ditemukan")
    if payload.allocated_amount is not None: b.allocated_amount = payload.allocated_amount
    if payload.spent_amount is not None: b.spent_amount = payload.spent_amount
    db.commit()
    db.refresh(b)
    return b

@router.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    b = db.query(DepartmentBudget).filter(DepartmentBudget.id == budget_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Budget tidak ditemukan")
    db.delete(b)
    db.commit()
    return {"status": "success", "message": f"Budget departemen '{b.department}' berhasil dihapus"}

@router.get("/financial-report/{company_id}")
def get_financial_report(company_id: int, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.company_id == company_id).all()
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()

    total_assets = sum(a.balance for a in accounts if a.account_type == "asset")
    total_liabilities = sum(a.balance for a in accounts if a.account_type == "liability")
    total_equity = sum(a.balance for a in accounts if a.account_type == "equity")

    total_revenue = state.revenue if state else sum(a.balance for a in accounts if a.account_type == "revenue")
    total_cogs = sum(a.balance for a in accounts if a.code == "5010")
    total_opex = sum(a.balance for a in accounts if a.account_type == "expense" and a.code != "5010")
    net_income = total_revenue - total_cogs - total_opex

    return {
        "balance_sheet": {
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "cash_and_bank": state.cash if state else 500000000.0,
            "is_balanced": abs(total_assets - (total_liabilities + total_equity)) < 100000.0
        },
        "profit_and_loss": {
            "gross_revenue": total_revenue,
            "cogs": total_cogs,
            "gross_profit": total_revenue - total_cogs,
            "operating_expenses": total_opex,
            "net_income": net_income
        }
    }

from backend.app.services.behavior_engine import trigger_random_black_swan
from backend.app.models.models import Company, CompanyStoryEvent
import json

@router.post("/trigger-black-swan/{company_id}")
def trigger_black_swan(company_id: int, db: Session = Depends(get_db)):
    shock = trigger_random_black_swan()
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    amount = shock["amount"]

    if shock["impact_type"] == "bad_debt":
        ar_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1020").first()
        if ar_acc:
            ar_acc.balance = max(0.0, ar_acc.balance - amount)
        if state:
            state.expenses += amount
            state.net_profit -= amount
    else:
        # Cash deduction
        cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1010").first()
        if cash_acc:
            cash_acc.balance = max(0.0, cash_acc.balance - amount)
        if state:
            state.cash = max(0.0, state.cash - amount)
            state.expenses += amount
            state.net_profit -= amount

    # Log to Audit Trail
    round_num = state.current_round if state else 1
    ripples = [
        {"dept": "Keuangan & Akuntansi", "icon": "💥", "impact": f"Peristiwa Luar Biasa (Black Swan): {shock['title']}. Kerugian finansial: Rp {amount:,.0f}."},
        {"dept": "Manajemen Risiko", "icon": "⚠️", "impact": f"Akun terdampak: {', '.join(shock['affected_accounts'])}. Evaluasi likuiditas darurat diperlukan."}
    ]

    story_ev = CompanyStoryEvent(
        company_id=company_id,
        round_number=round_num,
        period_name=f"Bulan {round_num}",
        domain="accounting",
        event_type="black_swan",
        title=f"⚡ BLACK SWAN: {shock['title']}",
        description=f"Konsol Dosen memicu peristiwa luar biasa (disrupsi makro / shock): {shock['description']}. Kerugian tak terduga sebesar Rp {amount:,.0f} telah didebet dari neraca perusahaan.",
        decision_taken="Disrupsi Makro oleh Dosen",
        ripple_summary=json.dumps(ripples),
        document_data=json.dumps({
            "doc_type": "BLACK_SWAN_NOTICE",
            "title": f"SURAT PEMBERITAHUAN INSIDEN LUAR BIASA: {shock['title']}",
            "recipient": "Seluruh Direksi & Tim Mahasiswa",
            "summary": f"Pemberitahuan Resmi Disrupsi Eksternal:\n\n• Kode Insiden: {shock['code']}\n• Judul Disrupsi: {shock['title']}\n• Dampak Finansial Langsung: Rp {amount:,.0f}\n• Rincian Peristiwa: {shock['description']}\n\nSeluruh tim wajib segera melakukan mitigasi risiko dan penyesuaian arus kas operasional.",
            "created_at": "Baru Saja"
        })
    )
    db.add(story_ev)
    db.commit()

    return {
        "status": "warning",
        "shock_code": shock["code"],
        "shock_title": shock["title"],
        "description": shock["description"],
        "financial_loss": amount,
        "affected_accounts": shock["affected_accounts"],
        "new_cash": state.cash if state else 500000000.0
    }

@router.post("/trigger-black-swan-session/{session_id}")
def trigger_black_swan_session(session_id: int, db: Session = Depends(get_db)):
    companies = db.query(Company).filter(Company.session_id == session_id).all()
    if not companies:
        raise HTTPException(status_code=404, detail="Tidak ada kelompok/perusahaan aktif pada sesi kelas ini")

    shock = trigger_random_black_swan()
    amount = shock["amount"]
    affected_groups = []

    for comp in companies:
        state = db.query(SimulationState).filter(SimulationState.company_id == comp.id).first()
        if shock["impact_type"] == "bad_debt":
            ar_acc = db.query(Account).filter(Account.company_id == comp.id, Account.code == "1020").first()
            if ar_acc:
                ar_acc.balance = max(0.0, ar_acc.balance - amount)
            if state:
                state.expenses += amount
                state.net_profit -= amount
        else:
            cash_acc = db.query(Account).filter(Account.company_id == comp.id, Account.code == "1010").first()
            if cash_acc:
                cash_acc.balance = max(0.0, cash_acc.balance - amount)
            if state:
                state.cash = max(0.0, state.cash - amount)
                state.expenses += amount
                state.net_profit -= amount

        round_num = state.current_round if state else 1
        ripples = [
            {"dept": "Keuangan & Akuntansi", "icon": "💥", "impact": f"Disrupsi Makro Kelas: {shock['title']}. Kerugian: Rp {amount:,.0f}."},
            {"dept": "Manajemen Risiko", "icon": "⚠️", "impact": f"Akun terdampak: {', '.join(shock['affected_accounts'])}."}
        ]

        story_ev = CompanyStoryEvent(
            company_id=comp.id,
            round_number=round_num,
            period_name=f"Bulan {round_num}",
            domain="accounting",
            event_type="black_swan",
            title=f"⚡ BLACK SWAN KELAS: {shock['title']}",
            description=f"Dosen Pengampu memicu disrupsi makro serentak ke seluruh kelas: {shock['description']}. Kerugian tak terduga sebesar Rp {amount:,.0f} dibebankan ke laporan keuangan.",
            decision_taken="Disrupsi Makro Kelas Serentak",
            ripple_summary=json.dumps(ripples),
            document_data=json.dumps({
                "doc_type": "BLACK_SWAN_NOTICE",
                "title": f"SURAT PEMBERITAHUAN DISRUPSI KELAS: {shock['title']}",
                "recipient": f"Manajemen {comp.name} ({comp.group_label})",
                "summary": f"Pemberitahuan Resmi Disrupsi Eksternal Kelas:\n\n• Kode Insiden: {shock['code']}\n• Judul Disrupsi: {shock['title']}\n• Kerugian Finansial: Rp {amount:,.0f}\n• Penjelasan: {shock['description']}\n\nInstruksi Dosen: Seluruh kelompok wajib merumuskan strategi penyehatan kas.",
                "created_at": "Baru Saja"
            })
        )
        db.add(story_ev)
        affected_groups.append(comp.name)

    db.commit()
    return {
        "status": "warning",
        "broadcast": True,
        "affected_companies_count": len(companies),
        "affected_groups": affected_groups,
        "shock_code": shock["code"],
        "shock_title": shock["title"],
        "description": shock["description"],
        "financial_loss": amount,
        "affected_accounts": shock["affected_accounts"]
    }


```


---
# FILE: backend/app/routers/hr.py
---
```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import Employee, SimulationState
from backend.app.schemas.schemas import EmployeeOut, ResolveStrikeRequest

router = APIRouter(prefix="/hr", tags=["hr"])

class CreateEmployeeRequest(BaseModel):
    company_id: int
    name: str
    department: str = "Produksi"
    role: str = "Operator Mesin"
    monthly_salary: float = 5000000.0

class UpdateEmployeeRequest(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    monthly_salary: Optional[float] = None
    status: Optional[str] = None

@router.get("/employees/{company_id}", response_model=List[EmployeeOut])
def list_employees(company_id: int, db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.company_id == company_id).all()

@router.post("/employees", response_model=EmployeeOut)
def create_employee(payload: CreateEmployeeRequest, db: Session = Depends(get_db)):
    emp = Employee(
        company_id=payload.company_id,
        name=payload.name,
        department=payload.department,
        role=payload.role,
        monthly_salary=payload.monthly_salary,
        morale_score=90.0,
        fatigue_score=20.0,
        status="active"
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp

@router.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, payload: UpdateEmployeeRequest, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")
    if payload.name is not None: emp.name = payload.name
    if payload.department is not None: emp.department = payload.department
    if payload.role is not None: emp.role = payload.role
    if payload.monthly_salary is not None: emp.monthly_salary = payload.monthly_salary
    if payload.status is not None: emp.status = payload.status
    db.commit()
    db.refresh(emp)
    return emp

@router.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan")
    db.delete(emp)
    db.commit()
    return {"status": "success", "message": f"Pegawai '{emp.name}' berhasil dihapus"}

from backend.app.services.behavior_engine import get_union_leader_for_company

@router.get("/union-profile/{company_id}")
def get_union_profile(company_id: int):
    leader = get_union_leader_for_company(company_id)
    return {
        "rep_name": leader.get("rep_name", "Bambang Sukirman"),
        "label": leader.get("label"),
        "speech": leader.get("speech"),
        "type": leader.get("type")
    }

@router.post("/resolve-strike/{company_id}")
def resolve_strike(company_id: int, payload: ResolveStrikeRequest, db: Session = Depends(get_db)):
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    employees = db.query(Employee).filter(Employee.company_id == company_id).all()
    union_leader = get_union_leader_for_company(company_id)

    # Check if student's offer meets the union leader's demands
    if payload.wage_increase_percentage < union_leader["min_wage_raise_accepted"] or payload.bonus_per_worker < union_leader["min_bonus_accepted"]:
        return {
            "status": "rejected",
            "accepted": False,
            "leader_type": union_leader["type"],
            "leader_label": union_leader["label"],
            "speech": union_leader["rejection_speech"],
            "message": f"Negosiasi Ditolak oleh {union_leader['label']}! Tawaran dinilai belum mencerminkan itikad baik pemenuhan hak buruh. {union_leader['rejection_speech']}"
        }

    # If accepted, apply wage increase and end strike
    for emp in employees:
        if payload.wage_increase_percentage > 0:
            emp.monthly_salary *= (1.0 + (payload.wage_increase_percentage / 100.0))
        emp.status = "active"
        emp.morale_score = min(100.0, emp.morale_score + 30.0)
        emp.fatigue_score = max(10.0, emp.fatigue_score - 20.0)

    bonus_total = payload.bonus_per_worker * len(employees)
    if state:
        state.is_strike_active = False
        state.strike_reason = None
        state.cash -= bonus_total
        state.worker_morale = min(98.0, state.worker_morale + 35.0)

    db.commit()
    return {
        "status": "success",
        "accepted": True,
        "leader_type": union_leader["type"],
        "leader_label": union_leader["label"],
        "speech": union_leader["acceptance_speech"],
        "message": f"Kesepakatan Bipartit Diterima! {union_leader['acceptance_speech']}",
        "bonus_total_paid": bonus_total,
        "new_worker_morale": state.worker_morale if state else 90.0
    }

```


---
# FILE: backend/app/routers/settings.py
---
```python
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import datetime

from backend.app.database import get_db
from backend.app.models.models import SystemSetting, User

router = APIRouter(prefix="/settings", tags=["settings"])

DEFAULT_BRANDING: Dict[str, str] = {
    "app_title": "VLab-ERP Enterprise Edition - FEB",
    "department_name": "Fakultas Ekonomi dan Bisnis (FEB) • Manajemen & Akuntansi Bisnis Digital",
    "lecturer_name": "Tim Dosen Pengampu FEB (Pemasaran, SDM, Keuangan)",
    "lecturer_marketing_name": "Dr. Maya Indah, S.E., M.M.",
    "lecturer_hr_name": "Drs. Bambang Prakoso, M.Psi.",
    "lecturer_finance_name": "Dr. Ir. Budi Santoso, Ak.",
    "lecturer_role_label": "Tim Pengampu FEB",
    "supervision_badge": "Supervisi Simulasi Bisnis FEB",
    "footer_text": "VLab-ERP Enterprise Edition • Fakultas Ekonomi dan Bisnis (FEB) • Port 8280 (Frontend) & Port 8281 (Backend)",
    "academic_term": "Semester Ganjil 2026/2027",
    "portal_subtitle": "Laboratorium Simulasi ERP, Manajemen Bisnis & Akuntansi Terintegrasi FEB"
}

class BrandingUpdateRequest(BaseModel):
    app_title: Optional[str] = None
    department_name: Optional[str] = None
    lecturer_name: Optional[str] = None
    lecturer_marketing_name: Optional[str] = None
    lecturer_hr_name: Optional[str] = None
    lecturer_finance_name: Optional[str] = None
    lecturer_role_label: Optional[str] = None
    supervision_badge: Optional[str] = None
    footer_text: Optional[str] = None
    academic_term: Optional[str] = None
    portal_subtitle: Optional[str] = None

@router.get("/branding")
def get_branding(db: Session = Depends(get_db)):
    result = dict(DEFAULT_BRANDING)
    settings = db.query(SystemSetting).all()
    for s in settings:
        if s.key in result:
            result[s.key] = s.value
    return result

@router.put("/branding")
def update_branding(payload: BrandingUpdateRequest, db: Session = Depends(get_db)):
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        if v is not None:
            setting = db.query(SystemSetting).filter(SystemSetting.key == k).first()
            if not setting:
                setting = SystemSetting(key=k, value=str(v))
                db.add(setting)
            else:
                setting.value = str(v)
                setting.updated_at = datetime.datetime.utcnow()

    # Update User table for corresponding dosen accounts
    if payload.lecturer_marketing_name:
        u = db.query(User).filter(User.username == "dosen.marketing").first()
        if u:
            u.full_name = payload.lecturer_marketing_name
    if payload.lecturer_hr_name:
        u = db.query(User).filter(User.username == "dosen.sdm").first()
        if u:
            u.full_name = payload.lecturer_hr_name
    if payload.lecturer_finance_name:
        u = db.query(User).filter(User.username == "dosen.keuangan").first()
        if u:
            u.full_name = payload.lecturer_finance_name
    if payload.lecturer_name:
        u = db.query(User).filter(User.username == "dosen").first()
        if u:
            u.full_name = payload.lecturer_name

    db.commit()

    # Return refreshed branding
    return get_branding(db)

@router.post("/branding/reset")
def reset_branding(db: Session = Depends(get_db)):
    for k, v in DEFAULT_BRANDING.items():
        setting = db.query(SystemSetting).filter(SystemSetting.key == k).first()
        if setting:
            setting.value = v
            setting.updated_at = datetime.datetime.utcnow()
        else:
            db.add(SystemSetting(key=k, value=v))
    
    # Reset lecturer names on users
    user_map = {
        "dosen.marketing": DEFAULT_BRANDING["lecturer_marketing_name"],
        "dosen.sdm": DEFAULT_BRANDING["lecturer_hr_name"],
        "dosen.keuangan": DEFAULT_BRANDING["lecturer_finance_name"],
        "dosen": DEFAULT_BRANDING["lecturer_name"],
    }
    for username, name in user_map.items():
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.full_name = name

    db.commit()
    return get_branding(db)

```


---
# FILE: backend/app/services/tenant_service.py
---
```python
import json
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Company, ClassSession, SimulationState, SimulationSlider, ScenarioCase,
    Vendor, VendorMetricHistory, Product, BillOfMaterials, BOMItem,
    WorkCenter, CRMLead, Account, DepartmentBudget, Employee, User,
    PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem,
    WorkOrder, JournalEntry, JournalItem, Customer, MarketingCampaign
)
from backend.app.services.behavior_engine import SCENARIO_MATRIX, get_scenario_by_id


def provision_company_data(db: Session, company: Company, session: ClassSession):
    """
    Provisions a complete, isolated ERP & Business Simulation environment
    for a student team tenant company.
    """
    # 1. Simulation State
    sim_state = db.query(SimulationState).filter(SimulationState.company_id == company.id).first()
    if not sim_state:
        sim_state = SimulationState(
            company_id=company.id,
            current_round=1,
            period_name="Bulan 1 (Januari 2026)",
            cash=company.initial_capital or 500000000.0,
            revenue=45000000.0,
            expenses=25000000.0,
            net_profit=20000000.0,
            csat_score=88.5,
            worker_morale=92.0,
            machine_health=95.0,
            supplier_health=91.0,
            overall_score=0.0,
            is_strike_active=False,
            active_case_title="Misi 1: Evaluasi Vendor & Pencegahan Bottleneck Bahan Baku",
            active_case_description="Kelompok diminta melakukan evaluasi kinerja 4 vendor bahan baku. Teliti grafik ketaatan dan defect rate sebelum menerbitkan PO."
        )
        db.add(sim_state)

    # 2. Simulation Slider
    slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == company.id).first()
    if not slider:
        slider = SimulationSlider(
            company_id=company.id,
            session_id=session.id if session else None,
            is_company_override=False,
            supply_disruption=25.0,
            machine_breakdown_risk=15.0,
            market_volatility=30.0,
            labor_strike_risk=10.0,
            bad_debt_risk=15.0,
            competitor_price_war=20.0
        )
        db.add(slider)

    # 3. Scenario Cases (3 Problem-Based Learning Missions)
    existing_cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == company.id).count()
    if existing_cases == 0:
        session_id = session.id if session else None
        cases = [
            ScenarioCase(
                session_id=session_id,
                company_id=company.id,
                code="CASE-01",
                stage_order=1,
                title="Misi 1: Evaluasi Vendor & Pencegahan Bottleneck Bahan Baku",
                category="procurement",
                description="Lini produksi Smartwatch membutuhkan pasokan baterai dan chipset yang konsisten. Ada 4 vendor yang tersedia dengan profil berbeda. Hindari vendor dengan defect rate tinggi yang berisiko merusak mesin di pabrik.",
                trigger_hint="Periksa grafik Completion Rate & Defect History pada menu Pengadaan/Vendor.",
                solvable_workflow="1. Buka modul Vendor/Purchasing -> Bandingkan chart 4 vendor.\n2. Buat Purchase Order (PO) ke vendor terpercaya dengan defect rate < 2%.\n3. Pertahankan safety stock minimal 50 unit.",
                resolution_criteria="PO diterbitkan ke vendor berkualitas, safety stock bahan baku terpenuhi.",
                status="active",
                round_introduced=1,
                resolution_score=0.0,
                grade="-",
                step_scores=None,
                fact_sheet_data=None
            ),
            ScenarioCase(
                session_id=session_id,
                company_id=company.id,
                code="CASE-02",
                stage_order=2,
                title="Misi 2: Penanganan Krisis Keluhan Pelanggan VIP di CRM",
                category="crm",
                description="Klien penting (CV Megah Sentosa) melaporkan 15 unit Smartwatch mengalami layar bergaris dari batch pengiriman sebelumnya dan mengancam memutus kontrak tahunan senilai Rp 150.000.000.",
                trigger_hint="Buka tiket keluhan bernotifikasi Urgent di modul CRM.",
                solvable_workflow="1. Buka modul CRM -> Cari tiket keluhan CV Megah Sentosa.\n2. Pilih tindakan penyelesaian: 'Ganti Unit Baru + Voucher Diskon 10%'.\n3. Terbitkan Credit Note di Akuntansi untuk mencatat retur barang.",
                resolution_criteria="Tiket keluhan terselesaikan, CSAT pulih di atas 80%.",
                status="pending",
                round_introduced=2,
                resolution_score=0.0,
                grade="-",
                step_scores=None,
                fact_sheet_data=None
            ),
            ScenarioCase(
                session_id=session_id,
                company_id=company.id,
                code="CASE-03",
                stage_order=3,
                title="Misi 3: Manajemen Likuiditas Kas & Pencegahan Mogok Kerja Buruh",
                category="hr",
                description="Terjadi penundaan pembayaran dari salah satu pelanggan retail. Jika saldo kas operasional tidak diamankan, pembayaran gaji operator pabrik akan terlambat dan memicu ancaman mogok kerja serikat buruh.",
                trigger_hint="Pantau rasio kas dan indikator Moral Pekerja di modul HR.",
                solvable_workflow="1. Buka modul Akuntansi -> Kurangi pengeluaran promosi non-esensial.\n2. Di modul HR -> Setujui paket uang lembur proporsional.\n3. Pastikan gaji dibayarkan tepat waktu.",
                resolution_criteria="Gaji terbayar, indikator moral buruh di atas 85%, mogok kerja dihindari.",
                status="pending",
                round_introduced=3,
                resolution_score=0.0,
                grade="-",
                step_scores=None,
                fact_sheet_data=None
            )
        ]
        db.add_all(cases)

    # 4. Realistic Vendors with Historical Charts
    existing_vendors = db.query(Vendor).filter(Vendor.company_id == company.id).count()
    if existing_vendors == 0:
        v1 = Vendor(
            company_id=company.id,
            name="PT Surya Logam Presisi",
            category="Casing Aluminium & Mekanikal Presisi",
            lead_time_days=4,
            fulfillment_rate=98.5,
            on_time_rate=97.0,
            defect_rate=0.4,
            price_multiplier=1.20,
            min_order_qty=20,
            credit_terms_days=30,
            notes="Supplier grade-1 terakreditasi ISO. Harga sedikit premium namun kualitas konsisten tanpa komplain."
        )
        v2 = Vendor(
            company_id=company.id,
            name="Apex Micro Components Ltd",
            category="Microcontroller MCU & Sensor Semikonduktor",
            lead_time_days=6,
            fulfillment_rate=94.0,
            on_time_rate=93.0,
            defect_rate=1.2,
            price_multiplier=1.10,
            min_order_qty=30,
            credit_terms_days=30,
            notes="Pemasok semikonduktor internasional. Ketaatan jadwal stabil, kapasitas pasokan besar."
        )
        v3 = Vendor(
            company_id=company.id,
            name="CV Mitra Bahari Sentosa",
            category="Baterai & Komponen Elektrik Grosir",
            lead_time_days=10,
            fulfillment_rate=78.0,
            on_time_rate=74.0,
            defect_rate=8.8,
            price_multiplier=0.72,
            min_order_qty=10,
            credit_terms_days=14,
            notes="Harga sangat miring (diskon 28%). Namun defect rate tinggi dan sering terlambat dari jadwal."
        )
        v4 = Vendor(
            company_id=company.id,
            name="PT Mandiri Cipta Display",
            category="Panel Layar AMOLED 1.4 Inch",
            lead_time_days=5,
            fulfillment_rate=91.0,
            on_time_rate=89.0,
            defect_rate=1.8,
            price_multiplier=1.00,
            min_order_qty=15,
            credit_terms_days=60,
            notes="Menyediakan termin pembayaran fleksibel tempo 60 hari. Sangat bersahabat untuk cashflow."
        )
        db.add_all([v1, v2, v3, v4])
        db.flush()

        histories = [
            VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -3", fulfillment_rate=99.0, on_time_rate=98.0, defect_rate=0.3, price_index=120.0),
            VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -2", fulfillment_rate=98.0, on_time_rate=96.5, defect_rate=0.5, price_index=120.0),
            VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -1", fulfillment_rate=98.5, on_time_rate=97.0, defect_rate=0.4, price_index=122.0),
            VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -3", fulfillment_rate=95.0, on_time_rate=94.0, defect_rate=1.1, price_index=110.0),
            VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -2", fulfillment_rate=93.5, on_time_rate=92.0, defect_rate=1.3, price_index=110.0),
            VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -1", fulfillment_rate=94.0, on_time_rate=93.0, defect_rate=1.2, price_index=112.0),
            VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -3", fulfillment_rate=82.0, on_time_rate=79.0, defect_rate=7.5, price_index=75.0),
            VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -2", fulfillment_rate=75.0, on_time_rate=71.0, defect_rate=9.2, price_index=70.0),
            VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -1", fulfillment_rate=78.0, on_time_rate=74.0, defect_rate=8.8, price_index=72.0),
            VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -3", fulfillment_rate=92.0, on_time_rate=90.0, defect_rate=1.6, price_index=100.0),
            VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -2", fulfillment_rate=90.0, on_time_rate=88.0, defect_rate=2.0, price_index=100.0),
            VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -1", fulfillment_rate=91.0, on_time_rate=89.0, defect_rate=1.8, price_index=102.0),
        ]
        db.add_all(histories)

    # 5. Products & BOM
    existing_products = db.query(Product).filter(Product.company_id == company.id).count()
    if existing_products == 0:
        p_mcu = Product(company_id=company.id, sku=f"RAW-MCU-{company.id:02d}", name="Chipset Microcontroller MCU-X", product_type="raw_material", cost_price=75000.0, list_price=0.0, current_stock=120.0, min_safety_stock=40.0)
        p_screen = Product(company_id=company.id, sku=f"RAW-DSP-{company.id:02d}", name="Layar AMOLED 1.4 Inch", product_type="raw_material", cost_price=60000.0, list_price=0.0, current_stock=110.0, min_safety_stock=40.0)
        p_bat = Product(company_id=company.id, sku=f"RAW-BAT-{company.id:02d}", name="Baterai Li-Po 450mAh", product_type="raw_material", cost_price=35000.0, list_price=0.0, current_stock=130.0, min_safety_stock=50.0)
        p_case = Product(company_id=company.id, sku=f"RAW-CAS-{company.id:02d}", name="Casing Aluminium CNC", product_type="raw_material", cost_price=40000.0, list_price=0.0, current_stock=90.0, min_safety_stock=30.0)
        p_smartwatch = Product(company_id=company.id, sku=f"FNG-SW-{company.id:02d}", name=f"Smartwatch VLab Pro {company.id} (Waterproof)", product_type="finished_good", cost_price=210000.0, list_price=550000.0, current_stock=45.0, min_safety_stock=20.0)

        db.add_all([p_mcu, p_screen, p_bat, p_case, p_smartwatch])
        db.flush()

        bom = BillOfMaterials(company_id=company.id, finished_product_id=p_smartwatch.id, name=f"BOM Standar Smartwatch Pro {company.id}", version="v1.0")
        db.add(bom)
        db.flush()

        bom_items = [
            BOMItem(bom_id=bom.id, raw_product_id=p_mcu.id, quantity_required=1.0),
            BOMItem(bom_id=bom.id, raw_product_id=p_screen.id, quantity_required=1.0),
            BOMItem(bom_id=bom.id, raw_product_id=p_bat.id, quantity_required=1.0),
            BOMItem(bom_id=bom.id, raw_product_id=p_case.id, quantity_required=1.0),
        ]
        db.add_all(bom_items)

    # 6. Work Centers
    existing_wc = db.query(WorkCenter).filter(WorkCenter.company_id == company.id).count()
    if existing_wc == 0:
        wc1 = WorkCenter(company_id=company.id, code=f"WC-SMT-{company.id:02d}", name="Lini Perakitan Elektronik SMT", capacity_units_per_hour=30.0, hourly_cost=180000.0, failure_rate=4.0, status="operational")
        wc2 = WorkCenter(company_id=company.id, code=f"WC-QC-{company.id:02d}", name="Lini Finishing & QC Packaging", capacity_units_per_hour=40.0, hourly_cost=140000.0, failure_rate=2.0, status="operational")
        db.add_all([wc1, wc2])

    # 7. CRM Leads & Customer Complaints
    existing_leads = db.query(CRMLead).filter(CRMLead.company_id == company.id).count()
    if existing_leads == 0:
        leads = [
            CRMLead(
                company_id=company.id,
                title="Inbound Inquiries: Retailer Gadget TokoPDA (50 Unit)",
                customer_name="TokoPDA Megastore Jakarta",
                customer_email="buying@tokopda.com",
                stage="new",
                expected_revenue=27500000.0,
                probability=30.0,
                priority="medium",
                credit_rating="low_risk",
                csat_score=88.0,
                notes="Permintaan penawaran via e-catalog untuk 50 unit Smartwatch VLab Pro batch reguler."
            ),
            CRMLead(
                company_id=company.id,
                title="Permintaan Kerjasama Distribusi Wilayah Timur (80 Unit)",
                customer_name="CV Borneo Smart Devices",
                customer_email="distribusi@borneosmart.id",
                stage="new",
                expected_revenue=44000000.0,
                probability=25.0,
                priority="medium",
                credit_rating="low_risk",
                csat_score=85.0,
                notes="Calon distributor regional Kalimantan meminta profil produk dan termin pembayaran konsinyasi/tempo 30 hari."
            ),
            CRMLead(
                company_id=company.id,
                title="Pengadaan 120 Unit Smartwatch Korporat",
                customer_name="PT Multi Integra Nusantara",
                customer_email="procurement@multi-integra.co.id",
                stage="proposition",
                expected_revenue=66000000.0,
                probability=75.0,
                priority="high",
                credit_rating="low_risk",
                csat_score=90.0,
                notes="Prospek korporasi untuk program kesehatan karyawan. Menunggu proposal final."
            ),
            CRMLead(
                company_id=company.id,
                title="Tender Perangkat Smart Band Daerah",
                customer_name="Dinas Pemuda & Olahraga Prov. Jabar",
                customer_email="kontak@dispora-jabar.go.id",
                stage="qualified",
                expected_revenue=137500000.0,
                probability=45.0,
                priority="medium",
                credit_rating="low_risk",
                csat_score=85.0,
                notes="Tender terbuka untuk 250 unit perangkat pelacak kebugaran."
            ),
            CRMLead(
                company_id=company.id,
                title="[URGENT KELUHAN] Retur Batch #08 Layar Bergaris",
                customer_name="CV Megah Sentosa",
                customer_email="direktur@megahsentosa.id",
                stage="qualified",
                expected_revenue=150000000.0,
                probability=20.0,
                priority="urgent",
                credit_rating="medium_risk",
                csat_score=35.0,
                is_complaint=True,
                complaint_details="15 unit dari pengiriman kemarin mengalami layar flicker & garis hitam. Akun VIP mengancam memutus kontrak jika tidak ada solusi hari ini!",
                notes="Kasus kritis yang harus segera diselesaikan di Misi 2."
            )
        ]
        db.add_all(leads)

    # 8. Chart of Accounts (COA)
    existing_accounts = db.query(Account).filter(Account.company_id == company.id).count()
    if existing_accounts == 0:
        accounts = [
            Account(company_id=company.id, code="1010", name="Kas & Rekening Bank", account_type="asset", balance=company.initial_capital or 500000000.0),
            Account(company_id=company.id, code="1020", name="Piutang Usaha (AR)", account_type="asset", balance=45000000.0),
            Account(company_id=company.id, code="1030", name="Persediaan Bahan Baku", account_type="asset", balance=45000000.0),
            Account(company_id=company.id, code="1040", name="Persediaan Barang Jadi", account_type="asset", balance=24750000.0),
            Account(company_id=company.id, code="2010", name="Utang Usaha (AP)", account_type="liability", balance=15000000.0),
            Account(company_id=company.id, code="3010", name="Modal Disetor Mahasiswa", account_type="equity", balance=company.initial_capital or 500000000.0),
            Account(company_id=company.id, code="4010", name="Pendapatan Penjualan", account_type="revenue", balance=45000000.0),
            Account(company_id=company.id, code="5010", name="Harga Pokok Penjualan (HPP)", account_type="expense", balance=18900000.0),
            Account(company_id=company.id, code="6010", name="Beban Gaji Karyawan", account_type="expense", balance=25000000.0),
            Account(company_id=company.id, code="6020", name="Beban Pemasaran & Iklan", account_type="expense", balance=10000000.0),
        ]
        db.add_all(accounts)

    # 9. Department Budgets
    existing_budgets = db.query(DepartmentBudget).filter(DepartmentBudget.company_id == company.id).count()
    if existing_budgets == 0:
        budgets = [
            DepartmentBudget(company_id=company.id, department="Produksi & Manufaktur", allocated_amount=120000000.0, spent_amount=25000000.0, period_name="Bulan 1"),
            DepartmentBudget(company_id=company.id, department="Pengadaan / Purchasing", allocated_amount=150000000.0, spent_amount=35000000.0, period_name="Bulan 1"),
            DepartmentBudget(company_id=company.id, department="Pemasaran / Marketing", allocated_amount=40000000.0, spent_amount=10000000.0, period_name="Bulan 1"),
            DepartmentBudget(company_id=company.id, department="Human Resources (HR)", allocated_amount=60000000.0, spent_amount=25000000.0, period_name="Bulan 1"),
        ]
        db.add_all(budgets)

    # 10. Employees
    existing_employees = db.query(Employee).filter(Employee.company_id == company.id).count()
    if existing_employees == 0:
        employees = [
            Employee(company_id=company.id, name="Ahmad Fauzi", department="Produksi", role="Kepala Lini Perakitan", monthly_salary=7500000.0, morale_score=92.0, fatigue_score=25.0, status="active"),
            Employee(company_id=company.id, name="Siti Rahma", department="Produksi", role="Operator SMT Mesin 1", monthly_salary=5200000.0, morale_score=90.0, fatigue_score=30.0, status="active"),
            Employee(company_id=company.id, name="Bambang Wijaya", department="Produksi", role="Operator SMT Mesin 2", monthly_salary=5200000.0, morale_score=88.0, fatigue_score=32.0, status="active"),
            Employee(company_id=company.id, name="Dewi Lestari", department="Quality Control", role="Spesialis Inspeksi QC", monthly_salary=6000000.0, morale_score=94.0, fatigue_score=20.0, status="active"),
            Employee(company_id=company.id, name="Rian Pratama", department="Sales & CRM", role="Key Account Executive", monthly_salary=6500000.0, morale_score=91.0, fatigue_score=22.0, status="active"),
        ]
        db.add_all(employees)

    db.commit()


def reset_company_data(db: Session, company_id: int):
    """
    Purges transactional and state data for a company and re-seeds baseline data.
    100% Robust purge of all student inputs and transactions.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return False
    
    session = company.session

    # 1. Clean all student transaction records
    sos = db.query(SalesOrder).filter(SalesOrder.company_id == company_id).all()
    for so in sos:
        db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == so.id).delete()
        db.delete(so)
    
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id).all()
    for po in pos:
        db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po.id).delete()
        db.delete(po)

    db.query(WorkOrder).filter(WorkOrder.company_id == company_id).delete()

    jes = db.query(JournalEntry).filter(JournalEntry.company_id == company_id).all()
    for je in jes:
        db.query(JournalItem).filter(JournalItem.journal_entry_id == je.id).delete()
        db.delete(je)

    db.query(Customer).filter(Customer.company_id == company_id).delete()
    db.query(MarketingCampaign).filter(MarketingCampaign.company_id == company_id).delete()

    # 2. Delete existing child master & state data
    db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).delete()
    db.query(CRMLead).filter(CRMLead.company_id == company_id).delete()
    db.query(Account).filter(Account.company_id == company_id).delete()
    db.query(DepartmentBudget).filter(DepartmentBudget.company_id == company_id).delete()
    db.query(Employee).filter(Employee.company_id == company_id).delete()
    db.query(WorkCenter).filter(WorkCenter.company_id == company_id).delete()
    
    # Clean BOM and Products
    boms = db.query(BillOfMaterials).filter(BillOfMaterials.company_id == company_id).all()
    for b in boms:
        db.delete(b)
    db.query(Product).filter(Product.company_id == company_id).delete()

    # Clean Vendors
    vendors = db.query(Vendor).filter(Vendor.company_id == company_id).all()
    for v in vendors:
        db.delete(v)

    # Clean state and sliders
    db.query(SimulationState).filter(SimulationState.company_id == company_id).delete()
    db.query(SimulationSlider).filter(SimulationSlider.company_id == company_id).delete()

    # Reset company cash balance to initial capital
    company.current_cash = company.initial_capital or 500000000.0
    db.commit()

    # 3. Re-provision clean baseline data
    provision_company_data(db, company, session)
    return True


def seed_multi_tenants(db: Session):
    """
    Ensures at least 3 distinct student group tenant companies and login accounts exist.
    """
    from passlib.context import CryptContext
    from backend.app.models.models import User
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    session = db.query(ClassSession).first()
    if not session:
        return

    # 1. Ensure student group users exist
    groups_data = [
        ("kelompok1", "Kelompok 1 (PT Inovasi Cipta Mandiri)", "k1@mahasiswa.vlaberp.ac.id"),
        ("kelompok2", "Kelompok 2 (PT Techno Sinergi Nusantara)", "k2@mahasiswa.vlaberp.ac.id"),
        ("kelompok3", "Kelompok 3 (PT Nusantara Elektronika Medika)", "k3@mahasiswa.vlaberp.ac.id"),
        ("kelompok4", "Kelompok 4 (PT Sinergi Baterai Nusantara)", "k4@mahasiswa.vlaberp.ac.id"),
    ]

    user_map = {}
    for username, full_name, email in groups_data:
        usr = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if not usr:
            usr = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=pwd_ctx.hash("mhs123"),
                role="MAHASISWA"
            )
            db.add(usr)
            db.commit()
            db.refresh(usr)
        else:
            usr.username = username
            usr.full_name = full_name
            db.commit()
        user_map[username] = usr

    # Also keep demo 'mahasiswa' alias linked to kelompok 1
    mhs_alias = db.query(User).filter(User.username == "mahasiswa").first()
    if not mhs_alias:
        mhs_alias = User(
            username="mahasiswa",
            email="mahasiswa@vlaberp.ac.id",
            full_name="Mahasiswa Kelompok 1",
            hashed_password=pwd_ctx.hash("mhs123"),
            role="MAHASISWA"
        )
        db.add(mhs_alias)
        db.commit()

    # Check companies
    existing_companies = db.query(Company).filter(Company.session_id == session.id).all()
    
    # 1. Company 1 (PT Inovasi Cipta Mandiri)
    if len(existing_companies) >= 1:
        c1 = existing_companies[0]
        if "kelompok1" in user_map:
            c1.team_leader_id = user_map["kelompok1"].id
            db.commit()
        provision_company_data(db, c1, session)

    # 2. Company 2 (Kelompok 2 - PT Techno Sinergi Nusantara)
    c2 = db.query(Company).filter(Company.name == "PT Techno Sinergi Nusantara").first()
    if not c2:
        c2 = Company(
            session_id=session.id,
            name="PT Techno Sinergi Nusantara",
            industry="Komponen IoT & Sensor Pintar",
            team_leader_id=user_map["kelompok2"].id if "kelompok2" in user_map else None,
            initial_capital=500000000.0,
            current_cash=500000000.0
        )
        db.add(c2)
        db.commit()
        db.refresh(c2)
    else:
        if not c2.team_leader_id and "kelompok2" in user_map:
            c2.team_leader_id = user_map["kelompok2"].id
            db.commit()
    provision_company_data(db, c2, session)

    # 3. Company 3 (Kelompok 3 - PT Nusantara Elektronika Medika)
    c3 = db.query(Company).filter(Company.name == "PT Nusantara Elektronika Medika").first()
    if not c3:
        c3 = Company(
            session_id=session.id,
            name="PT Nusantara Elektronika Medika",
            industry="Alat Kesehatan & Monitoring Digital",
            team_leader_id=user_map["kelompok3"].id if "kelompok3" in user_map else None,
            initial_capital=500000000.0,
            current_cash=500000000.0
        )
        db.add(c3)
        db.commit()
        db.refresh(c3)
    else:
        if not c3.team_leader_id and "kelompok3" in user_map:
            c3.team_leader_id = user_map["kelompok3"].id
            db.commit()
    provision_company_data(db, c3, session)

    # 4. Company 4 if exists (PT Sinergi Baterai Nusantara)
    c4 = db.query(Company).filter(Company.name == "PT Sinergi Baterai Nusantara").first()
    if c4 and not c4.team_leader_id and "kelompok4" in user_map:
        c4.team_leader_id = user_map["kelompok4"].id
        db.commit()


# =====================================================================
# 12 PRESET INDUSTRY PROFILES & CASE VARIATION CATALOG
# =====================================================================

PRESET_TENANTS = [
    {"name": "PT Inovasi Cipta Mandiri", "industry": "Smart Device IoT & Wearables", "group_num": 1},
    {"name": "PT Techno Sinergi Nusantara", "industry": "Komponen Sensor Industri & Robotika", "group_num": 2},
    {"name": "PT Nusantara Elektronika Medika", "industry": "Alat Kesehatan & Monitoring Digital", "group_num": 3},
    {"name": "PT Sinergi Baterai Nusantara", "industry": "Sistem Penyimpanan Energi & Baterai EV", "group_num": 4},
    {"name": "PT Otomasi Presisi Indonesia", "industry": "Mikrokontroler & Otomasi Lini Pabrik", "group_num": 5},
    {"name": "PT Aero Telemetri Global", "industry": "Sistem Avionik Drone & Navigasi Cerdas", "group_num": 6},
    {"name": "PT Optika Laser Nusantara", "industry": "Komponen Optik Presisi & Sensor Laser", "group_num": 7},
    {"name": "PT Eco Daya Energi", "industry": "Inverter Surya Pintar & Green Energy", "group_num": 8},
    {"name": "PT Bio Instrumentasi Medika", "industry": "Biosensor Diagnostik & Analisis Lab", "group_num": 9},
    {"name": "PT Telekomika Nusantara Satelit", "industry": "Modul Komunikasi Satelit & Antena Array", "group_num": 10},
    {"name": "PT Mekatronika Otomotif Mandiri", "industry": "ECU Kendaraan Cerdas & Instrument Cluster", "group_num": 11},
    {"name": "PT Quantum Nano Semikonduktor", "industry": "Komponen Semikonduktor & Nanomaterial", "group_num": 12},
]

DIFFERENTIATED_CASE_PACKS = [
    # Pack 1: SCM Supply Chain Crisis
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Krisis Pasokan: Rekanan Pemasok Utama Cacat 8.8% & Keterlambatan Pasokan",
            "category": "purchasing",
            "description": "Supplier bahan baku utama mengalami lonjakan tingkat cacat bahan hingga 8.8% serta keterlambatan kirim 10 hari. Lini perakitan terancam berhenti total jika PO baru diterbitkan ke supplier ini tanpa audit rekam jejak.",
            "trigger_hint": "Buka modul Rekanan Vendor, bandingkan rasio cacat (defect rate) dan waktu tunggu (lead time) keempat vendor.",
            "solvable_workflow": "1. Alihkan Purchase Order (PO) ke PT Surya Logam Presisi (defect 0.4%).\n2. Terbitkan PO minimal 50 unit.\n3. Tolak pesanan tambahan ke rekanan cacat.",
            "resolution_criteria": "PO berhasil diterbitkan ke supplier grade-1 dengan defect < 1.0% dan tingkat pemenuhan tepat waktu.",
            "fact_sheet_data": {
                "root_cause": "Ketergantungan pada satu rekanan murah tanpa memeriksa rekam jejak defect rate historis.",
                "best_practice": "Pilih rekanan terakreditasi ISO meskipun harga unit sedikit lebih tinggi guna menghindari kerugian retur massal."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Negosiasi Ulang Kontrak Pengadaan & Mitigasi Fluktuasi Harga Bahan Baku",
            "category": "purchasing",
            "description": "Vendor semikonduktor mengumumkan kenaikan harga 25% mendadak. Manajemen harus menegosiasikan kontrak pengadaan volume besar (bulk order) dengan klausul termin kredit 60 hari.",
            "trigger_hint": "Tinjau syarat kredit dan minimum order qty pada master data rekanan.",
            "solvable_workflow": "1. Evaluasi konsumsi bahan baku perakitan.\n2. Lakukan purchase order konsolidasi untuk mendapatkan diskon kuantitas.\n3. Catat komitmen termin pembayaran di Akuntansi.",
            "resolution_criteria": "HPP terkendali di bawah batas pagu dan kontinuitas suplai terjamin untuk 3 periode.",
            "fact_sheet_data": {
                "root_cause": "Pembelian spot market eceran menyebabkan harga beli rentan fluktuasi.",
                "best_practice": "Gunakan blanket purchase agreement dan manfaatkan skala ekonomis volume pembelian."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Audit Kepatuhan Rantai Pasok (SCM) & Implementasi Multi-Sourcing",
            "category": "purchasing",
            "description": "Risiko geopolitik mengancam jalur logistik impor. Perusahaan harus menetapkan pemasok alternatif cadangan lokal untuk menghindari single-point-of-failure.",
            "trigger_hint": "Daftarkan vendor cadangan baru di modul Purchasing.",
            "solvable_workflow": "1. Daftarkan master vendor lokal cadangan.\n2. Lakukan uji sampel batch kecil.\n3. Alokasikan 30% kuota PO ke suplier lokal.",
            "resolution_criteria": "Ketergantungan single-source tereliminasi, buffer stock aman.",
            "fact_sheet_data": {
                "root_cause": "Konsentrasi 100% pesanan pada satu suplier impor tunggal.",
                "best_practice": "Strategi dual-sourcing 70/30 membagi risiko tanpa mengorbankan skala diskon."
            }
        }
    ],

    # Pack 2: CRM Customer Quality Scandal
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Skandal Mutu Klien VIP Enterprise: Retur 100 Unit & Ancaman Pemutusan Kontrak",
            "category": "crm",
            "description": "Klien enterprise terbesar (CV Megah Sentosa, nilai kontrak Rp 150.000.000) menerima 100 unit perangkat bergaris. Klien mengancam menahan sisa pembayaran dan menuntut penalti ganti rugi.",
            "trigger_hint": "Buka modul CRM -> Cari tiket keluhan darurat CV Megah Sentosa.",
            "solvable_workflow": "1. Buka tiket keluhan darurat di modul CRM.\n2. Setujui paket mitigasi: Ganti 15 unit baru gratis + Voucher diskon 10% pesanan berikutnya.\n3. Konfirmasi Work Order darurat di Pabrik.",
            "resolution_criteria": "Tiket terselesaikan, retensi klien berhasil, CSAT pulih di atas 80%.",
            "fact_sheet_data": {
                "root_cause": "Kegagalan sensor QC pada stasiun akhir meloloskan batch cacat ke klien enterprise.",
                "best_practice": "Customer service proaktif dengan kompensasi nyata jauh lebih murah daripada kehilangan akun bernilai ratusan juta."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Kebijakan Garansi Cepat & Pemulihan Reputasi Merek (CSAT)",
            "category": "crm",
            "description": "Keluhan pelanggan menyebar di media sosial industri, menurunkan sentimen pasar dan moral tenaga penjualan. Layanan bantuan kilat 24 jam harus segera diaktifkan.",
            "trigger_hint": "Tinjau skor CSAT di CRM dan sesuaikan prioritas pipeline prospek.",
            "solvable_workflow": "1. Buka pipeline CRM.\n2. Tingkatkan prioritas akun komplain ke Urgent.\n3. Terbitkan surat permintaan maaf resmi dan garansi penggantian 1x24 jam.",
            "resolution_criteria": "CSAT naik kembali di atas 85%, pipeline prospek baru tidak mengalami churn.",
            "fact_sheet_data": {
                "root_cause": "Keterlambatan respon penanganan komplain di awal kejadian.",
                "best_practice": "Standar respon Service Level Agreement (SLA) ketat di bawah 2 jam untuk akun VIP."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Pencatatan Penyesuaian Akuntansi: Credit Note & Retensi Nilai Kontrak",
            "category": "crm",
            "description": "Kompensasi retur memerlukan penyesuaian nilai piutang di buku besar tanpa merusak struktur arus kas operasional.",
            "trigger_hint": "Sinkronkan modul CRM dengan Buku Besar Akuntansi.",
            "solvable_workflow": "1. Terbitkan Credit Note penyesuaian harga di CRM.\n2. Catat pemotongan piutang tertagih di Akuntansi.\n3. Perpanjang kontrak pemeliharaan tahunan.",
            "resolution_criteria": "Jurnal tercatat balance, klien menandatangani perpanjangan kontrak tahun depan.",
            "fact_sheet_data": {
                "root_cause": "Ketidaksinkronan data diskon penjualan antara bagian sales dan kasir akuntansi.",
                "best_practice": "Integrasi real-time antara CRM dan General Ledger mencegah perselisihan faktur."
            }
        }
    ],

    # Pack 3: HR Labor Relations & Strike Prevention
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Tuntutan Uang Lembur & Ancaman Mogok Kerja Serikat Buruh SPMI",
            "category": "hr",
            "description": "Operator lini perakitan mengeluhkan jam lembur berlebih akibat target pesanan dadakan tanpa kompensasi uang makan. Serikat buruh mengeluarkan surat peringatan mogok kerja 3 hari.",
            "trigger_hint": "Pantau indikator Moral Pekerja di modul HR dan rasio kas operasional.",
            "solvable_workflow": "1. Buka meja dialog bipartit di modul HR.\n2. Setujui kenaikan upah wajar (+8-12%) dan paket bonus lembur damai Rp 1.500.000.\n3. Pastikan kas operasional mencukupi pencairan payroll.",
            "resolution_criteria": "Moral pekerja di atas 85%, pemogokan dibatalkan, kontinuitas lini produksi aman.",
            "fact_sheet_data": {
                "root_cause": "Beban kerja lembur meningkat 40% tanpa penyesuaian insentif kesejahteraan.",
                "best_practice": "Dialog bipartit terbuka dan pembagian bonus insentif produktivitas menjamin stabilitas buruh."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Standardisasi Keselamatan Kerja (K3) & Ergonomi Lini Perakitan",
            "category": "hr",
            "description": "Terjadi 2 insiden cedera ringan pada stasiun solder manual akibat pencahayaan dan alat pelindung diri (APD) yang aus. Staf menolak bekerja lembur sebelum ada perbaikan K3.",
            "trigger_hint": "Tinjau kondisi pegawai di modul HR dan alokasikan pagu anggaran perbaikan lingkungan kerja.",
            "solvable_workflow": "1. Buka modul Akuntansi -> Tambahkan anggaran K3 senilai Rp 15.000.000.\n2. Perbarui catatan inventaris APD di modul HR.\n3. Berikan pelatihan K3 berkala kepada kepala regu perakitan.",
            "resolution_criteria": "Insiden kerja nol (zero incident), absensi menurun di bawah 2%.",
            "fact_sheet_data": {
                "root_cause": "Penghematan anggaran operasional yang memangkas pos perlengkapan keselamatan kerja.",
                "best_practice": "Investasi K3 merupakan perlindungan aset terpenting industri: tenaga kerja terampil."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Perjanjian Kerja Bersama (PKB) & Skema Bonus Berbasis KPI Produksi",
            "category": "hr",
            "description": "Guna menyelaraskan kepentingan manajemen dan buruh jangka panjang, serikat pekerja mengusulkan penandatanganan PKB baru dengan klausul profit sharing.",
            "trigger_hint": "Buka modul HR -> Selesaikan perundingan PKB jangka panjang.",
            "solvable_workflow": "1. Susun formula bonus berbasis persentase pencapaian output bebas cacat.\n2. Tanda tangani nota kesepakatan bersama serikat buruh.\n3. Monitor kenaikan produktivitas jam kerja.",
            "resolution_criteria": "PKB disepakati tanpa sengketa perburuhan, moral kerja mencapai 95%.",
            "fact_sheet_data": {
                "root_cause": "Ketidakpastian skema remunerasi tahunan menimbulkan kecurigaan serikat pekerja.",
                "best_practice": "Sistem insentif transparan berbasis KPI produktivitas menyatukan target buruh dan laba perusahaan."
            }
        }
    ],

    # Pack 4: Accounting Cash Liquidity & Bad Debt Crisis
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Krisis Piutang Macet (Bad Debt): Pelanggan Retail Gagal Bayar Rp 120 Juta",
            "category": "accounting",
            "description": "Distributor retail regional mengalami kebangkrutan, menyebabkan piutang dagang Rp 120.000.000 macet. Saldo kas bank menipis tajam mendekati batas kritis penggajian bulanan.",
            "trigger_hint": "Buka modul Akuntansi -> Tinjau saldo kas, rasio piutang tak tertagih, dan buku besar.",
            "solvable_workflow": "1. Bentuk cadangan kerugian piutang tak tertagih di buku besar.\n2. Lakukan penghematan anggaran promosi non-esensial.\n3. Perketat syarat pembayaran pelanggan baru menjadi DP minimal 50%.",
            "resolution_criteria": "Saldo kas tetap di atas safety cash level (Rp 200jt), penggajian tetap lancar.",
            "fact_sheet_data": {
                "root_cause": "Pemberian plafon kredit penjualan tanpa analisis kelayakan skor kredit pelanggan.",
                "best_practice": "Penerapan kebijakan batas kredit (credit limit) ketat dan penagihan berjangka."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Restrukturisasi Utang Vendor & Negosiasi Perpanjangan Fasilitas Kredit Bank",
            "category": "accounting",
            "description": "Jatuh tempo tagihan faktur pemasok Rp 85.000.000 bertepatan dengan tanggal pembayaran pajak penghasilan. Manajemen harus menegosiasikan perpanjangan tenor pembayaran tanpa penalti bunga.",
            "trigger_hint": "Periksa daftar akun utang dagang (Accounts Payable) dan pagu anggaran divisi.",
            "solvable_workflow": "1. Ajukan penjadwalan cicilan pembayaran utang (debt rescheduling) 3 termin.\n2. Bayar termin pertama secara tunai sebagai tanda itikad baik.\n3. Amankan fasilitas letter of credit bank.",
            "resolution_criteria": "Status kredit perusahaan terjaga 'Lancar', tidak ada pembekuan pasokan bahan.",
            "fact_sheet_data": {
                "root_cause": "Mismatch maturitas antara arus kas masuk dari piutang dan jadwal pembayaran tagihan utang.",
                "best_practice": "Penyusunan cash flow forecast mingguan mencegah kejutan defisit kas."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Optimalisasi Modal Kerja (Working Capital Management) & Efisiensi Biaya Overhead",
            "category": "accounting",
            "description": "Biaya listrik industri dan overhead pabrik membengkak 35% akibat utilisasi mesin di luar jam hemat tarif (WBP). Diperlukan rasionalisasi alokasi pagu anggaran departemen.",
            "trigger_hint": "Buka modul Akuntansi -> Kelola Pagu Anggaran Departemen (Budgets).",
            "solvable_workflow": "1. Pangkas pagu anggaran overhead non-kritis sebesar 20%.\n2. Jadwalkan ulang jam operasional mesin pabrik ke tarif listrik luar beban puncak.\n3. Pantau rasio laba bersih pada laporan laba rugi.",
            "resolution_criteria": "Margin laba bersih naik kembali di atas 15%, efisiensi overhead tercapai.",
            "fact_sheet_data": {
                "root_cause": "Pengoperasian mesin boros daya pada jam beban puncak PLN tanpa pemantauan kWh.",
                "best_practice": "Manajemen energi terintegrasi dengan jadwal Work Order memangkas biaya utilitas secara signifikan."
            }
        }
    ],

    # Pack 5: MRP Manufacturing Breakdown & Work Center Downtime
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Kerusakan Kritis Motor Servo Mesin SMT-01: Lini Pabrik Lumpuh Total",
            "category": "mrp",
            "description": "Motor servo pada stasiun Surface Mount Technology (SMT-01) mengalami overheat akibat lonjakan beban produksi tanpa jeda pendinginan. Output stasiun perakitan turun menjadi 0 unit/jam.",
            "trigger_hint": "Buka modul Mesin & Pabrik MRP -> Tinjau status stasiun kerja dan tombol maintenance.",
            "solvable_workflow": "1. Eksekusi tindakan darurat perbaikan/maintenance stasiun kerja SMT-01.\n2. Alihkan sebagian beban perakitan manual sementara ke stasiun kerja QC-02.\n3. Terbitkan work order penyesuaian kuantitas agar pesanan pelanggan tetap terkirim.",
            "resolution_criteria": "Status mesin pulih menjadi 'operational', kesehatan mesin naik di atas 90%, downtime teratasi.",
            "fact_sheet_data": {
                "root_cause": "Mesin dipaksa beroperasi 150% kapasitas tanpa pelumasan dan kalibrasi rutin.",
                "best_practice": "Total Productive Maintenance (TPM) terjadwal mencegah kerugian downtime miliaran rupiah."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Optimalisasi Resep Bill of Materials (BOM) & Eliminasi Scrap Bahan Baku",
            "category": "mrp",
            "description": "Proses perakitan menghasilkan limbah scrap aluminium dan solder paste sebesar 12% di atas standar industri. Resep BOM memerlukan penyesuaian presisi.",
            "trigger_hint": "Tinjau tabel Bill of Materials di modul MRP.",
            "solvable_workflow": "1. Periksa komponen pada resep BOM produk utama.\n2. Kalibrasi toleransi pemotongan bahan pada stasiun kerja.\n3. Uji coba perakitan batch 30 unit dengan parameter baru.",
            "resolution_criteria": "Scrap rate turun di bawah 1.5%, efisiensi bahan meningkat.",
            "fact_sheet_data": {
                "root_cause": "Penggunaan resep BOM usang yang tidak disesuaikan dengan spesifikasi bahan baku vendor baru.",
                "best_practice": "Engineering change order (ECO) berkala untuk memperbarui toleransi resep BOM."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Peningkatan Kapasitas Work Center Menuju Sertifikasi Standar Otomotif IATF",
            "category": "mrp",
            "description": "Untuk menembus pasar ekspor OEM tier-1, pabrik harus meningkatkan kapabilitas proses (Cpk > 1.33) dan mengadopsi stasiun pengujian otomatis.",
            "trigger_hint": "Tingkatkan kapasitas stasiun kerja QC di modul MRP.",
            "solvable_workflow": "1. Tambahkan work center sensor pengujian otomatis.\n2. Latih operator untuk menjalankan SPC (Statistical Process Control).\n3. Validasi hasil uji batch bebas cacat.",
            "resolution_criteria": "Kapasitas produksi naik 25%, tingkat lolos QC mencapai 99.5%.",
            "fact_sheet_data": {
                "root_cause": "Pengujian manual yang mengandalkan mata operator rentan terhadap kelelahan visual.",
                "best_practice": "Automated Optical Inspection (AOI) memastikan zero-defect pada komponen presisi tinggi."
            }
        }
    ],

    # Pack 6: Market Price War & Global Competitor Shock
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Perang Harga Kompetitor Global: Pemotongan Harga 25% Mengikis Margin",
            "category": "crm",
            "description": "Kompetitor multinasional meluncurkan produk substitusi dengan harga 25% lebih murah, menyebabkan penurunan prospek penutupan penjualan (closing rate) hingga separuh.",
            "trigger_hint": "Tinjau harga jual produk dan pipeline peluang di modul CRM.",
            "solvable_workflow": "1. Jangan langsung memangkas harga jual secara drastis.\n2. Tawarkan garansi purnajual 3 tahun dan paket instalasi gratis sebagai diferensiasi nilai.\n3. Dekati akun prospek potensial bernilai besar dengan penawaran kustom.",
            "resolution_criteria": "Closing rate pulih di atas 60%, marjin keuntungan tetap terjaga positif.",
            "fact_sheet_data": {
                "root_cause": "Komoditisasi produk akibat minimnya diferensiasi nilai tambah layanan.",
                "best_practice": "Value-based selling mengalahkan perang harga murah yang merusak industri."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Efisiensi Biaya Pokok Produksi (HPP) Lewat Rekayasa Nilai (Value Engineering)",
            "category": "mrp",
            "description": "Manajemen menargetkan penurunan HPP sebesar 15% tanpa mengurangi durabilitas produk agar harga jual lebih kompetitif di pasar retail.",
            "trigger_hint": "Evaluasi biaya komponen BOM dan harga beli rekanan di Purchasing.",
            "solvable_workflow": "1. Lakukan audit biaya per komponen di resep BOM.\n2. Negosiasi ulang harga casing aluminium dengan suplier grade-1.\n3. Kurangi waktu siklus perakitan di work center.",
            "resolution_criteria": "HPP per unit turun 15%, marjin laba kotor meningkat ke 35%.",
            "fact_sheet_data": {
                "root_cause": "Over-design pada komponen sekunder yang tidak menambah nilai fungsi utama bagi konsumen.",
                "best_practice": "Value engineering menyederhanakan desain suku cadang tanpa mengurangi kekuatan struktural."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Diversifikasi Portofolio Produk & Ekspansi Kanal Penjualan Institusi B2G",
            "category": "crm",
            "description": "Guna mengurangi ketergantungan pada pasar bebas yang fluktuatif, tim sales membidik tender pengadaan sistem digital instansi pemerintah bernilai Rp 300.000.000.",
            "trigger_hint": "Buka modul CRM -> Daftarkan akun prospek institusi baru.",
            "solvable_workflow": "1. Daftarkan prospek tender pengadaan institusi B2G di CRM.\n2. Lengkapi berkas kualifikasi teknis dan sertifikasi TKDN produk.\n3. Konversi prospek menjadi pesanan penjualan resmi.",
            "resolution_criteria": "Tender berhasil dimenangkan, pendapatan melonjak di atas target semester.",
            "fact_sheet_data": {
                "root_cause": "Ketergantungan 100% pada pasar konsumen retail yang sangat elastis terhadap harga.",
                "best_practice": "Porsi kontrak korporat dan institusi jangka panjang memberikan bantalan pendapatan yang stabil."
            }
        }
    ]
]


def differentiate_tenant_cases(db: Session, company_id: int, group_index: int):
    """
    Assigns a distinct realistic case pack to the company so different groups
    face different problems (SCM crisis, CRM VIP defect, Labor strike, Cash liquidity, MRP breakdown, Price war).
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return False

    # Pick case pack by modulo
    pack_idx = (group_index - 1) % len(DIFFERENTIATED_CASE_PACKS)
    chosen_pack = DIFFERENTIATED_CASE_PACKS[pack_idx]

    # Clear existing cases for this company
    db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).delete()
    db.commit()

    # Insert tailored cases
    for case_def in chosen_pack:
        sc = ScenarioCase(
            session_id=company.session_id,
            company_id=company.id,
            code=case_def["code"],
            stage_order=case_def["stage_order"],
            title=case_def["title"],
            category=case_def["category"],
            description=case_def["description"],
            trigger_hint=case_def.get("trigger_hint", ""),
            solvable_workflow=case_def.get("solvable_workflow", ""),
            resolution_criteria=case_def.get("resolution_criteria", ""),
            status="active" if case_def["stage_order"] == 1 else "pending",
            round_introduced=case_def["stage_order"],
            resolution_score=0.0,
            grade="-",
            step_scores=None,
            fact_sheet_data=None
        )
        db.add(sc)

    # Update sim_state's active case title if available
    st = company.sim_state
    if st and len(chosen_pack) > 0:
        st.active_case_title = chosen_pack[0]["title"]
        st.active_case_description = chosen_pack[0]["description"]

    db.commit()
    return True


def batch_generate_tenants(
    db: Session,
    session_id: int,
    target_count: int = 4,
    initial_capital: float = 500000000.0,
    differentiate_cases: bool = True
):
    """
    Batch provisions N companies with user accounts (kelompok1..N / mhs123),
    sets initial capital, provisions ERP master data, and optionally differentiates cases.
    """
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        session = db.query(ClassSession).first()
        if not session:
            return {"status": "error", "message": "Sesi kelas tidak ditemukan."}

    target_count = max(2, min(12, target_count))
    created_or_updated = []

    for i in range(1, target_count + 1):
        username = f"kelompok{i}"
        email = f"k{i}@mahasiswa.vlaberp.ac.id"
        preset = PRESET_TENANTS[(i - 1) % len(PRESET_TENANTS)]
        company_name = preset["name"]
        industry = preset["industry"]
        full_name = f"Kelompok {i} ({company_name})"

        # 1. Ensure user exists
        usr = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if not usr:
            usr = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=pwd_ctx.hash("mhs123"),
                role="MAHASISWA"
            )
            db.add(usr)
            db.commit()
            db.refresh(usr)
        else:
            usr.username = username
            usr.full_name = full_name
            db.commit()

        # 2. Ensure company exists for this session
        session_company_name = company_name if session.id == 1 else f"{company_name} ({session.code})"
        company = db.query(Company).filter(
            Company.session_id == session.id,
            Company.name == session_company_name
        ).first()
        if not company:
            # Check by group position in this session
            existing_by_order = db.query(Company).filter(Company.session_id == session.id).offset(i - 1).first()
            if existing_by_order:
                company = existing_by_order
                company.name = session_company_name
                company.industry = industry
            else:
                company = Company(
                    session_id=session.id,
                    name=session_company_name,
                    industry=industry,
                    team_leader_id=usr.id,
                    initial_capital=initial_capital,
                    current_cash=initial_capital
                )
                db.add(company)
                db.commit()
                db.refresh(company)

        # Update company properties
        company.team_leader_id = usr.id
        company.initial_capital = initial_capital
        company.current_cash = initial_capital
        company.industry = industry
        db.commit()

        # Provision full ERP data for this company
        provision_company_data(db, company, session)

        # Update sim_state cash to match initial capital
        if company.sim_state:
            company.sim_state.cash = initial_capital
            db.commit()

        # Differentiate cases if enabled
        if differentiate_cases:
            differentiate_tenant_cases(db, company.id, i)

        created_or_updated.append({
            "id": company.id,
            "name": company.name,
            "group_label": f"Kelompok {i}",
            "industry": company.industry,
            "initial_capital": company.initial_capital,
            "username": username
        })

    return {
        "status": "success",
        "message": f"Berhasil mem-provisioning {len(created_or_updated)} kelompok mahasiswa secara serentak dengan modal awal Rp {initial_capital:,.0f}!",
        "companies": created_or_updated
    }


# --- FEB TEAM TEACHING DISCIPLINE ROLLING ENGINE (12-BULAN CASCADE) ---

# Domain category map for ScenarioCase.category field
SCENARIO_CATEGORY_MAP = {
    "MFG-01": "mrp", "MFG-02": "mrp", "MFG-03": "mrp", "MFG-04": "mrp",
    "HR-01":  "hr",  "HR-02":  "hr",  "HR-03":  "hr",  "HR-04":  "hr",
    "ACC-01": "accounting", "ACC-02": "accounting", "ACC-03": "accounting", "ACC-04": "accounting",
    "CRM-01": "crm", "CRM-02": "crm", "CRM-03": "crm", "CRM-04": "crm",
    "PUR-01": "purchasing", "PUR-02": "purchasing", "PUR-03": "purchasing", "PUR-04": "purchasing",
}

# Initial state mutations when a scenario becomes ACTIVE (month N starts)
# Describes what external crisis arrives to set up the scenario
SCENARIO_INITIAL_MUTATIONS = {
    # --- MRP / Manufacturing ---
    "MFG-01": {"machine_health": 60.0, "worker_morale": 68.0, "is_strike": True,
               "strike_reason": "Mesin SMT korsleting inverter, operator menuntut upah lembur.",
               "wc_breakdown": True},
    "MFG-02": {"csat_score_cap": 70.0},   # batch cacat → CSAT terancam
    "MFG-03": {},                          # peluang kaizen, tidak ada krisis awal
    "MFG-04": {"machine_health_cap": 75.0, "worker_morale_cap": 78.0},  # inspeksi K3
    # --- HR ---
    "HR-01":  {"worker_morale": 52.0, "is_strike": True,
               "strike_reason": "Serikat buruh blokir pintu pabrik, menuntut upah +12%."},
    "HR-02":  {"worker_morale_cap": 80.0},  # poaching engineer, moral sedikit turun
    "HR-03":  {},                            # program upskilling, tidak ada krisis
    "HR-04":  {"worker_morale": 70.0},       # kecelakaan forklift
    # --- Accounting ---
    "ACC-01": {"cash_deduct": 25000000.0},   # SKPKB pajak mendadak
    "ACC-02": {},                             # pilihan metode penyusutan, tidak ada krisis
    "ACC-03": {"cash_deduct": 50000000.0},   # covenant breach: bank charge penalty
    "ACC-04": {},                             # peluang capex, tidak ada krisis
    # --- CRM ---
    "CRM-01": {"csat_score": 55.0},          # somasi hukum klien
    "CRM-02": {},                             # peluang tender, tidak ada krisis
    "CRM-03": {"csat_score_cap": 72.0},      # distributor minta TOP 90 hari
    "CRM-04": {},                             # program rebate, tidak ada krisis
    # --- Purchasing ---
    "PUR-01": {"supplier_health": 60.0, "cash_deduct": 10000000.0},  # kelangkaan chipset
    "PUR-02": {"supplier_health": 45.0},     # kebakaran gudang vendor
    "PUR-03": {},                             # tawaran bulk buy, tidak ada krisis
    "PUR-04": {"supplier_health_cap": 70.0}, # gratifikasi tim purchasing
}

# 12-bulan urutan skenario per track
# Blok 1 (Bulan 1-4): disiplin yg masuk duluan
# Blok 2 (Bulan 5-8): disiplin kedua
# Blok 3 (Bulan 9-12): disiplin ketiga
TRACK_SEQUENCES = {
    "hr_first": [
        # Blok SDM & Pabrik (Bulan 1-4)
        "MFG-01", "HR-01", "MFG-04", "HR-02",
        # Blok Keuangan & Pengadaan (Bulan 5-8)
        "ACC-01", "PUR-01", "ACC-03", "ACC-04",
        # Blok Pemasaran & CRM (Bulan 9-12)
        "CRM-01", "PUR-02", "CRM-03", "CRM-04",
    ],
    "finance_first": [
        # Blok Keuangan & Pengadaan (Bulan 1-4)
        "ACC-01", "ACC-03", "PUR-01", "ACC-04",
        # Blok Pemasaran & CRM (Bulan 5-8)
        "CRM-01", "PUR-02", "CRM-03", "CRM-04",
        # Blok SDM & Pabrik (Bulan 9-12)
        "MFG-01", "HR-01", "MFG-04", "HR-02",
    ],
    "marketing_first": [
        # Blok Pemasaran & CRM (Bulan 1-4)
        "CRM-01", "PUR-02", "CRM-03", "CRM-04",
        # Blok SDM & Pabrik (Bulan 5-8)
        "MFG-01", "HR-01", "MFG-04", "HR-02",
        # Blok Keuangan & Pengadaan (Bulan 9-12)
        "ACC-01", "PUR-01", "ACC-03", "ACC-04",
    ],
}


def _build_scenario_case_from_matrix(sc_id: str, company_id: int, session_id: int, stage_order: int, status: str, round_introduced: int) -> ScenarioCase:
    """Build a ScenarioCase DB record from a SCENARIO_MATRIX entry."""
    sc_data = get_scenario_by_id(sc_id)
    category = SCENARIO_CATEGORY_MAP.get(sc_id, "general")

    # Build trigger hint and workflow from scenario branches summary
    branches_summary = []
    for b in (sc_data.get("branches") or []):
        cost_str = f"Rp {b['immediate_cost']/1000000:.0f} Jt" if b.get("immediate_cost", 0) > 0 else "Tanpa biaya kas"
        branches_summary.append(f"  Pilihan {b['choice_id']}: {b['label']} ({cost_str})")

    solvable_workflow = "\n".join([
        "1. Analisis konteks krisis yang terjadi dan dampaknya.",
        "2. Buka tab modul ERP yang relevan untuk melihat data operasional terkini.",
        "3. Pilih cabang keputusan di tab 'Pohon Keputusan' → eksekusi pilihan terbaik.",
        "4. Validasi dampak keputusan di modul terkait (kas, mesin, moral, CSAT).",
        "5. Klik 'Validasi & Selesaikan Kasus' setelah tindakan dieksekusi.",
    ])

    trigger_hint = f"Buka tab modul {'Mesin & Pabrik MRP' if category == 'mrp' else 'Pegawai & HR' if category == 'hr' else 'Akuntansi & Kas' if category == 'accounting' else 'Pelanggan & CRM' if category == 'crm' else 'Rekanan Vendor'} → Identifikasi indikator krisis yang aktif bulan ini."

    fact_sheet = {
        "scenario_id": sc_id,
        "domain": sc_data.get("domain", ""),
        "urgency": sc_data.get("urgency", ""),
        "branches": branches_summary,
        "cfo_verdicts": [b.get("cfo_verdict", "") for b in (sc_data.get("branches") or [])],
    }

    return ScenarioCase(
        session_id=session_id,
        company_id=company_id,
        code=sc_id,
        stage_order=stage_order,
        title=f"Bulan {stage_order}: {sc_data['title']}",
        category=category,
        description=sc_data.get("context", sc_data.get("description", "")),
        trigger_hint=trigger_hint,
        solvable_workflow=solvable_workflow,
        resolution_criteria=f"Eksekusi keputusan cabang strategis pada skenario {sc_id} dan terapkan mitigasi yang tepat di modul ERP terkait.",
        status=status,
        round_introduced=round_introduced,
        resolution_score=0.0,
        grade="-",
        step_scores=None,
        fact_sheet_data=json.dumps(fact_sheet),
    )


def roll_session_cases(db: Session, session_id: int, sequence_mode: str):
    """
    Rolls 12-month scenario cascade for all companies in a session.
    Each track distributes 12 scenarios from SCENARIO_MATRIX across 3 discipline blocks:
    - 'hr_first':        SDM & Pabrik (1-4) → Keuangan (5-8) → Pemasaran (9-12)
    - 'finance_first':   Keuangan (1-4) → Pemasaran (5-8) → SDM & Pabrik (9-12)
    - 'marketing_first': Pemasaran (1-4) → SDM & Pabrik (5-8) → Keuangan (9-12)
    """
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        return False, "Sesi kelas FEB tidak ditemukan."

    companies = db.query(Company).filter(Company.session_id == session_id).all()
    if not companies:
        return False, "Tidak ada kelompok perusahaan pada sesi kelas ini."

    sequence = TRACK_SEQUENCES.get(sequence_mode, TRACK_SEQUENCES["hr_first"])

    label_map = {
        "hr_first":        "SDM & Pabrik MRP Duluan → Keuangan → Pemasaran",
        "finance_first":   "Keuangan Duluan → Pemasaran → SDM & Pabrik MRP",
        "marketing_first": "Pemasaran Duluan → SDM & Pabrik → Keuangan",
    }
    label = label_map.get(sequence_mode, "Rotasi Standar FEB")

    for company in companies:
        # Clear existing cases
        db.query(ScenarioCase).filter(ScenarioCase.company_id == company.id).delete()
        db.flush()

        for idx, sc_id in enumerate(sequence):
            stage_order = idx + 1
            is_first = (idx == 0)
            status = "active" if is_first else "pending"
            sc_case = _build_scenario_case_from_matrix(
                sc_id=sc_id,
                company_id=company.id,
                session_id=company.session_id,
                stage_order=stage_order,
                status=status,
                round_introduced=stage_order,
            )
            db.add(sc_case)

        # Apply initial state mutations for Month 1 scenario
        first_sc_id = sequence[0]
        mutation = SCENARIO_INITIAL_MUTATIONS.get(first_sc_id, {})
        st = company.sim_state
        if st:
            _apply_scenario_mutation(st, mutation, db, company.id)
            sc_data = get_scenario_by_id(first_sc_id)
            st.active_case_title = f"Bulan 1: {sc_data['title']}"
            st.active_case_description = sc_data.get("context", "")

        db.commit()

    return True, f"Berhasil me-rolling 12-bulan cascade untuk kelas '{session.name}' dengan track: {label}. {len(companies)} kelompok disinkronkan!"


def _apply_scenario_mutation(state, mutation: dict, db: Session, company_id: int):
    """Apply initial state mutation when a scenario becomes active."""
    if not mutation:
        return

    if "machine_health" in mutation:
        state.machine_health = mutation["machine_health"]
    if "machine_health_cap" in mutation:
        state.machine_health = min(state.machine_health, mutation["machine_health_cap"])

    if "worker_morale" in mutation:
        state.worker_morale = mutation["worker_morale"]
    if "worker_morale_cap" in mutation:
        state.worker_morale = min(state.worker_morale, mutation["worker_morale_cap"])

    if "csat_score" in mutation:
        state.csat_score = mutation["csat_score"]
    if "csat_score_cap" in mutation:
        state.csat_score = min(state.csat_score, mutation["csat_score_cap"])

    if "supplier_health" in mutation:
        state.supplier_health = mutation["supplier_health"]
    if "supplier_health_cap" in mutation:
        state.supplier_health = min(state.supplier_health, mutation["supplier_health_cap"])

    if "cash_deduct" in mutation:
        state.cash = max(0.0, state.cash - mutation["cash_deduct"])
        cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1010").first()
        if cash_acc:
            cash_acc.balance = state.cash

    if mutation.get("is_strike"):
        state.is_strike_active = True
        state.strike_reason = mutation.get("strike_reason", "Aksi serikat buruh dipicu oleh kondisi operasional.")

    if mutation.get("wc_breakdown"):
        wcs = db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all()
        for wc in wcs:
            if "SMT" in wc.code or "Perakitan" in wc.name:
                wc.status = "breakdown"
                wc.failure_rate = min(20.0, wc.failure_rate + 8.0)




```


---
# FILE: backend/app/services/behavior_engine.py
---
```python
import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.models import (
    Company, CompanyStoryEvent, JournalEntry, JournalItem, Account, Product,
    SimulationState, Vendor, WorkCenter, CRMLead, Employee
)

# ==========================================
# 1. BEHAVIORAL PROFILES & TEMPERAMENTS
# ==========================================

CUSTOMER_TEMPERAMENTS = [
    {
        "type": "annoyingly_angry",
        "label": "Akun Korporat Eskalasi Kritis",
        "tone": "anger",
        "color": "red",
        "tolerance": 15,
        "sample_dialogs": [
            "SAYA TUNTUT KE YLKI DAN AKAN SAYA SOMASI HARI INI JUGA! Barang cacat kok berani dikirim?! Uang muka saya kembali utuh 100% plus ganti rugi atau nama perusahaan kalian saya viralkan di media sosial!",
            "Pelayanan amatir sampah! Ini kontrak ratusan juta bukan beli cilok di pinggir jalan! Saya minta direktur kalian telepon saya dalam 1 jam atau kita ketemu di pengadilan!",
            "Kalian sengaja kirim barang rusak ya?! Jangan coba-coba alasan teknis, saya tidak terima alasan apapun! Ganti sekarang juga atau kontrak batal!"
        ],
        "min_discount_demanded": 15.0,
        "requires_executive": True
    },
    {
        "type": "calm_as_cucumber",
        "label": "Mitra Bisnis Jangka Panjang",
        "tone": "calm",
        "color": "emerald",
        "tolerance": 75,
        "sample_dialogs": [
            "Halo rekan-rekan manajemen, kami maklumi dalam proses manufaktur pasti ada kendala teknis tak terduga. Tolong dijadwalkan pengiriman penggantinya ya, kami percaya dengan itikad baik kalian.",
            "Selamat siang, kami temukan beberapa unit tidak sesuai spesifikasi. Tidak apa-apa, tolong diproses penukarannya saat batch berikutnya siap ya. Sukses selalu untuk tim.",
            "Hai tim VLab, kami mengerti kendala mesin kalian. Cukup kirimkan unit pengganti yang sudah lolos QC ganda saja ya, tidak perlu panik."
        ],
        "min_discount_demanded": 5.0,
        "requires_executive": False
    },
    {
        "type": "passive_aggressive",
        "label": "Klien Institusi Strategis",
        "tone": "snarky",
        "color": "purple",
        "tolerance": 40,
        "sample_dialogs": [
            "Wah hebat sekali ya, dari 50 unit yang dipesan yang nyala cuma 35. Mungkin tim QC kalian sedang liburan bersama waktu perakitan? Kami tunggu itikad baiknya sebelum kami cerita ke asosiasi.",
            "Terima kasih atas kiriman produknya yang sangat 'unik' ini. Kami baru tahu kalau layar bergaris sekarang jadi fitur baru. Mohon segera diselesaikan ya sebelum kesabaran kami habis.",
            "Luar biasa ya komitmen ketepatan waktunya, meleset 2 minggu dan barangnya pun rusak. Sangat profesional sekali."
        ],
        "min_discount_demanded": 10.0,
        "requires_executive": False
    },
    {
        "type": "shrewd_negotiator",
        "label": "Distributor Utama Regional",
        "tone": "calculating",
        "color": "blue",
        "tolerance": 50,
        "sample_dialogs": [
            "Kami tetap ingin bermitra, tapi kelalaian ini merugikan operasional kami. Kami bersedia tidak memutus kontrak ASALKAN diberikan diskon kompensasi untuk pemesanan berikutnya dan tempo pembayaran diperpanjang.",
            "Masalah kualitas ini bisa kita selesaikan secara kekeluargaan bisnis. Berikan kami kompensasi unit ekstra dan prioritas pengiriman pertama, baru kami tutup komplain ini.",
            "Setiap kesalahan ada harganya dalam bisnis. Berikan penyesuaian komersial yang sepadan dan kami lupakan masalah batch cacat ini."
        ],
        "min_discount_demanded": 20.0,
        "requires_executive": True
    }
]

UNION_PERSONALITIES = [
    {
        "type": "bebal_militan",
        "rep_name": "Bambang Sukirman",
        "label": "Ketua Dewan Pengurus SP-Mandiri",
        "tolerance": "low",
        "speech": "Tuntutan kaum buruh mutlak dan tidak bisa ditawar! Kami minta kenaikan gaji pokok yang signifikan dan uang saku damai per orang yang sepadan! Kalau direksi pelit dan masa bodoh, mesin pabrik tidak akan pernah menyala lagi!",
        "min_wage_raise_accepted": 12.0,
        "min_bonus_accepted": 1500000.0,
        "rejection_speech": "Tawaran penghinaan macam apa ini?! Direksi makan enak buruh disuruh puasa! Negosiasi DITOLAK! Kami perpanjang mogok kerja!",
        "acceptance_speech": "Hidup Buruh! Karena direksi menunjukkan kepedulian nyata, kami instruksikan seluruh operator kembali ke stasiun kerja shift malam ini!"
    },
    {
        "type": "manut_kooperatif",
        "rep_name": "Agus Prasetyo",
        "label": "Koordinator Forum Komunikasi Pekerja Pabrik",
        "tolerance": "high",
        "speech": "Kami memahami kondisi kas perusahaan sedang diuji oleh krisis pasar. Asalkan ada sedikit perhatian untuk uang lembur dan uang saku darurat rekan-rekan, kawan-kawan buruh siap bekerja keras mengejar target produksi.",
        "min_wage_raise_accepted": 5.0,
        "min_bonus_accepted": 500000.0,
        "rejection_speech": "Mohon maaf Pak/Bu Direksi, setidaknya bantulah sedikit untuk makan rekan-rekan buruh. Naikkan sedikit lagi ya tawaran bonus atau upahnya.",
        "acceptance_speech": "Terima kasih banyak atas kebijaksanaan manajemen! Seluruh pekerja siap lembur malam ini memastikan pesanan selesai tepat waktu!"
    },
    {
        "type": "skeptikal_pragmatis",
        "rep_name": "Hendra Wijaya",
        "label": "Ketua Presidium Aliansi Buruh Bersatu",
        "tolerance": "medium",
        "speech": "Kami sudah kenyang janji manis manajemen di masa lalu. Kami hanya butuh komitmen riil: kenaikan upah yang terukur dan uang kompensasi langsung cair hari ini ke rekening, baru kami cabut blokade mesin.",
        "min_wage_raise_accepted": 8.0,
        "min_bonus_accepted": 1000000.0,
        "rejection_speech": "Janji lisan tidak cukup. Angka tawaran Anda di bawah kalkulasi kebutuhan riil. Tolong hitung ulang atau pabrik tetap tutup.",
        "acceptance_speech": "Sepakat. Hitam di atas putih ditandatangani. Blokade lini produksi resmi kami buka kembali."
    }
]

BLACK_SWAN_SHOCKS = [
    {
        "code": "BAD_DEBT",
        "title": "Gagal Bayar Piutang Konsumen (Customer Default)",
        "description": "Klien korporat 'PT Megatama Retail' resmi dinyatakan pailit oleh pengadilan niaga. Piutang usaha sebesar Rp 35.000.000 tidak tertagih dan harus dihapusbukukan langsung ke kerugian Laba Rugi!",
        "impact_type": "bad_debt",
        "amount": 35000000.0,
        "affected_accounts": ["1020 Piutang Usaha", "5010 Beban Kerugian Piutang Macet"]
    },
    {
        "code": "VENDOR_FRAUD",
        "title": "Vendor Bawa Kabur Uang Uang Muka (Vendor Abscondment)",
        "description": "Pemasok suku cadang 'CV Kilat Sentosa' dilaporkan menutup kantornya secara sepihak dan pemiliknya menghilang! Uang muka PO sebesar Rp 20.000.000 lenyap dan bahan baku gagal dikirim.",
        "impact_type": "cash_loss",
        "amount": 20000000.0,
        "affected_accounts": ["1010 Kas & Bank", "6030 Kerugian Non-Operasional Fraud"]
    },
    {
        "code": "BANK_RESTRUCTURE",
        "title": "Restrukturisasi & Pinalti Suku Bunga Pinjaman Bank",
        "description": "Karena rasio likuiditas kas perusahaan turun di bawah batas aman (Covenant Breach), bank rekanan menaikkan bunga cerukan dan membebankan pinalti administrasi sebesar Rp 15.000.000.",
        "impact_type": "bank_penalty",
        "amount": 15000000.0,
        "affected_accounts": ["1010 Kas & Bank", "6040 Beban Bunga & Finansial"]
    },
    {
        "code": "TAX_AUDIT",
        "title": "Pemeriksaan Pajak Mendadak (Surprise Tax Audit)",
        "description": "Kantor Pelayanan Pajak (KPP) menerbitkan Surat Ketetapan Pajak Kurang Bayar (SKPKB) terkait rekonsiliasi PPN masa lalu. Denda pajak sebesar Rp 12.500.000 langsung dipotong dari rekening kas.",
        "impact_type": "cash_loss",
        "amount": 12500000.0,
        "affected_accounts": ["1010 Kas & Bank", "6050 Denda Pajak"]
    }
]

# ==========================================
# 2. 20-SCENARIO MULTI-DOMAIN MATRIX
# ==========================================

SCENARIO_MATRIX: List[Dict[str, Any]] = [
    # ------------------ PURCHASING & SUPPLY CHAIN (4 Scenarios) ------------------
    {
        "id": "PUR-01",
        "domain": "purchasing",
        "domain_label": "Pengadaan & Rantai Pasok",
        "title": "Kelangkaan Chipset Global & Kenaikan Harga Vendor Utama",
        "context": "Pemasok utama komponen motherboard dan IC controller memberitahukan bahwa krisis rantai pasok global memicu lonjakan harga komponen sebesar 40%. Vendor menuntut penyesuaian harga kontrak atau mereka akan mengalihkan alokasi stok ke kompetitor dalam 48 jam.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Setujui Kenaikan Harga Vendor 40% & Kunci Stok Prioritas",
                "rationale": "Menjamin kelancaran lini produksi dan pengiriman pesanan tepat waktu tanpa downtime, namun menekan Margin Laba Kotor secara signifikan.",
                "immediate_cost": 45000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Jadwal produksi berjalan 100% normal tanpa downtime", "type": "positive"},
                    {"dept": "finance", "effect": "Margin laba kotor turun 18% dan kas keluar membengkak", "type": "negative"},
                    {"dept": "crm", "effect": "Kepuasan klien tetap aman karena pengiriman tepat waktu", "type": "positive"}
                ],
                "document": {
                    "type": "ADDENDUM_KONTRAK",
                    "title": "Addendum Kontrak No. 044/ADD-PUR/2026",
                    "recipient": "PT Global Micro Parts Indonesia",
                    "summary": "Perjanjian penyesuaian harga pengadaan IC Chipset sebesar +40% dengan jaminan Service Level Agreement (SLA) pasokan prioritas 14 hari kerja."
                },
                "cfo_verdict": "Likuiditas terbebani jangka pendek, tetapi menyelamatkan reputasi operasional dari denda wanprestasi pelanggan."
            },
            {
                "choice_id": "B",
                "label": "Tolak Kenaikan & Alihkan ke Pemasok Alternatif Tier-3 (Harga Murah, Kualitas Belum Teruji)",
                "rationale": "Menjaga HPP tetap rendah, tetapi berisiko tinggi terhadap tingkat cacat produk (scrap rate) dan potensi penolakan QC.",
                "immediate_cost": 15000000.0,
                "ripples": [
                    {"dept": "purchasing", "effect": "Penghematan HPP sebesar 25% dibandingkan vendor lama", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Risiko scrap & defect rate meningkat hingga 35%", "type": "negative"},
                    {"dept": "crm", "effect": "Potensi eskalasi komplain garansi dari pelanggan akhir", "type": "negative"}
                ],
                "document": {
                    "type": "PO_BARU",
                    "title": "Surat Penunjukan Vendor Pengadaan No. 102/SPV/2026",
                    "recipient": "CV Sinar Logam Makmur Abadi",
                    "summary": "Penerbitan PO darurat bahan baku chipset Tier-3 dengan klausul garansi penukaran komponen bermasalah dalam 7 hari."
                },
                "cfo_verdict": "Menjaga margin kertas, namun membuka liabilitas kontijensi biaya garansi dan risiko audit mutu."
            },
            {
                "choice_id": "C",
                "label": "Tunda Pengadaan & Pangkas Kapasitas Produksi 50% Sementara Waktu",
                "rationale": "Menghindari komitmen kas besar di tengah volatilitas, menunggu harga komoditas turun di kuartal berikutnya.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Arus kas jangka pendek aman dan terkendali", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Kapasitas menganggur (idle capacity) naik, beban tetap tetap berjalan", "type": "negative"},
                    {"dept": "crm", "effect": "Lead time pengiriman molor 3-4 minggu memicu ancaman penalti kontrak", "type": "negative"}
                ],
                "document": {
                    "type": "MEMO_DIREKSI",
                    "title": "Surat Edaran Direksi No. 018/DIR-OPS/2026",
                    "recipient": "Seluruh Kepala Departemen Operasional",
                    "summary": "Instruksi penyesuaian jadwal lini perakitan dan penundaan pembelian persediaan untuk preservasi rasio likuiditas kas."
                },
                "cfo_verdict": "Strategi defensif konservatif; cash flow aman namun market share berisiko tergerus oleh pesaing."
            }
        ]
    },
    {
        "id": "PUR-02",
        "domain": "purchasing",
        "domain_label": "Pengadaan & Rantai Pasok",
        "title": "Vendor Utama Bahan Baku Mengalami Kebakaran Gudang",
        "context": "Gudang sentral pemasok casing dan panel metalik terbakar habis semalam. Vendor meminta penangguhan pengiriman selama 6 minggu atau pembatalan kontrak sepihak.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Impor Darurat via Jalur Udara (Air Freight) dari Singapura dengan Biaya Premium",
                "rationale": "Bahan baku tiba dalam 3 hari, lini produksi tetap berjalan tanpa jeda, namun biaya logistik membengkak 3x lipat.",
                "immediate_cost": 38000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Produksi zero downtime, target output tercapai", "type": "positive"},
                    {"dept": "finance", "effect": "Beban logistik & freight ekspres menggerus laba bersih operasional", "type": "negative"}
                ],
                "document": {
                    "type": "AIR_FREIGHT_PO",
                    "title": "Surat Perjanjian Pengiriman Cepat No. 088/LOG-INT/2026",
                    "recipient": "Apex Express Cargo Singapore Pte Ltd",
                    "summary": "Kontrak kargo udara darurat untuk pengangkutan 500 unit plat metal cetak presisi tinggi."
                },
                "cfo_verdict": "Biaya tinggi namun mempertahankan SLA pelanggan institusional."
            },
            {
                "choice_id": "B",
                "label": "Gunakan Material Subtitusi Lokal dengan Spesifikasi Lebih Rendah",
                "rationale": "Harga tetap murah dan pasokan cepat didapat, namun tampilan estetika dan durabilitas produk menurun.",
                "immediate_cost": 8000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Pengeluaran kas minim dan terkendali", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Toleransi perakitan berkurang, butuh penyesuaian mal mesin", "type": "negative"},
                    {"dept": "crm", "effect": "Keluhan estetika dari klien segmen premium meningkat", "type": "negative"}
                ],
                "document": {
                    "type": "DEV_SPEC",
                    "title": "Berita Acara Deviasi Spesifikasi Material No. 014/QC-BA/2026",
                    "recipient": "Departemen Quality Control & Produksi",
                    "summary": "Persetujuan penggunaan material substitusi plat aluminium 1.2mm dengan toleransi deviasi visual 5%."
                },
                "cfo_verdict": "Solusi pragmatis hemat kas, awasi respon retur konsumen."
            }
        ]
    },
    {
        "id": "PUR-03",
        "domain": "purchasing",
        "domain_label": "Pengadaan & Rantai Pasok",
        "title": "Tawaran Diskon Kuantitas Besar (Bulk Buy) dengan Syarat Kas Tunai",
        "context": "Pemasok kabel dan resistor menawarkan diskon 30% jika perusahaan memesan stok untuk kebutuhan 6 bulan ke depan dan membayar tunai di muka (Cash on Order).",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Ambil Penawaran Bulk Buy & Bayar Tunai Rp 60.000.000",
                "rationale": "Mengunci HPP murah untuk 6 bulan ke depan, namun menguras modal kerja kas likuid perusahaan secara drastis.",
                "immediate_cost": 60000000.0,
                "ripples": [
                    {"dept": "purchasing", "effect": "Efisiensi biaya pembelian 30% (saving Rp 25.000.000)", "type": "positive"},
                    {"dept": "finance", "effect": "Rasio kas likuid (Cash Ratio) anjlok ke level rentan", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Gudang bahan baku penuh, beban sewa ruang tambahan", "type": "negative"}
                ],
                "document": {
                    "type": "KONTRAK_BULK",
                    "title": "Perjanjian Pembelian Grosir Strategis No. 201/PUR-BLK/2026",
                    "recipient": "PT Elektronika Sentra Pasifik",
                    "summary": "Pembelian partai besar komponen pasif dengan potongan harga 30% termin pembayaran Cash Before Delivery."
                },
                "cfo_verdict": "Hati-hati risiko likuiditas macet bila terjadi pengeluaran mendadak dalam 30 hari ke depan."
            },
            {
                "choice_id": "B",
                "label": "Tolak Tawaran & Tetap Menggunakan Metode Pengadaan Just-In-Time (JIT)",
                "rationale": "Menjaga fleksibilitas kas likuid dan menghindari risiko kerusakan persediaan di gudang.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Kas tetap fleksibel dan likuiditas harian terjaga", "type": "positive"},
                    {"dept": "purchasing", "effect": "Kehilangan peluang penghematan marjin jangka panjang", "type": "negative"}
                ],
                "document": {
                    "type": "MEMO_PUR",
                    "title": "Nota Dinas Penolakan Program Bulk No. 042/ND-PUR/2026",
                    "recipient": "Komite Manajemen Modal Kerja",
                    "summary": "Keputusan mempertahankan pola pengadaan bulanan sesuai fluktuasi demand dinamis."
                },
                "cfo_verdict": "Kebijakan kas yang bijak bagi perusahaan dengan buffer modal kerja terbatas."
            }
        ]
    },
    {
        "id": "PUR-04",
        "domain": "purchasing",
        "domain_label": "Pengadaan & Rantai Pasok",
        "title": "Temuan Praktik Gratifikasi / Kickback pada Tim Purchasing",
        "context": "Audit internal menemukan indikasi bahwa salah satu staf procurement senior menerima komisi rahasia dari vendor baut dan packaging dengan imbalan harga beli yang di-mark up 15%.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Pemutusan Hubungan Kerja (PHK) Seketika & Blacklist Vendor Terlibat",
                "rationale": "Tindakan tegas menegakkan Good Corporate Governance (GCG) dan menghentikan kebocoran anggaran jangka panjang.",
                "immediate_cost": 5000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Efek jera bagi karyawan lain, integritas tim meningkat", "type": "positive"},
                    {"dept": "purchasing", "effect": "Gangguan sementara proses pengadaan saat mencari vendor pengganti", "type": "negative"},
                    {"dept": "finance", "effect": "Harga pengadaan terkoreksi turun 15% ke harga wajar pasar", "type": "positive"}
                ],
                "document": {
                    "type": "SURAT_PHK_ETIK",
                    "title": "Surat Keputusan Direksi Pemecatan No. 091/SK-DIR/2026",
                    "recipient": "Departemen HR & Komite Etik Perusahaan",
                    "summary": "Pemberhentian tidak dengan hormat atas pelanggaran berat integritas dan surat pemberitahuan blacklist vendor."
                },
                "cfo_verdict": "Langkah governance yang tepat untuk menekan inefisiensi laten."
            },
            {
                "choice_id": "B",
                "label": "Beri Surat Peringatan III (SP3) & Negosiasi Ulang Kontrak Vendor",
                "rationale": "Menghindari kekosongan personel procurement di tengah masa puncak produksi sambil meminta vendor mengembalikan selisih harga.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "purchasing", "effect": "Operasional pengadaan tetap berjalan lancar tanpa jeda", "type": "positive"},
                    {"dept": "hr", "effect": "Moral kedisiplinan berisiko melemah karena sanksi dianggap lunak", "type": "negative"}
                ],
                "document": {
                    "type": "SP3_SURAT",
                    "title": "Surat Peringatan Terakhir (SP-3) No. 033/HR-SP/2026",
                    "recipient": "Staf Bagian Pembelian Terkait",
                    "summary": "Peringatan keras pelanggaran kode etik pengadaan dengan kewajiban pengawasan melekat oleh Internal Auditor."
                },
                "cfo_verdict": "Kompromi operasional; butuh pengawasan internal yang lebih ketat."
            }
        ]
    },

    # ------------------ MANUFACTURING & PRODUCTION (4 Scenarios) ------------------
    {
        "id": "MFG-01",
        "domain": "manufacturing",
        "domain_label": "Produksi & Kualitas",
        "title": "Kerusakan Fatal Mesin SMT (Surface Mount Technology) Utama",
        "context": "Mesin solder presisi tinggi mengalami korsleting panel inverter pada saat pesanan ekspor sedang dikerjakan. Lini produksi terhenti total.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Panggil Teknisi Khusus Luar Negeri & Overhaul Mesin Kilat (24 Jam Selesai)",
                "rationale": "Pabrik kembali beroperasi penuh dalam sehari, namun biaya jasa teknisi ekspres dan suku cadang orisinal sangat tinggi.",
                "immediate_cost": 28000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Lini produksi beroperasi kembali 100% dalam tempo 24 jam", "type": "positive"},
                    {"dept": "finance", "effect": "Beban pemeliharaan mesin langsung terdebet dari kas", "type": "negative"},
                    {"dept": "crm", "effect": "Komitmen delivery tetap tercapai tepat waktu", "type": "positive"}
                ],
                "document": {
                    "type": "WORK_ORDER_DARURAT",
                    "title": "Surat Perintah Kerja Perbaikan Mesin No. 511/MNT-WO/2026",
                    "recipient": "PT Siemens Industrial Solutions Indonesia",
                    "summary": "Perintah darurat overhaul inverter SMT Line #1 dengan garansi operasional 6 bulan."
                },
                "cfo_verdict": "Investasi tepat untuk mencegah kerugian penalti keterlambatan kontrak ekspor."
            },
            {
                "choice_id": "B",
                "label": "Sub-kontrakkan (Maklon) Pekerjaan SMT ke Pabrik Rekanan Mitra",
                "rationale": "Mengalihkan perakitan ke pabrik luar; tidak perlu biaya perbaikan besar di awal, tapi biaya per unit naik 20% dan risiko bocornya desain PCB.",
                "immediate_cost": 12000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Produksi berjalan via mitra dengan biaya variabel lebih tinggi", "type": "positive"},
                    {"dept": "finance", "effect": "Margin laba kotor tergerus 12% selama masa maklon", "type": "negative"},
                    {"dept": "purchasing", "effect": "Ketergantungan terhadap kapasitas pabrik eksternal", "type": "negative"}
                ],
                "document": {
                    "type": "KONTRAK_MAKLON",
                    "title": "Perjanjian Kerjasama Jasa Manufaktur No. 077/MKL-OPS/2026",
                    "recipient": "PT Cipta Elektronika Mandiri",
                    "summary": "Kontrak outsourcing perakitan SMT sebanyak 1.000 PCB dengan klausul kerahasiaan NDA."
                },
                "cfo_verdict": "Melindungi likuiditas kas belanja modal (Capex) dengan mengorbankan margin operasional (Opex)."
            },
            {
                "choice_id": "C",
                "label": "Gunakan Tenaga Manual Solder Tangan oleh Operator Pabrik (Jadwal Kerja Lembur)",
                "rationale": "Tanpa biaya mesin eksternal, namun kecepatan produksi melambat drastis dan tingkat cacat perakitan meningkat.",
                "immediate_cost": 4000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Kelelahan operator dan beban upah lembur lembur meningkat", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Defect rate solder manual naik 20%, bottleneck output", "type": "negative"},
                    {"dept": "finance", "effect": "Biaya kas keluar terendah di awal", "type": "positive"}
                ],
                "document": {
                    "type": "INSTRUKSI_MANUAL",
                    "title": "Standard Operating Procedure Penyesuaian Manual No. 021/SOP-MAN/2026",
                    "recipient": "Seluruh Supervisor Lini Perakitan",
                    "summary": "Prosedur darurat pengerjaan solder manual dua shift dengan pengawasan QC sampling intensif."
                },
                "cfo_verdict": "Sangat berisiko merusak reputasi kualitas produk di pasar akhir."
            }
        ]
    },
    {
        "id": "MFG-02",
        "domain": "manufacturing",
        "domain_label": "Produksi & Kualitas",
        "title": "Temuan Batch Produksi Cacat Lolos QC pada Tahap Packing",
        "context": "Tim quality control menemukan bahwa 200 unit produk jadi yang siap dikirim mengalami masalah firmware crashing setelah uji coba acak terakhir.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tahan Seluruh Pengiriman & Lakukan Rework Flashing Firmware 100%",
                "rationale": "Mencegah barang cacat sampai ke tangan pembeli, namun pengiriman tertunda 4 hari.",
                "immediate_cost": 6000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Klien terlindungi dari produk cacat, kepercayaan jangka panjang terjaga", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Lembur tim engineering untuk proses flashing ulang 200 unit", "type": "negative"},
                    {"dept": "finance", "effect": "Biaya rework tambahan sebesar Rp 6.000.000", "type": "negative"}
                ],
                "document": {
                    "type": "BA_REWORK",
                    "title": "Berita Acara Karantina & Pengerjaan Ulang No. 045/QC-RW/2026",
                    "recipient": "Departemen Quality Assurance & Logistik",
                    "summary": "Karantina batch produk nomor seri BATCH-202609 dan instruksi flashing patch firmware v2.1."
                },
                "cfo_verdict": "Langkah mitigasi risiko komplain dan retur yang jauh lebih mahal jika barang terlanjur beredar."
            },
            {
                "choice_id": "B",
                "label": "Kirim Sesuai Jadwal & Siapkan Patch OTA (Over-The-Air) Pasca Penjualan",
                "rationale": "Target pengiriman dan penagihan invoice invoice tepat waktu, namun pembeli awal mungkin mengalami kendala sesaat sebelum update.",
                "immediate_cost": 1500000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Faktur penjualan dapat segera dicairkan tanpa keterlambatan", "type": "positive"},
                    {"dept": "crm", "effect": "Beban customer support melonjak untuk panduan update pengguna", "type": "negative"}
                ],
                "document": {
                    "type": "RELEASE_NOTE",
                    "title": "Catatan Rilis Patch Firmware No. 089/ENG-REL/2026",
                    "recipient": "Tim Customer Service & Technical Support",
                    "summary": "Dokumentasi panduan update firmware pelanggan dan alur penanganan tiket kendala sistem."
                },
                "cfo_verdict": "Mengamankan arus kas penagihan, namun awasi rating kepuasan konsumen di marketplace."
            }
        ]
    },
    {
        "id": "MFG-03",
        "domain": "manufacturing",
        "domain_label": "Produksi & Kualitas",
        "title": "Optimalisasi Efisiensi Lean Manufacturing & Reduksi Pemborosan (Kaizen)",
        "context": "Konsultan industri menyarankan implementasi sistem 5S dan Poka-Yoke di lini perakitan untuk memangkas waktu siklus per unit sebesar 15%.",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Investasi Program Kaizen & Sertifikasi Lean Manufacturing",
                "rationale": "Meningkatkan kapasitas produksi jangka panjang dan mengurangi scrap rate secara permanen.",
                "immediate_cost": 18000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Efisiensi lini naik 15% dan defect rate berkurang signifikan", "type": "positive"},
                    {"dept": "finance", "effect": "Capex pelatihan & perombakan tata letak (layout) pabrik", "type": "negative"},
                    {"dept": "hr", "effect": "Keterampilan operator meningkat berkat sertifikasi resmi", "type": "positive"}
                ],
                "document": {
                    "type": "KONTRAK_KONSULTAN",
                    "title": "Perjanjian Program Transformasi Lean No. 012/LEAN-OPS/2026",
                    "recipient": "Indonesia Productivity & Quality Institute",
                    "summary": "Program pendampingan implementasi 5S, Standard Work, dan Value Stream Mapping selama 3 bulan."
                },
                "cfo_verdict": "Investasi modal intelektual yang menghasilkan ROI positif dalam siklus 2-3 periode."
            },
            {
                "choice_id": "B",
                "label": "Jalankan Efisiensi Internal Swakelola Tanpa Konsultan Luar",
                "rationale": "Hemat biaya anggaran kas, namun progres lambat karena keterbatasan kompetensi internal.",
                "immediate_cost": 2000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Penghematan anggaran jasa konsultasi", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Peningkatan efisiensi minim (hanya ~3-5%)", "type": "neutral"}
                ],
                "document": {
                    "type": "MEMO_INTERNAL",
                    "title": "Instruksi Gugus Kendali Mutu Mandiri No. 008/GKM/2026",
                    "recipient": "Seluruh Ketua Tim Kerja Pabrik",
                    "summary": "Pembentukan gugus kendali mutu internal untuk identifikasi titik pemborosan material."
                },
                "cfo_verdict": "Pendekatan low-cost yang konservatif."
            }
        ]
    },
    {
        "id": "MFG-04",
        "domain": "manufacturing",
        "domain_label": "Produksi & Kualitas",
        "title": "Audit Keselamatan Kerja & Standardisasi K3 Lingkungan Pabrik",
        "context": "Inspektur Dinas Tenaga Kerja menemukan kekurangan alat pelindung diri (APD) dan sistem ventilasi pembuangan timbal di ruang perakitan.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Modernisasi Sistem Ventilasi K3 & Lengkapi APD Standar Internasional",
                "rationale": "Menghilangkan risiko sanksi penyegelan pabrik dan meningkatkan moral keselamatan pekerja.",
                "immediate_cost": 16000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Tingkat absensi sakit pekerja menurun drastis, moral kerja naik", "type": "positive"},
                    {"dept": "finance", "effect": "Beban investasi kepatuhan regulasi lingkungan K3", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Lolos audit sertifikasi ISO 45001", "type": "positive"}
                ],
                "document": {
                    "type": "SERTIFIKASI_K3",
                    "title": "Laporan Pemenuhan Rekomendasi K3 No. 034/K3-DISNAKER/2026",
                    "recipient": "Dinas Tenaga Kerja dan Transmigrasi Provinsi",
                    "summary": "Bukti pemenuhan standar instalasi exhaust blower dan pengadaan APD lengkap bagi seluruh pekerja pabrik."
                },
                "cfo_verdict": "Kepatuhan hukum wajib untuk menghindari risiko penutupan paksa operasional."
            },
            {
                "choice_id": "B",
                "label": "Pengadaan APD Minimum Sekadar Memenuhi Syarat Administrasi",
                "rationale": "Biaya minimal dalam jangka pendek, namun rentan sanksi inspeksi ulang di masa depan.",
                "immediate_cost": 4500000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Pengeluaran kas minim", "type": "positive"},
                    {"dept": "hr", "effect": "Potensi tuntutan serikat buruh terkait kenyamanan kerja", "type": "negative"}
                ],
                "document": {
                    "type": "BERITA_ACARA_APD",
                    "title": "Tanda Terima Pengadaan APD Dasar No. 056/HR-APD/2026",
                    "recipient": "Pengawas K3 Internal Pabrik",
                    "summary": "Distribusi masker filter standar dan sarung tangan anti-statis tahap awal."
                },
                "cfo_verdict": "Menekan biaya jangka pendek dengan mempertahankan risiko audit berkelanjutan."
            }
        ]
    },

    # ------------------ CRM, SALES & CONTRACT COMPLAINTS (4 Scenarios) ------------------
    {
        "id": "CRM-01",
        "domain": "crm",
        "domain_label": "Hubungan Pelanggan & Komplain",
        "title": "Ancaman Somasi Hukum dari Klien Korporat Utama (PT Megatama)",
        "context": "Klien korporat terbesar melayangkan Surat Peringatan Hukum (Somasi) karena 35 unit mesin yang dikirim terlambat 10 hari dan mengalami kendala kalibrasi. Klien menuntut ganti rugi Rp 50.000.000 atau perkara dibawa ke Pengadilan Niaga.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tawarkan Kompensasi Diskon 15% Invoice & Kirim Tim Teknisi Onsite 24 Jam",
                "rationale": "Meredam amarah klien, menyelamatkan kontrak tahunan bernilai miliaran, dengan beban potongan harga yang terukur.",
                "immediate_cost": 22000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Somasi dicabut, kontrak tahunan tetap aman diperpanjang", "type": "positive"},
                    {"dept": "finance", "effect": "Pendapatan invoice terpangkas Rp 22.000.000", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Tim teknisi dikerahkan onsite selama 3 hari berturut-turut", "type": "negative"}
                ],
                "document": {
                    "type": "AKTA_PERDAMAIAN",
                    "title": "Akta Perjanjian Perdamaian Bipartit No. 019/LEG-CRM/2026",
                    "recipient": "Direksi PT Megatama Retailindo Tbk",
                    "summary": "Pencabutan somasi hukum dengan komitmen kredit nota potongan 15% dan dukungan teknisi onsite prioritas."
                },
                "cfo_verdict": "Biaya perdamaian jauh lebih murah daripada biaya pengacara dan hilangnya klien jangkar perusahaan."
            },
            {
                "choice_id": "B",
                "label": "Lawan Somasi via Kuasa Hukum Perusahaan Menggunakan Klausul Force Majeure",
                "rationale": "Menolak membayar ganti rugi dengan dasar keterlambatan vendor pihak ketiga, namun memicu perang litigasi di pengadilan.",
                "immediate_cost": 15000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Biaya jasa pengacara retain fee langsung dibayar", "type": "negative"},
                    {"dept": "crm", "effect": "Hubungan dengan klien korporat putus total, reputasi pasar tercoreng", "type": "negative"},
                    {"dept": "accounting", "effect": "Piutang berjalan macet dan berpotensi menjadi Bad Debt 100%", "type": "negative"}
                ],
                "document": {
                    "type": "JAWABAN_SOMASI",
                    "title": "Surat Tanggapan Somasi Hukum No. 099/LEG-LAW/2026",
                    "recipient": "Kantor Advokat & Konsultan Hukum Siregar & Partners",
                    "summary": "Penolakan klaim ganti rugi wanprestasi berdasarkan klausul pembatasan tanggung jawab dalam Kontrak Induk Pengadaan."
                },
                "cfo_verdict": "Risiko reputasi dan kerugian piutang macet yang sangat destruktif bagi neraca keuangan."
            },
            {
                "choice_id": "C",
                "label": "Tawarkan Penggantian Unit Baru Utuh (Full Replacement) Tanpa Diskon Kas",
                "rationale": "Menjaga nilai invoice tetap utuh dengan membebankan biaya produksi unit pengganti ke HPP.",
                "immediate_cost": 18000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Klien puas dengan unit baru, komplain dinyatakan selesai", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Antrean produksi diselak untuk membuat 35 unit pengganti", "type": "negative"},
                    {"dept": "finance", "effect": "Beban HPP membengkak, namun nilai piutang utuh tertagih", "type": "positive"}
                ],
                "document": {
                    "type": "SURAT_PENGGANTIAN",
                    "title": "Berita Acara Penukaran Barang No. 063/BA-RETUR/2026",
                    "recipient": "General Manager Procurement PT Megatama Retailindo",
                    "summary": "Pengiriman 35 unit baru produk pengganti dengan garansi purna jual diperpanjang menjadi 24 bulan."
                },
                "cfo_verdict": "Solusi win-win yang menjaga nilai penjualan kotor tetap tercatat tinggi di laporan Laba Rugi."
            }
        ]
    },
    {
        "id": "CRM-02",
        "domain": "crm",
        "domain_label": "Hubungan Pelanggan & Komplain",
        "title": "Peluang Tender Pengadaan Pemerintah (E-Katalog B2G)",
        "context": "Kementerian Pendidikan membuka tender pengadaan perangkat lab senilai Rp 300.000.000 dengan syarat jaminan pelaksanaan (Bank Guarantee) dan sertifikasi TKDN minimal 40%.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Ikuti Tender Penuh: Beli Bank Guarantee & Sertifikasi TKDN Kilat",
                "rationale": "Peluang memenangkan kontrak jumbo dengan margin menarik, namun membutuhkan komitmen kas jaminan bank.",
                "immediate_cost": 25000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Lolos verifikasi teknis tender proyek pemerintah Rp 300 Juta", "type": "positive"},
                    {"dept": "finance", "effect": "Kas diblokir sementara untuk jaminan tender (Collateral)", "type": "negative"}
                ],
                "document": {
                    "type": "DOKUMEN_TENDER",
                    "title": "Pakta Integritas & Dokumen Penawaran Tender No. 003/TND-DIKTI/2026",
                    "recipient": "Pokja Pemilihan Pengadaan Barang/Jasa Kemendikbudristek",
                    "summary": "Pengajuan dokumen teknis penawaran tender e-katalog dilengkapi jaminan bank garansi senilai 5% nilai kontrak."
                },
                "cfo_verdict": "Langkah ekspansi pendapatan strategis; pastikan buffer kas harian tetap aman dari risiko lock up."
            },
            {
                "choice_id": "B",
                "label": "Bermitra Konsorsium (KSO) dengan Distributor Resmi Pemilik TKDN",
                "rationale": "Tanpa biaya sertifikasi mahal, berbagi margin 30% dengan mitra konsorsium.",
                "immediate_cost": 5000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Mengikuti tender dengan profil risiko finansial lebih ringan", "type": "positive"},
                    {"dept": "finance", "effect": "Margin keuntungan proyek dibagi dua dengan mitra KSO", "type": "neutral"}
                ],
                "document": {
                    "type": "PERJANJIAN_KSO",
                    "title": "Perjanjian Kerjasama Operasional (KSO) No. 028/KSO-GOV/2026",
                    "recipient": "PT Graha Rekayasa Nusantara",
                    "summary": "Kesepakatan pembagian lingkup kerja dan bagi hasil pengadaan perangkat laboratorium e-katalog."
                },
                "cfo_verdict": "Pilihan cerdas untuk mengincar volume besar tanpa membebani neraca modal sendiri."
            }
        ]
    },
    {
        "id": "CRM-03",
        "domain": "crm",
        "domain_label": "Hubungan Pelanggan & Komplain",
        "title": "Distributor Utama Meminta Perpanjangan Tempo Pembayaran (TOP 90 Hari)",
        "context": "Distributor terbesar yang menyerap 45% penjualan perusahaan meminta perpanjangan jangka waktu pembayaran (Term of Payment) dari 30 hari menjadi 90 hari karena perlambatan penjualan retail.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tolak Permintaan & Pertahankan Batas Kredit Ketat Maksimal 30 Hari",
                "rationale": "Mencegah penumpukan piutang macet (DSO membengkak), namun berisiko distributor mengurangi volume pesanan sebesar 30%.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Arus kas penagihan tetap stabil dan Days Sales Outstanding (DSO) rendah", "type": "positive"},
                    {"dept": "crm", "effect": "Distributor mengancam memindahkan sebagian kuota ke kompetitor", "type": "negative"}
                ],
                "document": {
                    "type": "SURAT_KEBIJAKAN_KREDIT",
                    "title": "Pemberitahuan Kebijakan Batas Kredit Usaha No. 017/FIN-CR/2026",
                    "recipient": "Direktur Keuangan PT Distribusi Mega Niaga",
                    "summary": "Penetapan batasan plafon kredit maksimum Rp 50.000.000 dengan tenor pembayaran tetap 30 hari kalender."
                },
                "cfo_verdict": "Sangat baik untuk menjaga Cash Conversion Cycle (CCC) tidak jebol."
            },
            {
                "choice_id": "B",
                "label": "Setujui TOP 90 Hari dengan Syarat Jaminan Bilyet Giro Mundur & Biaya Bunga 2%",
                "rationale": "Menjaga loyalitas distributor sambil melindungi risiko gagal bayar dengan instrumen perbankan.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "crm", "effect": "Distributor tetap memesan dalam volume maksimal", "type": "positive"},
                    {"dept": "finance", "effect": "Pendapatan bunga tambahan, namun piutang tertahan lebih lama di neraca", "type": "neutral"}
                ],
                "document": {
                    "type": "ADDENDUM_KREDIT",
                    "title": "Addendum Perjanjian Fasilitas Kredit No. 062/ADD-TOP/2026",
                    "recipient": "PT Distribusi Mega Niaga",
                    "summary": "Persetujuan perpanjangan tenor TOP 90 hari dengan kewajiban penyerahan Bilyet Giro tertanggal mundur."
                },
                "cfo_verdict": "Kompromi komersial yang aman secara hukum selama instrumen Giro sudah divalidasi bank."
            }
        ]
    },
    {
        "id": "CRM-04",
        "domain": "crm",
        "domain_label": "Hubungan Pelanggan & Komplain",
        "title": "Peluncuran Program Loyalitas & Insentif Rebate Tahunan Mitra",
        "context": "Asosiasi dealer menuntut program insentif akhir tahun (Year-End Rebate) untuk mendorong penjualan produk VLab menjelang tutup buku tahunan.",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Luncurkan Skema Rebate Berjenjang (Tiered Cashback) Berbasis Target Omzet",
                "rationale": "Memicu lonjakan pesanan borongan di akhir periode, dibayar setelah target penjualan tercapai.",
                "immediate_cost": 15000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Volume penjualan melonjak 28% dalam waktu 30 hari", "type": "positive"},
                    {"dept": "finance", "effect": "Pencadangan beban insentif penjualan pada laporan laba rugi", "type": "neutral"}
                ],
                "document": {
                    "type": "SK_REBATE",
                    "title": "Skema Insentif & Program Rebate Penjualan No. 041/MKT-REB/2026",
                    "recipient": "Seluruh Jaringan Agen & Reseller Resmi",
                    "summary": "Program insentif cashback berjenjang hingga 5% untuk pencapaian omzet penjualan di atas target kuartal."
                },
                "cfo_verdict": "Strategi ekspansi top-line yang terbukti efektif menaikkan omzet bersih."
            },
            {
                "choice_id": "B",
                "label": "Tidak Menerapkan Program Rebate Kas (Fokus Promosi Digital B2C)",
                "rationale": "Menghemat kas perusahaan dan mengalihkan dana promosi ke iklan media sosial langsung ke pengguna akhir.",
                "immediate_cost": 5000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Beban kas lebih hemat dan terkontrol", "type": "positive"},
                    {"dept": "crm", "effect": "Brand awareness konsumen naik, namun antusiasme reseller datar", "type": "neutral"}
                ],
                "document": {
                    "type": "RENCANA_IKLAN",
                    "title": "Alokasi Rencana Belanja Promosi Digital No. 077/MKT-DIG/2026",
                    "recipient": "Tim Digital Marketing & Media",
                    "summary": "Penetapan anggaran kampanye iklan berbayar di kanal digital dan marketplace."
                },
                "cfo_verdict": "Opsi konservatif menjaga laba operasional tetap stabil."
            }
        ]
    },

    # ------------------ HR & LABOR UNION CRISIS (4 Scenarios) ------------------
    {
        "id": "HR-01",
        "domain": "hr",
        "domain_label": "Ketenagakerjaan & Serikat Buruh",
        "title": "Mogok Kerja Massal Serikat Buruh (Tuntutan Upah Lembur & Bonus Shift)",
        "context": "Serikat Pekerja Mandiri menginstruksikan 40 pekerja pabrik melakukan aksi mogok kerja dan memblokir pintu akses lini perakitan. Mereka menuntut kenaikan upah pokok 12% dan uang saku damai Rp 1.500.000 per orang.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Capai Kesepakatan Bipartit: Beri Bonus Produktivitas & Naikkan Upah Pokok 7%",
                "rationale": "Blokade pabrik langsung dicabut dalam hitungan jam, produksi malam segera beroperasi normal.",
                "immediate_cost": 24000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Pabrik kembali beroperasi 100%, bottleneck selesai", "type": "positive"},
                    {"dept": "hr", "effect": "Moral dan loyalitas buruh meningkat pesat pasca kesepakatan", "type": "positive"},
                    {"dept": "finance", "effect": "Beban gaji bulanan tetap (Fixed Labor Cost) naik permanen 7%", "type": "negative"}
                ],
                "document": {
                    "type": "PERJANJIAN_BIPARTIT",
                    "title": "Perjanjian Bersama Bipartit No. 008/BIP-DISNAKER/2026",
                    "recipient": "Ketua Dewan Pengurus Serikat Pekerja Mandiri",
                    "summary": "Kesepakatan pengakhiran aksi mogok kerja, penyesuaian skala upah 7%, dan bonus insentif target output."
                },
                "cfo_verdict": "Menghentikan pendarahan kerugian downtime harian yang bisa menelan Rp 15 Juta per hari jika pabrik mangkrak."
            },
            {
                "choice_id": "B",
                "label": "Tolak Tuntutan, Nyatakan Mogok Tidak Sah & Rekrut Pekerja Outsourcing Pengganti",
                "rationale": "Menolak kenaikan biaya tetap gaji, namun memicu konflik hukum ketenagakerjaan dan penurunan efisiensi pekerja baru.",
                "immediate_cost": 16000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Eskalasi perselisihan ke Pengadilan Hubungan Industrial (PHI)", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Pekerja baru butuh waktu training 2 minggu, defect rate naik 15%", "type": "negative"},
                    {"dept": "finance", "effect": "Biaya rekrutmen outsourcing dan jasa hukum meningkat", "type": "negative"}
                ],
                "document": {
                    "type": "SURAT_PERINGATAN_BURUH",
                    "title": "Surat Peringatan & Pernyataan Mogok Kerja Tidak Sah No. 044/HR-DIR/2026",
                    "recipient": "Pengurus Serikat Pekerja & Dinas Tenaga Kerja Kota",
                    "summary": "Pemberitahuan sanksi disipliner atas mangkir kerja tanpa izin dan pemanggilan kembali dalam tempo 2x24 jam."
                },
                "cfo_verdict": "Sangat mahal dalam jangka menengah akibat inefisiensi kurva belajar pekerja baru."
            },
            {
                "choice_id": "C",
                "label": "Tawarkan Kompensasi Uang Saku Tunai Sekali Bayar (One-Off) Tanpa Kenaikan Gaji Pokok",
                "rationale": "Melindungi struktur beban tetap bulanan di neraca jangka panjang dengan pengeluaran tunai sekali bayar.",
                "immediate_cost": 12000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Struktur beban upah pokok bulanan tidak berubah naik", "type": "positive"},
                    {"dept": "hr", "effect": "Serikat buruh menerima bersyarat, tensi mereda sementara", "type": "neutral"},
                    {"dept": "manufacturing", "effect": "Pabrik beroperasi kembali esok hari", "type": "positive"}
                ],
                "document": {
                    "type": "NOTA_KESEPAHAMAN",
                    "title": "Nota Kesepahaman Bantuan Kesejahteraan Pekerja No. 029/MOU-HR/2026",
                    "recipient": "Perwakilan Karyawan Lini Produksi",
                    "summary": "Pemberian dana bantuan kesejahteraan transisi tunai sekali bayar untuk seluruh operator terdaftar."
                },
                "cfo_verdict": "Pilihan taktis cerdas seorang CFO untuk menghindari kenaikan fixed overhead cost permanen."
            }
        ]
    },
    {
        "id": "HR-02",
        "domain": "hr",
        "domain_label": "Ketenagakerjaan & Serikat Buruh",
        "title": "Pembajakan (Poaching) Kepala Engineer Litbang oleh Kompetitor Utama",
        "context": "Lead Hardware Engineer dan dua teknisi kunci menerima tawaran kerja dari kompetitor multinasional dengan tawaran kenaikan gaji 40%. Mereka memegang formula desain produk generasi terbaru.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tawarkan Counter-Offer: Kenaikan Gaji 25% + Bonus Retensi Loyalitas",
                "rationale": "Mempertahankan talenta kunci dan kerahasiaan kekayaan intelektual (IP) produk generasi berikutnya.",
                "immediate_cost": 15000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Tim inti R&D bertahan 100%, stabilitas riset produk terjamin", "type": "positive"},
                    {"dept": "finance", "effect": "Kenaikan beban gaji divisi engineering di Laba Rugi", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Proyek inovasi produk baru selesai sesuai roadmap", "type": "positive"}
                ],
                "document": {
                    "type": "RETENTION_AGREEMENT",
                    "title": "Perjanjian Retensi Talenta Kunci & Non-Disclosure No. 051/HR-RET/2026",
                    "recipient": "Kepala Divisi Riset & Pengembangan",
                    "summary": "Pemberian paket retensi loyalitas kerja 2 tahun disertai klausul Non-Compete dan Non-Disclosure Agreement ketat."
                },
                "cfo_verdict": "Melindungi asset tak berwujud (Intangible Asset / Intellectual Property) yang krusial bagi masa depan bisnis."
            },
            {
                "choice_id": "B",
                "label": "Lepas Karyawan & Tuntut Penerapan Klausul Non-Compete Agreement (NCA)",
                "rationale": "Menghemat kas beban gaji dan menuntut mantan karyawan secara hukum jika membocorkan rahasia dagang.",
                "immediate_cost": 4000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Kekosongan posisi kunci, butuh waktu rekrutmen 2-3 bulan", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Pengembangan produk baru mengalami penundaan (delay)", "type": "negative"},
                    {"dept": "finance", "effect": "Penghematan beban kompensasi gaji jangka pendek", "type": "positive"}
                ],
                "document": {
                    "type": "SURAT_PERINGATAN_NCA",
                    "title": "Peringatan Kepatuhan Perjanjian Non-Kompensasi Rahasia Dagang No. 082/LEG-NCA/2026",
                    "recipient": "Mantan Staf Divisi Engineering",
                    "summary": "Pemberitahuan kewajiban pembatasan bekerja pada entitas kompetitor langsung selama periode 12 bulan."
                },
                "cfo_verdict": "Menghemat kas bulanan namun mengorbankan kecepatan inovasi teknologi perusahaan."
            }
        ]
    },
    {
        "id": "HR-03",
        "domain": "hr",
        "domain_label": "Ketenagakerjaan & Serikat Buruh",
        "title": "Program Upskilling Digital & Otomasi Robotik Tenaga Kerja Pabrik",
        "context": "Manajemen merencanakan otomatisasi lini packing yang akan menggantikan 10 posisi manual. Manajemen harus memutuskan nasib 10 pekerja tersebut.",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Lakukan Pelatihan Alih Keterampilan (Reskilling) Menjadi Operator QC Robotik",
                "rationale": "Tanpa pemecatan buruh, moral pekerja terjaga tinggi, produktivitas pabrik meningkat berlipat.",
                "immediate_cost": 14000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Zero layoff, reputasi perusahaan sebagai Best Employer naik", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Kapasitas lini packing naik 40% setelah otomasi", "type": "positive"},
                    {"dept": "finance", "effect": "Beban investasi modul pelatihan teknologi", "type": "negative"}
                ],
                "document": {
                    "type": "PROGRAM_PELATIHAN",
                    "title": "Surat Keputusan Program Alih Kompetensi Karyawan No. 035/SK-RESKILL/2026",
                    "recipient": "Departemen HR & 10 Karyawan Divisi Perakitan",
                    "summary": "Program sertifikasi pengoperasian sistem kontrol otomatisasi perakitan dan jaminan status kepegawaian tetap."
                },
                "cfo_verdict": "Investasi human capital yang menaikkan produktivitas output per tenaga kerja secara permanen."
            },
            {
                "choice_id": "B",
                "label": "Program Pensiun Dini Sukarela (Golden Shakehand) dengan Pesangon Penuh",
                "rationale": "Memangkas jumlah tenaga kerja secara permanen dan menurunkan beban gaji bulanan di masa depan.",
                "immediate_cost": 35000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Pengeluaran kas pesangon besar di awal, namun hemat gaji di periode berikutnya", "type": "neutral"},
                    {"dept": "manufacturing", "effect": "Otomasi berjalan penuh tanpa beban headcount berlebih", "type": "positive"}
                ],
                "document": {
                    "type": "PERJANJIAN_PESANGON",
                    "title": "Perjanjian Pengakhiran Hubungan Kerja Sukarela No. 066/PHK-GOLD/2026",
                    "recipient": "Departemen Tenaga Kerja & Rekening Karyawan",
                    "summary": "Penyelesaian hak pesangon pensiun dini sukarela 10 karyawan sesuai regulasi ketenagakerjaan yang berlaku."
                },
                "cfo_verdict": "Tinggi di pengeluaran kas awal, namun mempercantik Operating Margin pada periode-periode berikutnya."
            }
        ]
    },
    {
        "id": "HR-04",
        "domain": "hr",
        "domain_label": "Ketenagakerjaan & Serikat Buruh",
        "title": "Kecelakaan Kerja di Area Pergudangan (Forklift Incident)",
        "context": "Sebuah forklift menabrak rak penyimpanan akibat rem aus, melukai seorang staf gudang dan merusak persediaan senilai Rp 8.000.000.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tanggung Penuh Biaya Pengobatan VIP, Santunan & Perbaiki Sistem Pergudangan",
                "rationale": "Menunjukkan tanggung jawab penuh perusahaan, menjaga keharmonisan hubungan kerja, dan audit kelayakan armada gudang.",
                "immediate_cost": 12000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Solidaritas dan kepercayaan karyawan terhadap manajemen sangat tinggi", "type": "positive"},
                    {"dept": "finance", "effect": "Beban santunan medis dan perbaikan rak gudang", "type": "negative"},
                    {"dept": "purchasing", "effect": "Pemeriksaan total kelayakan seluruh armada forklift", "type": "positive"}
                ],
                "document": {
                    "type": "BA_INSIDEN_K3",
                    "title": "Laporan Penanganan Kecelakaan Kerja No. 011/K3-MED/2026",
                    "recipient": "BPJS Ketenagakerjaan & Keluarga Karyawan",
                    "summary": "Pertanggungjawaban penanganan medis menyeluruh dan evaluasi kelayakan peralatan material handling."
                },
                "cfo_verdict": "Penanganan krisis yang bertanggung jawab untuk melindungi stabilitas sosial internal perusahaan."
            },
            {
                "choice_id": "B",
                "label": "Klaim Santunan Melalui BPJS Ketenagakerjaan Saja Sesuai Batas Minimum",
                "rationale": "Mengandalkan asuransi wajib untuk meminimalkan beban kas langsung perusahaan.",
                "immediate_cost": 2000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Pengeluaran kas langsung perusahaan sangat minim", "type": "positive"},
                    {"dept": "hr", "effect": "Keluarga korban dan serikat buruh mempertanyakan kepedulian moril manajemen", "type": "negative"}
                ],
                "document": {
                    "type": "KLAIM_BPJS",
                    "title": "Formulir Pengajuan Klaim Jaminan Kecelakaan Kerja No. 048/BPJS-JKK/2026",
                    "recipient": "Kantor Cabang BPJS Ketenagakerjaan",
                    "summary": "Pengajuan manfaat jaminan kecelakaan kerja sesuai pagu standar pertanggungan."
                },
                "cfo_verdict": "Menjaga efisiensi kas jangka pendek namun dapat menurunkan employee engagement."
            }
        ]
    },

    # ------------------ ACCOUNTING, TAX & FINANCIAL STRATEGY (4 Scenarios) ------------------
    {
        "id": "ACC-01",
        "domain": "accounting",
        "domain_label": "Akuntansi & Keuangan Strategis",
        "title": "Pemeriksaan Pajak Mendadak (Surat Ketetapan Pajak Kurang Bayar - SKPKB)",
        "context": "Kantor Pelayanan Pajak (KPP) menerbitkan SKPKB atas ketidaksesuaian faktur pajak masukan 2 tahun lalu senilai Rp 25.000.000. Perusahaan diberi waktu 14 hari untuk melunasi atau mengajukan surat keberatan resmi.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Bayar Lunas SKPKB Rp 25.000.000 & Tutup Pemeriksaan Pajak Segera",
                "rationale": "Menghilangkan risiko sanksi bunga denda berjalan 2% per bulan dan menjaga reputasi kepatuhan pajak.",
                "immediate_cost": 25000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Kas langsung terpotong Rp 25.000.000 untuk setor kas negara", "type": "negative"},
                    {"dept": "accounting", "effect": "Buku pajak dinyatakan Clean & Clear oleh otoritas fiskus", "type": "positive"}
                ],
                "document": {
                    "type": "SKPKB_LUNAS",
                    "title": "Surat Setoran Pajak (SSP) & Pelunasan SKPKB No. 082/SSP-KPP/2026",
                    "recipient": "Kantor Pelayanan Pajak Pratama",
                    "summary": "Bukti penyetoran pelunasan ketetapan pajak kurang bayar ke kas negara melalui Bank Persepsi."
                },
                "cfo_verdict": "Menghilangkan risiko kontinjensi denda membengkak; pastikan cash runway setelah pembayaran masih di atas 60 hari."
            },
            {
                "choice_id": "B",
                "label": "Sewa Konsultan Pajak & Ajukan Surat Keberatan Resmi ke Kanwil Pajak",
                "rationale": "Menunda kewajiban pembayaran pokok sambil memperjuangkan pengurangan pokok denda hingga 70%.",
                "immediate_cost": 8000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Hemat kas saat ini, hanya bayar jasa konsultan pajak", "type": "positive"},
                    {"dept": "accounting", "effect": "Proses sengketa pajak memakan waktu 6-12 bulan", "type": "neutral"}
                ],
                "document": {
                    "type": "SURAT_KEBERATAN_PAJAK",
                    "title": "Surat Pengajuan Keberatan Atas SKPKB No. 015/TAX-KEB/2026",
                    "recipient": "Kepala Kantor Wilayah Direktorat Jenderal Pajak",
                    "summary": "Pengajuan banding keberatan perpajakan dengan bukti lampiran rekonsiliasi faktur pajak elektronik."
                },
                "cfo_verdict": "Langkah cerdas bila data pembukuan internal kita kuat dan teruji di mata hukum."
            }
        ]
    },
    {
        "id": "ACC-02",
        "domain": "accounting",
        "domain_label": "Akuntansi & Keuangan Strategis",
        "title": "Pilihan Kebijakan Penyusutan Aset Tetap (Garis Lurus vs Saldo Menurun)",
        "context": "Manajemen baru saja membeli mesin produksi senilai Rp 100.000.000. Tim akuntansi meminta penetapan metode depresiasi: Straight Line (Garis Lurus) atau Double Declining Balance (Saldo Menurun Ganda).",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Gunakan Metode Saldo Menurun Ganda (Depresiasi Cepat / Tax Shield di Awal)",
                "rationale": "Beban penyusutan besar di tahun pertama memperkecil Laba Kena Pajak (Tax Shield), menghemat kas pajak riil perusahaan.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "accounting", "effect": "Penghematan pajak penghasilan riil (Cash Tax Savings)", "type": "positive"},
                    {"dept": "finance", "effect": "Laba bersih di laporan keuangan tampak lebih rendah di tahun awal", "type": "neutral"}
                ],
                "document": {
                    "type": "KEBIJAKAN_AKUNTANSI",
                    "title": "Surat Keputusan Kebijakan Depresiasi Aset Tetap No. 004/SK-ACC/2026",
                    "recipient": "Departemen Keuangan & Auditor Eksternal",
                    "summary": "Penetapan metode depresiasi Double Declining Balance untuk kelompok mesin teknologi tinggi."
                },
                "cfo_verdict": "Strategi keuangan klasik untuk memaksimalkan arus kas operasi via Tax Shield."
            },
            {
                "choice_id": "B",
                "label": "Gunakan Metode Garis Lurus (Straight Line Method)",
                "rationale": "Beban penyusutan merata setiap tahun, menjaga stabilitas laba bersih yang dilaporkan kepada pemegang saham.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "accounting", "effect": "Pencatatan pembukuan sederhana dan stabil antar periode", "type": "positive"},
                    {"dept": "finance", "effect": "Laba bersih stabil, namun tidak ada manfaat percepatan penghematan pajak", "type": "neutral"}
                ],
                "document": {
                    "type": "KEBIJAKAN_AKUNTANSI",
                    "title": "Surat Keputusan Kebijakan Depresiasi Garis Lurus No. 005/SK-ACC/2026",
                    "recipient": "Departemen Keuangan & Auditor Eksternal",
                    "summary": "Penetapan metode depresiasi garis lurus dengan masa manfaat 5 tahun tanpa nilai residu."
                },
                "cfo_verdict": "Pilihan standar industri untuk stabilitas laba komersial."
            }
        ]
    },
    {
        "id": "ACC-03",
        "domain": "accounting",
        "domain_label": "Akuntansi & Keuangan Strategis",
        "title": "Peringatan Likuiditas Bank & Ancaman Pelanggaran Covenant Pinjaman (Covenant Breach)",
        "context": "Bank mitra mengirimkan surat peringatan bahwa rasio lancar (Current Ratio) perusahaan turun mendekati batas minimum 1.2x. Jika terlanggar, bank berhak mengenakan pinalti bunga 3% dan menuntut pelunasan dipercepat.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Lakukan Restrukturisasi Utang Bank & Tambah Modal Disetor Pemegang Saham",
                "rationale": "Menyuntikkan kas segar ekuitas dan menegosiasikan perpanjangan tenor fasilitas kredit dengan bank.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Current Ratio kembali aman di atas 1.8x, ancaman wanprestasi bank gugur", "type": "positive"},
                    {"dept": "accounting", "effect": "Penambahan pos Modal Saham Disetor di bagian Ekuitas Neraca", "type": "positive"}
                ],
                "document": {
                    "type": "ADDENDUM_KREDIT_BANK",
                    "title": "Addendum Perjanjian Kredit & Restrukturisasi No. 093/BNK-REST/2026",
                    "recipient": "Divisi Corporate Banking Bank Mandiri (Persero) Tbk",
                    "summary": "Penyelarasan rasio covenant keuangan dan komitmen penambahan modal disetor pemegang saham pengendali."
                },
                "cfo_verdict": "Keputusan penyelamatan solvency paling solid untuk menjamin kelangsungan usaha (Going Concern)."
            },
            {
                "choice_id": "B",
                "label": "Likuidasi Cepat Persediaan Lambat Bergerak (Slow-Moving Inventory) dengan Diskon 40%",
                "rationale": "Mengonversi stok mati di gudang menjadi kas tunai seketika untuk memperbaiki rasio kas.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Inflow kas segar masuk seketika dari obral stok", "type": "positive"},
                    {"dept": "accounting", "effect": "Pencatatan kerugian diskon persediaan pada Laba Rugi", "type": "negative"},
                    {"dept": "purchasing", "effect": "Kapasitas ruang gudang kembali lapang", "type": "positive"}
                ],
                "document": {
                    "type": "PROGRAM_CLEARANCE",
                    "title": "Surat Program Cuci Gudang Likuidasi Persediaan No. 049/SLS-CLR/2026",
                    "recipient": "Distributor & Pedagang Grosir Komponen",
                    "summary": "Penjualan borongan persediaan lambat bergerak dengan potongan harga likuidasi tunai."
                },
                "cfo_verdict": "Langkah taktis membebaskan kas yang terperangkap dalam bentuk barang mati."
            }
        ]
    },
    {
        "id": "ACC-04",
        "domain": "accounting",
        "domain_label": "Akuntansi & Keuangan Strategis",
        "title": "Peluang Investasi Ekspansi Fasilitas Perakitan Baru (Capex Decision)",
        "context": "Direksi mempertimbangkan pembelian mesin lini produksi otomatis senilai Rp 80.000.000 dengan proyeksi pengembalian investasi (Payback Period) selama 14 bulan.",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Danai Investasi dengan Kombinasi Kas Internal 50% & Leasing Finansial 50%",
                "rationale": "Membagi beban pendanaan agar tidak menguras kas operasional harian secara berlebihan.",
                "immediate_cost": 40000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Kapasitas produksi pabrik melonjak 60% dalam 2 bulan", "type": "positive"},
                    {"dept": "finance", "effect": "Liabilitas sewa pembiayaan (Leasing) tercatat di neraca", "type": "neutral"},
                    {"dept": "accounting", "effect": "Aset tetap bertambah Rp 80.000.000", "type": "positive"}
                ],
                "document": {
                    "type": "KONTRAK_LEASING",
                    "title": "Perjanjian Sewa Pembiayaan Fasilitas Mesin No. 018/LSG-FIN/2026",
                    "recipient": "PT ORIX Indonesia Finance",
                    "summary": "Fasilitas pembiayaan investasi mesin perakitan otomatis dengan skema sewa guna usaha berbunga kompetitif."
                },
                "cfo_verdict": "Struktur permodalan yang seimbang antara Debt vs Equity untuk mendanai pertumbuhan."
            },
            {
                "choice_id": "B",
                "label": "Tunda Investasi Ekspansi & Fokus Memaksimalkan Utilitas Mesin yang Ada",
                "rationale": "Menghindari komitmen utang baru di tengah ketidakpastian iklim suku bunga makro.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Posisi kas dan neraca tetap konservatif tanpa utang baru", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Kapasitas produksi tetap di batas saat ini", "type": "neutral"}
                ],
                "document": {
                    "type": "MEMO_CAPEX",
                    "title": "Notulen Rapat Komite Investasi Modal No. 009/CAPEX-MGT/2026",
                    "recipient": "Dewan Komisaris & Direksi",
                    "summary": "Penundaan realisasi belanja modal ekspansi untuk prioritas konsolidasi likuiditas kas."
                },
                "cfo_verdict": "Pilihan bijak jika proyeksi demand pasar ke depan belum stabil."
            }
        ]
    }
]

# ==========================================
# 3. HELPER FUNCTIONS FOR SELECTION
# ==========================================

def get_scenario_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
    for sc in SCENARIO_MATRIX:
        if sc["id"] == scenario_id:
            return sc
    return None

def get_all_scenarios_matrix() -> List[Dict[str, Any]]:
    return SCENARIO_MATRIX

def get_random_customer_temperament(seed_id: int = None) -> Dict[str, Any]:
    if seed_id is not None:
        idx = seed_id % len(CUSTOMER_TEMPERAMENTS)
        item = CUSTOMER_TEMPERAMENTS[idx].copy()
    else:
        item = random.choice(CUSTOMER_TEMPERAMENTS).copy()
    item["dialog"] = random.choice(item["sample_dialogs"])
    return item

def get_union_leader_for_company(company_id: int) -> Dict[str, Any]:
    idx = company_id % len(UNION_PERSONALITIES)
    return UNION_PERSONALITIES[idx]

def trigger_random_black_swan() -> Dict[str, Any]:
    return random.choice(BLACK_SWAN_SHOCKS)

# ==========================================
# 4. ACTION RIPPLES ENGINE (Cross-Dept Causality)
# ==========================================

def calculate_action_ripples(
    company_id: int,
    action_type: str,
    action_payload: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Computes cross-departmental impacts when user takes routine ERP actions.
    Returns structured domino consequence objects for UI toast & analytics.
    """
    ripples = []
    summary = ""
    severity = "info"

    if action_type == "PURCHASE_ORDER_APPROVED":
        total_amount = float(action_payload.get("total_amount", 0.0))
        ripples = [
            {"dept": "Purchasing", "effect": f"Pesanan Bahan Baku senilai Rp {total_amount:,.0f} disetujui", "type": "positive"},
            {"dept": "Finance", "effect": f"Komitmen Kas keluar Rp {total_amount:,.0f} dijadwalkan pada jatuh tempo AP", "type": "negative"},
            {"dept": "Manufacturing", "effect": "Jadwal MRP otomatis sinkron, bahan baku siap dialokasikan ke Work Center", "type": "positive"},
            {"dept": "Warehouse", "effect": "Penerimaan barang (Goods Receipt) dijadwalkan masuk sistem pergudangan", "type": "neutral"}
        ]
        summary = f"PO Approved: Bahan baku masuk alur MRP, kewajiban AP kas Rp {total_amount:,.0f} tercatat."
        severity = "success"

    elif action_type == "PRODUCTION_BATCH_COMPLETED":
        qty = action_payload.get("quantity", 0)
        product_name = action_payload.get("product_name", "Produk Jadi")
        ripples = [
            {"dept": "Manufacturing", "effect": f"Batch {qty} unit {product_name} selesai diproduksi", "type": "positive"},
            {"dept": "Warehouse", "effect": f"Persediaan barang jadi (FG) bertambah +{qty} unit", "type": "positive"},
            {"dept": "Purchasing", "effect": f"Stok bahan baku (BOM) otomatis terpotong sesuai rasio perakitan", "type": "neutral"},
            {"dept": "Accounting", "effect": "Jurnal mutasi persediaan Bahan Baku (WIP) ke Barang Jadi terbentuk", "type": "positive"}
        ]
        summary = f"Produksi Selesai: +{qty} {product_name} masuk gudang, HPP manufaktur dikapitalisasi."
        severity = "success"

    elif action_type == "HR_WAGE_INCREASE":
        percentage = action_payload.get("raise_percentage", 5.0)
        ripples = [
            {"dept": "HR", "effect": f"Kenaikan upah +{percentage}% disepakati, moral pekerja meningkat pesat", "type": "positive"},
            {"dept": "Manufacturing", "effect": "Efisiensi lini produksi naik +10%, risiko mogok kerja turun ke 0%", "type": "positive"},
            {"dept": "Finance", "effect": f"Beban gaji bulanan tetap (Fixed Overhead) naik permanen", "type": "negative"}
        ]
        summary = f"Kesepakatan Buruh: Upah naik +{percentage}%, produktivitas pabrik pulih 100%."
        severity = "success"

    elif action_type == "CRM_DISCOUNT_APPROVED":
        discount = action_payload.get("discount_percentage", 10.0)
        ripples = [
            {"dept": "CRM", "effect": f"Diskon kompensasi {discount}% disetujui, somasi/komplain pelanggan dicabut", "type": "positive"},
            {"dept": "Finance", "effect": f"Pendapatan invoice berkurang {discount}%, margin laba kotor terkoreksi", "type": "negative"},
            {"dept": "Accounting", "effect": "Credit Note diterbitkan untuk memotong saldo piutang pelanggan", "type": "neutral"}
        ]
        summary = f"Komplain Selesai: Diskon {discount}% diberikan, kontrak jangka panjang pelanggan terselamatkan."
        severity = "warning"

    elif action_type == "TAX_SETTLEMENT":
        amount = float(action_payload.get("amount", 0.0))
        ripples = [
            {"dept": "Accounting", "effect": f"Pelunasan SKPKB Pajak Rp {amount:,.0f} sukses disetor ke kas negara", "type": "positive"},
            {"dept": "Finance", "effect": f"Kas likuid terpotong seketika Rp {amount:,.0f}", "type": "negative"},
            {"dept": "Executive", "effect": "Status audit fiskal dinyatakan 'Kepatuhan Pajak Baik (Good Tax Standing)'", "type": "positive"}
        ]
        summary = f"Pajak Lunas: SKPKB Rp {amount:,.0f} terbayar, sengketa perpajakan ditutup resmi."
        severity = "info"

    else:
        ripples = [
            {"dept": "General Operations", "effect": f"Aksi sistem '{action_type}' diproses", "type": "neutral"}
        ]
        summary = f"Aksi '{action_type}' berhasil dicatat ke sistem ERP."

    return {
        "action_type": action_type,
        "company_id": company_id,
        "timestamp": datetime.now().isoformat(),
        "severity": severity,
        "summary": summary,
        "ripples": ripples
    }

# ==========================================
# 5. SCENARIO BRANCH EXECUTION ENGINE
# ==========================================

def execute_scenario_branch(
    company_id: int,
    scenario_id: str,
    choice_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Executes a branching decision, applies financial/operational mutations,
    persists a CompanyStoryEvent, and returns comprehensive outcome data.
    """
    scenario = get_scenario_by_id(scenario_id)
    if not scenario:
        raise ValueError(f"Skenario ID '{scenario_id}' tidak ditemukan.")

    selected_branch = None
    for b in scenario["branches"]:
        if b["choice_id"] == choice_id:
            selected_branch = b
            break

    if not selected_branch:
        raise ValueError(f"Pilihan cabang '{choice_id}' tidak valid untuk skenario {scenario_id}.")

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"Company ID {company_id} tidak ditemukan.")

    # Check if this scenario has already been decided for this company
    existing_event = (
        db.query(CompanyStoryEvent)
        .filter(
            CompanyStoryEvent.company_id == company_id,
            CompanyStoryEvent.title.like(f"[{scenario_id}]%")
        )
        .first()
    )
    if existing_event:
        raise ValueError(f"Skenario [{scenario_id}] sudah memiliki keputusan resmi yang mengikat ({existing_event.decision_taken}) dan tidak dapat diganti sepihak.")

    cost = float(selected_branch.get("immediate_cost", 0.0))

    # 1. Mutate Company and SimulationState
    if cost > 0:
        company.current_cash = max(0.0, float(company.current_cash or 0.0) - cost)
        db.add(company)

    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if state:
        if cost > 0:
            state.cash = max(0.0, state.cash - cost)
            state.expenses += cost
            state.net_profit -= cost * 0.4
        
        # Domain-specific operational ripples
        dom = scenario.get("domain", "")
        if dom == "purchasing":
            if choice_id == "A":
                state.supplier_health = min(100.0, state.supplier_health + 12.0)
                # Boost raw material stock
                raw_prod = db.query(Product).filter(Product.company_id == company_id, Product.product_type == "raw_material").first()
                if raw_prod:
                    raw_prod.current_stock += 50
            elif choice_id == "B":
                state.supplier_health = max(30.0, state.supplier_health - 15.0)
                # Increase vendor defect rate
                v_obj = db.query(Vendor).filter(Vendor.company_id == company_id).first()
                if v_obj:
                    v_obj.defect_rate = min(15.0, v_obj.defect_rate + 3.5)
            elif choice_id == "C":
                state.csat_score = max(30.0, state.csat_score - 10.0)

        elif dom == "manufacturing":
            if choice_id == "A":
                state.machine_health = min(100.0, state.machine_health + 20.0)
                wc_obj = db.query(WorkCenter).filter(WorkCenter.company_id == company_id).first()
                if wc_obj:
                    wc_obj.status = "operational"
                    wc_obj.failure_rate = max(1.0, wc_obj.failure_rate - 2.5)
            elif choice_id == "B":
                state.machine_health = max(40.0, state.machine_health - 10.0)
            elif choice_id == "C":
                fg_prod = db.query(Product).filter(Product.company_id == company_id, Product.product_type == "finished_good").first()
                if fg_prod:
                    fg_prod.current_stock += 30

        elif dom == "crm":
            if choice_id == "A":
                state.csat_score = min(100.0, state.csat_score + 15.0)
                state.revenue += 45000000.0
            elif choice_id == "B":
                state.csat_score = min(100.0, state.csat_score + 8.0)
            elif choice_id == "C":
                state.csat_score = max(20.0, state.csat_score - 25.0)

        elif dom == "hr":
            if choice_id == "A":
                state.worker_morale = min(100.0, state.worker_morale + 18.0)
                state.is_strike_active = False
                # Update employee salaries
                for emp in db.query(Employee).filter(Employee.company_id == company_id).all():
                    emp.monthly_salary = float(emp.monthly_salary) * 1.05
            elif choice_id == "B":
                state.worker_morale = min(100.0, state.worker_morale + 5.0)
            elif choice_id == "C":
                state.worker_morale = max(25.0, state.worker_morale - 25.0)
                state.is_strike_active = True
                state.strike_reason = "Tuntutan kenaikan upah lembur ditolak oleh manajemen."

        elif dom == "accounting":
            if choice_id == "A":
                state.overall_score = min(100.0, state.overall_score + 5.0)
            elif choice_id == "B":
                state.cash = min(999999999.0, state.cash + 25000000.0)
                company.current_cash = state.cash

        # Update Cash Account 1001 in General Ledger
        cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1001").first()
        if cash_acc:
            cash_acc.balance = state.cash

    # 2. Persist CompanyStoryEvent
    event = CompanyStoryEvent(
        company_id=company.id,
        round_number=state.current_round if state else 1,
        period_name=state.period_name if state else "Periode Berjalan",
        domain=scenario["domain"],
        event_type="scenario_branch",
        title=f"[{scenario['id']}] {scenario['title']}",
        description=f"Keputusan: {selected_branch['label']}. {selected_branch['rationale']}",
        decision_taken=f"Pilihan {selected_branch['choice_id']}: {selected_branch['label']}",
        ripple_summary=json.dumps(selected_branch.get("ripples", [])),
        document_data=json.dumps(selected_branch.get("document", None)) if selected_branch.get("document") else None,
        created_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "event_id": event.id,
        "company_id": company.id,
        "company_name": company.name,
        "scenario_id": scenario["id"],
        "scenario_title": scenario["title"],
        "domain": scenario["domain"],
        "choice_id": selected_branch["choice_id"],
        "choice_label": selected_branch["label"],
        "rationale": selected_branch["rationale"],
        "cost_incurred": cost,
        "remaining_cash": float(state.cash if state else company.current_cash or 0.0),
        "ripples": selected_branch.get("ripples", []),
        "document": selected_branch.get("document", None),
        "cfo_verdict": selected_branch.get("cfo_verdict", ""),
        "executed_at": event.created_at.isoformat()
    }

# ==========================================
# 6. SMART DETERMINISTIC CFO DIAGNOSTICS
# ==========================================

def run_smart_cfo_diagnostics(company_id: int, db: Session) -> Dict[str, Any]:
    """
    Pure Python deterministic CFO financial analysis:
    - Working Capital Analysis (Current Ratio, Quick Ratio, Cash Ratio)
    - DuPont Analysis (ROE = Net Profit Margin x Asset Turnover x Equity Multiplier)
    - Altman Z-Score for private/manufacturing firms
    - Qualitative Risk Flags & Pedagogical Lecturer Recommendations
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"Company ID {company_id} tidak ditemukan.")

    cash = float(company.current_cash or 0.0)

    # Calculate Accounts Receivable (Piutang) from Sales invoices or journals
    # Default baseline simulation values if ledger is fresh
    receivables = 25000000.0
    inventory_value = 45000000.0
    fixed_assets = 120000000.0
    
    current_liabilities = 35000000.0
    long_term_debt = 40000000.0
    
    total_revenue = 180000000.0
    cogs = 95000000.0
    operating_expenses = 35000000.0
    
    gross_profit = total_revenue - cogs
    operating_profit = gross_profit - operating_expenses
    tax_rate = 0.11
    net_income = max(1000000.0, operating_profit * (1 - tax_rate))

    current_assets = cash + receivables + inventory_value
    total_assets = current_assets + fixed_assets
    total_liabilities = current_liabilities + long_term_debt
    total_equity = max(10000000.0, total_assets - total_liabilities)

    # 1. Liquidity & Working Capital Ratios
    working_capital = current_assets - current_liabilities
    current_ratio = round(current_assets / max(1.0, current_liabilities), 2)
    quick_ratio = round((cash + receivables) / max(1.0, current_liabilities), 2)
    cash_ratio = round(cash / max(1.0, current_liabilities), 2)

    # 2. DuPont Analysis
    # ROE = (Net Income / Revenue) * (Revenue / Total Assets) * (Total Assets / Equity)
    profit_margin = round((net_income / max(1.0, total_revenue)) * 100, 2)
    asset_turnover = round(total_revenue / max(1.0, total_assets), 2)
    equity_multiplier = round(total_assets / max(1.0, total_equity), 2)
    roe = round((net_income / max(1.0, total_equity)) * 100, 2)
    roa = round((net_income / max(1.0, total_assets)) * 100, 2)

    # 3. Altman Z-Score for Emerging Markets / Private Manufacturing
    # Z' = 0.717(X1) + 0.847(X2) + 3.107(X3) + 0.420(X4) + 0.998(X5)
    # X1 = Working Capital / Total Assets
    # X2 = Retained Earnings / Total Assets (approx 0.15)
    # X3 = EBIT / Total Assets
    # X4 = Book Value Equity / Total Liabilities
    # X5 = Sales / Total Assets
    x1 = working_capital / max(1.0, total_assets)
    x2 = (total_equity * 0.3) / max(1.0, total_assets)
    x3 = operating_profit / max(1.0, total_assets)
    x4 = total_equity / max(1.0, total_liabilities)
    x5 = total_revenue / max(1.0, total_assets)

    z_score = round(
        (0.717 * x1) + (0.847 * x2) + (3.107 * x3) + (0.420 * x4) + (0.998 * x5),
        2
    )

    if z_score >= 2.9:
        z_status = "SAFE ZONE (Sehat)"
        z_color = "emerald"
    elif z_score >= 1.23:
        z_status = "GREY ZONE (Waspada)"
        z_color = "amber"
    else:
        z_status = "DISTRESS ZONE (Bahaya Kebangkrutan)"
        z_color = "rose"

    # 4. Strategic Recommendations & Risk Flags
    risk_flags = []
    recommendations = []

    if cash_ratio < 0.5:
        risk_flags.append({
            "code": "CASH_CRUNCH",
            "title": "Rasio Kas Rendah (Likuiditas Rentan)",
            "detail": f"Cash Ratio saat ini {cash_ratio}x (standar aman > 0.5x). Rentan terhadap pengeluaran tak terduga."
        })
        recommendations.append("Percepat penagihan piutang pelanggan (AR Collection) dan tunda pengeluaran belanja modal non-kritis.")

    if current_ratio < 1.3:
        risk_flags.append({
            "code": "WORKING_CAP_PRESSURE",
            "title": "Tekanan Modal Kerja Jangka Pendek",
            "detail": f"Current Ratio {current_ratio}x mendekati batas minimum covenant perbankan (1.2x)."
        })
        recommendations.append("Negosiasikan perpanjangan tenor utang dagang (AP) ke pemasok bahan baku.")

    if roe > 15:
        recommendations.append("Kinerja efisiensi ekuitas (ROE) sangat baik; pertahankan perputaran persediaan di tingkat optimal.")
    else:
        recommendations.append("Tingkatkan Asset Turnover dengan menggenjot volume penjualan barang jadi tanpa menambah utang baru.")

    if not risk_flags:
        risk_flags.append({
            "code": "OPTIMAL_HEALTH",
            "title": "Fundamental Keuangan Prima",
            "detail": "Seluruh rasio likuiditas, solvabilitas, dan profitabilitas berada dalam rentang standar industri yang sangat sehat."
        })

    # Recent story decisions made by this company
    recent_events = (
        db.query(CompanyStoryEvent)
        .filter(CompanyStoryEvent.company_id == company.id)
        .order_by(CompanyStoryEvent.created_at.desc())
        .limit(5)
        .all()
    )

    event_history = []
    for ev in recent_events:
        doc_parsed = None
        if ev.document_data:
            try:
                doc_parsed = json.loads(ev.document_data) if isinstance(ev.document_data, str) else ev.document_data
            except Exception:
                doc_parsed = None
        
        event_history.append({
            "id": ev.id,
            "title": ev.title,
            "domain": ev.domain,
            "decision_taken": ev.decision_taken,
            "description": ev.description,
            "document": doc_parsed,
            "executed_at": ev.created_at.isoformat()
        })

    return {
        "company_id": company.id,
        "company_name": company.name,
        "as_of_date": datetime.now().strftime("%d %B %Y"),
        "balance_sheet_summary": {
            "cash": cash,
            "receivables": receivables,
            "inventory": inventory_value,
            "fixed_assets": fixed_assets,
            "total_assets": total_assets,
            "current_liabilities": current_liabilities,
            "long_term_debt": long_term_debt,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "working_capital": working_capital
        },
        "income_statement_summary": {
            "total_revenue": total_revenue,
            "cogs": cogs,
            "gross_profit": gross_profit,
            "operating_expenses": operating_expenses,
            "operating_profit": operating_profit,
            "net_income": net_income
        },
        "ratios": {
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "cash_ratio": cash_ratio,
            "gross_margin_pct": round((gross_profit / total_revenue) * 100, 2),
            "operating_margin_pct": round((operating_profit / total_revenue) * 100, 2),
            "net_profit_margin_pct": profit_margin,
            "asset_turnover": asset_turnover,
            "equity_multiplier": equity_multiplier,
            "return_on_assets_pct": roa,
            "return_on_equity_pct": roe
        },
        "altman_z_score": {
            "score": z_score,
            "status": z_status,
            "color": z_color,
            "interpretation": "Model prediksi kesehatan finansial Altman Z-Score untuk manufaktur swasta."
        },
        "risk_flags": risk_flags,
        "cfo_recommendations": recommendations,
        "event_history": event_history
    }

```
