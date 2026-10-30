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
