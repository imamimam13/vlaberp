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
