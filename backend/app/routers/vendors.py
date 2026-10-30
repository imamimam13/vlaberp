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

