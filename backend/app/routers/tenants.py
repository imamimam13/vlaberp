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

