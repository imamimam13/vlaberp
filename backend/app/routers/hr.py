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
