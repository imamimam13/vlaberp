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

