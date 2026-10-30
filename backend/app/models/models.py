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


