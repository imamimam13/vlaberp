import json
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Company, ClassSession, SimulationState, SimulationSlider, ScenarioCase,
    Vendor, VendorMetricHistory, Product, BillOfMaterials, BOMItem,
    WorkCenter, CRMLead, Account, DepartmentBudget, Employee, User,
    PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem,
    WorkOrder, JournalEntry, JournalItem, Customer, MarketingCampaign
)
from backend.app.services.behavior_engine import SCENARIO_MATRIX, get_scenario_by_id


def provision_company_data(db: Session, company: Company, session: ClassSession):
    """
    Provisions a complete, isolated ERP & Business Simulation environment
    for a student team tenant company.
    """
    # 1. Simulation State
    sim_state = db.query(SimulationState).filter(SimulationState.company_id == company.id).first()
    if not sim_state:
        sim_state = SimulationState(
            company_id=company.id,
            current_round=1,
            period_name="Bulan 1 (Januari 2026)",
            cash=company.initial_capital or 500000000.0,
            revenue=45000000.0,
            expenses=25000000.0,
            net_profit=20000000.0,
            csat_score=88.5,
            worker_morale=92.0,
            machine_health=95.0,
            supplier_health=91.0,
            overall_score=0.0,
            is_strike_active=False,
            active_case_title="Misi 1: Evaluasi Vendor & Pencegahan Bottleneck Bahan Baku",
            active_case_description="Kelompok diminta melakukan evaluasi kinerja 4 vendor bahan baku. Teliti grafik ketaatan dan defect rate sebelum menerbitkan PO."
        )
        db.add(sim_state)

    # 2. Simulation Slider
    slider = db.query(SimulationSlider).filter(SimulationSlider.company_id == company.id).first()
    if not slider:
        slider = SimulationSlider(
            company_id=company.id,
            session_id=session.id if session else None,
            is_company_override=False,
            supply_disruption=25.0,
            machine_breakdown_risk=15.0,
            market_volatility=30.0,
            labor_strike_risk=10.0,
            bad_debt_risk=15.0,
            competitor_price_war=20.0
        )
        db.add(slider)

    # 3. Scenario Cases (3 Problem-Based Learning Missions)
    existing_cases = db.query(ScenarioCase).filter(ScenarioCase.company_id == company.id).count()
    if existing_cases == 0:
        session_id = session.id if session else None
        cases = [
            ScenarioCase(
                session_id=session_id,
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
                session_id=session_id,
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
                session_id=session_id,
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

    # 4. Realistic Vendors with Historical Charts
    existing_vendors = db.query(Vendor).filter(Vendor.company_id == company.id).count()
    if existing_vendors == 0:
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
        db.flush()

        histories = [
            VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -3", fulfillment_rate=99.0, on_time_rate=98.0, defect_rate=0.3, price_index=120.0),
            VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -2", fulfillment_rate=98.0, on_time_rate=96.5, defect_rate=0.5, price_index=120.0),
            VendorMetricHistory(vendor_id=v1.id, period_label="Bulan -1", fulfillment_rate=98.5, on_time_rate=97.0, defect_rate=0.4, price_index=122.0),
            VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -3", fulfillment_rate=95.0, on_time_rate=94.0, defect_rate=1.1, price_index=110.0),
            VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -2", fulfillment_rate=93.5, on_time_rate=92.0, defect_rate=1.3, price_index=110.0),
            VendorMetricHistory(vendor_id=v2.id, period_label="Bulan -1", fulfillment_rate=94.0, on_time_rate=93.0, defect_rate=1.2, price_index=112.0),
            VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -3", fulfillment_rate=82.0, on_time_rate=79.0, defect_rate=7.5, price_index=75.0),
            VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -2", fulfillment_rate=75.0, on_time_rate=71.0, defect_rate=9.2, price_index=70.0),
            VendorMetricHistory(vendor_id=v3.id, period_label="Bulan -1", fulfillment_rate=78.0, on_time_rate=74.0, defect_rate=8.8, price_index=72.0),
            VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -3", fulfillment_rate=92.0, on_time_rate=90.0, defect_rate=1.6, price_index=100.0),
            VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -2", fulfillment_rate=90.0, on_time_rate=88.0, defect_rate=2.0, price_index=100.0),
            VendorMetricHistory(vendor_id=v4.id, period_label="Bulan -1", fulfillment_rate=91.0, on_time_rate=89.0, defect_rate=1.8, price_index=102.0),
        ]
        db.add_all(histories)

    # 5. Products & BOM
    existing_products = db.query(Product).filter(Product.company_id == company.id).count()
    if existing_products == 0:
        p_mcu = Product(company_id=company.id, sku=f"RAW-MCU-{company.id:02d}", name="Chipset Microcontroller MCU-X", product_type="raw_material", cost_price=75000.0, list_price=0.0, current_stock=120.0, min_safety_stock=40.0)
        p_screen = Product(company_id=company.id, sku=f"RAW-DSP-{company.id:02d}", name="Layar AMOLED 1.4 Inch", product_type="raw_material", cost_price=60000.0, list_price=0.0, current_stock=110.0, min_safety_stock=40.0)
        p_bat = Product(company_id=company.id, sku=f"RAW-BAT-{company.id:02d}", name="Baterai Li-Po 450mAh", product_type="raw_material", cost_price=35000.0, list_price=0.0, current_stock=130.0, min_safety_stock=50.0)
        p_case = Product(company_id=company.id, sku=f"RAW-CAS-{company.id:02d}", name="Casing Aluminium CNC", product_type="raw_material", cost_price=40000.0, list_price=0.0, current_stock=90.0, min_safety_stock=30.0)
        p_smartwatch = Product(company_id=company.id, sku=f"FNG-SW-{company.id:02d}", name=f"Smartwatch VLab Pro {company.id} (Waterproof)", product_type="finished_good", cost_price=210000.0, list_price=550000.0, current_stock=45.0, min_safety_stock=20.0)

        db.add_all([p_mcu, p_screen, p_bat, p_case, p_smartwatch])
        db.flush()

        bom = BillOfMaterials(company_id=company.id, finished_product_id=p_smartwatch.id, name=f"BOM Standar Smartwatch Pro {company.id}", version="v1.0")
        db.add(bom)
        db.flush()

        bom_items = [
            BOMItem(bom_id=bom.id, raw_product_id=p_mcu.id, quantity_required=1.0),
            BOMItem(bom_id=bom.id, raw_product_id=p_screen.id, quantity_required=1.0),
            BOMItem(bom_id=bom.id, raw_product_id=p_bat.id, quantity_required=1.0),
            BOMItem(bom_id=bom.id, raw_product_id=p_case.id, quantity_required=1.0),
        ]
        db.add_all(bom_items)

    # 6. Work Centers
    existing_wc = db.query(WorkCenter).filter(WorkCenter.company_id == company.id).count()
    if existing_wc == 0:
        wc1 = WorkCenter(company_id=company.id, code=f"WC-SMT-{company.id:02d}", name="Lini Perakitan Elektronik SMT", capacity_units_per_hour=30.0, hourly_cost=180000.0, failure_rate=4.0, status="operational")
        wc2 = WorkCenter(company_id=company.id, code=f"WC-QC-{company.id:02d}", name="Lini Finishing & QC Packaging", capacity_units_per_hour=40.0, hourly_cost=140000.0, failure_rate=2.0, status="operational")
        db.add_all([wc1, wc2])

    # 7. CRM Leads & Customer Complaints
    existing_leads = db.query(CRMLead).filter(CRMLead.company_id == company.id).count()
    if existing_leads == 0:
        leads = [
            CRMLead(
                company_id=company.id,
                title="Inbound Inquiries: Retailer Gadget TokoPDA (50 Unit)",
                customer_name="TokoPDA Megastore Jakarta",
                customer_email="buying@tokopda.com",
                stage="new",
                expected_revenue=27500000.0,
                probability=30.0,
                priority="medium",
                credit_rating="low_risk",
                csat_score=88.0,
                notes="Permintaan penawaran via e-catalog untuk 50 unit Smartwatch VLab Pro batch reguler."
            ),
            CRMLead(
                company_id=company.id,
                title="Permintaan Kerjasama Distribusi Wilayah Timur (80 Unit)",
                customer_name="CV Borneo Smart Devices",
                customer_email="distribusi@borneosmart.id",
                stage="new",
                expected_revenue=44000000.0,
                probability=25.0,
                priority="medium",
                credit_rating="low_risk",
                csat_score=85.0,
                notes="Calon distributor regional Kalimantan meminta profil produk dan termin pembayaran konsinyasi/tempo 30 hari."
            ),
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

    # 8. Chart of Accounts (COA)
    existing_accounts = db.query(Account).filter(Account.company_id == company.id).count()
    if existing_accounts == 0:
        accounts = [
            Account(company_id=company.id, code="1010", name="Kas & Rekening Bank", account_type="asset", balance=company.initial_capital or 500000000.0),
            Account(company_id=company.id, code="1020", name="Piutang Usaha (AR)", account_type="asset", balance=45000000.0),
            Account(company_id=company.id, code="1030", name="Persediaan Bahan Baku", account_type="asset", balance=45000000.0),
            Account(company_id=company.id, code="1040", name="Persediaan Barang Jadi", account_type="asset", balance=24750000.0),
            Account(company_id=company.id, code="2010", name="Utang Usaha (AP)", account_type="liability", balance=15000000.0),
            Account(company_id=company.id, code="3010", name="Modal Disetor Mahasiswa", account_type="equity", balance=company.initial_capital or 500000000.0),
            Account(company_id=company.id, code="4010", name="Pendapatan Penjualan", account_type="revenue", balance=45000000.0),
            Account(company_id=company.id, code="5010", name="Harga Pokok Penjualan (HPP)", account_type="expense", balance=18900000.0),
            Account(company_id=company.id, code="6010", name="Beban Gaji Karyawan", account_type="expense", balance=25000000.0),
            Account(company_id=company.id, code="6020", name="Beban Pemasaran & Iklan", account_type="expense", balance=10000000.0),
        ]
        db.add_all(accounts)

    # 9. Department Budgets
    existing_budgets = db.query(DepartmentBudget).filter(DepartmentBudget.company_id == company.id).count()
    if existing_budgets == 0:
        budgets = [
            DepartmentBudget(company_id=company.id, department="Produksi & Manufaktur", allocated_amount=120000000.0, spent_amount=25000000.0, period_name="Bulan 1"),
            DepartmentBudget(company_id=company.id, department="Pengadaan / Purchasing", allocated_amount=150000000.0, spent_amount=35000000.0, period_name="Bulan 1"),
            DepartmentBudget(company_id=company.id, department="Pemasaran / Marketing", allocated_amount=40000000.0, spent_amount=10000000.0, period_name="Bulan 1"),
            DepartmentBudget(company_id=company.id, department="Human Resources (HR)", allocated_amount=60000000.0, spent_amount=25000000.0, period_name="Bulan 1"),
        ]
        db.add_all(budgets)

    # 10. Employees
    existing_employees = db.query(Employee).filter(Employee.company_id == company.id).count()
    if existing_employees == 0:
        employees = [
            Employee(company_id=company.id, name="Ahmad Fauzi", department="Produksi", role="Kepala Lini Perakitan", monthly_salary=7500000.0, morale_score=92.0, fatigue_score=25.0, status="active"),
            Employee(company_id=company.id, name="Siti Rahma", department="Produksi", role="Operator SMT Mesin 1", monthly_salary=5200000.0, morale_score=90.0, fatigue_score=30.0, status="active"),
            Employee(company_id=company.id, name="Bambang Wijaya", department="Produksi", role="Operator SMT Mesin 2", monthly_salary=5200000.0, morale_score=88.0, fatigue_score=32.0, status="active"),
            Employee(company_id=company.id, name="Dewi Lestari", department="Quality Control", role="Spesialis Inspeksi QC", monthly_salary=6000000.0, morale_score=94.0, fatigue_score=20.0, status="active"),
            Employee(company_id=company.id, name="Rian Pratama", department="Sales & CRM", role="Key Account Executive", monthly_salary=6500000.0, morale_score=91.0, fatigue_score=22.0, status="active"),
        ]
        db.add_all(employees)

    db.commit()


def reset_company_data(db: Session, company_id: int):
    """
    Purges transactional and state data for a company and re-seeds baseline data.
    100% Robust purge of all student inputs and transactions.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return False
    
    session = company.session

    # 1. Clean all student transaction records
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

    db.query(Customer).filter(Customer.company_id == company_id).delete()
    db.query(MarketingCampaign).filter(MarketingCampaign.company_id == company_id).delete()

    # 2. Delete existing child master & state data
    db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).delete()
    db.query(CRMLead).filter(CRMLead.company_id == company_id).delete()
    db.query(Account).filter(Account.company_id == company_id).delete()
    db.query(DepartmentBudget).filter(DepartmentBudget.company_id == company_id).delete()
    db.query(Employee).filter(Employee.company_id == company_id).delete()
    db.query(WorkCenter).filter(WorkCenter.company_id == company_id).delete()
    
    # Clean BOM and Products
    boms = db.query(BillOfMaterials).filter(BillOfMaterials.company_id == company_id).all()
    for b in boms:
        db.delete(b)
    db.query(Product).filter(Product.company_id == company_id).delete()

    # Clean Vendors
    vendors = db.query(Vendor).filter(Vendor.company_id == company_id).all()
    for v in vendors:
        db.delete(v)

    # Clean state and sliders
    db.query(SimulationState).filter(SimulationState.company_id == company_id).delete()
    db.query(SimulationSlider).filter(SimulationSlider.company_id == company_id).delete()

    # Reset company cash balance to initial capital
    company.current_cash = company.initial_capital or 500000000.0
    db.commit()

    # 3. Re-provision clean baseline data
    provision_company_data(db, company, session)
    return True


def seed_multi_tenants(db: Session):
    """
    Ensures at least 3 distinct student group tenant companies and login accounts exist.
    """
    from passlib.context import CryptContext
    from backend.app.models.models import User
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    session = db.query(ClassSession).first()
    if not session:
        return

    # 1. Ensure student group users exist
    groups_data = [
        ("kelompok1", "Kelompok 1 (PT Inovasi Cipta Mandiri)", "k1@mahasiswa.vlaberp.ac.id"),
        ("kelompok2", "Kelompok 2 (PT Techno Sinergi Nusantara)", "k2@mahasiswa.vlaberp.ac.id"),
        ("kelompok3", "Kelompok 3 (PT Nusantara Elektronika Medika)", "k3@mahasiswa.vlaberp.ac.id"),
        ("kelompok4", "Kelompok 4 (PT Sinergi Baterai Nusantara)", "k4@mahasiswa.vlaberp.ac.id"),
    ]

    user_map = {}
    for username, full_name, email in groups_data:
        usr = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if not usr:
            usr = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=pwd_ctx.hash("mhs123"),
                role="MAHASISWA"
            )
            db.add(usr)
            db.commit()
            db.refresh(usr)
        else:
            usr.username = username
            usr.full_name = full_name
            db.commit()
        user_map[username] = usr

    # Also keep demo 'mahasiswa' alias linked to kelompok 1
    mhs_alias = db.query(User).filter(User.username == "mahasiswa").first()
    if not mhs_alias:
        mhs_alias = User(
            username="mahasiswa",
            email="mahasiswa@vlaberp.ac.id",
            full_name="Mahasiswa Kelompok 1",
            hashed_password=pwd_ctx.hash("mhs123"),
            role="MAHASISWA"
        )
        db.add(mhs_alias)
        db.commit()

    # Check companies
    existing_companies = db.query(Company).filter(Company.session_id == session.id).all()
    
    # 1. Company 1 (PT Inovasi Cipta Mandiri)
    if len(existing_companies) >= 1:
        c1 = existing_companies[0]
        if "kelompok1" in user_map:
            c1.team_leader_id = user_map["kelompok1"].id
            db.commit()
        provision_company_data(db, c1, session)

    # 2. Company 2 (Kelompok 2 - PT Techno Sinergi Nusantara)
    c2 = db.query(Company).filter(Company.name == "PT Techno Sinergi Nusantara").first()
    if not c2:
        c2 = Company(
            session_id=session.id,
            name="PT Techno Sinergi Nusantara",
            industry="Komponen IoT & Sensor Pintar",
            team_leader_id=user_map["kelompok2"].id if "kelompok2" in user_map else None,
            initial_capital=500000000.0,
            current_cash=500000000.0
        )
        db.add(c2)
        db.commit()
        db.refresh(c2)
    else:
        if not c2.team_leader_id and "kelompok2" in user_map:
            c2.team_leader_id = user_map["kelompok2"].id
            db.commit()
    provision_company_data(db, c2, session)

    # 3. Company 3 (Kelompok 3 - PT Nusantara Elektronika Medika)
    c3 = db.query(Company).filter(Company.name == "PT Nusantara Elektronika Medika").first()
    if not c3:
        c3 = Company(
            session_id=session.id,
            name="PT Nusantara Elektronika Medika",
            industry="Alat Kesehatan & Monitoring Digital",
            team_leader_id=user_map["kelompok3"].id if "kelompok3" in user_map else None,
            initial_capital=500000000.0,
            current_cash=500000000.0
        )
        db.add(c3)
        db.commit()
        db.refresh(c3)
    else:
        if not c3.team_leader_id and "kelompok3" in user_map:
            c3.team_leader_id = user_map["kelompok3"].id
            db.commit()
    provision_company_data(db, c3, session)

    # 4. Company 4 if exists (PT Sinergi Baterai Nusantara)
    c4 = db.query(Company).filter(Company.name == "PT Sinergi Baterai Nusantara").first()
    if c4 and not c4.team_leader_id and "kelompok4" in user_map:
        c4.team_leader_id = user_map["kelompok4"].id
        db.commit()


# =====================================================================
# 12 PRESET INDUSTRY PROFILES & CASE VARIATION CATALOG
# =====================================================================

PRESET_TENANTS = [
    {"name": "PT Inovasi Cipta Mandiri", "industry": "Smart Device IoT & Wearables", "group_num": 1},
    {"name": "PT Techno Sinergi Nusantara", "industry": "Komponen Sensor Industri & Robotika", "group_num": 2},
    {"name": "PT Nusantara Elektronika Medika", "industry": "Alat Kesehatan & Monitoring Digital", "group_num": 3},
    {"name": "PT Sinergi Baterai Nusantara", "industry": "Sistem Penyimpanan Energi & Baterai EV", "group_num": 4},
    {"name": "PT Otomasi Presisi Indonesia", "industry": "Mikrokontroler & Otomasi Lini Pabrik", "group_num": 5},
    {"name": "PT Aero Telemetri Global", "industry": "Sistem Avionik Drone & Navigasi Cerdas", "group_num": 6},
    {"name": "PT Optika Laser Nusantara", "industry": "Komponen Optik Presisi & Sensor Laser", "group_num": 7},
    {"name": "PT Eco Daya Energi", "industry": "Inverter Surya Pintar & Green Energy", "group_num": 8},
    {"name": "PT Bio Instrumentasi Medika", "industry": "Biosensor Diagnostik & Analisis Lab", "group_num": 9},
    {"name": "PT Telekomika Nusantara Satelit", "industry": "Modul Komunikasi Satelit & Antena Array", "group_num": 10},
    {"name": "PT Mekatronika Otomotif Mandiri", "industry": "ECU Kendaraan Cerdas & Instrument Cluster", "group_num": 11},
    {"name": "PT Quantum Nano Semikonduktor", "industry": "Komponen Semikonduktor & Nanomaterial", "group_num": 12},
]

DIFFERENTIATED_CASE_PACKS = [
    # Pack 1: SCM Supply Chain Crisis
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Krisis Pasokan: Rekanan Pemasok Utama Cacat 8.8% & Keterlambatan Pasokan",
            "category": "purchasing",
            "description": "Supplier bahan baku utama mengalami lonjakan tingkat cacat bahan hingga 8.8% serta keterlambatan kirim 10 hari. Lini perakitan terancam berhenti total jika PO baru diterbitkan ke supplier ini tanpa audit rekam jejak.",
            "trigger_hint": "Buka modul Rekanan Vendor, bandingkan rasio cacat (defect rate) dan waktu tunggu (lead time) keempat vendor.",
            "solvable_workflow": "1. Alihkan Purchase Order (PO) ke PT Surya Logam Presisi (defect 0.4%).\n2. Terbitkan PO minimal 50 unit.\n3. Tolak pesanan tambahan ke rekanan cacat.",
            "resolution_criteria": "PO berhasil diterbitkan ke supplier grade-1 dengan defect < 1.0% dan tingkat pemenuhan tepat waktu.",
            "fact_sheet_data": {
                "root_cause": "Ketergantungan pada satu rekanan murah tanpa memeriksa rekam jejak defect rate historis.",
                "best_practice": "Pilih rekanan terakreditasi ISO meskipun harga unit sedikit lebih tinggi guna menghindari kerugian retur massal."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Negosiasi Ulang Kontrak Pengadaan & Mitigasi Fluktuasi Harga Bahan Baku",
            "category": "purchasing",
            "description": "Vendor semikonduktor mengumumkan kenaikan harga 25% mendadak. Manajemen harus menegosiasikan kontrak pengadaan volume besar (bulk order) dengan klausul termin kredit 60 hari.",
            "trigger_hint": "Tinjau syarat kredit dan minimum order qty pada master data rekanan.",
            "solvable_workflow": "1. Evaluasi konsumsi bahan baku perakitan.\n2. Lakukan purchase order konsolidasi untuk mendapatkan diskon kuantitas.\n3. Catat komitmen termin pembayaran di Akuntansi.",
            "resolution_criteria": "HPP terkendali di bawah batas pagu dan kontinuitas suplai terjamin untuk 3 periode.",
            "fact_sheet_data": {
                "root_cause": "Pembelian spot market eceran menyebabkan harga beli rentan fluktuasi.",
                "best_practice": "Gunakan blanket purchase agreement dan manfaatkan skala ekonomis volume pembelian."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Audit Kepatuhan Rantai Pasok (SCM) & Implementasi Multi-Sourcing",
            "category": "purchasing",
            "description": "Risiko geopolitik mengancam jalur logistik impor. Perusahaan harus menetapkan pemasok alternatif cadangan lokal untuk menghindari single-point-of-failure.",
            "trigger_hint": "Daftarkan vendor cadangan baru di modul Purchasing.",
            "solvable_workflow": "1. Daftarkan master vendor lokal cadangan.\n2. Lakukan uji sampel batch kecil.\n3. Alokasikan 30% kuota PO ke suplier lokal.",
            "resolution_criteria": "Ketergantungan single-source tereliminasi, buffer stock aman.",
            "fact_sheet_data": {
                "root_cause": "Konsentrasi 100% pesanan pada satu suplier impor tunggal.",
                "best_practice": "Strategi dual-sourcing 70/30 membagi risiko tanpa mengorbankan skala diskon."
            }
        }
    ],

    # Pack 2: CRM Customer Quality Scandal
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Skandal Mutu Klien VIP Enterprise: Retur 100 Unit & Ancaman Pemutusan Kontrak",
            "category": "crm",
            "description": "Klien enterprise terbesar (CV Megah Sentosa, nilai kontrak Rp 150.000.000) menerima 100 unit perangkat bergaris. Klien mengancam menahan sisa pembayaran dan menuntut penalti ganti rugi.",
            "trigger_hint": "Buka modul CRM -> Cari tiket keluhan darurat CV Megah Sentosa.",
            "solvable_workflow": "1. Buka tiket keluhan darurat di modul CRM.\n2. Setujui paket mitigasi: Ganti 15 unit baru gratis + Voucher diskon 10% pesanan berikutnya.\n3. Konfirmasi Work Order darurat di Pabrik.",
            "resolution_criteria": "Tiket terselesaikan, retensi klien berhasil, CSAT pulih di atas 80%.",
            "fact_sheet_data": {
                "root_cause": "Kegagalan sensor QC pada stasiun akhir meloloskan batch cacat ke klien enterprise.",
                "best_practice": "Customer service proaktif dengan kompensasi nyata jauh lebih murah daripada kehilangan akun bernilai ratusan juta."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Kebijakan Garansi Cepat & Pemulihan Reputasi Merek (CSAT)",
            "category": "crm",
            "description": "Keluhan pelanggan menyebar di media sosial industri, menurunkan sentimen pasar dan moral tenaga penjualan. Layanan bantuan kilat 24 jam harus segera diaktifkan.",
            "trigger_hint": "Tinjau skor CSAT di CRM dan sesuaikan prioritas pipeline prospek.",
            "solvable_workflow": "1. Buka pipeline CRM.\n2. Tingkatkan prioritas akun komplain ke Urgent.\n3. Terbitkan surat permintaan maaf resmi dan garansi penggantian 1x24 jam.",
            "resolution_criteria": "CSAT naik kembali di atas 85%, pipeline prospek baru tidak mengalami churn.",
            "fact_sheet_data": {
                "root_cause": "Keterlambatan respon penanganan komplain di awal kejadian.",
                "best_practice": "Standar respon Service Level Agreement (SLA) ketat di bawah 2 jam untuk akun VIP."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Pencatatan Penyesuaian Akuntansi: Credit Note & Retensi Nilai Kontrak",
            "category": "crm",
            "description": "Kompensasi retur memerlukan penyesuaian nilai piutang di buku besar tanpa merusak struktur arus kas operasional.",
            "trigger_hint": "Sinkronkan modul CRM dengan Buku Besar Akuntansi.",
            "solvable_workflow": "1. Terbitkan Credit Note penyesuaian harga di CRM.\n2. Catat pemotongan piutang tertagih di Akuntansi.\n3. Perpanjang kontrak pemeliharaan tahunan.",
            "resolution_criteria": "Jurnal tercatat balance, klien menandatangani perpanjangan kontrak tahun depan.",
            "fact_sheet_data": {
                "root_cause": "Ketidaksinkronan data diskon penjualan antara bagian sales dan kasir akuntansi.",
                "best_practice": "Integrasi real-time antara CRM dan General Ledger mencegah perselisihan faktur."
            }
        }
    ],

    # Pack 3: HR Labor Relations & Strike Prevention
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Tuntutan Uang Lembur & Ancaman Mogok Kerja Serikat Buruh SPMI",
            "category": "hr",
            "description": "Operator lini perakitan mengeluhkan jam lembur berlebih akibat target pesanan dadakan tanpa kompensasi uang makan. Serikat buruh mengeluarkan surat peringatan mogok kerja 3 hari.",
            "trigger_hint": "Pantau indikator Moral Pekerja di modul HR dan rasio kas operasional.",
            "solvable_workflow": "1. Buka meja dialog bipartit di modul HR.\n2. Setujui kenaikan upah wajar (+8-12%) dan paket bonus lembur damai Rp 1.500.000.\n3. Pastikan kas operasional mencukupi pencairan payroll.",
            "resolution_criteria": "Moral pekerja di atas 85%, pemogokan dibatalkan, kontinuitas lini produksi aman.",
            "fact_sheet_data": {
                "root_cause": "Beban kerja lembur meningkat 40% tanpa penyesuaian insentif kesejahteraan.",
                "best_practice": "Dialog bipartit terbuka dan pembagian bonus insentif produktivitas menjamin stabilitas buruh."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Standardisasi Keselamatan Kerja (K3) & Ergonomi Lini Perakitan",
            "category": "hr",
            "description": "Terjadi 2 insiden cedera ringan pada stasiun solder manual akibat pencahayaan dan alat pelindung diri (APD) yang aus. Staf menolak bekerja lembur sebelum ada perbaikan K3.",
            "trigger_hint": "Tinjau kondisi pegawai di modul HR dan alokasikan pagu anggaran perbaikan lingkungan kerja.",
            "solvable_workflow": "1. Buka modul Akuntansi -> Tambahkan anggaran K3 senilai Rp 15.000.000.\n2. Perbarui catatan inventaris APD di modul HR.\n3. Berikan pelatihan K3 berkala kepada kepala regu perakitan.",
            "resolution_criteria": "Insiden kerja nol (zero incident), absensi menurun di bawah 2%.",
            "fact_sheet_data": {
                "root_cause": "Penghematan anggaran operasional yang memangkas pos perlengkapan keselamatan kerja.",
                "best_practice": "Investasi K3 merupakan perlindungan aset terpenting industri: tenaga kerja terampil."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Perjanjian Kerja Bersama (PKB) & Skema Bonus Berbasis KPI Produksi",
            "category": "hr",
            "description": "Guna menyelaraskan kepentingan manajemen dan buruh jangka panjang, serikat pekerja mengusulkan penandatanganan PKB baru dengan klausul profit sharing.",
            "trigger_hint": "Buka modul HR -> Selesaikan perundingan PKB jangka panjang.",
            "solvable_workflow": "1. Susun formula bonus berbasis persentase pencapaian output bebas cacat.\n2. Tanda tangani nota kesepakatan bersama serikat buruh.\n3. Monitor kenaikan produktivitas jam kerja.",
            "resolution_criteria": "PKB disepakati tanpa sengketa perburuhan, moral kerja mencapai 95%.",
            "fact_sheet_data": {
                "root_cause": "Ketidakpastian skema remunerasi tahunan menimbulkan kecurigaan serikat pekerja.",
                "best_practice": "Sistem insentif transparan berbasis KPI produktivitas menyatukan target buruh dan laba perusahaan."
            }
        }
    ],

    # Pack 4: Accounting Cash Liquidity & Bad Debt Crisis
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Krisis Piutang Macet (Bad Debt): Pelanggan Retail Gagal Bayar Rp 120 Juta",
            "category": "accounting",
            "description": "Distributor retail regional mengalami kebangkrutan, menyebabkan piutang dagang Rp 120.000.000 macet. Saldo kas bank menipis tajam mendekati batas kritis penggajian bulanan.",
            "trigger_hint": "Buka modul Akuntansi -> Tinjau saldo kas, rasio piutang tak tertagih, dan buku besar.",
            "solvable_workflow": "1. Bentuk cadangan kerugian piutang tak tertagih di buku besar.\n2. Lakukan penghematan anggaran promosi non-esensial.\n3. Perketat syarat pembayaran pelanggan baru menjadi DP minimal 50%.",
            "resolution_criteria": "Saldo kas tetap di atas safety cash level (Rp 200jt), penggajian tetap lancar.",
            "fact_sheet_data": {
                "root_cause": "Pemberian plafon kredit penjualan tanpa analisis kelayakan skor kredit pelanggan.",
                "best_practice": "Penerapan kebijakan batas kredit (credit limit) ketat dan penagihan berjangka."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Restrukturisasi Utang Vendor & Negosiasi Perpanjangan Fasilitas Kredit Bank",
            "category": "accounting",
            "description": "Jatuh tempo tagihan faktur pemasok Rp 85.000.000 bertepatan dengan tanggal pembayaran pajak penghasilan. Manajemen harus menegosiasikan perpanjangan tenor pembayaran tanpa penalti bunga.",
            "trigger_hint": "Periksa daftar akun utang dagang (Accounts Payable) dan pagu anggaran divisi.",
            "solvable_workflow": "1. Ajukan penjadwalan cicilan pembayaran utang (debt rescheduling) 3 termin.\n2. Bayar termin pertama secara tunai sebagai tanda itikad baik.\n3. Amankan fasilitas letter of credit bank.",
            "resolution_criteria": "Status kredit perusahaan terjaga 'Lancar', tidak ada pembekuan pasokan bahan.",
            "fact_sheet_data": {
                "root_cause": "Mismatch maturitas antara arus kas masuk dari piutang dan jadwal pembayaran tagihan utang.",
                "best_practice": "Penyusunan cash flow forecast mingguan mencegah kejutan defisit kas."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Optimalisasi Modal Kerja (Working Capital Management) & Efisiensi Biaya Overhead",
            "category": "accounting",
            "description": "Biaya listrik industri dan overhead pabrik membengkak 35% akibat utilisasi mesin di luar jam hemat tarif (WBP). Diperlukan rasionalisasi alokasi pagu anggaran departemen.",
            "trigger_hint": "Buka modul Akuntansi -> Kelola Pagu Anggaran Departemen (Budgets).",
            "solvable_workflow": "1. Pangkas pagu anggaran overhead non-kritis sebesar 20%.\n2. Jadwalkan ulang jam operasional mesin pabrik ke tarif listrik luar beban puncak.\n3. Pantau rasio laba bersih pada laporan laba rugi.",
            "resolution_criteria": "Margin laba bersih naik kembali di atas 15%, efisiensi overhead tercapai.",
            "fact_sheet_data": {
                "root_cause": "Pengoperasian mesin boros daya pada jam beban puncak PLN tanpa pemantauan kWh.",
                "best_practice": "Manajemen energi terintegrasi dengan jadwal Work Order memangkas biaya utilitas secara signifikan."
            }
        }
    ],

    # Pack 5: MRP Manufacturing Breakdown & Work Center Downtime
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Kerusakan Kritis Motor Servo Mesin SMT-01: Lini Pabrik Lumpuh Total",
            "category": "mrp",
            "description": "Motor servo pada stasiun Surface Mount Technology (SMT-01) mengalami overheat akibat lonjakan beban produksi tanpa jeda pendinginan. Output stasiun perakitan turun menjadi 0 unit/jam.",
            "trigger_hint": "Buka modul Mesin & Pabrik MRP -> Tinjau status stasiun kerja dan tombol maintenance.",
            "solvable_workflow": "1. Eksekusi tindakan darurat perbaikan/maintenance stasiun kerja SMT-01.\n2. Alihkan sebagian beban perakitan manual sementara ke stasiun kerja QC-02.\n3. Terbitkan work order penyesuaian kuantitas agar pesanan pelanggan tetap terkirim.",
            "resolution_criteria": "Status mesin pulih menjadi 'operational', kesehatan mesin naik di atas 90%, downtime teratasi.",
            "fact_sheet_data": {
                "root_cause": "Mesin dipaksa beroperasi 150% kapasitas tanpa pelumasan dan kalibrasi rutin.",
                "best_practice": "Total Productive Maintenance (TPM) terjadwal mencegah kerugian downtime miliaran rupiah."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Optimalisasi Resep Bill of Materials (BOM) & Eliminasi Scrap Bahan Baku",
            "category": "mrp",
            "description": "Proses perakitan menghasilkan limbah scrap aluminium dan solder paste sebesar 12% di atas standar industri. Resep BOM memerlukan penyesuaian presisi.",
            "trigger_hint": "Tinjau tabel Bill of Materials di modul MRP.",
            "solvable_workflow": "1. Periksa komponen pada resep BOM produk utama.\n2. Kalibrasi toleransi pemotongan bahan pada stasiun kerja.\n3. Uji coba perakitan batch 30 unit dengan parameter baru.",
            "resolution_criteria": "Scrap rate turun di bawah 1.5%, efisiensi bahan meningkat.",
            "fact_sheet_data": {
                "root_cause": "Penggunaan resep BOM usang yang tidak disesuaikan dengan spesifikasi bahan baku vendor baru.",
                "best_practice": "Engineering change order (ECO) berkala untuk memperbarui toleransi resep BOM."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Peningkatan Kapasitas Work Center Menuju Sertifikasi Standar Otomotif IATF",
            "category": "mrp",
            "description": "Untuk menembus pasar ekspor OEM tier-1, pabrik harus meningkatkan kapabilitas proses (Cpk > 1.33) dan mengadopsi stasiun pengujian otomatis.",
            "trigger_hint": "Tingkatkan kapasitas stasiun kerja QC di modul MRP.",
            "solvable_workflow": "1. Tambahkan work center sensor pengujian otomatis.\n2. Latih operator untuk menjalankan SPC (Statistical Process Control).\n3. Validasi hasil uji batch bebas cacat.",
            "resolution_criteria": "Kapasitas produksi naik 25%, tingkat lolos QC mencapai 99.5%.",
            "fact_sheet_data": {
                "root_cause": "Pengujian manual yang mengandalkan mata operator rentan terhadap kelelahan visual.",
                "best_practice": "Automated Optical Inspection (AOI) memastikan zero-defect pada komponen presisi tinggi."
            }
        }
    ],

    # Pack 6: Market Price War & Global Competitor Shock
    [
        {
            "code": "CASE-01",
            "stage_order": 1,
            "title": "Perang Harga Kompetitor Global: Pemotongan Harga 25% Mengikis Margin",
            "category": "crm",
            "description": "Kompetitor multinasional meluncurkan produk substitusi dengan harga 25% lebih murah, menyebabkan penurunan prospek penutupan penjualan (closing rate) hingga separuh.",
            "trigger_hint": "Tinjau harga jual produk dan pipeline peluang di modul CRM.",
            "solvable_workflow": "1. Jangan langsung memangkas harga jual secara drastis.\n2. Tawarkan garansi purnajual 3 tahun dan paket instalasi gratis sebagai diferensiasi nilai.\n3. Dekati akun prospek potensial bernilai besar dengan penawaran kustom.",
            "resolution_criteria": "Closing rate pulih di atas 60%, marjin keuntungan tetap terjaga positif.",
            "fact_sheet_data": {
                "root_cause": "Komoditisasi produk akibat minimnya diferensiasi nilai tambah layanan.",
                "best_practice": "Value-based selling mengalahkan perang harga murah yang merusak industri."
            }
        },
        {
            "code": "CASE-02",
            "stage_order": 2,
            "title": "Efisiensi Biaya Pokok Produksi (HPP) Lewat Rekayasa Nilai (Value Engineering)",
            "category": "mrp",
            "description": "Manajemen menargetkan penurunan HPP sebesar 15% tanpa mengurangi durabilitas produk agar harga jual lebih kompetitif di pasar retail.",
            "trigger_hint": "Evaluasi biaya komponen BOM dan harga beli rekanan di Purchasing.",
            "solvable_workflow": "1. Lakukan audit biaya per komponen di resep BOM.\n2. Negosiasi ulang harga casing aluminium dengan suplier grade-1.\n3. Kurangi waktu siklus perakitan di work center.",
            "resolution_criteria": "HPP per unit turun 15%, marjin laba kotor meningkat ke 35%.",
            "fact_sheet_data": {
                "root_cause": "Over-design pada komponen sekunder yang tidak menambah nilai fungsi utama bagi konsumen.",
                "best_practice": "Value engineering menyederhanakan desain suku cadang tanpa mengurangi kekuatan struktural."
            }
        },
        {
            "code": "CASE-03",
            "stage_order": 3,
            "title": "Diversifikasi Portofolio Produk & Ekspansi Kanal Penjualan Institusi B2G",
            "category": "crm",
            "description": "Guna mengurangi ketergantungan pada pasar bebas yang fluktuatif, tim sales membidik tender pengadaan sistem digital instansi pemerintah bernilai Rp 300.000.000.",
            "trigger_hint": "Buka modul CRM -> Daftarkan akun prospek institusi baru.",
            "solvable_workflow": "1. Daftarkan prospek tender pengadaan institusi B2G di CRM.\n2. Lengkapi berkas kualifikasi teknis dan sertifikasi TKDN produk.\n3. Konversi prospek menjadi pesanan penjualan resmi.",
            "resolution_criteria": "Tender berhasil dimenangkan, pendapatan melonjak di atas target semester.",
            "fact_sheet_data": {
                "root_cause": "Ketergantungan 100% pada pasar konsumen retail yang sangat elastis terhadap harga.",
                "best_practice": "Porsi kontrak korporat dan institusi jangka panjang memberikan bantalan pendapatan yang stabil."
            }
        }
    ]
]


def differentiate_tenant_cases(db: Session, company_id: int, group_index: int):
    """
    Assigns a distinct realistic case pack to the company so different groups
    face different problems (SCM crisis, CRM VIP defect, Labor strike, Cash liquidity, MRP breakdown, Price war).
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return False

    # Pick case pack by modulo
    pack_idx = (group_index - 1) % len(DIFFERENTIATED_CASE_PACKS)
    chosen_pack = DIFFERENTIATED_CASE_PACKS[pack_idx]

    # Clear existing cases for this company
    db.query(ScenarioCase).filter(ScenarioCase.company_id == company_id).delete()
    db.commit()

    # Insert tailored cases
    for case_def in chosen_pack:
        sc = ScenarioCase(
            session_id=company.session_id,
            company_id=company.id,
            code=case_def["code"],
            stage_order=case_def["stage_order"],
            title=case_def["title"],
            category=case_def["category"],
            description=case_def["description"],
            trigger_hint=case_def.get("trigger_hint", ""),
            solvable_workflow=case_def.get("solvable_workflow", ""),
            resolution_criteria=case_def.get("resolution_criteria", ""),
            status="active" if case_def["stage_order"] == 1 else "pending",
            round_introduced=case_def["stage_order"],
            resolution_score=0.0,
            grade="-",
            step_scores=None,
            fact_sheet_data=None
        )
        db.add(sc)

    # Update sim_state's active case title if available
    st = company.sim_state
    if st and len(chosen_pack) > 0:
        st.active_case_title = chosen_pack[0]["title"]
        st.active_case_description = chosen_pack[0]["description"]

    db.commit()
    return True


def batch_generate_tenants(
    db: Session,
    session_id: int,
    target_count: int = 4,
    initial_capital: float = 500000000.0,
    differentiate_cases: bool = True
):
    """
    Batch provisions N companies with user accounts (kelompok1..N / mhs123),
    sets initial capital, provisions ERP master data, and optionally differentiates cases.
    """
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        session = db.query(ClassSession).first()
        if not session:
            return {"status": "error", "message": "Sesi kelas tidak ditemukan."}

    target_count = max(2, min(12, target_count))
    created_or_updated = []

    for i in range(1, target_count + 1):
        username = f"kelompok{i}"
        email = f"k{i}@mahasiswa.vlaberp.ac.id"
        preset = PRESET_TENANTS[(i - 1) % len(PRESET_TENANTS)]
        company_name = preset["name"]
        industry = preset["industry"]
        full_name = f"Kelompok {i} ({company_name})"

        # 1. Ensure user exists
        usr = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if not usr:
            usr = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=pwd_ctx.hash("mhs123"),
                role="MAHASISWA"
            )
            db.add(usr)
            db.commit()
            db.refresh(usr)
        else:
            usr.username = username
            usr.full_name = full_name
            db.commit()

        # 2. Ensure company exists for this session
        session_company_name = company_name if session.id == 1 else f"{company_name} ({session.code})"
        company = db.query(Company).filter(
            Company.session_id == session.id,
            Company.name == session_company_name
        ).first()
        if not company:
            # Check by group position in this session
            existing_by_order = db.query(Company).filter(Company.session_id == session.id).offset(i - 1).first()
            if existing_by_order:
                company = existing_by_order
                company.name = session_company_name
                company.industry = industry
            else:
                company = Company(
                    session_id=session.id,
                    name=session_company_name,
                    industry=industry,
                    team_leader_id=usr.id,
                    initial_capital=initial_capital,
                    current_cash=initial_capital
                )
                db.add(company)
                db.commit()
                db.refresh(company)

        # Update company properties
        company.team_leader_id = usr.id
        company.initial_capital = initial_capital
        company.current_cash = initial_capital
        company.industry = industry
        db.commit()

        # Provision full ERP data for this company
        provision_company_data(db, company, session)

        # Update sim_state cash to match initial capital
        if company.sim_state:
            company.sim_state.cash = initial_capital
            db.commit()

        # Differentiate cases if enabled
        if differentiate_cases:
            differentiate_tenant_cases(db, company.id, i)

        created_or_updated.append({
            "id": company.id,
            "name": company.name,
            "group_label": f"Kelompok {i}",
            "industry": company.industry,
            "initial_capital": company.initial_capital,
            "username": username
        })

    return {
        "status": "success",
        "message": f"Berhasil mem-provisioning {len(created_or_updated)} kelompok mahasiswa secara serentak dengan modal awal Rp {initial_capital:,.0f}!",
        "companies": created_or_updated
    }


# --- FEB TEAM TEACHING DISCIPLINE ROLLING ENGINE (12-BULAN CASCADE) ---

# Domain category map for ScenarioCase.category field
SCENARIO_CATEGORY_MAP = {
    "MFG-01": "mrp", "MFG-02": "mrp", "MFG-03": "mrp", "MFG-04": "mrp",
    "HR-01":  "hr",  "HR-02":  "hr",  "HR-03":  "hr",  "HR-04":  "hr",
    "ACC-01": "accounting", "ACC-02": "accounting", "ACC-03": "accounting", "ACC-04": "accounting",
    "CRM-01": "crm", "CRM-02": "crm", "CRM-03": "crm", "CRM-04": "crm",
    "PUR-01": "purchasing", "PUR-02": "purchasing", "PUR-03": "purchasing", "PUR-04": "purchasing",
}

# Initial state mutations when a scenario becomes ACTIVE (month N starts)
# Describes what external crisis arrives to set up the scenario
SCENARIO_INITIAL_MUTATIONS = {
    # --- MRP / Manufacturing ---
    "MFG-01": {"machine_health": 60.0, "worker_morale": 68.0, "is_strike": True,
               "strike_reason": "Mesin SMT korsleting inverter, operator menuntut upah lembur.",
               "wc_breakdown": True},
    "MFG-02": {"csat_score_cap": 70.0},   # batch cacat → CSAT terancam
    "MFG-03": {},                          # peluang kaizen, tidak ada krisis awal
    "MFG-04": {"machine_health_cap": 75.0, "worker_morale_cap": 78.0},  # inspeksi K3
    # --- HR ---
    "HR-01":  {"worker_morale": 52.0, "is_strike": True,
               "strike_reason": "Serikat buruh blokir pintu pabrik, menuntut upah +12%."},
    "HR-02":  {"worker_morale_cap": 80.0},  # poaching engineer, moral sedikit turun
    "HR-03":  {},                            # program upskilling, tidak ada krisis
    "HR-04":  {"worker_morale": 70.0},       # kecelakaan forklift
    # --- Accounting ---
    "ACC-01": {"cash_deduct": 25000000.0},   # SKPKB pajak mendadak
    "ACC-02": {},                             # pilihan metode penyusutan, tidak ada krisis
    "ACC-03": {"cash_deduct": 50000000.0},   # covenant breach: bank charge penalty
    "ACC-04": {},                             # peluang capex, tidak ada krisis
    # --- CRM ---
    "CRM-01": {"csat_score": 55.0},          # somasi hukum klien
    "CRM-02": {},                             # peluang tender, tidak ada krisis
    "CRM-03": {"csat_score_cap": 72.0},      # distributor minta TOP 90 hari
    "CRM-04": {},                             # program rebate, tidak ada krisis
    # --- Purchasing ---
    "PUR-01": {"supplier_health": 60.0, "cash_deduct": 10000000.0},  # kelangkaan chipset
    "PUR-02": {"supplier_health": 45.0},     # kebakaran gudang vendor
    "PUR-03": {},                             # tawaran bulk buy, tidak ada krisis
    "PUR-04": {"supplier_health_cap": 70.0}, # gratifikasi tim purchasing
}

# 12-bulan urutan skenario per track
# Blok 1 (Bulan 1-4): disiplin yg masuk duluan
# Blok 2 (Bulan 5-8): disiplin kedua
# Blok 3 (Bulan 9-12): disiplin ketiga
TRACK_SEQUENCES = {
    "hr_first": [
        # Blok SDM & Pabrik (Bulan 1-4)
        "MFG-01", "HR-01", "MFG-04", "HR-02",
        # Blok Keuangan & Pengadaan (Bulan 5-8)
        "ACC-01", "PUR-01", "ACC-03", "ACC-04",
        # Blok Pemasaran & CRM (Bulan 9-12)
        "CRM-01", "PUR-02", "CRM-03", "CRM-04",
    ],
    "finance_first": [
        # Blok Keuangan & Pengadaan (Bulan 1-4)
        "ACC-01", "ACC-03", "PUR-01", "ACC-04",
        # Blok Pemasaran & CRM (Bulan 5-8)
        "CRM-01", "PUR-02", "CRM-03", "CRM-04",
        # Blok SDM & Pabrik (Bulan 9-12)
        "MFG-01", "HR-01", "MFG-04", "HR-02",
    ],
    "marketing_first": [
        # Blok Pemasaran & CRM (Bulan 1-4)
        "CRM-01", "PUR-02", "CRM-03", "CRM-04",
        # Blok SDM & Pabrik (Bulan 5-8)
        "MFG-01", "HR-01", "MFG-04", "HR-02",
        # Blok Keuangan & Pengadaan (Bulan 9-12)
        "ACC-01", "PUR-01", "ACC-03", "ACC-04",
    ],
}


def _build_scenario_case_from_matrix(sc_id: str, company_id: int, session_id: int, stage_order: int, status: str, round_introduced: int) -> ScenarioCase:
    """Build a ScenarioCase DB record from a SCENARIO_MATRIX entry."""
    sc_data = get_scenario_by_id(sc_id)
    category = SCENARIO_CATEGORY_MAP.get(sc_id, "general")

    # Build trigger hint and workflow from scenario branches summary
    branches_summary = []
    for b in (sc_data.get("branches") or []):
        cost_str = f"Rp {b['immediate_cost']/1000000:.0f} Jt" if b.get("immediate_cost", 0) > 0 else "Tanpa biaya kas"
        branches_summary.append(f"  Pilihan {b['choice_id']}: {b['label']} ({cost_str})")

    solvable_workflow = "\n".join([
        "1. Analisis konteks krisis yang terjadi dan dampaknya.",
        "2. Buka tab modul ERP yang relevan untuk melihat data operasional terkini.",
        "3. Pilih cabang keputusan di tab 'Pohon Keputusan' → eksekusi pilihan terbaik.",
        "4. Validasi dampak keputusan di modul terkait (kas, mesin, moral, CSAT).",
        "5. Klik 'Validasi & Selesaikan Kasus' setelah tindakan dieksekusi.",
    ])

    trigger_hint = f"Buka tab modul {'Mesin & Pabrik MRP' if category == 'mrp' else 'Pegawai & HR' if category == 'hr' else 'Akuntansi & Kas' if category == 'accounting' else 'Pelanggan & CRM' if category == 'crm' else 'Rekanan Vendor'} → Identifikasi indikator krisis yang aktif bulan ini."

    fact_sheet = {
        "scenario_id": sc_id,
        "domain": sc_data.get("domain", ""),
        "urgency": sc_data.get("urgency", ""),
        "branches": branches_summary,
        "cfo_verdicts": [b.get("cfo_verdict", "") for b in (sc_data.get("branches") or [])],
    }

    return ScenarioCase(
        session_id=session_id,
        company_id=company_id,
        code=sc_id,
        stage_order=stage_order,
        title=f"Bulan {stage_order}: {sc_data['title']}",
        category=category,
        description=sc_data.get("context", sc_data.get("description", "")),
        trigger_hint=trigger_hint,
        solvable_workflow=solvable_workflow,
        resolution_criteria=f"Eksekusi keputusan cabang strategis pada skenario {sc_id} dan terapkan mitigasi yang tepat di modul ERP terkait.",
        status=status,
        round_introduced=round_introduced,
        resolution_score=0.0,
        grade="-",
        step_scores=None,
        fact_sheet_data=json.dumps(fact_sheet),
    )


def roll_session_cases(db: Session, session_id: int, sequence_mode: str):
    """
    Rolls 12-month scenario cascade for all companies in a session.
    Each track distributes 12 scenarios from SCENARIO_MATRIX across 3 discipline blocks:
    - 'hr_first':        SDM & Pabrik (1-4) → Keuangan (5-8) → Pemasaran (9-12)
    - 'finance_first':   Keuangan (1-4) → Pemasaran (5-8) → SDM & Pabrik (9-12)
    - 'marketing_first': Pemasaran (1-4) → SDM & Pabrik (5-8) → Keuangan (9-12)
    """
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        return False, "Sesi kelas FEB tidak ditemukan."

    companies = db.query(Company).filter(Company.session_id == session_id).all()
    if not companies:
        return False, "Tidak ada kelompok perusahaan pada sesi kelas ini."

    sequence = TRACK_SEQUENCES.get(sequence_mode, TRACK_SEQUENCES["hr_first"])

    label_map = {
        "hr_first":        "SDM & Pabrik MRP Duluan → Keuangan → Pemasaran",
        "finance_first":   "Keuangan Duluan → Pemasaran → SDM & Pabrik MRP",
        "marketing_first": "Pemasaran Duluan → SDM & Pabrik → Keuangan",
    }
    label = label_map.get(sequence_mode, "Rotasi Standar FEB")

    for company in companies:
        # Clear existing cases
        db.query(ScenarioCase).filter(ScenarioCase.company_id == company.id).delete()
        db.flush()

        for idx, sc_id in enumerate(sequence):
            stage_order = idx + 1
            is_first = (idx == 0)
            status = "active" if is_first else "pending"
            sc_case = _build_scenario_case_from_matrix(
                sc_id=sc_id,
                company_id=company.id,
                session_id=company.session_id,
                stage_order=stage_order,
                status=status,
                round_introduced=stage_order,
            )
            db.add(sc_case)

        # Apply initial state mutations for Month 1 scenario
        first_sc_id = sequence[0]
        mutation = SCENARIO_INITIAL_MUTATIONS.get(first_sc_id, {})
        st = company.sim_state
        if st:
            _apply_scenario_mutation(st, mutation, db, company.id)
            sc_data = get_scenario_by_id(first_sc_id)
            st.active_case_title = f"Bulan 1: {sc_data['title']}"
            st.active_case_description = sc_data.get("context", "")

        db.commit()

    return True, f"Berhasil me-rolling 12-bulan cascade untuk kelas '{session.name}' dengan track: {label}. {len(companies)} kelompok disinkronkan!"


def _apply_scenario_mutation(state, mutation: dict, db: Session, company_id: int):
    """Apply initial state mutation when a scenario becomes active."""
    if not mutation:
        return

    if "machine_health" in mutation:
        state.machine_health = mutation["machine_health"]
    if "machine_health_cap" in mutation:
        state.machine_health = min(state.machine_health, mutation["machine_health_cap"])

    if "worker_morale" in mutation:
        state.worker_morale = mutation["worker_morale"]
    if "worker_morale_cap" in mutation:
        state.worker_morale = min(state.worker_morale, mutation["worker_morale_cap"])

    if "csat_score" in mutation:
        state.csat_score = mutation["csat_score"]
    if "csat_score_cap" in mutation:
        state.csat_score = min(state.csat_score, mutation["csat_score_cap"])

    if "supplier_health" in mutation:
        state.supplier_health = mutation["supplier_health"]
    if "supplier_health_cap" in mutation:
        state.supplier_health = min(state.supplier_health, mutation["supplier_health_cap"])

    if "cash_deduct" in mutation:
        state.cash = max(0.0, state.cash - mutation["cash_deduct"])
        cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1010").first()
        if cash_acc:
            cash_acc.balance = state.cash

    if mutation.get("is_strike"):
        state.is_strike_active = True
        state.strike_reason = mutation.get("strike_reason", "Aksi serikat buruh dipicu oleh kondisi operasional.")

    if mutation.get("wc_breakdown"):
        wcs = db.query(WorkCenter).filter(WorkCenter.company_id == company_id).all()
        for wc in wcs:
            if "SMT" in wc.code or "Perakitan" in wc.name:
                wc.status = "breakdown"
                wc.failure_rate = min(20.0, wc.failure_rate + 8.0)



