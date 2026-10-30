from sqlalchemy.orm import Session
from passlib.context import CryptContext
from backend.app.database import engine, Base, SessionLocal
from backend.app.models.models import (
    User, ClassSession, ClassSessionLecturer, Company, SimulationState, SimulationSlider, ScenarioCase,
    Vendor, VendorMetricHistory, Product, BillOfMaterials, BOMItem,
    WorkCenter, CRMLead, Customer, Account, JournalEntry, JournalItem,
    DepartmentBudget, Employee, MarketingCampaign
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def ensure_team_lecturers(db: Session):
    """Ensures all class sessions have their multidisciplinary team teaching lecturers mapped."""
    sessions = db.query(ClassSession).all()
    dosen_lead = db.query(User).filter(User.username == "dosen").first()
    dosen_mkt = db.query(User).filter(User.username == "dosen.marketing").first()
    dosen_sdm = db.query(User).filter(User.username == "dosen.sdm").first()
    dosen_fin = db.query(User).filter(User.username == "dosen.keuangan").first()

    for s in sessions:
        count = db.query(ClassSessionLecturer).filter(ClassSessionLecturer.session_id == s.id).count()
        if count == 0:
            if dosen_lead:
                db.add(ClassSessionLecturer(session_id=s.id, user_id=dosen_lead.id, role_title="Koordinator Matakuliah & Pengampu Utama", is_primary=True))
            if dosen_mkt:
                db.add(ClassSessionLecturer(session_id=s.id, user_id=dosen_mkt.id, role_title="Dosen Bidang Pemasaran & CRM", is_primary=False))
            if dosen_sdm:
                db.add(ClassSessionLecturer(session_id=s.id, user_id=dosen_sdm.id, role_title="Dosen Bidang SDM & Organisasi", is_primary=False))
            if dosen_fin:
                db.add(ClassSessionLecturer(session_id=s.id, user_id=dosen_fin.id, role_title="Dosen Bidang Keuangan & Akuntansi", is_primary=False))
    db.commit()

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if already seeded
    if db.query(User).filter(User.username == "admin").first():
        ensure_team_lecturers(db)
        print("Database already seeded. Team lecturers verified.")
        db.close()
        return

    print("Seeding initial data...")

    # 1. Users
    admin = User(
        username="admin",
        email="admin@vlaberp.ac.id",
        full_name="System Administrator FEB",
        hashed_password=get_password_hash("admin123"),
        role="ADMIN"
    )
    dosen = User(
        username="dosen",
        email="dosen@vlaberp.ac.id",
        full_name="Tim Dosen Pengampu FEB",
        hashed_password=get_password_hash("dosen123"),
        role="DOSEN"
    )
    dosen_mkt = User(
        username="dosen.marketing",
        email="maya.indah@vlaberp.ac.id",
        full_name="Dr. Maya Indah, S.E., M.M. (Dosen Pemasaran FEB)",
        hashed_password=get_password_hash("dosen123"),
        role="DOSEN"
    )
    dosen_sdm = User(
        username="dosen.sdm",
        email="bambang.prakoso@vlaberp.ac.id",
        full_name="Drs. Bambang Prakoso, M.Psi., M.M. (Dosen SDM FEB)",
        hashed_password=get_password_hash("dosen123"),
        role="DOSEN"
    )
    dosen_fin = User(
        username="dosen.keuangan",
        email="budi.santoso@vlaberp.ac.id",
        full_name="Dr. Ir. Budi Santoso, S.E., Ak., M.Ak. (Dosen Keuangan FEB)",
        hashed_password=get_password_hash("dosen123"),
        role="DOSEN"
    )
    mahasiswa = User(
        username="mahasiswa",
        email="kelompok1.a@mahasiswa.vlaberp.ac.id",
        full_name="Kelompok 1 (Kelas FEB A)",
        hashed_password=get_password_hash("mhs123"),
        role="MAHASISWA"
    )
    mahasiswa_b = User(
        username="mahasiswa_b",
        email="kelompok1.b@mahasiswa.vlaberp.ac.id",
        full_name="Kelompok 1 (Kelas FEB B)",
        hashed_password=get_password_hash("mhs123"),
        role="MAHASISWA"
    )
    db.add_all([admin, dosen, dosen_mkt, dosen_sdm, dosen_fin, mahasiswa, mahasiswa_b])
    db.commit()
    db.refresh(dosen)
    db.refresh(dosen_mkt)
    db.refresh(dosen_sdm)
    db.refresh(dosen_fin)
    db.refresh(mahasiswa)
    db.refresh(mahasiswa_b)

    # 2. Class Sessions (FEB-A and FEB-B)
    session_a = ClassSession(
        name="Praktikum ERP & Simulasi Bisnis - Kelas FEB A",
        code="ERP-FEB-A",
        academic_term="Semester Ganjil 2026/2027",
        department="S1 Manajemen & Bisnis Digital FEB",
        lecturer_id=dosen.id,
        progression_mode="problem_based",
        current_round=1,
        total_rounds=12
    )
    session_b = ClassSession(
        name="Praktikum ERP & Simulasi Bisnis - Kelas FEB B",
        code="ERP-FEB-B",
        academic_term="Semester Ganjil 2026/2027",
        department="S1 Akuntansi & Keuangan FEB",
        lecturer_id=dosen.id,
        progression_mode="problem_based",
        current_round=1,
        total_rounds=12
    )
    db.add_all([session_a, session_b])
    db.commit()
    db.refresh(session_a)
    db.refresh(session_b)
    session = session_a

    # Seed Team Lecturers for Session A and B
    ensure_team_lecturers(db)

    # 3. Company
    company = Company(
        session_id=session.id,
        name="PT Inovasi Cipta Mandiri",
        industry="Manufaktur Perangkat Cerdas (Smart Devices)",
        team_leader_id=mahasiswa.id,
        initial_capital=500000000.0,
        current_cash=500000000.0
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    # 4. Simulation State & Sliders
    sim_state = SimulationState(
        company_id=company.id,
        current_round=1,
        period_name="Bulan 1 (Januari)",
        cash=500000000.0,
        revenue=45000000.0,
        expenses=25000000.0,
        net_profit=20000000.0,
        csat_score=88.5,
        worker_morale=92.0,
        machine_health=95.0,
        supplier_health=91.0,
        overall_score=0.0,
        is_strike_active=False,
        active_case_title="Tahap 1: Due Diligence Vendor & Kesiapan Produksi",
        active_case_description="Kelompok diminta melakukan evaluasi kinerja 4 vendor bahan baku. Teliti grafik ketaatan dan defect rate sebelum menerbitkan PO."
    )
    slider = SimulationSlider(
        company_id=company.id,
        session_id=session.id,
        is_company_override=False,
        supply_disruption=25.0,
        machine_breakdown_risk=15.0,
        market_volatility=30.0,
        labor_strike_risk=10.0,
        bad_debt_risk=15.0,
        competitor_price_war=20.0
    )
    db.add_all([sim_state, slider])
    db.commit()

    # 5. Solvable Scenario Cases (Misi Bertahap)
    cases = [
        ScenarioCase(
            session_id=session.id,
            company_id=company.id,
            code="CASE-01",
            stage_order=1,
            title="Misi 1: Evaluasi Vendor & Pencegahan Bottleneck Bahan Baku",
            category="procurement",
            description="Lini produksi Smartwatch membutuhkan pasokan baterai dan chipset yang konsisten. Ada 4 vendor yang tersedia dengan profil berbeda. Hindari vendor dengan defect rate tinggi yang berisiko merusak mesin di pabrik.",
            trigger_hint="Periksa grafik Completion Rate & Defect History pada menu Pengadaan/Vendor.",
            solvable_workflow="1. Buka modul Vendor/Purchasing -> Bandingkan chart 4 vendor.\n2. Buat Purchase Order (PO) ke vendor terpercaya dengan defect rate < 2%.\n3. Pertahankan safety stock minimal 50 unit.",
            resolution_criteria="PO diterbitkan ke vendor berkualitas, safety stock bahan baku terpenuhi.",
            status="active",
            round_introduced=1,
            resolution_score=0.0,
            grade="-",
            step_scores=None,
            fact_sheet_data=None
        ),
        ScenarioCase(
            session_id=session.id,
            company_id=company.id,
            code="CASE-02",
            stage_order=2,
            title="Misi 2: Penanganan Krisis Keluhan Pelanggan VIP di CRM",
            category="crm",
            description="Klien penting (CV Megah Sentosa) melaporkan 15 unit Smartwatch mengalami layar bergaris dari batch pengiriman sebelumnya dan mengancam memutus kontrak tahunan senilai Rp 150.000.000.",
            trigger_hint="Buka tiket keluhan bernotifikasi Urgent di modul CRM.",
            solvable_workflow="1. Buka modul CRM -> Cari tiket keluhan CV Megah Sentosa.\n2. Pilih tindakan penyelesaian: 'Ganti Unit Baru + Voucher Diskon 10%'.\n3. Terbitkan Credit Note di Akuntansi untuk mencatat retur barang.",
            resolution_criteria="Tiket keluhan terselesaikan, CSAT pulih di atas 80%.",
            status="pending",
            round_introduced=2,
            resolution_score=0.0,
            grade="-",
            step_scores=None,
            fact_sheet_data=None
        ),
        ScenarioCase(
            session_id=session.id,
            company_id=company.id,
            code="CASE-03",
            stage_order=3,
            title="Misi 3: Manajemen Likuiditas Kas & Pencegahan Mogok Kerja Buruh",
            category="hr",
            description="Terjadi penundaan pembayaran dari salah satu pelanggan retail. Jika saldo kas operasional tidak diamankan, pembayaran gaji operator pabrik akan terlambat dan memicu ancaman mogok kerja serikat buruh.",
            trigger_hint="Pantau rasio kas dan indikator Moral Pekerja di modul HR.",
            solvable_workflow="1. Buka modul Akuntansi -> Kurangi pengeluaran promosi non-esensial.\n2. Di modul HR -> Setujui paket uang lembur proporsional.\n3. Pastikan gaji dibayarkan tepat waktu.",
            resolution_criteria="Gaji terbayar, indikator moral buruh di atas 85%, mogok kerja dihindari.",
            status="pending",
            round_introduced=3,
            resolution_score=0.0,
            grade="-",
            step_scores=None,
            fact_sheet_data=None
        )
    ]
    db.add_all(cases)
    db.commit()

    # 6. Realistic Vendors with Historical Charts
    v1 = Vendor(
        company_id=company.id,
        name="PT Surya Logam Presisi",
        category="Casing Aluminium & Mekanikal Presisi",
        lead_time_days=4,
        fulfillment_rate=98.5,
        on_time_rate=97.0,
        defect_rate=0.4,
        price_multiplier=1.20,
        min_order_qty=20,
        credit_terms_days=30,
        notes="Supplier grade-1 terakreditasi ISO. Harga sedikit premium namun kualitas konsisten tanpa komplain."
    )
    v2 = Vendor(
        company_id=company.id,
        name="Apex Micro Components Ltd",
        category="Microcontroller MCU & Sensor Semikonduktor",
        lead_time_days=6,
        fulfillment_rate=94.0,
        on_time_rate=93.0,
        defect_rate=1.2,
        price_multiplier=1.10,
        min_order_qty=30,
        credit_terms_days=30,
        notes="Pemasok semikonduktor internasional. Ketaatan jadwal stabil, kapasitas pasokan besar."
    )
    v3 = Vendor(
        company_id=company.id,
        name="CV Mitra Bahari Sentosa",
        category="Baterai & Komponen Elektrik Grosir",
        lead_time_days=10,
        fulfillment_rate=78.0,
        on_time_rate=74.0,
        defect_rate=8.8,
        price_multiplier=0.72,
        min_order_qty=10,
        credit_terms_days=14,
        notes="Harga sangat miring (diskon 28%). Namun defect rate tinggi dan sering terlambat dari jadwal."
    )
    v4 = Vendor(
        company_id=company.id,
        name="PT Mandiri Cipta Display",
        category="Panel Layar AMOLED 1.4 Inch",
        lead_time_days=5,
        fulfillment_rate=91.0,
        on_time_rate=89.0,
        defect_rate=1.8,
        price_multiplier=1.00,
        min_order_qty=15,
        credit_terms_days=60,
        notes="Menyediakan termin pembayaran fleksibel tempo 60 hari. Sangat bersahabat untuk cashflow."
    )
    db.add_all([v1, v2, v3, v4])
    db.commit()
    db.refresh(v1)
    db.refresh(v2)
    db.refresh(v3)
    db.refresh(v4)

    # Historical Metrics for Charts (Bulan -4 s/d Bulan -1)
    histories = [
        # V1
        VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -3", fulfillment_rate=99.0, on_time_rate=98.0, defect_rate=0.3, price_index=120.0),
        VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -2", fulfillment_rate=98.0, on_time_rate=96.5, defect_rate=0.5, price_index=120.0),
        VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -1", fulfillment_rate=98.5, on_time_rate=97.0, defect_rate=0.4, price_index=122.0),
        # V2
        VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -3", fulfillment_rate=95.0, on_time_rate=94.0, defect_rate=1.1, price_index=110.0),
        VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -2", fulfillment_rate=93.5, on_time_rate=92.0, defect_rate=1.3, price_index=110.0),
        VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -1", fulfillment_rate=94.0, on_time_rate=93.0, defect_rate=1.2, price_index=112.0),
        # V3 (High risk)
        VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -3", fulfillment_rate=82.0, on_time_rate=79.0, defect_rate=7.5, price_index=75.0),
        VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -2", fulfillment_rate=75.0, on_time_rate=71.0, defect_rate=9.2, price_index=70.0),
        VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -1", fulfillment_rate=78.0, on_time_rate=74.0, defect_rate=8.8, price_index=72.0),
        # V4
        VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -3", fulfillment_rate=92.0, on_time_rate=90.0, defect_rate=1.6, price_index=100.0),
        VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -2", fulfillment_rate=90.0, on_time_rate=88.0, defect_rate=2.0, price_index=100.0),
        VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -1", fulfillment_rate=91.0, on_time_rate=89.0, defect_rate=1.8, price_index=102.0),
    ]
    db.add_all(histories)
    db.commit()

    # 7. Products & BOM
    p_mcu = Product(company_id=company.id, sku="RAW-MCU-01", name="Chipset Microcontroller MCU-X", product_type="raw_material", cost_price=75000.0, list_price=0.0, current_stock=120.0, min_safety_stock=40.0)
    p_screen = Product(company_id=company.id, sku="RAW-DSP-01", name="Layar AMOLED 1.4 Inch", product_type="raw_material", cost_price=60000.0, list_price=0.0, current_stock=110.0, min_safety_stock=40.0)
    p_bat = Product(company_id=company.id, sku="RAW-BAT-01", name="Baterai Li-Po 450mAh", product_type="raw_material", cost_price=35000.0, list_price=0.0, current_stock=130.0, min_safety_stock=50.0)
    p_case = Product(company_id=company.id, sku="RAW-CAS-01", name="Casing Aluminium CNC", product_type="raw_material", cost_price=40000.0, list_price=0.0, current_stock=90.0, min_safety_stock=30.0)
    p_smartwatch = Product(company_id=company.id, sku="FNG-SW-01", name="Smartwatch VLab Pro 1 (Waterproof)", product_type="finished_good", cost_price=210000.0, list_price=550000.0, current_stock=45.0, min_safety_stock=20.0)

    db.add_all([p_mcu, p_screen, p_bat, p_case, p_smartwatch])
    db.commit()
    db.refresh(p_smartwatch)
    db.refresh(p_mcu)
    db.refresh(p_screen)
    db.refresh(p_bat)
    db.refresh(p_case)

    # BOM
    bom = BillOfMaterials(company_id=company.id, finished_product_id=p_smartwatch.id, name="BOM Standar Smartwatch VLab Pro 1", version="v1.0")
    db.add(bom)
    db.commit()
    db.refresh(bom)

    bom_items = [
        BOMItem(bom_id=bom.id, raw_product_id=p_mcu.id, quantity_required=1.0),
        BOMItem(bom_id=bom.id, raw_product_id=p_screen.id, quantity_required=1.0),
        BOMItem(bom_id=bom.id, raw_product_id=p_bat.id, quantity_required=1.0),
        BOMItem(bom_id=bom.id, raw_product_id=p_case.id, quantity_required=1.0),
    ]
    db.add_all(bom_items)
    db.commit()

    # 8. Work Centers
    wc1 = WorkCenter(company_id=company.id, code="WC-SMT-01", name="Lini Perakitan Elektronik SMT", capacity_units_per_hour=30.0, hourly_cost=180000.0, failure_rate=4.0, status="operational")
    wc2 = WorkCenter(company_id=company.id, code="WC-QC-02", name="Lini Finishing & QC Packaging", capacity_units_per_hour=40.0, hourly_cost=140000.0, failure_rate=2.0, status="operational")
    db.add_all([wc1, wc2])
    db.commit()

    # 9. CRM Leads & Customer Complaints
    leads = [
        CRMLead(
            company_id=company.id,
            title="Pengadaan 120 Unit Smartwatch Korporat",
            customer_name="PT Multi Integra Nusantara",
            customer_email="procurement@multi-integra.co.id",
            stage="proposition",
            expected_revenue=66000000.0,
            probability=75.0,
            priority="high",
            credit_rating="low_risk",
            csat_score=90.0,
            notes="Prospek korporasi untuk program kesehatan karyawan. Menunggu proposal final."
        ),
        CRMLead(
            company_id=company.id,
            title="Tender Perangkat Smart Band Daerah",
            customer_name="Dinas Pemuda & Olahraga Prov. Jabar",
            customer_email="kontak@dispora-jabar.go.id",
            stage="qualified",
            expected_revenue=137500000.0,
            probability=45.0,
            priority="medium",
            credit_rating="low_risk",
            csat_score=85.0,
            notes="Tender terbuka untuk 250 unit perangkat pelacak kebugaran."
        ),
        CRMLead(
            company_id=company.id,
            title="[URGENT KELUHAN] Retur Batch #08 Layar Bergaris",
            customer_name="CV Megah Sentosa",
            customer_email="direktur@megahsentosa.id",
            stage="qualified",
            expected_revenue=150000000.0,
            probability=20.0,
            priority="urgent",
            credit_rating="medium_risk",
            csat_score=35.0,
            is_complaint=True,
            complaint_details="15 unit dari pengiriman kemarin mengalami layar flicker & garis hitam. Akun VIP mengancam memutus kontrak jika tidak ada solusi hari ini!",
            notes="Kasus kritis yang harus segera diselesaikan di Misi 2."
        )
    ]
    db.add_all(leads)
    db.commit()

    # 10. Accounts & Initial Balances
    accounts = [
        Account(company_id=company.id, code="1010", name="Kas & Rekening Bank", account_type="asset", balance=500000000.0),
        Account(company_id=company.id, code="1020", name="Piutang Usaha (AR)", account_type="asset", balance=45000000.0),
        Account(company_id=company.id, code="1030", name="Persediaan Bahan Baku", account_type="asset", balance=45000000.0),
        Account(company_id=company.id, code="1040", name="Persediaan Barang Jadi", account_type="asset", balance=24750000.0),
        Account(company_id=company.id, code="2010", name="Utang Usaha (AP)", account_type="liability", balance=15000000.0),
        Account(company_id=company.id, code="3010", name="Modal Disetor Mahasiswa", account_type="equity", balance=500000000.0),
        Account(company_id=company.id, code="4010", name="Pendapatan Penjualan", account_type="revenue", balance=45000000.0),
        Account(company_id=company.id, code="5010", name="Harga Pokok Penjualan (HPP)", account_type="expense", balance=18900000.0),
        Account(company_id=company.id, code="6010", name="Beban Gaji Karyawan", account_type="expense", balance=25000000.0),
        Account(company_id=company.id, code="6020", name="Beban Pemasaran & Iklan", account_type="expense", balance=10000000.0),
    ]
    db.add_all(accounts)
    db.commit()

    # 11. Department Budgets
    budgets = [
        DepartmentBudget(company_id=company.id, department="Produksi & Manufaktur", allocated_amount=120000000.0, spent_amount=25000000.0, period_name="Bulan 1"),
        DepartmentBudget(company_id=company.id, department="Pengadaan / Purchasing", allocated_amount=150000000.0, spent_amount=35000000.0, period_name="Bulan 1"),
        DepartmentBudget(company_id=company.id, department="Pemasaran / Marketing", allocated_amount=40000000.0, spent_amount=10000000.0, period_name="Bulan 1"),
        DepartmentBudget(company_id=company.id, department="Human Resources (HR)", allocated_amount=60000000.0, spent_amount=25000000.0, period_name="Bulan 1"),
    ]
    db.add_all(budgets)
    db.commit()

    # 12. Employees
    employees = [
        Employee(company_id=company.id, name="Ahmad Fauzi", department="Produksi", role="Kepala Lini Perakitan", monthly_salary=7500000.0, morale_score=92.0, fatigue_score=25.0, status="active"),
        Employee(company_id=company.id, name="Siti Rahma", department="Produksi", role="Operator SMT Mesin 1", monthly_salary=5200000.0, morale_score=90.0, fatigue_score=30.0, status="active"),
        Employee(company_id=company.id, name="Bambang Wijaya", department="Produksi", role="Operator SMT Mesin 2", monthly_salary=5200000.0, morale_score=88.0, fatigue_score=32.0, status="active"),
        Employee(company_id=company.id, name="Dewi Lestari", department="Quality Control", role="Spesialis Inspeksi QC", monthly_salary=6000000.0, morale_score=94.0, fatigue_score=20.0, status="active"),
        Employee(company_id=company.id, name="Rian Pratama", department="Sales & CRM", role="Key Account Executive", monthly_salary=6500000.0, morale_score=91.0, fatigue_score=22.0, status="active"),
    ]
    db.add_all(employees)
    db.commit()

    # 13. Provision Company & Rolling Initial Data for Kelas FEB B
    from backend.app.services.tenant_service import provision_company_data, roll_session_cases
    company_b = Company(
        session_id=session_b.id,
        name="PT Sinergi Prima Nusantara",
        industry="Manufaktur & Distribusi Perangkat Cerdas FEB",
        team_leader_id=mahasiswa_b.id,
        initial_capital=500000000.0,
        current_cash=500000000.0
    )
    db.add(company_b)
    db.commit()
    db.refresh(company_b)
    provision_company_data(db, company_b, session_b)

    # Initial Rolling: Kelas FEB A (Pemasaran Duluan), Kelas FEB B (Keuangan Duluan)
    roll_session_cases(db, session_a.id, "marketing_first")
    roll_session_cases(db, session_b.id, "finance_first")

    print("Seeding completed successfully for FEB A & FEB B!")
    db.close()

if __name__ == "__main__":
    seed_database()
