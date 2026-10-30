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
