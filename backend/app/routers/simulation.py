import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database import get_db
from backend.app.models.models import (
    SimulationState, SimulationSlider, ScenarioCase, Company, ClassSession,
    WorkCenter, Account, Employee, CRMLead, Product, PurchaseOrder, PurchaseOrderItem,
    Vendor, DepartmentBudget, SalesOrder, SalesOrderItem, WorkOrder,
    JournalEntry, JournalItem, Customer, MarketingCampaign, CompanyStoryEvent
)
from backend.app.schemas.schemas import (
    SimulationStateOut, SimulationSliderOut, SimulationSliderUpdate,
    ScenarioCaseOut, SolveCaseRequest
)
from backend.app.services.behavior_engine import (
    get_all_scenarios_matrix, get_scenario_by_id,
    calculate_action_ripples, execute_scenario_branch,
    run_smart_cfo_diagnostics, get_random_customer_temperament,
    get_union_leader_for_company, trigger_random_black_swan
)
from backend.app.services.tenant_service import (
    _apply_scenario_mutation, SCENARIO_INITIAL_MUTATIONS
)


router = APIRouter(prefix="/simulation", tags=["simulation"])

class CreateCaseRequest(BaseModel):
    session_id: int
    company_id: Optional[int] = None
    code: str
    stage_order: int
    title: str
    category: str
    description: str
    trigger_hint: Optional[str] = None
    solvable_workflow: str
    resolution_criteria: str

class UpdateCaseRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    trigger_hint: Optional[str] = None
    solvable_workflow: Optional[str] = None
    resolution_criteria: Optional[str] = None
    status: Optional[str] = None

# --- CRUD SCENARIO CASES (Dosen Management) ---
@router.post("/cases", response_model=ScenarioCaseOut)
def create_case(payload: CreateCaseRequest, db: Session = Depends(get_db)):
    new_case = ScenarioCase(
        session_id=payload.session_id,
        company_id=payload.company_id,
        code=payload.code,
        stage_order=payload.stage_order,
        title=payload.title,
        category=payload.category,
        description=payload.description,
        trigger_hint=payload.trigger_hint,
        solvable_workflow=payload.solvable_workflow,
        resolution_criteria=payload.resolution_criteria,
        status="pending",
        resolution_score=0.0
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

@router.put("/cases/{case_id}", response_model=ScenarioCaseOut)
def update_case(case_id: int, payload: UpdateCaseRequest, db: Session = Depends(get_db)):
    case = db.query(ScenarioCase).filter(ScenarioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    
    if payload.title is not None: case.title = payload.title
    if payload.category is not None: case.category = payload.category
    if payload.description is not None: case.description = payload.description
    if payload.trigger_hint is not None: case.trigger_hint = payload.trigger_hint
    if payload.solvable_workflow is not None: case.solvable_workflow = payload.solvable_workflow
    if payload.resolution_criteria is not None: case.resolution_criteria = payload.resolution_criteria
    if payload.status is not None: case.status = payload.status

    db.commit()
    db.refresh(case)
    return case

@router.delete("/cases/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(ScenarioCase).filter(ScenarioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    db.delete(case)
    db.commit()
    return {"status": "success", "message": f"Kasus {case.code} berhasil dihapus"}

# --- SIMULATION STATE & SLIDERS ---
@router.get("/state/{company_id}", response_model=SimulationStateOut)
def get_simulation_state(company_id: int, db: Session = Depends(get_db)):
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="Status simulasi perusahaan tidak ditemukan")
    return state

@router.get("/sliders/{company_id}", response_model=SimulationSliderOut)
def get_sliders(company_id: int, db: Session = Depends(get_db)):
    slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == company_id).first()
    if not slider:
        slider = SimulationSlider(company_id=company_id)
        db.add(slider)
        db.commit()
        db.refresh(slider)
    return slider

@router.put("/sliders/{company_id}", response_model=SimulationSliderOut)
def update_sliders(company_id: int, payload: SimulationSliderUpdate, db: Session = Depends(get_db)):
    slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == company_id).first()
    if not slider:
        slider = SimulationSlider(company_id=company_id)
        db.add(slider)
    
    slider.supply_disruption = payload.supply_disruption
    slider.machine_breakdown_risk = payload.machine_breakdown_risk
    slider.market_volatility = payload.market_volatility
    slider.labor_strike_risk = payload.labor_strike_risk
    slider.bad_debt_risk = payload.bad_debt_risk
    slider.competitor_price_war = payload.competitor_price_war
    slider.is_company_override = True

    # Adjust company metrics dynamically based on slider values
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if state:
        if payload.machine_breakdown_risk >= 60.0:
            wc = db.query(WorkCenter).filter(WorkCenter.company_id == company_id).first()
            if wc and wc.status == "operational":
                wc.status = "breakdown"
                state.machine_health = max(20.0, state.machine_health - 35.0)

        if payload.labor_strike_risk >= 70.0:
            state.is_strike_active = True
            state.strike_reason = "Tuntutan kenaikan upah lembur & UMR dari serikat buruh"
            state.worker_morale = max(25.0, state.worker_morale - 40.0)

    db.commit()
    db.refresh(slider)
    return slider

@router.put("/sliders/session/{session_id}")
def update_sliders_session(session_id: int, payload: SimulationSliderUpdate, db: Session = Depends(get_db)):
    companies = db.query(Company).filter(Company.session_id == session_id).all()
    if not companies:
        raise HTTPException(status_code=404, detail="Tidak ada perusahaan pada sesi kelas ini")

    for comp in companies:
        slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == comp.id).first()
        if not slider:
            slider = SimulationSlider(company_id=comp.id)
            db.add(slider)

        slider.supply_disruption = payload.supply_disruption
        slider.machine_breakdown_risk = payload.machine_breakdown_risk
        slider.market_volatility = payload.market_volatility
        slider.labor_strike_risk = payload.labor_strike_risk
        slider.bad_debt_risk = payload.bad_debt_risk
        slider.competitor_price_war = payload.competitor_price_war
        slider.is_company_override = True

        state = db.query(SimulationState).filter(SimulationState.company_id == comp.id).first()
        if state:
            if payload.machine_breakdown_risk >= 60.0:
                wc = db.query(WorkCenter).filter(WorkCenter.company_id == comp.id).first()
                if wc and wc.status == "operational":
                    wc.status = "breakdown"
                    state.machine_health = max(20.0, state.machine_health - 35.0)

            if payload.labor_strike_risk >= 70.0:
                state.is_strike_active = True
                state.strike_reason = "Tuntutan kenaikan upah lembur & UMR dari serikat buruh"
                state.worker_morale = max(25.0, state.worker_morale - 40.0)

    db.commit()
    return {
        "status": "success",
        "message": f"Parameter simulasi berhasil diterapkan serentak ke {len(companies)} kelompok pada sesi kelas {session_id}!",
        "affected_companies": len(companies)
    }


@router.get("/cases/{company_id}", response_model=List[ScenarioCaseOut])
def get_cases(company_id: int, db: Session = Depends(get_db)):
    return db.query(ScenarioCase).filter(
        (ScenarioCase.company_id == company_id) | (ScenarioCase.company_id == None)
    ).order_by(ScenarioCase.stage_order.asc()).all()

# --- DYNAMIC STEP-BY-STEP SCORING & FACT SHEET EVALUATOR (NO HARDCODING) ---
@router.post("/cases/{case_id}/solve")
def solve_case(case_id: int, payload: SolveCaseRequest, db: Session = Depends(get_db)):
    case = db.query(ScenarioCase).filter(ScenarioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    company_id = case.company_id
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    step_scores = []
    total_score = 0.0
    passed = True
    fact_sheet = {}

    # DYNAMIC EVALUATION PER MISSION CATEGORY
    cat = (case.category or "").lower()
    
    if cat in ["procurement", "purchasing", "scm"]:
        # 1. Check vendor selection from actual POs
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id).all()
        has_bad_vendor_po = False
        for po in pos:
            vendor = db.query(Vendor).filter(Vendor.id == po.vendor_id).first()
            if vendor and vendor.defect_rate > 5.0:
                has_bad_vendor_po = True

        # Step 1: Due Diligence
        s1_max = 30
        s1_score = 30 if len(pos) > 0 else 15
        step_scores.append({"step": "Due Diligence & Analisis Data Historis Vendor", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        # Step 2: Quality Supplier Selection (Defect < 2%)
        s2_max = 40
        s2_score = 15 if has_bad_vendor_po else 38
        step_scores.append({"step": "Pemilihan Pemasok Berkualitas Rendah Defect (< 2%)", "max_score": s2_max, "earned_score": s2_score, "status": "failed" if has_bad_vendor_po else "passed"})

        # Step 3: Stock Buffer Fulfillment
        raw_products = db.query(Product).filter(Product.company_id == company_id, Product.product_type == "raw_material").all()
        sufficient_stocks = [p for p in raw_products if p.current_stock >= p.min_safety_stock]
        stock_ratio = (len(sufficient_stocks) / len(raw_products)) if raw_products else 1.0
        s3_max = 30
        s3_score = int(30 * stock_ratio)
        step_scores.append({"step": "Pemenuhan Batas Minimum Safety Stock Gudang", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 20 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0) and not has_bad_vendor_po

        fact_sheet = {
            "root_cause": "Godaan harga murah menyembunyikan risiko cacat bahan baku tinggi yang dapat merusak mesin perakitan SMT.",
            "student_actions_taken": f"Menerbitkan {len(pos)} PO. Terpilih vendor cacat tinggi: {'Ya' if has_bad_vendor_po else 'Tidak'}. Safety stock tercapai: {int(stock_ratio*100)}%.",
            "why_evaluation": "Berhasil memilih vendor dengan kualifikasi andal dan menjaga kontinuitas persediaan." if passed else "Mahasiswa tergoda diskon vendor murah (CV Mitra Bahari) dengan tingkat cacat 8.8% yang memicu risiko gagal produksi.",
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Prioritaskan PT Surya Logam Presisi / Apex Micro Components (Zero Defect).\n2. Opsi Dual-Sourcing: 70% vendor grade-1 + 30% buffer suplier lokal.\n3. Pertahankan stok di atas safety stock minimal 40 unit.",
            "key_takeaway": "Total Cost of Ownership (TCO) jauh lebih penting daripada sekadar harga beli termurah di invoice."
        }

    elif cat in ["crm", "marketing", "sales"]:
        # Check complaint lead resolution
        complaints = db.query(CRMLead).filter(CRMLead.company_id == company_id, CRMLead.is_complaint == True).all()
        resolved_complaint = next((c for c in complaints if c.stage == "won" or c.resolution_action), None)
        complaint = resolved_complaint or (complaints[0] if complaints else None)
        
        is_replaced = complaint and complaint.stage == "won"
        csat_current = state.csat_score if state else 80.0

        s1_max = 30
        s1_score = 30 if complaint and complaint.resolution_action else 10
        step_scores.append({"step": "Kecepatan Respon & Penanganan Tiket Darurat Akun VIP", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        s2_max = 40
        s2_score = 40 if is_replaced else (20 if complaint and complaint.stage == "proposition" else 5)
        step_scores.append({"step": "Eksekusi Mitigasi Kompensasi yang Memuaskan Konsumen", "max_score": s2_max, "earned_score": s2_score, "status": "passed" if s2_score >= 30 else "failed"})

        s3_max = 30
        s3_score = int(min(30, (csat_current / 100.0) * 30))
        step_scores.append({"step": "Pemulihan Indeks CSAT & Penyelamatan Kontrak", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 22 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0)

        action_taken = complaint.resolution_action if complaint and complaint.resolution_action else "Belum ada tindakan mitigasi"
        if passed:
            if "Addendum Diskon" in action_taken:
                why_eval = "Keputusan Manajerial Brilian! Negosiasi mediasi direksi berhasil mempertahankan kontrak Rp 150M sekaligus mengamankan arus kas dan stok gudang tanpa pemotongan fisik."
            elif "Penggantian" in action_taken or "Ganti" in action_taken:
                why_eval = "SOP Customer-First Berhasil! Menjalankan penggantian 15 unit fisik mengembalikan kepercayaan penuh klien VIP dan menyelamatkan kontrak jangka panjang."
            elif "Servis" in action_taken or "Audit" in action_taken:
                why_eval = "Investigasi Pragmatis! Layanan teknisi lapangan menyelesaikan keluhan dan memberikan data forensik untuk menuntut ganti rugi ke vendor bahan baku cacat."
            else:
                why_eval = "Keluhan pelanggan VIP ditangani secara elegan sehingga loyalitas dan kontrak pulih."
        else:
            why_eval = "Penanganan keluhan lambat, gantung, atau tidak memberikan kompensasi riil sehingga klien memutus kontrak dan CSAT jatuh."

        fact_sheet = {
            "root_cause": "Lolosnya 15 unit Smartwatch berlayar cacat ke klien enterprise CV Megah Sentosa mengancam pembatalan kontrak Rp 150.000.000.",
            "student_actions_taken": f"Status tiket keluhan: {complaint.stage if complaint else 'N/A'}. Tindakan: {action_taken}.",
            "why_evaluation": why_eval,
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Opsi A: Ganti 15 Unit Fisik (SOP Standar, potong stok & HPP).\n2. Opsi B: Mediasi Direksi -> Addendum Diskon 15% (Hemat kas & aman stok).\n3. Opsi C: Mediasi Direksi -> Servis Lapangan & Audit Vendor Cacat.",
            "key_takeaway": "Retensi pelanggan enterprise memiliki banyak jalur solusi; manajer yang matang memilih trade-off terbaik antara kepuasan konsumen vs likuiditas kas operasional."
        }

    elif cat in ["accounting", "finance"]:
        # Finance & Bad debt mitigation
        cash = state.cash if state else 500000000.0
        budgets = db.query(DepartmentBudget).filter(DepartmentBudget.company_id == company_id).all()
        total_budget = sum(b.allocated_amount for b in budgets) if budgets else 370000000.0

        s1_max = 30
        s1_score = 30 if cash >= 200000000.0 else (18 if cash >= 100000000.0 else 5)
        step_scores.append({"step": "Pengamanan Likuiditas Kas di Atas Batas Kritis (Safety Cash Level)", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        s2_max = 40
        budget_controlled = total_budget <= 400000000.0
        s2_score = 38 if budget_controlled else 22
        step_scores.append({"step": "Rasionalisasi Pagu Anggaran Operasional Departemen", "max_score": s2_max, "earned_score": s2_score, "status": "passed" if s2_score >= 30 else "failed"})

        s3_max = 30
        s3_score = 28 if cash > 0 else 5
        step_scores.append({"step": "Mitigasi Risiko Piutang Macet & Keseimbangan Neraca", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 20 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0) and (cash >= 150000000.0)

        fact_sheet = {
            "root_cause": "Gagal bayar distributor retail mengancam likuiditas kas operasional perusahaan.",
            "student_actions_taken": f"Saldo Kas Saat Ini: Rp {cash:,.0f}. Total Plafon Anggaran: Rp {total_budget:,.0f}.",
            "why_evaluation": "Keberhasilan manajemen kas menjaga saldo di atas batas aman (Safety Cash Level) dan merasionalisasi anggaran." if passed else "Saldo kas jatuh mendekati titik nol akibat kelalaian dalam manajemen modal kerja dan mitigasi piutang macet.",
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Rasionalisasi pagu anggaran operasional non-kritis di modul Budgeting.\n2. Terapkan syarat pembayaran tunai / DP minimal untuk pesanan baru di CRM.\n3. Bentuk cadangan kerugian piutang di Akuntansi.",
            "key_takeaway": "Revenue is vanity, profit is sanity, cash is king. Likuiditas adalah oksigen keberlangsungan hidup entitas bisnis."
        }

    elif cat in ["hr", "sdm"]:
        # HR & Bipartite labor relations
        employees = db.query(Employee).filter(Employee.company_id == company_id).all()
        is_strike = state.is_strike_active if state else False
        morale_avg = sum(e.morale_score for e in employees) / len(employees) if employees else 90.0
        cash = state.cash if state else 500000000.0

        s1_max = 30
        s1_score = 30 if cash >= 50000000.0 else 10
        step_scores.append({"step": "Pengamanan Likuiditas Kas Operasional & Cadangan Gaji", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        s2_max = 40
        s2_score = 38 if not is_strike else 10
        step_scores.append({"step": "Penyelesaian Sengketa Hubungan Industrial Bipartit", "max_score": s2_max, "earned_score": s2_score, "status": "passed" if s2_score >= 25 else "failed"})

        s3_max = 30
        s3_score = int(min(30, (morale_avg / 100.0) * 30))
        step_scores.append({"step": "Pemulihan Moral Pekerja & Operasional Lini Pabrik", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 22 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0) and not is_strike

        fact_sheet = {
            "root_cause": "Arus kas menipis memicu keterlambatan pembayaran gaji, ditambah beban lembur memicu mogok kerja buruh pabrik.",
            "student_actions_taken": f"Saldo Kas: Rp {cash:,.0f}. Status Mogok: {'Aktif' if is_strike else 'Selesai'}. Rata-rata Moral Buruh: {morale_avg:.1f}%.",
            "why_evaluation": "Mampu mencapai kesepakatan bipartit damai dan menjaga kesinambungan lini produksi." if passed else "Gagal mengakhiri aksi mogok kerja, lini pabrik lumpuh dan beban biaya tetap terus membengkak.",
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Jalur Bipartit Kompromi: Setujui bonus produktivitas wajar di modul HR.\n2. Jalur Efisiensi: Realokasi pos non-esensial ke dana payroll.\n3. Nyalakan kembali lini perakitan pabrik.",
            "key_takeaway": "Likuiditas kas adalah darah perusahaan; terganggunya kas gaji berakibat langsung pada kelumpuhan operasional."
        }

    else:
        # MRP & Production operations
        work_centers = db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all()
        all_operational = all(wc.status == "operational" for wc in work_centers) if work_centers else True
        machine_health = state.machine_health if state else 95.0
        work_orders = db.query(WorkOrder).filter(WorkOrder.company_id == company_id).all()

        s1_max = 30
        s1_score = 30 if all_operational else 10
        step_scores.append({"step": "Kehandalan Stasiun Kerja & Pencegahan Downtime Pabrik", "max_score": s1_max, "earned_score": s1_score, "status": "passed" if s1_score >= 20 else "failed"})

        s2_max = 40
        s2_score = int(min(40, (machine_health / 100.0) * 40))
        step_scores.append({"step": "Pemeliharaan Mesin SMT & Penerapan Standar TPM", "max_score": s2_max, "earned_score": s2_score, "status": "passed" if s2_score >= 30 else "failed"})

        s3_max = 30
        s3_score = 28 if (len(work_orders) > 0 or all_operational) else 15
        step_scores.append({"step": "Realisasi Jadwal Produksi & Pengendalian Scrap", "max_score": s3_max, "earned_score": s3_score, "status": "passed" if s3_score >= 20 else "failed"})

        total_score = float(s1_score + s2_score + s3_score)
        passed = (total_score >= 70.0) and all_operational

        fact_sheet = {
            "root_cause": "Downtime stasiun perakitan dan tingginya scrap rate mengikis kapasitas pabrik.",
            "student_actions_taken": f"Kesehatan Mesin: {machine_health:.1f}%. Status Stasiun Kerja: {'Seluruhnya Operasional' if all_operational else 'Ada Kerusakan'}. Work Order Diterbitkan: {len(work_orders)}.",
            "why_evaluation": "Berhasil memelihara kehandalan mesin dan menjaga kesinambungan lini manufaktur." if passed else "Mesin perakitan mengalami kerusakan kritis dan belum dilakukan tindakan perbaikan darurat.",
            "benchmark_solution": "Pilihan Terbuka (Open-World):\n1. Eksekusi perbaikan/maintenance stasiun kerja di modul MRP.\n2. Kalibrasi toleransi resep BOM untuk meminimalkan scrap.\n3. Rilis Work Order penyesuaian kuantitas.",
            "key_takeaway": "Total Productive Maintenance (TPM) adalah kunci efisiensi pabrik dan kepuasan pelanggan."
        }

    # Grade calculation
    grade = "A+" if total_score >= 93 else ("A" if total_score >= 83 else ("B" if total_score >= 70 else ("C" if total_score >= 55 else "D")))

    case.resolution_score = total_score
    case.grade = grade
    case.step_scores = json.dumps(step_scores)
    case.fact_sheet_data = json.dumps(fact_sheet)
    case.status = "resolved" if passed else "failed"

    if state:
        all_cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).all()
        res_list = [c for c in all_cases if c.status == "resolved"]
        if res_list:
            state.overall_score = round(sum(c.resolution_score for c in res_list) / len(res_list), 1)
        else:
            state.overall_score = 0.0

    if passed and state:
        # Unlock next case
        next_case = db.query(ScenarioCase).filter(
            ScenarioCase.company_id == company_id,
            ScenarioCase.stage_order == case.stage_order + 1
        ).first()
        if next_case:
            next_case.status = "active"
            state.active_case_title = next_case.title
            state.active_case_description = next_case.description

    db.commit()
    return {
        "status": "success" if passed else "warning",
        "case_status": case.status,
        "total_score": total_score,
        "grade": grade,
        "step_scores": step_scores,
        "fact_sheet": fact_sheet,
        "message": f"Evaluasi Selesai! Skor: {total_score:.1f}/100 (Predikat: {grade}). {'Kasus Berhasil Dipecahkan!' if passed else 'Kasus Belum Berhasil. Tinjau Fact Sheet Problem Solving!'}"
    }

@router.post("/advance-round/{company_id}")
def advance_round(company_id: int, db: Session = Depends(get_db)):
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="Simulasi tidak ditemukan")
    
    slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == company_id).first()
    state.current_round += 1
    months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    month_idx = (state.current_round - 1) % 12
    state.period_name = f"Bulan {state.current_round} ({months[month_idx]})"

    monthly_sales = 55000000.0 * (1.0 - (slider.competitor_price_war / 200.0 if slider else 0.1))
    monthly_payroll = 30400000.0
    monthly_overhead = 12000000.0
    
    bad_debt_loss = 0.0
    if slider and slider.bad_debt_risk >= 40.0:
        bad_debt_loss = monthly_sales * (slider.bad_debt_risk / 200.0)
    
    monthly_net = monthly_sales - monthly_payroll - monthly_overhead - bad_debt_loss
    
    state.revenue += monthly_sales
    state.expenses += (monthly_payroll + monthly_overhead + bad_debt_loss)
    state.net_profit += monthly_net
    state.cash += monthly_net

    # CASCADE CHECKS:
    bankruptcy_alert = None
    if state.cash < 0:
        state.overall_score = max(5.0, state.overall_score - 35.0)
        bankruptcy_alert = "⚠️ PERUSAHAAN INSOLVENT: Saldo kas minus! Perusahaan berada di ambang kebangkrutan likuidasi!"

    strike_triggered = False
    if state.cash < monthly_payroll:
        state.worker_morale = max(10.0, state.worker_morale - 35.0)
        state.is_strike_active = True
        state.strike_reason = "Gagal bayar gaji karyawan akibat krisis likuiditas kas operasional!"
        strike_triggered = True

    cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1010").first()
    if cash_acc:
        cash_acc.balance = state.cash

    # ============================================================
    # CASCADING SCENARIO ENGINE
    # ============================================================
    cascade_event = None

    # Step 1: Evaluate currently ACTIVE ScenarioCase — penalise if unresolved
    active_cases = db.query(ScenarioCase).filter(
        ScenarioCase.company_id == company_id,
        ScenarioCase.status == "active"
    ).all()

    penalty_messages = []
    for ac in active_cases:
        cat = ac.category or ""
        if cat in ("mrp", "manufacturing"):
            state.machine_health = max(20.0, state.machine_health - 8.0)
            state.worker_morale = max(20.0, state.worker_morale - 5.0)
            for wc in db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all():
                if "SMT" in wc.code or "Perakitan" in wc.name:
                    wc.failure_rate = min(25.0, wc.failure_rate + 3.0)
            penalty_messages.append("⚙️ Mesin semakin aus (Kesehatan Mesin -8%), moral pekerja turun -5%")
        elif cat == "accounting":
            state.cash = max(0.0, state.cash - 15000000.0)
            state.overall_score = max(0.0, state.overall_score - 3.0)
            if cash_acc:
                cash_acc.balance = state.cash
            penalty_messages.append("💸 Denda keterlambatan akuntansi: Kas -Rp 15.000.000")
        elif cat == "crm":
            state.csat_score = max(10.0, state.csat_score - 8.0)
            state.overall_score = max(0.0, state.overall_score - 3.0)
            penalty_messages.append("📉 Keluhan pelanggan memburuk: CSAT -8%")
        elif cat == "hr":
            state.worker_morale = max(10.0, state.worker_morale - 10.0)
            if state.worker_morale < 40.0 and not state.is_strike_active:
                state.is_strike_active = True
                state.strike_reason = "Moral buruh kritis akibat misi SDM yang terbengkalai!"
                strike_triggered = True
            penalty_messages.append("👷 Moral buruh anjlok -10%, risiko mogok kerja meningkat!")
        elif cat == "purchasing":
            state.supplier_health = max(20.0, state.supplier_health - 8.0)
            penalty_messages.append("🚚 Relasi vendor memburuk: Supplier Health -8%")

    # Step 2: Activate next PENDING ScenarioCase (lowest stage_order)
    next_pending = db.query(ScenarioCase).filter(
        ScenarioCase.company_id == company_id,
        ScenarioCase.status == "pending"
    ).order_by(ScenarioCase.stage_order).first()

    new_mission_info = None
    if next_pending:
        next_pending.status = "active"
        next_pending.round_introduced = state.current_round

        cat = next_pending.category or ""
        # Apply specific scenario mutation if defined, otherwise fallback by category
        sc_code = next_pending.code or ""
        mutation = SCENARIO_INITIAL_MUTATIONS.get(sc_code)
        if mutation:
            _apply_scenario_mutation(state, mutation, db, company_id)
        else:
            if cat in ("mrp", "manufacturing"):
                state.machine_health = min(state.machine_health, 62.0)
                state.worker_morale = min(state.worker_morale, 68.0)
                state.is_strike_active = True
                state.strike_reason = "Mesin SMT korsleting inverter dan operator menuntut kenaikan upah lembur."
                for wc in db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all():
                    if "SMT" in wc.code or "Perakitan" in wc.name:
                        wc.status = "breakdown"
                        wc.failure_rate = min(20.0, wc.failure_rate + 5.0)
            elif cat == "accounting":
                bad_debt_hit = 25000000.0
                state.cash = max(0.0, state.cash - bad_debt_hit)
                if cash_acc:
                    cash_acc.balance = state.cash
            elif cat == "crm":
                state.csat_score = min(state.csat_score, 62.0)
            elif cat == "hr":
                state.worker_morale = min(state.worker_morale, 65.0)
                state.is_strike_active = True
                state.strike_reason = "Operator pabrik kelelahan lembur dan menuntut kenaikan upah."
            elif cat == "purchasing":
                state.supplier_health = min(state.supplier_health, 55.0)

        state.active_case_title = next_pending.title
        state.active_case_description = next_pending.description

        new_mission_info = {
            "id": next_pending.id,
            "code": next_pending.code,
            "title": next_pending.title,
            "category": cat,
            "description": next_pending.description,
            "stage_order": next_pending.stage_order,
        }

    # Step 3: Build cascade_event for frontend
    if penalty_messages or new_mission_info:
        module_map = {
            "mrp": "manufacturing", "manufacturing": "manufacturing",
            "accounting": "accounting", "crm": "crm",
            "hr": "hr", "purchasing": "purchasing"
        }
        cascade_module = None
        if new_mission_info:
            cascade_module = module_map.get(new_mission_info["category"], "missions")

        cascade_event = {
            "penalties_applied": penalty_messages,
            "new_mission": new_mission_info,
            "module": cascade_module,
        }

    db.commit()
    return {
        "status": "success",
        "current_round": state.current_round,
        "period_name": state.period_name,
        "net_profit_month": monthly_net,
        "current_cash": state.cash,
        "bad_debt_deducted": bad_debt_loss,
        "bankruptcy_alert": bankruptcy_alert,
        "strike_triggered": strike_triggered,
        "cascade_event": cascade_event,
    }


@router.get("/ending-report/{company_id}")
def get_ending_report(company_id: int, db: Session = Depends(get_db)):
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="Data simulasi tidak ditemukan")

    cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).all()
    resolved_cases = sum(1 for c in cases if c.status == "resolved")
    total_cases = len(cases)

    # Determine Ending Archetype (7 Multi-Ending Spectrum)
    if state.cash < 0:
        ending = {
            "code": "BANKRUPTCY",
            "badge": "PAILIT & LIKUIDASI",
            "badge_color": "bg-red-600 text-white",
            "title": "💀 KEBANGKRUTAN & LIKUIDASI ASET (Chapter 7 Bankruptcy)",
            "subtitle": "Kegagalan Manajemen Likuiditas Kas Operasional",
            "status": "FAILED",
            "verdict": "Perusahaan dinyatakan pailit oleh Pengadilan Niaga. Pembengkakan kompensasi yang tidak terkendali, piutang macet yang tak tertagih, dan saldo kas yang minus membuat perusahaan tidak mampu membayar kewajiban jangka pendek.",
            "autopsy": [
                f"Defisit Kas: Saldo kas tercatat minus Rp {abs(state.cash):,.0f}.",
                "Krisis Solvabilitas: Arus kas masuk tidak mampu menutup beban operasional dan HPP.",
                "Pelajaran Kunci: 'Cash is King' — Margin laba di atas kertas tidak berguna jika kas riil habis."
            ],
            "grade": "F"
        }
    elif state.is_strike_active or state.worker_morale < 45.0:
        ending = {
            "code": "STRIKE_SHUTDOWN",
            "badge": "MOGOK MASSAL",
            "badge_color": "bg-rose-700 text-white",
            "title": "🛑 KELUMPUHAN PABRIK AKIBAT MOGOK KERJA MASSAL",
            "subtitle": "Krisis Hubungan Industrial & Kegagalan Hak Buruh",
            "status": "FAILED",
            "verdict": "Lini perakitan manufaktur diduduki oleh serikat buruh. Kebijakan pemotongan sepihak atau keterlambatan gaji memicu pemogokan berkepanjangan. Mesin pabrik padam, pesanan klien terbengkalai, dan iklim kerja rusak total.",
            "autopsy": [
                f"Moral Pekerja Kritis: Indeks moral buruh berada di {state.worker_morale:.1f}% (Batas aman > 75%).",
                f"Alasan Pemogokan: {state.strike_reason or 'Kekecewaan buruh atas kompensasi dan beban kerja'}.",
                "Pelajaran Kunci: Keberlanjutan industri manufaktur bergantung pada keadilan kemitraan bipartit buruh-manajemen."
            ],
            "grade": "D"
        }
    elif state.csat_score < 45.0:
        ending = {
            "code": "REPUTATION_CRISIS",
            "badge": "SKANDAL MUTU",
            "badge_color": "bg-amber-600 text-white",
            "title": "📉 SKANDAL MUTU & BOIKOT KONSUMEN KORPORAT",
            "subtitle": "Keruntuhan Loyalitas Klien B2B Enterprise",
            "status": "FAILED",
            "verdict": "Akibat meremehkan komplain cacat produk dan memaksakan suku cadang bermutu rendah, CV Megah Sentosa dan jejaring klien korporat lainnya memutus seluruh kontrak pengadaan. Berita cacat produk viral di komunitas bisnis.",
            "autopsy": [
                f"Skor CSAT Jatuh: Indeks kepuasan konsumen hanya {state.csat_score:.1f}% (Batas aman > 70%).",
                "Kehilangan Pendapatan: Kontrak tahunan bernilai ratusan juta rupiah dibatalkan sepihak oleh klien.",
                "Pelajaran Kunci: Biaya retensi klien loyal jauh lebih murah daripada dampak boikot akibat cacat mutu produk."
            ],
            "grade": "D"
        }
    elif state.cash < 50000000.0 or state.overall_score < 60.0:
        ending = {
            "code": "ZOMBIE_CORP",
            "badge": "PERUSAHAAN ZOMBIE",
            "badge_color": "bg-slate-600 text-white",
            "title": "🏢 PERUSAHAAN ZOMBIE (Stagnant Survival Mode)",
            "subtitle": "Bertahan Hidup dengan Margin Tipis & Keterbatasan Modal",
            "status": "SURVIVED",
            "verdict": "Perusahaan berhasil lolos dari jurang kebangkrutan, namun terjebak dalam kondisi stagnan. Saldo kas pas-pasan, peralatan pabrik rentan mogok, dan perusahaan tidak memiliki kapasitas finansial untuk berekspansi.",
            "autopsy": [
                f"Saldo Kas Kritis: Tersisa Rp {state.cash:,.0f} (cadangan operasional sangat sempit).",
                f"Tingkat Penyelesaian Masalah: {resolved_cases}/{total_cases} misi terselesaikan.",
                "Pelajaran Kunci: Efisiensi reaktif hanya cukup untuk bertahan, dibutuhkan inovasi strategis terencana untuk tumbuh."
            ],
            "grade": "C"
        }
    elif state.cash < 150000000.0 or state.overall_score < 78.0:
        ending = {
            "code": "DEBT_RESTRUCTURING",
            "badge": "RESTRUKTURISASI UTANG",
            "badge_color": "bg-orange-600 text-white",
            "title": "🔄 RESTRUKTURISASI UTANG & TURNAROUND (Crisis Navigation)",
            "subtitle": "Manuver Penyelamatan Arus Kas Pasca-Disrupsi Makro",
            "status": "TURNAROUND",
            "verdict": "Perusahaan berhasil selamat dari rentetan disrupsi berkat manuver restrukturisasi utang dan pengetatan biaya operasional. Likuiditas mulai pulih meskipun beban kewajiban jangka panjang masih membayangi.",
            "autopsy": [
                f"Kas Pemulihan: Rp {state.cash:,.0f} dengan laba bersih Rp {state.net_profit:,.0f}.",
                f"Tingkat Resiliensi: Mampu menyerap goncangan pasar dan menyelesaikan {resolved_cases}/{total_cases} skenario.",
                "Pelajaran Kunci: Disiplin anggaran dan negosiasi perpanjangan tenor utang adalah kunci penyelamatan saat krisis likuiditas."
            ],
            "grade": "B-"
        }
    elif state.cash >= 350000000.0 and state.csat_score >= 90.0 and state.worker_morale >= 85.0 and resolved_cases == total_cases:
        ending = {
            "code": "UNICORN_LEADER",
            "badge": "MARKET LEADER",
            "badge_color": "bg-indigo-600 text-white",
            "title": "🏆 MARKET LEADER & UNICORN SCALE-UP (Operational Apex)",
            "subtitle": "Pencapaian Keunggulan Manajerial Paripurna Kelas Dunia",
            "status": "DISTINCTION",
            "verdict": "Pencapaian luar biasa! Perusahaan mendominasi industri berkat integrasi rantai pasok tangguh, lini perakitan nir-cacat (Zero Defect), kepuasan klien 90%+, dan neraca kas yang sangat sehat. Menjadi benchmark nasional!",
            "autopsy": [
                f"Kas Gemilang: Rp {state.cash:,.0f} dengan akumulasi laba bersih Rp {state.net_profit:,.0f}.",
                f"Harmoni Operasional: CSAT {state.csat_score:.1f}% • Moral Buruh {state.worker_morale:.1f}% • Mesin {state.machine_health:.1f}%.",
                f"Misi Tuntas: {resolved_cases}/{total_cases} tantangan industri dipecahkan dengan nilai prima.",
                "Pelajaran Kunci: Kolaborasi harmonis antara pengadaan, manufaktur, pemasaran, dan SDM adalah kunci kejayaan enterprise."
            ],
            "grade": "A+"
        }
    else:
        ending = {
            "code": "PRUDENT_PARTNER",
            "badge": "MITRA STRATEGIS",
            "badge_color": "bg-emerald-600 text-white",
            "title": "🛡️ MITRA STRATEGIS KORPORAT & BUMN (Prudent Enterprise)",
            "subtitle": "Ekosistem B2B Stabil dengan Pertumbuhan Berkelanjutan",
            "status": "PASSED",
            "verdict": "Manajemen mampu menerapkan negosiasi B2B yang matang dan menjaga kesinambungan neraca keuangan. Mediasi cerdas berhasil menyelamatkan kontrak tanpa mengorbankan likuiditas operasional dan hak pekerja.",
            "autopsy": [
                f"Kesehatan Finansial: Saldo kas Rp {state.cash:,.0f} dengan arus kas stabil.",
                f"Loyalitas Kemitraan: CSAT {state.csat_score:.1f}% • Moral Buruh {state.worker_morale:.1f}%.",
                f"Misi Berhasil: {resolved_cases}/{total_cases} kasus berhasil dimitigasi.",
                "Pelajaran Kunci: Kepemimpinan yang cermat dalam mitigasi risiko menghasilkan stabilitas bisnis jangka panjang."
            ],
            "grade": "A"
        }

    return {
        "company_id": company_id,
        "round": state.current_round,
        "period_name": state.period_name,
        "ending": ending,
        "metrics": {
            "cash": state.cash,
            "net_profit": state.net_profit,
            "revenue": state.revenue,
            "expenses": state.expenses,
            "csat_score": state.csat_score,
            "worker_morale": state.worker_morale,
            "machine_health": state.machine_health,
            "supplier_health": state.supplier_health,
            "overall_score": state.overall_score,
            "is_strike": state.is_strike_active,
            "resolved_cases": resolved_cases,
            "total_cases": total_cases
        }
    }

@router.get("/leaderboard/{session_id}")
def get_leaderboard(session_id: int, db: Session = Depends(get_db)):
    companies = db.query(Company).filter(Company.session_id == session_id).all()
    results = []
    for co in companies:
        st = co.sim_state
        sl = co.slider_config
        results.append({
            "company_id": co.id,
            "company_name": co.name,
            "overall_score": st.overall_score if st else 0.0,
            "cash": st.cash if st else 500000000.0,
            "net_profit": st.net_profit if st else 0.0,
            "csat_score": st.csat_score if st else 85.0,
            "worker_morale": st.worker_morale if st else 90.0,
            "machine_health": st.machine_health if st else 95.0,
            "supplier_health": st.supplier_health if st else 90.0,
            "is_strike": st.is_strike_active if st else False,
            "sliders": {
                "supply": sl.supply_disruption if sl else 20.0,
                "breakdown": sl.machine_breakdown_risk if sl else 15.0,
                "strike": sl.labor_strike_risk if sl else 10.0,
                "bad_debt": sl.bad_debt_risk if sl else 15.0,
            }
        })
    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results

@router.post("/companies/{company_id}/reset-missions")
def reset_company_missions(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Perusahaan tidak ditemukan")

    # 1. Clean transactions generated by student
    sos = db.query(SalesOrder).filter(SalesOrder.company_id == company_id).all()
    for so in sos:
        db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == so.id).delete()
        db.delete(so)
    
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == company_id).all()
    for po in pos:
        db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po.id).delete()
        db.delete(po)

    db.query(WorkOrder).filter(WorkOrder.company_id == company_id).delete()

    jes = db.query(JournalEntry).filter(JournalEntry.company_id == company_id).all()
    for je in jes:
        db.query(JournalItem).filter(JournalItem.journal_entry_id == je.id).delete()
        db.delete(je)

    # 2. Reset product stock to initial baseline
    products = db.query(Product).filter(Product.company_id == company_id).all()
    for p in products:
        if p.product_type == "raw_material":
            p.current_stock = 40.0
        elif p.product_type == "finished_good":
            p.current_stock = 25.0

    # 3. Reset scenario cases to initial pending/active
    cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).order_by(ScenarioCase.stage_order.asc()).all()
    for idx, c in enumerate(cases):
        if idx == 0:
            c.status = "active"
        else:
            c.status = "pending"
        c.resolution_score = 0.0
        c.grade = "-"
        c.step_scores = None
        c.fact_sheet_data = None

    # 4. Reset CRM Complaints to unresolved so student can mitigate it
    complaints = db.query(CRMLead).filter(CRMLead.company_id == company_id, CRMLead.is_complaint == True).all()
    for comp in complaints:
        comp.stage = "proposition"
        comp.resolution_action = None

    # 5. Reset cash and simulation state
    init_cash = company.initial_capital or 500000000.0
    company.current_cash = init_cash
    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if state:
        state.cash = init_cash
        state.revenue = 0.0
        state.expenses = 0.0
        state.net_profit = 0.0
        state.csat_score = 88.0
        state.worker_morale = 92.0
        state.machine_health = 95.0
        state.is_strike_active = False
        state.strike_reason = None
        state.overall_score = 0.0
        if cases:
            state.active_case_title = cases[0].title
            state.active_case_description = cases[0].description

    # Reset account cash (1010)
    cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1010").first()
    if cash_acc:
        cash_acc.balance = init_cash

    db.commit()
    return {
        "status": "success",
        "message": f"Seluruh isian transaksi, stok gudang & skor misi untuk '{company.name}' berhasil di-reset ke kondisi awal!"
    }

@router.post("/reset-all-missions")
def reset_all_companies_missions(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    for co in companies:
        # Clean transactions
        sos = db.query(SalesOrder).filter(SalesOrder.company_id == co.id).all()
        for so in sos:
            db.query(SalesOrderItem).filter(SalesOrderItem.sales_order_id == so.id).delete()
            db.delete(so)
        
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == co.id).all()
        for po in pos:
            db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po.id).delete()
            db.delete(po)

        db.query(WorkOrder).filter(WorkOrder.company_id == co.id).delete()

        jes = db.query(JournalEntry).filter(JournalEntry.company_id == co.id).all()
        for je in jes:
            db.query(JournalItem).filter(JournalItem.journal_entry_id == je.id).delete()
            db.delete(je)

        # Reset stock
        products = db.query(Product).filter(Product.company_id == co.id).all()
        for p in products:
            if p.product_type == "raw_material":
                p.current_stock = 40.0
            elif p.product_type == "finished_good":
                p.current_stock = 25.0

        # Reset cases
        cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == co.id).order_by(ScenarioCase.stage_order.asc()).all()
        for idx, c in enumerate(cases):
            if idx == 0:
                c.status = "active"
            else:
                c.status = "pending"
            c.resolution_score = 0.0
            c.grade = "-"
            c.step_scores = None
            c.fact_sheet_data = None
        
        # Reset complaints
        complaints = db.query(CRMLead).filter(CRMLead.company_id == co.id, CRMLead.is_complaint == True).all()
        for comp in complaints:
            comp.stage = "proposition"
            comp.resolution_action = None

        # Reset state & cash
        init_cash = co.initial_capital or 500000000.0
        co.current_cash = init_cash
        state = db.query(SimulationState).filter(SimulationState.company_id == co.id).first()
        if state:
            state.cash = init_cash
            state.revenue = 0.0
            state.expenses = 0.0
            state.net_profit = 0.0
            state.csat_score = 88.0
            state.worker_morale = 92.0
            state.machine_health = 95.0
            state.is_strike_active = False
            state.strike_reason = None
            state.overall_score = 0.0
            if cases:
                state.active_case_title = cases[0].title
                state.active_case_description = cases[0].description

        cash_acc = db.query(Account).filter(Account.company_id == co.id, Account.code == "1010").first()
        if cash_acc:
            cash_acc.balance = init_cash

    db.commit()
    return {
        "status": "success",
        "message": f"Seluruh isian transaksi & misi untuk {len(companies)} perusahaan berhasil di-reset ke kondisi awal!"
    }

@router.post("/cases/{case_id}/reset")
def reset_single_case(case_id: int, db: Session = Depends(get_db)):
    case = db.query(ScenarioCase).filter(ScenarioCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    
    case.status = "active"
    case.resolution_score = 0.0
    case.grade = "-"
    case.step_scores = None
    case.fact_sheet_data = None

    cat = (case.category or "").lower()
    if cat in ["crm", "marketing", "sales"]:
        complaints = db.query(CRMLead).filter(CRMLead.company_id == case.company_id, CRMLead.is_complaint == True).all()
        for complaint in complaints:
            complaint.stage = "proposition"
            complaint.resolution_action = None
    elif cat in ["procurement", "purchasing", "scm"]:
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.company_id == case.company_id).all()
        for po in pos:
            db.query(PurchaseOrderItem).filter(PurchaseOrderItem.purchase_order_id == po.id).delete()
            db.delete(po)

    db.commit()
    return {
        "status": "success",
        "message": f"Misi '{case.title}' berhasil di-reset ke status aktif tanpa jawaban tersimpan!"
    }


# =======================================================
# --- SMART PYTHON BRAIN: SCENARIO MATRIX & STORYLINE ---
# =======================================================

class ExecuteBranchRequest(BaseModel):
    scenario_id: str
    choice_id: str

class CalculateRippleRequest(BaseModel):
    company_id: int
    action_type: str
    action_payload: Optional[dict] = {}

@router.get("/scenarios/matrix")
def get_scenario_matrix():
    """
    Returns the full 20-scenario multi-domain matrix with branch options,
    rationale, ripple consequences, and formal document templates.
    """
    return {
        "total_scenarios": 20,
        "scenarios": get_all_scenarios_matrix()
    }

@router.get("/scenarios/{scenario_id}")
def get_scenario_detail(scenario_id: str):
    sc = get_scenario_by_id(scenario_id)
    if not sc:
        raise HTTPException(status_code=404, detail="Skenario tidak ditemukan")
    return sc

@router.post("/scenarios/{company_id}/execute-branch")
def post_execute_scenario_branch(
    company_id: int,
    payload: ExecuteBranchRequest,
    db: Session = Depends(get_db)
):
    """
    Executes a branching decision for a specific company tenant, applying
    financial impacts, persisting story events, and generating formal business documents.
    """
    try:
        result = execute_scenario_branch(
            company_id=company_id,
            scenario_id=payload.scenario_id,
            choice_id=payload.choice_id,
            db=db
        )
        return {
            "status": "success",
            "message": f"Keputusan Cabang '{payload.choice_id}' untuk skenario '{payload.scenario_id}' berhasil dieksekusi!",
            "data": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal execution error: {str(e)}")

@router.get("/storyline/{company_id}")
def get_company_storyline(company_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the chronological story event log, branch choices made,
    generated documents, and cumulative consequences for a company.
    """
    events = (
        db.query(CompanyStoryEvent)
        .filter(CompanyStoryEvent.company_id == company_id)
        .order_by(CompanyStoryEvent.created_at.desc())
        .all()
    )
    story_list = []
    for ev in events:
        ripples = []
        if ev.ripple_summary:
            try:
                ripples = json.loads(ev.ripple_summary) if isinstance(ev.ripple_summary, str) else ev.ripple_summary
            except Exception:
                ripples = []
        doc = None
        if ev.document_data:
            try:
                doc = json.loads(ev.document_data) if isinstance(ev.document_data, str) else ev.document_data
            except Exception:
                doc = None

        story_list.append({
            "id": ev.id,
            "round_number": ev.round_number,
            "period_name": ev.period_name,
            "domain": ev.domain,
            "event_type": ev.event_type,
            "title": ev.title,
            "description": ev.description,
            "decision_taken": ev.decision_taken,
            "ripples": ripples,
            "document": doc,
            "created_at": ev.created_at.isoformat()
        })

    return {
        "company_id": company_id,
        "total_events": len(events),
        "events": story_list
    }

@router.get("/cfo-diagnostics/{company_id}")
def get_cfo_diagnostics(company_id: int, db: Session = Depends(get_db)):
    """
    Returns automated DuPont analysis, Altman Z-Score, Working Capital breakdown,
    and strategic recommendations for lecturers and student teams.
    """
    try:
        diagnostics = run_smart_cfo_diagnostics(company_id=company_id, db=db)
        return diagnostics
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CFO diagnostics computation error: {str(e)}")

@router.post("/ripples/calculate")
def post_calculate_ripples(
    payload: CalculateRippleRequest,
    db: Session = Depends(get_db)
):
    """
    Calculates multi-departmental domino impacts for standard ERP user actions.
    """
    try:
        ripples = calculate_action_ripples(
            company_id=payload.company_id,
            action_type=payload.action_type,
            action_payload=payload.action_payload or {},
            db=db
        )
        return ripples
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ripple calculation error: {str(e)}")

