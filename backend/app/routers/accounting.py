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

