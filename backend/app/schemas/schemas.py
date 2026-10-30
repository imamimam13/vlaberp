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
