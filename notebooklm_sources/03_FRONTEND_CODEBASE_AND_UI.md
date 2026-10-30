# BUNDLE FRONTEND CODEBASE VLAB-ERP (NEXT.JS 14 & TAILWIND)



---
# FILE: frontend/src/app/page.tsx
---
```tsx
"use client";

import React, { useState, useEffect } from "react";
import {
  Building2,
  Users,
  Briefcase,
  Layers,
  Factory,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  Award,
  Activity,
  RefreshCw,
  ShoppingBag,
  Clock,
  ShieldAlert,
  ChevronRight,
  Sparkles,
  Zap,
  RotateCcw,
  BarChart3,
  Plus,
  Trash2,
  X,
  MessageSquare,
  Flame,
  Search,
  Wrench,
  Filter,
  Download,
  ArrowUpRight,
  ArrowDownRight,
  FileText,
  Check,
  ChevronDown,
  BookOpen,
  UserCheck,
  AlertCircle,
  Eye,
  EyeOff,
  HelpCircle,
  FolderOpen,
  Settings,
  Bell,
  Calendar,
  Grid,
  ListFilter,
  Lock,
  Unlock,
  LogOut,
  KeyRound,
  ShieldCheck,
  GraduationCap,
  Copy,
  Edit3,
  UserPlus,
  Archive,
  CheckSquare
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  Legend,
  AreaChart,
  Area
} from "recharts";

const API_BASE = typeof window !== "undefined"
  ? (process.env.NEXT_PUBLIC_API_URL || `http://${window.location.hostname}:8281/api/v1`)
  : "http://127.0.0.1:8281/api/v1";

export default function VLabERPEnterprise() {
  // Navigation & Role
  const [activePortal, setActivePortal] = useState<"erp" | "dosen">("erp");
  const [activeModule, setActiveModule] = useState<"overview" | "missions" | "purchasing" | "crm" | "mrp" | "accounting" | "hcm">("overview");
  const [dosenSubTab, setDosenSubTab] = useState<"sliders" | "tenants" | "cases" | "branding" | "users">("sliders");

  // System Branding States (White-label & Free Customization FEB)
  const [branding, setBranding] = useState({
    app_title: "VLab-ERP Enterprise Edition - FEB",
    department_name: "Fakultas Ekonomi dan Bisnis (FEB) • Manajemen & Akuntansi Bisnis Digital",
    lecturer_name: "Tim Dosen Pengampu FEB (Pemasaran, SDM, Keuangan)",
    lecturer_marketing_name: "Dr. Maya Indah, S.E., M.M.",
    lecturer_hr_name: "Drs. Bambang Prakoso, M.Psi.",
    lecturer_finance_name: "Dr. Ir. Budi Santoso, Ak.",
    lecturer_role_label: "Tim Pengampu FEB",
    supervision_badge: "Supervisi Simulasi Bisnis FEB",
    footer_text: "VLab-ERP Enterprise Edition • Fakultas Ekonomi dan Bisnis (FEB) • Port 8280 (Frontend) & Port 8281 (Backend)",
    academic_term: "Semester Ganjil 2026/2027",
    portal_subtitle: "Laboratorium Simulasi ERP, Manajemen Bisnis & Akuntansi Terintegrasi FEB"
  });
  const [brandingForm, setBrandingForm] = useState({ ...branding });
  const [isSavingBranding, setIsSavingBranding] = useState(false);
  const [showBrandingModal, setShowBrandingModal] = useState(false);

  // User Management & Password CRUD States
  const [usersList, setUsersList] = useState<any[]>([]);
  const [usersLoading, setUsersLoading] = useState<boolean>(false);
  const [userSearchTerm, setUserSearchTerm] = useState<string>("");
  const [userRoleFilter, setUserRoleFilter] = useState<string>("ALL");
  const [userSessionFilter, setUserSessionFilter] = useState<string>("ALL");
  const [selectedUserIds, setSelectedUserIds] = useState<number[]>([]);
  const [showEditUserModal, setShowEditUserModal] = useState<boolean>(false);
  const [editUserForm, setEditUserForm] = useState({
    id: 0,
    username: "",
    full_name: "",
    email: "",
    role: "MAHASISWA",
    password: "",
    company_id: 0,
    session_id: 0
  });
  const [showPasswordInModal, setShowPasswordInModal] = useState<boolean>(false);
  const [isSavingUser, setIsSavingUser] = useState<boolean>(false);
  const [showCreateUserModal, setShowCreateUserModal] = useState<boolean>(false);
  const [newUserForm, setNewUserForm] = useState({
    username: "",
    full_name: "",
    email: "",
    role: "MAHASISWA",
    password: "",
    company_id: 0,
    session_id: 0
  });
  const [showQuickPasswordModal, setShowQuickPasswordModal] = useState<boolean>(false);
  const [quickPasswordForm, setQuickPasswordForm] = useState({ id: 0, username: "", password: "mhs123" });
  const [userToDelete, setUserToDelete] = useState<any | null>(null);
  const [isDeletingUser, setIsDeletingUser] = useState<boolean>(false);

  // Batch Multi-Tenant Generator States (Sliders)
  const [batchGroupCount, setBatchGroupCount] = useState<number>(4);
  const [batchInitialCapital, setBatchInitialCapital] = useState<number>(500000000);
  const [batchDifferentiate, setBatchDifferentiate] = useState<boolean>(true);
  const [batchLoading, setBatchLoading] = useState<boolean>(false);

  // Case Differentiation & Editor States (Dosen Console)
  const [selectedCompanyForCases, setSelectedCompanyForCases] = useState<number>(1);
  const [companyCases, setCompanyCases] = useState<any[]>([]);
  const [showAddCustomCaseModal, setShowAddCustomCaseModal] = useState<boolean>(false);
  const [newCustomCaseForm, setNewCustomCaseForm] = useState({
    code: "CASE-04",
    stage_order: 4,
    title: "",
    category: "purchasing",
    description: "",
    trigger_hint: "",
    solvable_workflow: "",
    resolution_criteria: ""
  });

  // Academic Mission Hub drawer/toggle
  const [showMissionDrawer, setShowMissionDrawer] = useState(false);

  // Multi-Tenant & Multi-Class State (FEB)
  const [companies, setCompanies] = useState<any[]>([]);
  const [companyId, setCompanyId] = useState<number>(1);
  const [sessions, setSessions] = useState<any[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<number>(1);
  const [dosenList, setDosenList] = useState<any[]>([]);
  const [isSavingSession, setIsSavingSession] = useState<boolean>(false);
  const [sessionToDelete, setSessionToDelete] = useState<any | null>(null);

  const [showAddSessionModal, setShowAddSessionModal] = useState<boolean>(false);
  const [newSessionForm, setNewSessionForm] = useState({
    name: "",
    code: "",
    academic_term: "Semester Ganjil 2026/2027",
    department: "S1 Manajemen & Bisnis Digital FEB",
    description: "",
    progression_mode: "problem_based",
    total_rounds: 12,
    lecturers: [] as { user_id: number; role_title: string; is_primary: boolean }[],
    auto_provision_groups: 4,
    initial_capital: 500000000.0
  });

  const [showEditSessionModal, setShowEditSessionModal] = useState<boolean>(false);
  const [editSessionForm, setEditSessionForm] = useState({
    id: 0,
    name: "",
    code: "",
    academic_term: "Semester Ganjil 2026/2027",
    department: "S1 Manajemen & Bisnis Digital FEB",
    description: "",
    status: "active",
    progression_mode: "problem_based",
    total_rounds: 12,
    lecturers: [] as { user_id: number; role_title: string; is_primary: boolean }[]
  });

  const [showCloneSessionModal, setShowCloneSessionModal] = useState<boolean>(false);
  const [cloneSessionForm, setCloneSessionForm] = useState({
    source_id: 0,
    source_name: "",
    new_name: "",
    new_code: "",
    academic_term: "Semester Ganjil 2026/2027",
    department: "S1 Manajemen & Bisnis Digital FEB",
    clone_companies: true,
    differentiate_cases: true
  });

  const [lecturerDiscipline, setLecturerDiscipline] = useState<"all" | "marketing" | "hr" | "finance">("all");
  const [rollingLoading, setRollingLoading] = useState<boolean>(false);
  const [showCompanyDropdown, setShowCompanyDropdown] = useState(false);
  const [showAddCompanyModal, setShowAddCompanyModal] = useState(false);
  const [newCompanyForm, setNewCompanyForm] = useState({
    name: "",
    industry: "Manufaktur & Bisnis Digital FEB",
    initial_capital: 500000000.0
  });
  const [simState, setSimState] = useState<any>({
    company_id: 1,
    current_round: 1,
    period_name: "Bulan 1 (Januari 2026)",
    cash: 500000000.0,
    revenue: 45000000.0,
    expenses: 25000000.0,
    net_profit: 20000000.0,
    csat_score: 88.5,
    worker_morale: 92.0,
    machine_health: 95.0,
    supplier_health: 91.0,
    overall_score: 0.0,
    is_strike_active: false,
    strike_reason: null,
    active_case_title: "Tahap 1: Due Diligence Vendor & Kesiapan Produksi",
    active_case_description: "Lakukan audit mendalam terhadap rekam jejak 4 rekanan pemasok sebelum menerbitkan Purchase Order (PO). Analisis rasio cacat bahan dan kepatuhan pengiriman."
  });

  // Lecturer Sliders State
  const [sliders, setSliders] = useState<any>({
    supply_disruption: 25.0,
    machine_breakdown_risk: 15.0,
    market_volatility: 30.0,
    labor_strike_risk: 10.0,
    bad_debt_risk: 15.0,
    competitor_price_war: 20.0
  });

  // ERP Domain Data States
  const [cases, setCases] = useState<any[]>([]);
  const [vendors, setVendors] = useState<any[]>([]);
  const [leads, setLeads] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [workCenters, setWorkCenters] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [budgets, setBudgets] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  // Search & Filter States
  const [vendorSearch, setVendorSearch] = useState("");
  const [leadSearch, setLeadSearch] = useState("");
  const [employeeSearch, setEmployeeSearch] = useState("");
  const [selectedVendorForDetail, setSelectedVendorForDetail] = useState<any>(null);

  // Operational Action Inputs
  const [poQty, setPoQty] = useState<{ [key: number]: number }>({ 1: 50, 2: 50, 3: 50, 4: 50 });
  const [woQty, setWoQty] = useState(30);
  const [notification, setNotification] = useState<string | null>(null);

  // HR Bipartite Inputs
  const [wageRaise, setWageRaise] = useState(10);
  const [workerBonus, setWorkerBonus] = useState(1500000);

  // Fact Sheet Modal State
  const [selectedFactSheet, setSelectedFactSheet] = useState<any>(null);

  // Open-World Mediation & Dynamic SO Modals
  const [showMediationModal, setShowMediationModal] = useState(false);
  const [activeMediationComplaint, setActiveMediationComplaint] = useState<any>(null);

  const [convertingLead, setConvertingLead] = useState<any>(null);
  const [soQuantity, setSoQuantity] = useState(100);
  const [soPaymentTerms, setSoPaymentTerms] = useState("Tempo 30 Hari");
  const [soProductId, setSoProductId] = useState(1);

  // Dynamic Multiple Endings Modal
  const [showEndingModal, setShowEndingModal] = useState(false);
  const [endingData, setEndingData] = useState<any>(null);
  const [isLoadingEnding, setIsLoadingEnding] = useState(false);

  // Behavioral Engine States (Non-obvious)
  const [unionProfile, setUnionProfile] = useState<any>(null);
  const [blackSwanAlert, setBlackSwanAlert] = useState<any>(null);
  const [strikeNegotiationResult, setStrikeNegotiationResult] = useState<any>(null);

  // Smart Python Brain: Multi-Scenario Matrix, Storyline & CFO Diagnostics States
  const [missionsSubTab, setMissionsSubTab] = useState<"cases" | "scenarios" | "cfo" | "storyline">("cases");
  const [scenarioMatrix, setScenarioMatrix] = useState<any[]>([]);
  const [selectedScenarioDomain, setSelectedScenarioDomain] = useState<string>("all");
  const [activeBranchExecution, setActiveBranchExecution] = useState<any>(null);
  const [executingBranchChoice, setExecutingBranchChoice] = useState<boolean>(false);
  const [companyStoryline, setCompanyStoryline] = useState<any[]>([]);
  const [cfoDiagnostics, setCfoDiagnostics] = useState<any>(null);
  const [cfoLoading, setCfoLoading] = useState<boolean>(false);
  const [activeRippleEvent, setActiveRippleEvent] = useState<any>(null);
  const [activeDocument, setActiveDocument] = useState<any>(null);
  const [auditDomainFilter, setAuditDomainFilter] = useState<string>("all");
  const [showMonthTracker, setShowMonthTracker] = useState<boolean>(true);
  const [previewMonthCase, setPreviewMonthCase] = useState<any>(null);
  const [confirmingPOVendor, setConfirmingPOVendor] = useState<any>(null);
  const [poPaymentMethod, setPoPaymentMethod] = useState<"tempo" | "cash">("tempo");
  const [isSubmittingPO, setIsSubmittingPO] = useState<boolean>(false);
  const [confirmingComplaintAction, setConfirmingComplaintAction] = useState<any>(null);

  const handleViewDocument = (doc: any) => {
    if (!doc) return;
    if (doc.title && doc.summary) {
      setActiveDocument(doc);
      return;
    }
    if (doc.doc_type === "SALES_ORDER") {
      setActiveDocument({
        title: `FAKTUR PENJUALAN & SALES ORDER #${doc.doc_code}`,
        recipient: doc.customer || "Pelanggan Enterprise",
        type: "SALES_ORDER_OFFICIAL",
        summary: `Telah diterbitkan Sales Order resmi untuk ${doc.customer || 'Pelanggan'} dengan rincian:\n\n• Produk: ${doc.product}\n• Kuantitas: ${doc.quantity} unit\n• Harga Satuan: Rp ${(doc.unit_price || 0).toLocaleString('id-ID')}\n• Total Nilai SO: Rp ${(doc.total_amount || 0).toLocaleString('id-ID')}\n• Termin Pembayaran: ${doc.payment_terms || 'Tempo 30 Hari'}\n• Nomor Jurnal Akuntansi: ${doc.journal_entry || '-'}\n${doc.auto_wo ? `• Pemicu Work Order Otomatis: #${doc.auto_wo} (Defisit Stok Gudang)\n` : ''}\nDokumen ini sah sebagai bukti pengakuan Piutang/Kas dan pengakuan pendapatan usaha.`
      });
    } else if (doc.doc_type === "PURCHASE_ORDER") {
      setActiveDocument({
        title: `SURAT PESANAN PEMBELIAN (PURCHASE ORDER) #${doc.doc_code}`,
        recipient: doc.vendor || "Mitra Vendor Rekanan",
        type: "PURCHASE_ORDER_OFFICIAL",
        summary: `Telah diterbitkan Purchase Order resmi kepada pemasok ${doc.vendor}:\n\n• Bahan Baku / Komponen: ${doc.product}\n• Kuantitas Dipesan: ${doc.quantity_ordered} unit\n• Kuantitas Diterima Gudang: ${doc.quantity_delivered} unit\n• Reject / Cacat Disortir: ${doc.defect_discarded || 0} unit\n• Total Tagihan Kewajiban (AP): Rp ${(doc.total_cost || 0).toLocaleString('id-ID')}\n• Termin Kredit: ${doc.credit_terms_days || 30} Hari\n• Nomor Jurnal Akuntansi: ${doc.journal_entry || '-'}\n\nDokumen ini sah sebagai dasar pengakuan Utang Usaha (Accounts Payable) dan penambahan saldo persediaan.`
      });
    } else if (doc.doc_type === "WORK_ORDER") {
      setActiveDocument({
        title: `SURAT PERINTAH KERJA (WORK ORDER) #${doc.doc_code}`,
        recipient: `Lini Produksi SMT & Perakitan: ${doc.work_center}`,
        type: "WORK_ORDER_COMPLETION",
        summary: `Laporan Hasil Pelaksanaan Perintah Kerja Manufaktur:\n\n• Stasiun Kerja: ${doc.work_center}\n• Produk Dirakit: ${doc.product_produced}\n• Target Produksi: ${doc.qty_target} unit\n• Hasil Selesai (Good Units): ${doc.qty_produced} unit\n• Scrap / Cacat: ${doc.scrap_qty || 0} unit\n• Nilai Bahan Baku Terkonsumsi: Rp ${(doc.raw_cost || 0).toLocaleString('id-ID')}\n\nUnit selesai telah diverifikasi QC dan dipindahkan ke rak persediaan barang jadi.`
      });
    } else if (doc.doc_type === "COMPLAINT_SETTLEMENT") {
      setActiveDocument({
        title: `SURAT KESEPAKATAN RESOLUSI KELUHAN PELANGGAN`,
        recipient: doc.customer || "Klien VIP Terkait",
        type: "CUSTOMER_SERVICE_SETTLEMENT",
        summary: `Surat Pengesahan Tindakan Penanganan Keluhan Pelanggan:\n\n• Nama Klien: ${doc.customer}\n• Kesepakatan / Solusi Terpilih: ${doc.action_taken}\n• Indeks Kepuasan Klien (CSAT): ${doc.csat_score}%\n• Status Relasi Dagang: Kontrak Berjalan Aman\n\nKeputusan ini berlaku mengikat demi menjamin kepuasan kemitraan enterprise.`
      });
    } else if (doc.doc_type === "MAINTENANCE_LOG") {
      setActiveDocument({
        title: `BERITA ACARA PEMELIHARAAN & REKALIBRASI MESIN`,
        recipient: `Stasiun Kerja: ${doc.work_center}`,
        type: "MAINTENANCE_RECORD",
        summary: `Berita Acara Pemeliharaan & Overhaul Mesin Pabrik:\n\n• Mesin: ${doc.work_center}\n• Biaya Perbaikan & Suku Cadang: Rp ${(doc.cost || 0).toLocaleString('id-ID')}\n• Status Pasca-Perbaikan: ${doc.status}\n• Waktu: ${doc.date}\n\nMesin telah diuji coba dan kembali beroperasi dengan tingkat kegagalan minimum.`
      });
    } else {
      setActiveDocument({
        title: "DOKUMEN OPERASIONAL RESMI ERP",
        recipient: "Departemen Terkait",
        type: "OPERATIONAL_RECORD",
        summary: typeof doc === "string" ? doc : JSON.stringify(doc, null, 2)
      });
    }
  };

  // Memoized map of executed decisions per scenario ID to guarantee one binding decision
  const executedDecisionsMap = React.useMemo(() => {
    const map: Record<string, { choice_id: string; title: string; decision_taken: string; executed_at: string }> = {};
    (companyStoryline || []).forEach((ev: any) => {
      const match = ev.title?.match(/^\[([A-Z0-9-]+)\]/);
      if (match) {
        const scId = match[1];
        const choiceMatch = ev.decision_taken?.match(/^Pilihan\s+([A-Z0-9]+)/i);
        const choiceId = choiceMatch ? choiceMatch[1] : "A";
        map[scId] = {
          choice_id: choiceId,
          title: ev.title,
          decision_taken: ev.decision_taken,
          executed_at: ev.executed_at || ev.created_at
        };
      }
    });
    return map;
  }, [companyStoryline]);

  const [showAddLeadModal, setShowAddLeadModal] = useState(false);
  const [newLeadForm, setNewLeadForm] = useState({
    title: "",
    customer_name: "",
    customer_email: "",
    expected_revenue: 25000000,
    stage: "new",
    priority: "medium",
    notes: ""
  });

  const [showAddVendorModal, setShowAddVendorModal] = useState(false);
  const [newVendorForm, setNewVendorForm] = useState({
    name: "",
    category: "Komponen Presisi & Bahan Baku",
    lead_time_days: 5,
    defect_rate: 2.0,
    price_multiplier: 1.0,
    notes: ""
  });

  const [showAddBudgetModal, setShowAddBudgetModal] = useState(false);
  const [newBudgetForm, setNewBudgetForm] = useState({
    department: "",
    allocated_amount: 50000000
  });

  const [showAddEmployeeModal, setShowAddEmployeeModal] = useState(false);
  const [newEmployeeForm, setNewEmployeeForm] = useState({
    name: "",
    department: "Produksi",
    role: "Operator Perakitan",
    monthly_salary: 5000000
  });

  const showNotification = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 5000);
  };

  // User Authentication & Multi-Tenant RBAC State
  const [isFetchingData, setIsFetchingData] = useState(false);
  const [dataFetchError, setDataFetchError] = useState<string | null>(null);
  const [lastSyncedTime, setLastSyncedTime] = useState<string>("");

  const [currentUser, setCurrentUser] = useState<{
    username: string;
    full_name: string;
    role: "MAHASISWA" | "DOSEN" | "ADMIN";
    company_id: number;
    company_name: string;
    group_label: string;
    access_token?: string;
  } | null>(null);
  const [authMounted, setAuthMounted] = useState(false);
  const [loginForm, setLoginForm] = useState({ username: "kelompok1", password: "mhs123" });
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loginLoading, setLoginLoading] = useState(false);

  // Restore auth session from localStorage
  useEffect(() => {
    setAuthMounted(true);
    try {
      const savedUser = localStorage.getItem("vlab_auth_user");
      if (savedUser) {
        const parsed = JSON.parse(savedUser);
        setCurrentUser(parsed);
        const targetCoId = parsed.company_id || 1;
        setCompanyId(targetCoId);
        setSelectedCompanyForCases(targetCoId);
        fetchData(targetCoId);
        fetchCasesForCompany(targetCoId);
        if (parsed.role === "DOSEN" || parsed.role === "ADMIN") {
          setActivePortal("dosen");
        }
      }
    } catch (e) {
      console.error("Failed to load cached auth:", e);
    }
  }, []);

  const handleLogin = async (overrideUser?: { username: string; password: string }) => {
    const creds = overrideUser || loginForm;
    setLoginLoading(true);
    setLoginError(null);
    try {
      let res: Response;
      try {
        res = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(creds)
        });
      } catch (err1) {
        const altUrl = typeof window !== "undefined" ? `http://${window.location.hostname}:8281/api/v1/auth/login` : "http://127.0.0.1:8281/api/v1/auth/login";
        res = await fetch(altUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(creds)
        });
      }
      const data = await res.json();
      if (!res.ok) {
        setLoginError(data.detail || "Autentikasi gagal. Periksa username dan kata sandi.");
        setLoginLoading(false);
        return;
      }

      const userPayload = {
        username: creds.username,
        full_name: data.role === "DOSEN" ? (branding.lecturer_name || "Dr. Ir. Hendra Gunawan, M.T.") : (data.role === "ADMIN" ? "Administrator Lab ERP" : (data.group_label || creds.username)),
        role: data.role,
        company_id: data.company_id || 1,
        company_name: data.company_name || "PT Inovasi Cipta Mandiri",
        group_label: data.group_label || "Kelompok 1",
        access_token: data.access_token
      };

      setCurrentUser(userPayload);
      localStorage.setItem("vlab_auth_user", JSON.stringify(userPayload));

      const targetCoId = userPayload.company_id || 1;
      setCompanyId(targetCoId);
      setSelectedCompanyForCases(targetCoId);

      // Instantly fetch all ERP data and companies for this tenant
      fetchData(targetCoId);
      fetchCompaniesAndSessions();
      fetchBranding();
      fetchCasesForCompany(targetCoId);

      if (userPayload.role === "DOSEN" || userPayload.role === "ADMIN") {
        setActivePortal("dosen");
      } else {
        setActivePortal("erp");
      }
      showNotification(`Akses diberikan: ${userPayload.full_name} (${userPayload.role})`);
    } catch (err) {
      setLoginError("Gagal menghubungi server backend di port 8281.");
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("vlab_auth_user");
    setCurrentUser(null);
    setActivePortal("erp");
    showNotification("Anda telah berhasil logout dari sistem VLab-ERP.");
  };

  // Fetch multi-tenant companies & sessions with tenant integrity validation
  async function fetchCompaniesAndSessions(targetSessionId?: number) {
    try {
      const resSes = await fetch(`${API_BASE}/simulation/sessions`);
      let curSesId = targetSessionId || selectedSessionId;
      if (resSes.ok) {
        const sesData = await resSes.json();
        setSessions(sesData);
        if (sesData.length > 0 && (!curSesId || !sesData.some((s: any) => s.id === curSesId))) {
          curSesId = sesData[0].id;
          setSelectedSessionId(curSesId);
        }
      }
      const coUrl = curSesId ? `${API_BASE}/simulation/companies?session_id=${curSesId}` : `${API_BASE}/simulation/companies`;
      const resCo = await fetch(coUrl);
      if (resCo.ok) {
        const data = await resCo.json();
        setCompanies(data);
        // Tenant integrity recovery: if current companyId is not in companies list, fallback to first company
        if (data.length > 0 && !data.some((c: any) => c.id === companyId)) {
          setCompanyId(data[0].id);
          setSelectedCompanyForCases(data[0].id);
        }
      }
    } catch (err) {
      console.error("Error fetching companies & sessions:", err);
    }
  };

  const handleSelectSession = (sId: number) => {
    setSelectedSessionId(sId);
    fetchCompaniesAndSessions(sId);
    const ses = sessions.find((s: any) => s.id === sId);
    showNotification(`Beralih ke Sesi Kelas: ${ses ? ses.name : `ID ${sId}`}`);
  };

  const handleRollCases = async (sequence: "marketing_first" | "finance_first" | "hr_first") => {
    setRollingLoading(true);
    try {
      const sId = selectedSessionId || (sessions.length > 0 ? sessions[0].id : 1);
      const res = await fetch(`${API_BASE}/simulation/sessions/${sId}/roll-cases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sequence })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message || "Rolling urutan kasus berhasil diterapkan!");
        await fetchCompaniesAndSessions(sId);
        if (companyId) {
          fetchCasesForCompany(companyId);
        }
        fetchData();
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan sistem"}`);
      }
    } catch {
      showNotification("Gagal menghubungi server backend.");
    } finally {
      setRollingLoading(false);
    }
  };

  async function fetchDosenList() {
    try {
      const res = await fetch(`${API_BASE}/simulation/dosen-list`);
      if (res.ok) {
        const data = await res.json();
        setDosenList(data);
      }
    } catch (err) {
      console.error("Error fetching dosen list:", err);
    }
  };

  const handleOpenAddSession = () => {
    const defaultLecturers = dosenList.map((d, idx) => ({
      user_id: d.id,
      role_title: d.username.includes("mkt") || d.username.includes("marketing")
        ? "Dosen Bidang Pemasaran & CRM"
        : d.username.includes("sdm")
        ? "Dosen Bidang SDM & Organisasi"
        : d.username.includes("keuangan") || d.username.includes("fin")
        ? "Dosen Bidang Keuangan & Akuntansi"
        : idx === 0 || d.username === "dosen"
        ? "Koordinator Matakuliah & Pengampu Utama"
        : "Dosen Pengampu",
      is_primary: idx === 0 || d.username === "dosen"
    }));

    setNewSessionForm({
      name: "",
      code: "",
      academic_term: branding.academic_term || "Semester Ganjil 2026/2027",
      department: "S1 Manajemen & Bisnis Digital FEB",
      description: "Praktikum ERP & Simulasi Bisnis Terpadu FEB",
      progression_mode: "problem_based",
      total_rounds: 12,
      lecturers: defaultLecturers.length > 0 ? defaultLecturers : [],
      auto_provision_groups: 4,
      initial_capital: 500000000.0
    });
    setShowAddSessionModal(true);
  };

  const handleCreateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSessionForm.name || !newSessionForm.code) {
      showNotification("Nama dan kode kelas wajib diisi!");
      return;
    }
    setIsSavingSession(true);
    try {
      const res = await fetch(`${API_BASE}/simulation/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSessionForm)
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message || `Sesi kelas '${newSessionForm.name}' berhasil dibuat!`);
        setShowAddSessionModal(false);
        if (data.session_id) {
          setSelectedSessionId(data.session_id);
          await fetchCompaniesAndSessions(data.session_id);
          fetchDosenList();
        }
      } else {
        showNotification(`Gagal membuat sesi: ${data.detail || "Error"}`);
      }
    } catch {
      showNotification("Gagal menghubungi server backend.");
    } finally {
      setIsSavingSession(false);
    }
  };

  const handleOpenEditSession = (session: any) => {
    const existingTeam = session.team_lecturers && session.team_lecturers.length > 0
      ? session.team_lecturers.map((l: any) => ({
          user_id: l.user_id,
          role_title: l.role_title,
          is_primary: l.is_primary
        }))
      : dosenList.map((d, idx) => ({
          user_id: d.id,
          role_title: idx === 0 ? "Koordinator Matakuliah & Pengampu Utama" : "Dosen Pengampu",
          is_primary: idx === 0
        }));

    setEditSessionForm({
      id: session.id,
      name: session.name,
      code: session.code,
      academic_term: session.academic_term || "Semester Ganjil 2026/2027",
      department: session.department || "S1 Manajemen & Bisnis Digital FEB",
      description: session.description || "",
      status: session.status || "active",
      progression_mode: session.progression_mode || "problem_based",
      total_rounds: session.total_rounds || 12,
      lecturers: existingTeam
    });
    setShowEditSessionModal(true);
  };

  const handleUpdateSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editSessionForm.name || !editSessionForm.code) {
      showNotification("Nama dan kode kelas wajib diisi!");
      return;
    }
    setIsSavingSession(true);
    try {
      const res = await fetch(`${API_BASE}/simulation/sessions/${editSessionForm.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editSessionForm)
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message || `Sesi kelas '${editSessionForm.name}' berhasil diperbarui!`);
        setShowEditSessionModal(false);
        await fetchCompaniesAndSessions(selectedSessionId);
        fetchDosenList();
      } else {
        showNotification(`Gagal memperbarui sesi: ${data.detail || "Error"}`);
      }
    } catch {
      showNotification("Gagal menghubungi server backend.");
    } finally {
      setIsSavingSession(false);
    }
  };

  const handleOpenCloneSession = (session: any) => {
    setCloneSessionForm({
      source_id: session.id,
      source_name: session.name,
      new_name: `${session.name} (Paralel)`,
      new_code: `${session.code}-PARALEL`,
      academic_term: session.academic_term || branding.academic_term || "Semester Ganjil 2026/2027",
      department: session.department || "S1 Manajemen & Bisnis Digital FEB",
      clone_companies: true,
      differentiate_cases: true
    });
    setShowCloneSessionModal(true);
  };

  const handleCloneSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cloneSessionForm.new_name || !cloneSessionForm.new_code) {
      showNotification("Nama dan kode kelas baru wajib diisi!");
      return;
    }
    setIsSavingSession(true);
    try {
      const res = await fetch(`${API_BASE}/simulation/sessions/${cloneSessionForm.source_id}/clone`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cloneSessionForm)
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message || "Sesi kelas berhasil diduplikasi!");
        setShowCloneSessionModal(false);
        if (data.session_id) {
          setSelectedSessionId(data.session_id);
          await fetchCompaniesAndSessions(data.session_id);
          fetchDosenList();
        }
      } else {
        showNotification(`Gagal menduplikasi sesi: ${data.detail || "Error"}`);
      }
    } catch {
      showNotification("Gagal menghubungi server backend.");
    } finally {
      setIsSavingSession(false);
    }
  };

  const handleDeleteSession = async (session: any) => {
    if (sessions.length <= 1) {
      showNotification("Tidak dapat menghapus satu-satunya sesi kelas yang tersisa!");
      return;
    }
    if (!confirm(`Hapus sesi kelas '${session.name}' (${session.code}) beserta seluruh entitas perusahaannya secara permanen?`)) {
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/simulation/sessions/${session.id}`, {
        method: "DELETE"
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message || "Sesi kelas berhasil dihapus.");
        const remaining = sessions.filter(s => s.id !== session.id);
        const nextId = remaining.length > 0 ? remaining[0].id : 1;
        setSelectedSessionId(nextId);
        await fetchCompaniesAndSessions(nextId);
        fetchDosenList();
      } else {
        showNotification(`Gagal menghapus sesi: ${data.detail || "Error"}`);
      }
    } catch {
      showNotification("Gagal menghubungi server backend.");
    }
  };

  async function fetchUsers() {
    setUsersLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/users`);
      if (res.ok) {
        const data = await res.json();
        setUsersList(data);
      }
    } catch (err) {
      console.error("Error fetching users:", err);
    } finally {
      setUsersLoading(false);
    }
  };

  const handleOpenEditUser = (user: any) => {
    setEditUserForm({
      id: user.id,
      username: user.username,
      full_name: user.full_name,
      email: user.email || `${user.username}@vlab.edu`,
      role: user.role,
      password: "",
      company_id: user.company_id || 0,
      session_id: user.session_id || 0
    });
    setShowPasswordInModal(false);
    setShowEditUserModal(true);
  };

  const handleOpenQuickPassword = (user: any) => {
    setQuickPasswordForm({
      id: user.id,
      username: user.username,
      password: user.role === "ADMIN" ? "admin123" : (user.role === "DOSEN" ? "dosen123" : "mhs123")
    });
    setShowQuickPasswordModal(true);
  };

  const handleSaveQuickPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickPasswordForm.password || quickPasswordForm.password.trim().length < 4) {
      showNotification("Password minimal 4 karakter.");
      return;
    }
    setIsSavingUser(true);
    try {
      const res = await fetch(`${API_BASE}/auth/users/${quickPasswordForm.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: quickPasswordForm.password.trim() })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`🔑 Password untuk akun '${quickPasswordForm.username}' berhasil diperbarui!`);
        setShowQuickPasswordModal(false);
        fetchUsers();
      } else {
        showNotification(`❌ Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch {
      showNotification("Gagal menghubungi server untuk mereset password.");
    } finally {
      setIsSavingUser(false);
    }
  };

  const handleBatchResetPassword = async (newPass: string) => {
    if (selectedUserIds.length === 0) {
      showNotification("Pilih minimal 1 akun dari tabel untuk reset massal.");
      return;
    }
    setIsSavingUser(true);
    try {
      const res = await fetch(`${API_BASE}/auth/users/batch-reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_ids: selectedUserIds,
          new_password: newPass
        })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`✅ ${data.message}`);
        setSelectedUserIds([]);
        fetchUsers();
      } else {
        showNotification(`❌ Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch {
      showNotification("Gagal menghubungi server untuk reset massal.");
    } finally {
      setIsSavingUser(false);
    }
  };

  const handleSaveUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingUser(true);
    try {
      const payload: any = {
        username: editUserForm.username.trim(),
        full_name: editUserForm.full_name.trim(),
        email: editUserForm.email.trim(),
        role: editUserForm.role,
        company_id: editUserForm.company_id,
        session_id: editUserForm.session_id
      };
      if (editUserForm.password && editUserForm.password.trim().length > 0) {
        payload.password = editUserForm.password.trim();
      }

      const res = await fetch(`${API_BASE}/auth/users/${editUserForm.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`✅ ${data.message || "Akun berhasil diperbarui!"}`);
        setShowEditUserModal(false);
        fetchUsers();
        // If current logged-in user was updated, keep session synced
        if (currentUser && currentUser.username === editUserForm.username) {
          const updatedCurrentUser = {
            ...currentUser,
            full_name: editUserForm.full_name.trim(),
            role: editUserForm.role as "MAHASISWA" | "DOSEN" | "ADMIN"
          };
          setCurrentUser(updatedCurrentUser);
          localStorage.setItem("vlab_auth_user", JSON.stringify(updatedCurrentUser));
        }
      } else {
        showNotification(`❌ Gagal: ${data.detail || "Terjadi kesalahan saat menyimpan"}`);
      }
    } catch (err) {
      showNotification("Gagal menghubungi server untuk memperbarui akun.");
    } finally {
      setIsSavingUser(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUserForm.username.trim() || !newUserForm.password.trim()) {
      showNotification("Username dan password wajib diisi.");
      return;
    }
    setIsSavingUser(true);
    try {
      const res = await fetch(`${API_BASE}/auth/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: newUserForm.username.trim(),
          full_name: newUserForm.full_name.trim() || newUserForm.username.trim(),
          email: newUserForm.email.trim() || `${newUserForm.username.trim()}@vlab.edu`,
          role: newUserForm.role,
          password: newUserForm.password.trim(),
          company_id: newUserForm.company_id,
          session_id: newUserForm.session_id
        })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`✅ ${data.message || "Akun baru berhasil dibuat!"}`);
        setShowCreateUserModal(false);
        setNewUserForm({ username: "", full_name: "", email: "", role: "MAHASISWA", password: "", company_id: 0, session_id: 0 });
        fetchUsers();
      } else {
        showNotification(`❌ Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("Gagal membuat akun baru.");
    } finally {
      setIsSavingUser(false);
    }
  };

  const handleConfirmDeleteUser = async () => {
    if (!userToDelete) return;
    setIsDeletingUser(true);
    try {
      const res = await fetch(`${API_BASE}/auth/users/${userToDelete.id}`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok) {
        showNotification(`🗑️ ${data.message || "Akun berhasil dihapus."}`);
        setUserToDelete(null);
        fetchUsers();
      } else {
        showNotification(`❌ Gagal: ${data.detail || "Tidak dapat menghapus pengguna"}`);
      }
    } catch {
      showNotification("Terjadi kesalahan koneksi.");
    } finally {
      setIsDeletingUser(false);
    }
  };

  async function fetchBranding() {
    try {
      const res = await fetch(`${API_BASE}/settings/branding`);
      if (res.ok) {
        const data = await res.json();
        setBranding(data);
        setBrandingForm(data);
      }
    } catch (err) {
      console.error("Error fetching branding:", err);
    }
  };

  const handleSaveBranding = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setIsSavingBranding(true);
    try {
      const res = await fetch(`${API_BASE}/settings/branding`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(brandingForm)
      });
      if (res.ok) {
        const data = await res.json();
        setBranding(data);
        setBrandingForm(data);
        if (currentUser && currentUser.role === "DOSEN") {
          setCurrentUser(prev => prev ? { ...prev, full_name: data.lecturer_name } : null);
        }
        showNotification("🎨 Identitas & Branding Kampus berhasil diperbarui secara live!");
        setShowBrandingModal(false);
      } else {
        showNotification("Gagal menyimpan perubahan branding.");
      }
    } catch (err) {
      showNotification("Terjadi kesalahan koneksi saat menyimpan branding.");
    } finally {
      setIsSavingBranding(false);
    }
  };

  const handleResetBranding = async () => {
    if (!confirm("Kembalikan seluruh identitas branding ke format standar bawaan sistem?")) return;
    setIsSavingBranding(true);
    try {
      const res = await fetch(`${API_BASE}/settings/branding/reset`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setBranding(data);
        setBrandingForm(data);
        if (currentUser && currentUser.role === "DOSEN") {
          setCurrentUser(prev => prev ? { ...prev, full_name: data.lecturer_name } : null);
        }
        showNotification("Branding berhasil di-reset ke nilai default!");
      }
    } catch (err) {
      showNotification("Gagal me-reset branding.");
    } finally {
      setIsSavingBranding(false);
    }
  };

  useEffect(() => {
    fetchCompaniesAndSessions();
    fetchBranding();
    fetchUsers();
  }, []);

  async function fetchCasesForCompany(cId: number) {
    try {
      const res = await fetch(`${API_BASE}/simulation/cases/${cId}`);
      if (res.ok) {
        setCompanyCases(await res.json());
      }
    } catch (e) {
      console.error("Error fetching company cases:", e);
    }
  };

  useEffect(() => {
    if (selectedCompanyForCases) {
      fetchCasesForCompany(selectedCompanyForCases);
    }
  }, [selectedCompanyForCases]);

  const handleBatchGenerateTenants = async () => {
    if (!confirm(`Konfirmasi pembuatan & sinkronisasi ${batchGroupCount} kelompok dengan modal awal Rp ${batchInitialCapital.toLocaleString("id-ID")}? Seluruh data tenant dan akun mahasiswa (kelompok1..${batchGroupCount}) akan diprovisioning otomatis.`)) return;
    setBatchLoading(true);
    try {
      const sessionId = selectedSessionId || (sessions.length > 0 ? sessions[0].id : 1);
      const res = await fetch(`${API_BASE}/simulation/companies/batch-generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          target_count: batchGroupCount,
          initial_capital: batchInitialCapital,
          differentiate_cases: batchDifferentiate
        })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message || `${batchGroupCount} kelompok berhasil dibuat dan disinkronkan!`);
        await fetchCompaniesAndSessions(sessionId);
        if (data.companies && data.companies.length > 0) {
          setCompanyId(data.companies[0].id);
          setSelectedCompanyForCases(data.companies[0].id);
        }
        fetchData();
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan sistem"}`);
      }
    } catch {
      showNotification("Gagal menghubungi server backend di port 8281.");
    } finally {
      setBatchLoading(false);
    }
  };

  const handleRandomizeSingleCompanyCases = async (cId: number) => {
    try {
      const res = await fetch(`${API_BASE}/simulation/companies/${cId}/randomize-cases`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message);
        fetchCasesForCompany(cId);
        if (cId === companyId) fetchData();
      } else {
        showNotification("Gagal mengacak masalah kasus.");
      }
    } catch {
      showNotification("Gagal menghubungi server.");
    }
  };

  const handleDifferentiateAllCases = async () => {
    if (!confirm("Acak paket masalah bisnis yang berbeda untuk seluruh kelompok di sesi ini? Tiap kelompok akan menerima tantangan skenario yang unik.")) return;
    try {
      const res = await fetch(`${API_BASE}/simulation/differentiate-all-cases`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message);
        await fetchCompaniesAndSessions();
        if (selectedCompanyForCases) fetchCasesForCompany(selectedCompanyForCases);
        fetchData();
      } else {
        showNotification("Gagal mendiferensiasikan kasus.");
      }
    } catch {
      showNotification("Gagal menghubungi server.");
    }
  };

  const handleCreateCustomCase = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const sessionId = selectedSessionId || (sessions.length > 0 ? sessions[0].id : 1);
      const res = await fetch(`${API_BASE}/simulation/cases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          company_id: selectedCompanyForCases,
          ...newCustomCaseForm
        })
      });
      if (res.ok) {
        showNotification(`Skenario baru ${newCustomCaseForm.code} berhasil ditambahkan ke perusahaan!`);
        setShowAddCustomCaseModal(false);
        setNewCustomCaseForm({
          code: `CASE-0${companyCases.length + 2}`,
          stage_order: companyCases.length + 2,
          title: "",
          category: "purchasing",
          description: "",
          trigger_hint: "",
          solvable_workflow: "",
          resolution_criteria: ""
        });
        fetchCasesForCompany(selectedCompanyForCases);
        if (selectedCompanyForCases === companyId) fetchData();
      } else {
        showNotification("Gagal menyimpan kasus baru.");
      }
    } catch {
      showNotification("Gagal menghubungi server.");
    }
  };

  const handleDeleteCase = async (caseId: number) => {
    if (!confirm("Hapus skenario masalah ini dari perusahaan?")) return;
    try {
      const res = await fetch(`${API_BASE}/simulation/cases/${caseId}`, { method: "DELETE" });
      if (res.ok) {
        showNotification("Skenario masalah berhasil dihapus.");
        fetchCasesForCompany(selectedCompanyForCases);
        if (selectedCompanyForCases === companyId) fetchData();
      }
    } catch {
      showNotification("Gagal menghapus kasus.");
    }
  };

  const handleInjectQuickCase = async (presetType: string) => {
    let caseData: any = null;
    const nextOrder = companyCases.length + 1;
    const nextCode = `CASE-0${nextOrder}`;

    if (presetType === "scm_defect") {
      caseData = {
        code: nextCode,
        stage_order: nextOrder,
        title: "Krisis Pasokan: Pemasok Bahan Baku Mengalami Cacat 8.8% & Keterlambatan",
        category: "purchasing",
        description: "Supplier rekanan utama mengalami lonjakan tingkat cacat bahan hingga 8.8% serta keterlambatan pengiriman 10 hari. Lini pabrik terancam berhenti.",
        trigger_hint: "Buka modul Rekanan Vendor, teliti defect rate dan alihkan PO ke supplier grade-1.",
        solvable_workflow: "1. Tinjau performa 4 vendor.\n2. Terbitkan PO darurat ke vendor terpercaya.\n3. Batalkan pesanan ke rekanan cacat.",
        resolution_criteria: "PO diterbitkan ke vendor grade-1, buffer stock aman."
      };
    } else if (presetType === "crm_recall") {
      caseData = {
        code: nextCode,
        stage_order: nextOrder,
        title: "Skandal Mutu Produk VIP Enterprise: Retur 100 Unit & Ancaman Denda Rp 150 Juta",
        category: "crm",
        description: "Klien enterprise terbesar menerima unit cacat layar bergaris. Klien menahan pembayaran Rp 150jt dan menuntut ganti rugi.",
        trigger_hint: "Buka modul CRM, tangani tiket keluhan darurat CV Megah Sentosa.",
        solvable_workflow: "1. Buka tiket keluhan di CRM.\n2. Setujui penggantian unit baru + voucher diskon.\n3. Terbitkan Credit Note di Akuntansi.",
        resolution_criteria: "Tiket disetujui, CSAT pulih, retensi klien berhasil."
      };
    } else if (presetType === "hr_strike") {
      caseData = {
        code: nextCode,
        stage_order: nextOrder,
        title: "Tuntutan Uang Lembur & Ancaman Mogok Kerja Serikat Buruh SPMI",
        category: "hr",
        description: "Operator lini pabrik kelelahan lembur dan menuntut pembayaran insentif darurat. Serikat buruh mengeluarkan surat mogok kerja.",
        trigger_hint: "Buka modul HR, pantau moral buruh dan setujui paket kompromi bipartit.",
        solvable_workflow: "1. Buka meja bipartit di HR.\n2. Setujui kenaikan upah wajar dan bonus damai.\n3. Pastikan kas mencukupi pencairan payroll.",
        resolution_criteria: "Moral buruh di atas 85%, pemogokan batal, pabrik beroperasi normal."
      };
    } else if (presetType === "mrp_breakdown") {
      caseData = {
        code: nextCode,
        stage_order: nextOrder,
        title: "Kerusakan Kritis Motor Servo Stasiun SMT-01: Lini Pabrik Lumpuh Total",
        category: "mrp",
        description: "Motor servo stasiun perakitan SMT mengalami overheat dan mati mendadak. Output produksi turun menjadi nol unit/jam.",
        trigger_hint: "Buka modul Mesin & Pabrik MRP, eksekusi maintenance darurat dan jadwalkan work order.",
        solvable_workflow: "1. Eksekusi tindakan darurat maintenance mesin SMT.\n2. Alihkan sebagian beban ke stasiun perakitan cadangan.\n3. Terbitkan Work Order penyesuaian kuantitas.",
        resolution_criteria: "Mesin SMT berstatus 'operational', kesehatan mesin di atas 90%."
      };
    } else if (presetType === "accounting_baddebt") {
      caseData = {
        code: nextCode,
        stage_order: nextOrder,
        title: "Krisis Piutang Macet: Pelanggan Retail Gagal Bayar Rp 120 Juta",
        category: "accounting",
        description: "Distributor retail regional bangkrut dan gagal melunasi faktur Rp 120jt. Saldo kas bank menipis tajam mendekati batas gaji karyawan.",
        trigger_hint: "Buka modul Akuntansi, amankan likuiditas kas dan lakukan realokasi pagu anggaran.",
        solvable_workflow: "1. Bentuk cadangan kerugian piutang di buku besar.\n2. Pangkas anggaran non-esensial.\n3. Perketat termin kredit penjualan baru.",
        resolution_criteria: "Kas operasional aman di atas safety level, payroll terbayar lancar."
      };
    } else if (presetType === "price_war") {
      caseData = {
        code: nextCode,
        stage_order: nextOrder,
        title: "Perang Harga Kompetitor Global: Pemotongan Harga 25% Mengikis Margin",
        category: "crm",
        description: "Kompetitor memangkas harga jual sebesar 25%, menyebabkan closing rate prospek penjualan anjlok.",
        trigger_hint: "Buka CRM & MRP, terapkan value-based selling dan rekayasa nilai HPP.",
        solvable_workflow: "1. Tawarkan garansi purnajual 3 tahun sebagai diferensiasi nilai.\n2. Evaluasi resep BOM di MRP untuk memangkas biaya perakitan.\n3. Dekati akun prospek potensial.",
        resolution_criteria: "Closing rate pulih di atas 60%, marjin laba tetap positif."
      };
    }

    if (!caseData) return;

    try {
      const sessionId = sessions.length > 0 ? sessions[0].id : 1;
      const res = await fetch(`${API_BASE}/simulation/cases`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          company_id: selectedCompanyForCases,
          ...caseData
        })
      });
      if (res.ok) {
        showNotification(`Skenario '${caseData.title}' berhasil disuntikkan ke kelompok terpilih!`);
        fetchCasesForCompany(selectedCompanyForCases);
        if (selectedCompanyForCases === companyId) fetchData();
      } else {
        showNotification("Gagal menyuntikkan skenario.");
      }
    } catch {
      showNotification("Gagal menghubungi server backend.");
    }
  };

  // Multi-tenant Tenant Management Handlers
  const handleCreateCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const sessionId = selectedSessionId || (sessions.length > 0 ? sessions[0].id : 1);
      const res = await fetch(`${API_BASE}/simulation/companies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          name: newCompanyForm.name,
          industry: newCompanyForm.industry,
          initial_capital: newCompanyForm.initial_capital
        })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message || "Tenant perusahaan berhasil dibuat & diprovisioning lengkap!");
        setShowAddCompanyModal(false);
        setNewCompanyForm({ name: "", industry: "Manufaktur & Bisnis Digital FEB", initial_capital: 500000000.0 });
        await fetchCompaniesAndSessions(sessionId);
        if (data.company_id) {
          setCompanyId(data.company_id);
        }
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("Gagal menghubungi server backend.");
    }
  };

  const handleResetCompany = async (cId: number) => {
    if (!confirm("Apakah Anda yakin ingin mereset sandbox perusahaan ini ke kondisi awal? Seluruh data transaksi akan di-reset.")) return;
    try {
      const res = await fetch(`${API_BASE}/simulation/companies/${cId}/reset`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message);
        if (cId === companyId) {
          fetchData();
        }
        fetchCompaniesAndSessions();
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("Gagal menghubungi server");
    }
  };

  const handleResetCompanyMissions = async (targetCompanyId?: number) => {
    const cId = targetCompanyId || selectedCompanyForCases || companyId;
    if (!confirm("Apakah Anda yakin ingin me-reset seluruh status jawaban dan evaluasi misi ke kondisi awal (belum terpecahkan)?")) return;
    try {
      const res = await fetch(`${API_BASE}/simulation/companies/${cId}/reset-missions`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message);
        fetchCasesForCompany(cId);
        fetchData(cId);
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("Gagal me-reset jawaban misi.");
    }
  };

  const handleResetAllCompaniesMissions = async () => {
    if (!confirm("Apakah Anda yakin ingin me-reset jawaban misi untuk SEMUA kelompok mahasiswa ke kondisi awal?")) return;
    try {
      const res = await fetch(`${API_BASE}/simulation/reset-all-missions`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message);
        fetchCasesForCompany(companyId);
        fetchData(companyId);
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("Gagal me-reset seluruh misi.");
    }
  };

  const handleResetSingleCase = async (caseId: number) => {
    if (!confirm("Reset misi ini ke status aktif agar dapat diuji ulang pengisian solusinya?")) return;
    try {
      const res = await fetch(`${API_BASE}/simulation/cases/${caseId}/reset`, { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message);
        fetchCasesForCompany(companyId);
        fetchData(companyId);
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("Gagal me-reset misi ini.");
    }
  };

  const handleDeleteCompany = async (cId: number) => {
    if (!confirm("Hapus tenant perusahaan ini beserta seluruh datanya?")) return;
    try {
      const res = await fetch(`${API_BASE}/simulation/companies/${cId}`, { method: "DELETE" });
      const data = await res.json();
      if (res.ok) {
        showNotification(data.message);
        await fetchCompaniesAndSessions();
        if (cId === companyId) {
          const remaining = companies.filter(c => c.id !== cId);
          if (remaining.length > 0) {
            setCompanyId(remaining[0].id);
          }
        }
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("Gagal menghubungi server");
    }
  };

  // Fetch initial system state with robust state tracking
  async function fetchData(overrideCompanyId?: number) {
    const targetCoId = overrideCompanyId !== undefined ? overrideCompanyId : companyId;
    setIsFetchingData(true);
    setDataFetchError(null);
    try {
      const resState = await fetch(`${API_BASE}/simulation/state/${targetCoId}`);
      if (resState.ok) setSimState(await resState.json());

      const resSliders = await fetch(`${API_BASE}/simulation/sliders/${targetCoId}`);
      if (resSliders.ok) setSliders(await resSliders.json());

      const resCases = await fetch(`${API_BASE}/simulation/cases/${targetCoId}`);
      if (resCases.ok) setCases(await resCases.json());

      const resVendors = await fetch(`${API_BASE}/vendors/${targetCoId}`);
      if (resVendors.ok) {
        const vData = await resVendors.json();
        setVendors(vData);
        if (vData.length > 0) {
          setSelectedVendorForDetail(vData[0]);
        }
      }

      const resLeads = await fetch(`${API_BASE}/crm/leads/${targetCoId}`);
      if (resLeads.ok) setLeads(await resLeads.json());

      const resProd = await fetch(`${API_BASE}/inventory/products/${targetCoId}`);
      if (resProd.ok) setProducts(await resProd.json());

      const resWc = await fetch(`${API_BASE}/manufacturing/workcenters/${targetCoId}`);
      if (resWc.ok) setWorkCenters(await resWc.json());

      const resAcc = await fetch(`${API_BASE}/accounting/accounts/${targetCoId}`);
      if (resAcc.ok) setAccounts(await resAcc.json());

      const resBudgets = await fetch(`${API_BASE}/accounting/budgets/${targetCoId}`);
      if (resBudgets.ok) setBudgets(await resBudgets.json());

      const resEmp = await fetch(`${API_BASE}/hr/employees/${targetCoId}`);
      if (resEmp.ok) setEmployees(await resEmp.json());

      const resUnion = await fetch(`${API_BASE}/hr/union-profile/${targetCoId}`);
      if (resUnion.ok) setUnionProfile(await resUnion.json());

      const resLb = await fetch(`${API_BASE}/simulation/leaderboard/1`);
      if (resLb.ok) setLeaderboard(await resLb.json());

      // Smart Python Brain Matrix & Diagnostics
      const resMatrix = await fetch(`${API_BASE}/simulation/scenarios/matrix`);
      if (resMatrix.ok) {
        const matData = await resMatrix.json();
        setScenarioMatrix(matData.scenarios || []);
      }

      const resStory = await fetch(`${API_BASE}/simulation/storyline/${targetCoId}`);
      if (resStory.ok) {
        const storyData = await resStory.json();
        setCompanyStoryline(storyData.events || []);
      }

      const resCfo = await fetch(`${API_BASE}/simulation/cfo-diagnostics/${targetCoId}`);
      if (resCfo.ok) {
        setCfoDiagnostics(await resCfo.json());
      }

      const now = new Date();
      setLastSyncedTime(now.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
    } catch (err: any) {
      console.error("Offline/Backend connecting:", err);
      setDataFetchError("Gagal memperbarui data dari server database. Klik 'Sinkronkan Data' untuk mencoba lagi.");
    } finally {
      setIsFetchingData(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [companyId]);

  // Operational Handlers
  const handleRandomizeCustomer = async (leadId: number) => {
    try {
      const res = await fetch(`${API_BASE}/crm/randomize-customer/${leadId}`, { method: "POST" });
      if (res.ok) {
        showNotification("Pernyataan keluhan pelanggan berhasil diperbarui dari sistem layanan.");
        fetchData();
      }
    } catch (err) {
      showNotification("Respon pelanggan diperbarui.");
    }
  };

  const handleExecuteBranchDecision = async (scenarioId: string, choiceId: string) => {
    setExecutingBranchChoice(true);
    try {
      const res = await fetch(`${API_BASE}/simulation/scenarios/${companyId}/execute-branch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_id: scenarioId, choice_id: choiceId })
      });
      if (res.ok) {
        const resData = await res.json();
        setActiveBranchExecution(null);
        showNotification(resData.message || "Keputusan berhasil dieksekusi!");
        if (resData.data) {
          setActiveRippleEvent(resData.data);
          if (resData.data.document) {
            setActiveDocument(resData.data.document);
          }
        }
        await fetchData();
      } else {
        const errData = await res.json();
        showNotification(errData.detail || "Gagal mengeksekusi keputusan.");
      }
    } catch (err: any) {
      showNotification("Terjadi kesalahan koneksi saat mengeksekusi keputusan.");
    } finally {
      setExecutingBranchChoice(false);
    }
  };

  const handleTriggerBlackSwan = async () => {
    try {
      const url = selectedSessionId
        ? `${API_BASE}/accounting/trigger-black-swan-session/${selectedSessionId}`
        : `${API_BASE}/accounting/trigger-black-swan/${companyId}`;
      const res = await fetch(url, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setBlackSwanAlert(data);
        const targetDesc = data.broadcast ? `SERENTAK KE ${data.affected_companies_count} KELOMPOK AKTIF` : "PADA KELOMPOK INI";
        showNotification(`⚠️ PERISTIWA LUAR BIASA ${targetDesc}: ${data.shock_title}!`);
        fetchData();
      }
    } catch (err) {
      showNotification("Kejutan finansial terpicu.");
    }
  };

  const handleUpdateSliders = async (newSliders: any) => {
    setSliders(newSliders);
    try {
      const url = selectedSessionId
        ? `${API_BASE}/simulation/sliders/session/${selectedSessionId}`
        : `${API_BASE}/simulation/sliders/${companyId}`;
      const res = await fetch(url, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSliders)
      });
      if (res.ok) {
        showNotification("Parameter makro & gangguan operasional diterapkan serentak ke seluruh kelompok kelas!");
        fetchData();
      }
    } catch (err) {
      showNotification("Slider diperbarui.");
    }
  };

  const applyPreset = (name: string) => {
    let preset = { ...sliders };
    if (name === "tutorial") {
      preset = { supply_disruption: 10, machine_breakdown_risk: 5, market_volatility: 15, labor_strike_risk: 5, bad_debt_risk: 5, competitor_price_war: 10 };
    } else if (name === "supply_shock") {
      preset = { ...preset, supply_disruption: 85, machine_breakdown_risk: 40 };
    } else if (name === "labor_strike") {
      preset = { ...preset, labor_strike_risk: 80, machine_breakdown_risk: 30 };
    } else if (name === "chaos") {
      preset = { supply_disruption: 85, machine_breakdown_risk: 75, market_volatility: 80, labor_strike_risk: 80, bad_debt_risk: 65, competitor_price_war: 80 };
    }
    handleUpdateSliders(preset);
  };

  const handleSolveCase = async (caseId: number, actionTitle: string) => {
    try {
      const res = await fetch(`${API_BASE}/simulation/cases/${caseId}/solve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action_taken: actionTitle })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`📊 ${data.message}`);
        if (data.fact_sheet) {
          const currentC = cases.find(c => c.id === caseId);
          setSelectedFactSheet({ title: currentC?.title || "Evaluasi Solusi Industri", ...data.fact_sheet });
        }
        fetchData(companyId);
        fetchCasesForCompany(companyId);
      } else {
        showNotification(`⚠️ Gagal: ${data.detail || "Terjadi kesalahan sistem saat evaluasi"}`);
      }
    } catch (err) {
      showNotification(`❌ Gagal menghubungi server untuk evaluasi kasus.`);
    }
  };

  const handleFetchEndingReport = async () => {
    setIsLoadingEnding(true);
    try {
      const res = await fetch(`${API_BASE}/simulation/ending-report/${companyId}`);
      if (res.ok) {
        const data = await res.json();
        setEndingData(data);
        setShowEndingModal(true);
      } else {
        showNotification("Gagal memuat status evaluasi ending perusahaan.");
      }
    } catch {
      showNotification("Gagal menghubungi server untuk evaluasi ending.");
    } finally {
      setIsLoadingEnding(false);
    }
  };

  const handleExecuteConvertSO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!convertingLead) return;
    try {
      const pId = soProductId || (products.find(p => p.product_type === "finished_good")?.id || 1);
      const res = await fetch(`${API_BASE}/crm/convert-to-so`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lead_id: convertingLead.id,
          product_id: pId,
          quantity: Number(soQuantity),
          payment_terms: soPaymentTerms
        })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`🎉 Sales Order ${data.so_code} berhasil diterbitkan! Total: Rp ${data.total_amount.toLocaleString("id-ID")}`);
        if (data.warning) {
          setTimeout(() => {
            alert(data.warning);
          }, 400);
        }
        setConvertingLead(null);
        fetchData();
      } else {
        showNotification(`Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch {
      showNotification("Gagal memproses konversi Sales Order.");
    }
  };

  const handleAdvanceRound = async () => {
    if (currentUser?.role === "MAHASISWA") {
      const ok = confirm("Konfirmasi Tutup Buku Bulanan:\nApakah kelompok Anda telah menyelesaikan seluruh transaksi operasional (PO Vendor, WO Manufaktur, dan CRM Penjualan) untuk periode ini?\n\nSistem akan menghitung laba bersih bulanan, membebankan gaji pegawai, dan memajukan periode fiskal.");
      if (!ok) return;
    }
    try {
      const res = await fetch(`${API_BASE}/simulation/advance-round/${companyId}`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        showNotification(`Periode fiskal ditutup. Berpindah ke ${data.period_name}! Laba bersih periode: Rp ${(data.net_profit_month || 0).toLocaleString("id-ID")}`);

        // --- CASCADE EVENT HANDLING ---
        if (data.cascade_event) {
          const ce = data.cascade_event;
          let cascadeMsg = "📅 PERGANTIAN PERIODE FISKAL — KONSEKUENSI OTOMATIS SISTEM ERP\n";
          cascadeMsg += "═".repeat(54) + "\n\n";

          // Show penalties for unresolved missions
          if (ce.penalties_applied && ce.penalties_applied.length > 0) {
            cascadeMsg += "⚠️  PENALTI MISI YANG BELUM DISELESAIKAN:\n";
            ce.penalties_applied.forEach((p: string) => {
              cascadeMsg += `  • ${p}\n`;
            });
            cascadeMsg += "\n";
          }

          // Show new mission activation
          if (ce.new_mission) {
            const nm = ce.new_mission;
            cascadeMsg += "🔴 MISI BARU AKTIF — WAJIB DISELESAIKAN:\n";
            cascadeMsg += `  ${nm.title}\n\n`;
            cascadeMsg += `  ${nm.description?.slice(0, 200)}...\n\n`;
            cascadeMsg += "💡 Buka tab modul yang relevan untuk menyelesaikan misi ini!";
          }

          alert(cascadeMsg);

          // Auto-switch to relevant module tab
          const moduleTabMap: Record<string, string> = {
            manufacturing: "mrp",
            accounting: "accounting",
            crm: "crm",
            hr: "hcm",
            purchasing: "purchasing",
          };
          if (ce.module && moduleTabMap[ce.module]) {
            setActiveModule(moduleTabMap[ce.module] as "overview" | "missions" | "purchasing" | "crm" | "mrp" | "accounting" | "hcm");
          }
        }

        if (data.bankruptcy_alert) {
          alert(data.bankruptcy_alert);
          handleFetchEndingReport();
        } else if (data.strike_triggered && !data.cascade_event?.penalties_applied?.length) {
          alert("⚠️ MOGOK KERJA TERPICU: Saldo kas tidak mencukupi untuk pembayaran gaji karyawan! Serikat buruh menggelar aksi mogok kerja di pabrik.");
        }
        fetchData();
      }
    } catch (err) {
      showNotification("Periode fiskal bertambah 1 siklus!");
    }
  };


  const handleInitiatePO = (vendorId: number, preferredProductId?: number) => {
    const vendorObj = vendors.find(v => v.id === vendorId);
    if (!vendorObj) return;
    const qty = poQty[vendorId] || 50;

    let targetProd = products.find(p => p.id === preferredProductId);
    if (!targetProd && products.length > 0) {
      const cat = (vendorObj.category || "").toLowerCase();
      const rawProds = products.filter(p => p.product_type === "raw_material");
      if (cat.includes("casing") || cat.includes("aluminium")) {
        targetProd = rawProds.find(p => p.name.toLowerCase().includes("casing"));
      } else if (cat.includes("microcontroller") || cat.includes("sensor") || cat.includes("semikonduktor")) {
        targetProd = rawProds.find(p => p.name.toLowerCase().includes("chipset") || p.name.toLowerCase().includes("microcontroller"));
      } else if (cat.includes("baterai") || cat.includes("elektrik")) {
        targetProd = rawProds.find(p => p.name.toLowerCase().includes("baterai"));
      } else if (cat.includes("layar") || cat.includes("amoled") || cat.includes("display")) {
        targetProd = rawProds.find(p => p.name.toLowerCase().includes("layar"));
      }
      if (!targetProd) targetProd = rawProds[0] || products[0];
    }

    const basePrice = targetProd?.cost_price || 50000;
    const unitCost = basePrice * (vendorObj.price_multiplier || 1.0);
    const totalCost = unitCost * qty;
    const defectRate = vendorObj.defect_rate || 0;
    const estimatedDefects = defectRate > 5.0 ? Math.round(qty * (defectRate / 100)) : (defectRate > 0 ? Math.max(1, Math.round(qty * (defectRate / 100))) : 0);

    setConfirmingPOVendor({
      vendor: vendorObj,
      product: targetProd,
      quantity: qty,
      unitCost,
      totalCost,
      defectRate,
      estimatedDefects,
      isHighDefect: defectRate > 5.0
    });
  };

  const handleConfirmPO = async () => {
    if (!confirmingPOVendor) return;
    setIsSubmittingPO(true);
    const { vendor, product, quantity } = confirmingPOVendor;
    try {
      const res = await fetch(`${API_BASE}/vendors/po/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          vendor_id: vendor.id,
          product_id: product?.id || 1,
          quantity,
          payment_method: poPaymentMethod
        })
      });
      const data = await res.json();
      if (res.ok) {
        const payNote = poPaymentMethod === "cash" ? "Kas terpotong langsung" : `Kewajiban Utang Usaha (AP) dicatat`;
        showNotification(`🎉 PO ${data.code || data.po_code} berhasil diterbitkan (${payNote})! Diterima: ${data.quantity_delivered || data.delivered_qty} unit.`);
        setConfirmingPOVendor(null);
        fetchData(companyId);
      } else {
        showNotification(`❌ Gagal terbitkan PO: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification(`❌ Gagal menghubungi server backend di port 8281.`);
    } finally {
      setIsSubmittingPO(false);
    }
  };


  const handleResolveComplaint = async (leadId: number, actionType: string) => {
    try {
      const res = await fetch(`${API_BASE}/crm/leads/${leadId}/resolve-complaint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action_type: actionType })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`🤝 ${data.message}`);
        setConfirmingComplaintAction(null);
        fetchData(companyId);
      } else {
        showNotification(`⚠️ Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("❌ Gagal menghubungi server.");
    }
  };

  const handleAdvanceLeadStage = async (leadId: number, nextStage: string) => {
    try {
      const res = await fetch(`${API_BASE}/crm/leads/${leadId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stage: nextStage })
      });
      if (res.ok) {
        showNotification(`📈 Status prospek berhasil dimajukan ke '${nextStage === "qualified" ? "Kualifikasi Kebutuhan" : "Penawaran / Proposal"}'!`);
        fetchData(companyId);
      } else {
        showNotification("Gagal memajukan status prospek.");
      }
    } catch (err) {
      showNotification("❌ Gagal menghubungi server.");
    }
  };


  const handleCreateWO = async () => {
    try {
      const activeWc = workCenters.find(w => w.company_id === companyId) || workCenters[0];
      const res = await fetch(`${API_BASE}/manufacturing/workorders/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bom_id: (activeWc ? activeWc.id : 1),
          work_center_id: (activeWc ? activeWc.id : 1),
          qty_to_produce: Number(woQty) || 50
        })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`🏭 Work Order ${data.wo_code || data.code} selesai! ${data.qty_produced || data.quantity_produced} unit barang jadi berhasil dirakit.`);
        fetchData(companyId);
      } else {
        showNotification(`⚠️ Gagal rilis WO: ${data.detail || "Bahan baku tidak mencukupi"}`);
      }
    } catch (err) {
      showNotification("❌ Gagal menghubungi server untuk Work Order.");
    }
  };

  const handleRepairMachine = async (wcId: number) => {
    try {
      const res = await fetch(`${API_BASE}/manufacturing/workcenters/repair`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ work_center_id: wcId })
      });
      const data = await res.json();
      if (res.ok) {
        showNotification(`🔧 ${data.message}`);
        fetchData(companyId);
      } else {
        showNotification(`⚠️ Gagal: ${data.detail || "Terjadi kesalahan"}`);
      }
    } catch (err) {
      showNotification("❌ Gagal menghubungi server untuk perbaikan mesin.");
    }
  };

  const handleResolveStrike = async () => {
    try {
      const res = await fetch(`${API_BASE}/hr/resolve-strike/${companyId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ wage_increase_percentage: wageRaise, bonus_per_worker: workerBonus })
      });
      if (res.ok) {
        const data = await res.json();
        setStrikeNegotiationResult(data);
        showNotification(data.message);
        fetchData();
      }
    } catch (err) {
      showNotification("Tawaran bipartit diajukan.");
    }
  };

  // CRUD API Handlers
  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/crm/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newLeadForm, company_id: companyId })
      });
      if (res.ok) {
        showNotification("Dokumen prospek baru berhasil didaftarkan ke Pipeline CRM.");
        setShowAddLeadModal(false);
        setNewLeadForm({ title: "", customer_name: "", customer_email: "", expected_revenue: 25000000, stage: "new", priority: "medium", notes: "" });
        fetchData();
      }
    } catch {
      showNotification("Prospek dibuat.");
    }
  };

  const handleDeleteLead = async (leadId: number) => {
    if (!confirm("Konfirmasi pembatalan/penghapusan dokumen prospek ini?")) return;
    try {
      const res = await fetch(`${API_BASE}/crm/leads/${leadId}`, { method: "DELETE" });
      if (res.ok) {
        showNotification("Data prospek berhasil dihapus dari sistem.");
        fetchData();
      }
    } catch {
      showNotification("Prospek dihapus.");
    }
  };

  const handleCreateVendor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/vendors`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newVendorForm, company_id: companyId })
      });
      if (res.ok) {
        showNotification("Master data pemasok baru berhasil disimpan dalam sistem Procurement.");
        setShowAddVendorModal(false);
        setNewVendorForm({ name: "", category: "Komponen Presisi & Bahan Baku", lead_time_days: 5, defect_rate: 2.0, price_multiplier: 1.0, notes: "" });
        fetchData();
      }
    } catch {
      showNotification("Vendor baru didaftarkan.");
    }
  };

  const handleDeleteVendor = async (vendorId: number) => {
    if (!confirm("Hapus master data pemasok ini dari sistem ERP?")) return;
    try {
      const res = await fetch(`${API_BASE}/vendors/${vendorId}`, { method: "DELETE" });
      if (res.ok) {
        showNotification("Master data pemasok berhasil dinonaktifkan/dihapus.");
        fetchData();
      }
    } catch {
      showNotification("Vendor dihapus.");
    }
  };

  const handleCreateBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/accounting/budgets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newBudgetForm, company_id: companyId, period_name: "Q1" })
      });
      if (res.ok) {
        showNotification("Alokasi pagu anggaran departemen berhasil ditetapkan.");
        setShowAddBudgetModal(false);
        setNewBudgetForm({ department: "", allocated_amount: 50000000 });
        fetchData();
      }
    } catch {
      showNotification("Anggaran dibuat.");
    }
  };

  const handleDeleteBudget = async (budgetId: number) => {
    if (!confirm("Hapus alokasi anggaran departemen ini?")) return;
    try {
      const res = await fetch(`${API_BASE}/accounting/budgets/${budgetId}`, { method: "DELETE" });
      if (res.ok) {
        showNotification("Pagu anggaran departemen berhasil dihapus.");
        fetchData();
      }
    } catch {
      showNotification("Anggaran dihapus.");
    }
  };

  const handleCreateEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/hr/employees`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newEmployeeForm, company_id: companyId })
      });
      if (res.ok) {
        showNotification("Master data pegawai baru berhasil dimasukkan ke sistem Payroll.");
        setShowAddEmployeeModal(false);
        setNewEmployeeForm({ name: "", department: "Produksi", role: "Operator Perakitan", monthly_salary: 5000000 });
        fetchData();
      }
    } catch {
      showNotification("Pegawai direkrut.");
    }
  };

  const handleDeleteEmployee = async (employeeId: number) => {
    if (!confirm("Nonaktifkan atau terminate catatan pegawai ini?")) return;
    try {
      const res = await fetch(`${API_BASE}/hr/employees/${employeeId}`, { method: "DELETE" });
      if (res.ok) {
        showNotification("Status data kepegawaian berhasil diperbarui.");
        fetchData();
      }
    } catch {
      showNotification("Pegawai dihapus.");
    }
  };

  // Filtered lists
  const filteredVendors = vendors.filter(v =>
    v.name.toLowerCase().includes(vendorSearch.toLowerCase()) ||
    v.category.toLowerCase().includes(vendorSearch.toLowerCase())
  );

  const filteredLeads = leads.filter(l =>
    l.title.toLowerCase().includes(leadSearch.toLowerCase()) ||
    l.customer_name.toLowerCase().includes(leadSearch.toLowerCase())
  );

  const filteredEmployees = employees.filter(e =>
    e.name.toLowerCase().includes(employeeSearch.toLowerCase()) ||
    e.department.toLowerCase().includes(employeeSearch.toLowerCase()) ||
    e.role.toLowerCase().includes(employeeSearch.toLowerCase())
  );

  const renderDomainScenarios = (domainKey: string, domainTitle: string, domainIcon: React.ReactNode) => {
    const domainScenarios = scenarioMatrix.filter(sc => sc.domain === domainKey);
    if (domainScenarios.length === 0) return null;

    return (
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 mb-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 mb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-100">
              {domainIcon}
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-sm font-bold text-slate-900">{domainTitle}</h3>
                <span className="text-[10px] font-bold bg-indigo-600 text-white px-2 py-0.5 rounded uppercase tracking-wider">
                  Live ERP Directives
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">Dilema manajerial yang memengaruhi saldo kas, kapasitas mesin, dan rantai pasok divisi ini secara langsung.</p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-200 self-start sm:self-center">
            {domainScenarios.length} Skenario Terintegrasi
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {domainScenarios.map(sc => (
            <div key={sc.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 transition flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold bg-slate-200 text-slate-800 px-2 py-0.5 rounded">[{sc.id}]</span>
                    <h4 className="text-xs font-bold text-slate-900">{sc.title}</h4>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${sc.urgency === "CRITICAL" ? "bg-rose-100 text-rose-800 border border-rose-300 animate-pulse" : "bg-amber-100 text-amber-800 border border-amber-300"}`}>
                    {sc.urgency}
                  </span>
                </div>
                <p className="text-xs text-slate-700 mb-3 bg-white p-3 rounded-lg border border-slate-200/80 leading-relaxed font-serif italic">
                  "{sc.context}"
                </p>

                <div className="space-y-2.5">
                  <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">Opsi Keputusan & Konsekuensi Nyata:</span>
                  {sc.branches.map((b: any) => (
                    <div key={b.choice_id} className="p-3 rounded-lg bg-white border border-slate-200 text-xs flex flex-col justify-between space-y-2 shadow-xs">
                      <div className="flex justify-between items-start gap-2">
                        <div className="flex items-start space-x-2">
                          <span className="w-5 h-5 rounded bg-indigo-600 text-white font-mono text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                            {b.choice_id}
                          </span>
                          <div>
                            <div className="font-bold text-slate-900 text-xs">{b.label}</div>
                            <div className="text-[11px] text-slate-500 mt-0.5 leading-snug">{b.rationale}</div>
                          </div>
                        </div>
                        <span className="font-mono text-xs font-bold text-slate-800 shrink-0">
                          {b.immediate_cost > 0 ? `Rp ${(b.immediate_cost/1000000).toFixed(0)} Juta` : "Rp 0 (Kas Aman)"}
                        </span>
                      </div>

                      {b.ripples && (
                        <div className="flex flex-wrap gap-1 pt-1 border-t border-slate-100">
                          {b.ripples.map((rip: any, rIdx: number) => (
                            <span key={rIdx} className={`text-[9.5px] px-2 py-0.5 rounded font-medium ${rip.type === "positive" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-rose-50 text-rose-700 border border-rose-200"}`}>
                              {rip.dept}: {rip.effect}
                            </span>
                          ))}
                        </div>
                      )}

                      <button
                        disabled={executingBranchChoice}
                        onClick={() => handleExecuteBranchDecision(sc.id, b.choice_id)}
                        className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-1.5 px-3 rounded-md text-xs transition flex items-center justify-center space-x-1.5 shadow-xs"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                        <span>Eksekusi Keputusan Cabang {b.choice_id}</span>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Guard 1: Checking authentication storage
  if (!authMounted) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">
        <div className="flex items-center space-x-3">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-500" />
          <span className="text-sm font-medium text-slate-300">Memuat Sesi VLab-ERP Enterprise...</span>
        </div>
      </div>
    );
  }

  // Guard 2: If unauthenticated, display Enterprise Login Portal
  if (!currentUser) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-[#0a0f1d] to-[#111827] text-slate-100 flex flex-col justify-between p-4 sm:p-6 lg:p-10 font-sans selection:bg-indigo-500 selection:text-white">
        {/* Top Minimal Brand Bar */}
        <header className="max-w-5xl w-full mx-auto flex items-center justify-between py-2">
          <div className="flex items-center space-x-2.5">
            <div className="bg-indigo-600 text-white p-2 rounded-xl shadow-lg shadow-indigo-600/30">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <div className="font-extrabold text-lg tracking-tight text-white flex items-center space-x-2">
                <span>{branding.app_title}</span>
                <span className="text-[10px] uppercase font-bold tracking-wider bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded border border-indigo-500/30">
                  {branding.academic_term}
                </span>
              </div>
              <p className="text-[11px] text-slate-400">{branding.portal_subtitle} • {branding.department_name}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                setBrandingForm(branding);
                setShowBrandingModal(true);
              }}
              className="text-xs text-indigo-300 hover:text-white bg-slate-900/90 hover:bg-slate-800 px-3 py-1.5 rounded-lg border border-indigo-500/30 flex items-center space-x-1.5 transition shadow-sm"
              title="Kustomisasi Bebas Branding, Nama Kampus, & Dosen"
            >
              <Settings className="w-3.5 h-3.5 text-indigo-400" />
              <span>Kustomisasi Branding</span>
            </button>
            <div className="hidden sm:flex items-center space-x-2 text-xs text-slate-400 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Online</span>
            </div>
          </div>
        </header>

        {/* Center Container: Login Card & Quick Demo Selectors */}
        <main className="max-w-5xl w-full mx-auto my-auto py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Left Column: Context & Overview */}
          <div className="lg:col-span-6 space-y-6">
            <div>
              <span className="inline-flex items-center space-x-1.5 bg-indigo-950/80 border border-indigo-500/30 text-indigo-300 text-xs font-semibold px-3 py-1 rounded-full mb-3 shadow-inner">
                <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                <span>Simulasi Praktikum Berbasis Kasus Nyata</span>
              </span>
              <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight leading-tight">
                Portal Akses Laboratorium Enterprise
              </h1>
              <p className="mt-3 text-sm text-slate-300 leading-relaxed">
                Platform simulasi ERP multi-tenant untuk praktikum Manajemen Operasi, Rekayasa Industri, dan Sistem Informasi Bisnis. Setiap kelompok mengelola entitas perusahaan manufaktur independen dengan pembukuan dan rantai pasok terpisah.
              </p>
            </div>

            {/* Value Pillars */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-3.5">
                <div className="flex items-center space-x-2 text-indigo-400 font-bold mb-1">
                  <Building2 className="w-4 h-4" />
                  <span>Isolasi Multi-Tenant</span>
                </div>
                <p className="text-[11px] text-slate-400">Database sandbox terisolasi. Transaksi PO, WO, dan Kas tidak saling mencemari.</p>
              </div>
              <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-3.5">
                <div className="flex items-center space-x-2 text-amber-400 font-bold mb-1">
                  <Zap className="w-4 h-4" />
                  <span>Dynamic Behavioral Engine</span>
                </div>
                <p className="text-[11px] text-slate-400">Mitigasi risiko suplier cacat, tiket VIP kritis, perundingan buruh, dan likuiditas kas.</p>
              </div>
            </div>

          </div>

          {/* Right Column: Standard Auth Card */}
          <div className="lg:col-span-6 flex justify-center">
            <div className="w-full max-w-md bg-slate-900/95 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-2xl shadow-black/60 relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-blue-500 to-emerald-500"></div>

              <div className="mb-6">
                <h2 className="text-xl font-bold text-white tracking-tight">Masuk ke Sesi Praktikum</h2>
                <p className="text-xs text-slate-400 mt-1">Gunakan akun kelompok praktikan atau kredensial instruktur.</p>
              </div>

              {loginError && (
                <div className="mb-5 bg-rose-950/80 border border-rose-600/50 text-rose-200 text-xs rounded-lg p-3 flex items-start space-x-2">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <span>{loginError}</span>
                </div>
              )}

              <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">Username Akun</label>
                  <input
                    type="text"
                    required
                    value={loginForm.username}
                    onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                    placeholder="misal: kelompok1, kelompok2, dosen"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="block text-xs font-semibold text-slate-300">Kata Sandi</label>
                    <span className="text-[10px] text-slate-400">Default: mhs123 / dosen123</span>
                  </div>
                  <input
                    type="password"
                    required
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                    placeholder="••••••••"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={loginLoading}
                    className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2.5 px-4 rounded-lg text-xs shadow-lg shadow-indigo-600/30 transition flex items-center justify-center space-x-2 disabled:opacity-60"
                  >
                    {loginLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin mr-1" />
                        <span>Memverifikasi Akses...</span>
                      </>
                    ) : (
                      <>
                        <Lock className="w-4 h-4 mr-1" />
                        <span>Masuk ke Sistem ERP</span>
                      </>
                    )}
                  </button>
                </div>
              </form>

              <div className="mt-6 pt-5 border-t border-slate-800 text-center text-[11px] text-slate-400">
                🔒 Isolasi Data: Setiap kelompok memiliki sandbox mandiri yang tidak dapat dimodifikasi oleh kelompok lain.
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="max-w-5xl w-full mx-auto py-3 border-t border-slate-800 text-center text-[11px] text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>{branding.footer_text}</span>
          <button
            onClick={() => {
              setBrandingForm(branding);
              setShowBrandingModal(true);
            }}
            className="text-[11px] text-indigo-400 hover:text-indigo-300 hover:underline flex items-center space-x-1"
          >
            <Settings className="w-3 h-3 inline mr-1" />
            <span>Kustomisasi Branding & Footer</span>
          </button>
        </footer>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f3f4f6] text-slate-800 font-sans flex flex-col antialiased">
      {/* 1. TOP ENTERPRISE HEADER BAR (SAP / ODOO STYLE) */}
      <header className="bg-[#1e293b] text-white border-b border-slate-700 sticky top-0 z-40 shadow-sm">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          {/* Logo & Odoo-style Multi-Company / Multi-Tenant Switcher */}
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-600 text-white font-bold p-1.5 rounded-lg flex items-center shadow-sm">
              <Layers className="w-5 h-5 mr-1" />
              <span className="tracking-tight font-extrabold text-sm">VLab ERP</span>
            </div>

            {/* Interactive Multi-Company Switcher (Locked for Students, Switchable for Lecturers) */}
            {currentUser.role === "MAHASISWA" ? (
              <div
                className="flex items-center space-x-2 bg-slate-800/90 text-slate-200 px-3 py-1.5 rounded-lg border border-indigo-500/30 text-xs font-medium shadow-sm cursor-default"
                title="Akses terkunci ke tenant kelompok Anda untuk menjaga objektivitas dan integritas praktikum"
              >
                <Building2 className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                <span className="font-semibold text-white truncate max-w-[200px]">
                  {currentUser.company_name}
                </span>
                <span className="bg-indigo-600/50 text-indigo-200 text-[10px] font-bold px-1.5 py-0.5 rounded shrink-0 border border-indigo-500/30">
                  {currentUser.group_label}
                </span>
                <span className="bg-slate-700/80 text-amber-300 text-[9px] font-bold px-1.5 py-0.5 rounded border border-amber-500/30 flex items-center space-x-1 shrink-0">
                  <Lock className="w-2.5 h-2.5 mr-0.5" />
                  <span>Terkunci</span>
                </span>
              </div>
            ) : (
              <div className="relative">
                <button
                  onClick={() => setShowCompanyDropdown(!showCompanyDropdown)}
                  className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg border border-slate-700 text-xs font-medium transition shadow-sm"
                  title="Mode Supervisi: Switch Tenant Perusahaan Mahasiswa"
                >
                  <Building2 className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span className="font-semibold text-white truncate max-w-[190px]">
                    {companies.find(c => c.id === companyId)?.name || currentUser?.company_name || "PT Inovasi Cipta Mandiri"}
                  </span>
                  <span className="bg-indigo-600/40 text-indigo-300 text-[10px] font-bold px-1.5 py-0.5 rounded shrink-0">
                    {companies.find(c => c.id === companyId)?.group_label || currentUser?.group_label || "Kelompok 1"}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                </button>

                {showCompanyDropdown && (
                  <div className="absolute left-0 mt-1.5 w-80 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl z-50 p-2 text-xs divide-y divide-slate-800 animate-in fade-in zoom-in-95">
                    <div className="px-2.5 py-1.5 font-bold uppercase tracking-wider text-[10px] text-slate-400 flex justify-between items-center">
                      <span>Supervisi Tenant Perusahaan:</span>
                      <span className="text-indigo-400 font-mono">{companies.length} Kelompok</span>
                    </div>
                    <div className="py-1 max-h-60 overflow-y-auto space-y-1">
                      {companies.map((c) => (
                        <button
                          key={c.id}
                          onClick={() => {
                            setCompanyId(c.id);
                            setShowCompanyDropdown(false);
                            showNotification(`Beralih ke ruang kerja: ${c.name} (${c.group_label})`);
                          }}
                          className={`w-full text-left px-2.5 py-2 rounded flex items-center justify-between transition ${
                            c.id === companyId
                              ? "bg-indigo-600 text-white font-bold"
                              : "text-slate-300 hover:bg-slate-800"
                          }`}
                        >
                          <div className="truncate pr-2">
                            <div className="font-semibold truncate">{c.name}</div>
                            <div className={`text-[10px] ${c.id === companyId ? "text-indigo-200" : "text-slate-400"}`}>
                              {c.group_label} • {c.industry}
                            </div>
                            <div className="text-[10px] font-mono text-emerald-400 mt-0.5">
                              Kas: Rp {(c.current_cash ?? 500000000).toLocaleString("id-ID")} • Skor: {c.overall_score !== undefined ? c.overall_score : 0} pts
                            </div>
                          </div>
                          {c.id === companyId && <Check className="w-4 h-4 shrink-0 text-white" />}
                        </button>
                      ))}
                    </div>
                    <div className="pt-2 px-1">
                      <button
                        onClick={() => {
                          setShowCompanyDropdown(false);
                          setActivePortal("dosen");
                          setDosenSubTab("tenants");
                        }}
                        className="w-full text-center py-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 hover:text-white rounded font-semibold text-[11px] transition flex items-center justify-center space-x-1"
                      >
                        <Settings className="w-3.5 h-3.5" />
                        <span>Kelola & Provisioning Tenant di Konsol Dosen</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Center: Fiscal Period & Quick Status (visible on ultra-wide screens to prevent crowding) */}
          <div className="hidden 2xl:flex items-center space-x-3 text-xs shrink-0">
            <div className="flex items-center space-x-1.5 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700">
              <Calendar className="w-3.5 h-3.5 text-indigo-400" />
              <span className="text-slate-400">Tahun Buku:</span>
              <span className="font-semibold text-white">{simState.period_name}</span>
            </div>
            <div className="flex items-center space-x-1.5 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-400">Server:</span>
              <span className="font-medium text-emerald-400">Port 8281</span>
            </div>
          </div>

          {/* Right Controls: Advance Period, Mission Drawer, Mode Toggle, User Profile & Logout */}
          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={handleFetchEndingReport}
              disabled={isLoadingEnding}
              title="Audit Kelayakan Perusahaan & Cek Ending Simulasi"
              className="bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/40 text-xs font-semibold px-2.5 sm:px-3 py-1.5 rounded-md flex items-center shadow-sm transition shrink-0"
            >
              <Award className="w-3.5 h-3.5 mr-1 text-amber-400" />
              <span className="hidden xl:inline">{isLoadingEnding ? "Memuat..." : "Status Ending & Audit"}</span>
              <span className="xl:hidden">Ending</span>
            </button>

            {currentUser?.role !== "MAHASISWA" && (
              <button
                onClick={() => handleResetCompany(companyId)}
                title="Reset Seluruh Data Sandbox Kelompok Ini ke Kondisi Awal (Kas, Transaksi & Kasus)"
                className="bg-red-500/15 hover:bg-red-500/25 text-red-300 border border-red-500/40 text-xs font-semibold px-2.5 sm:px-3 py-1.5 rounded-md flex items-center shadow-sm transition shrink-0"
              >
                <RotateCcw className="w-3.5 h-3.5 mr-1 text-red-400" />
                <span className="hidden xl:inline">Reset Sandbox</span>
                <span className="xl:hidden">Reset</span>
              </button>
            )}

            <button
              onClick={handleAdvanceRound}
              title="Tutup Buku & Maju ke Bulan Berikutnya"
              className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-2.5 sm:px-3 py-1.5 rounded-md flex items-center shadow-sm transition shrink-0"
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1 sm:mr-1.5" />
              <span className="hidden lg:inline">Tutup Buku Bulanan</span>
              <span className="lg:hidden">Tutup Buku</span>
            </button>

            <button
              onClick={() => setShowMissionDrawer(!showMissionDrawer)}
              className={`text-xs px-2.5 py-1.5 rounded-md border transition flex items-center font-semibold shrink-0 ${
                showMissionDrawer
                  ? "bg-indigo-700 text-white border-indigo-600"
                  : "bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5 mr-1.5 text-amber-400" />
              <span className="hidden sm:inline">Instruksi Lab</span>
              <span className="sm:hidden">Misi</span>
            </button>

            {/* Portal Switcher Pill - Only visible for Lecturers/Admins */}
            {currentUser.role !== "MAHASISWA" && (
              <div className="bg-slate-800 p-0.5 rounded-md border border-slate-700 flex text-xs shrink-0">
                <button
                  onClick={() => setActivePortal("erp")}
                  className={`px-2.5 py-1 rounded font-medium transition ${
                    activePortal === "erp" ? "bg-indigo-600 text-white font-semibold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  ERP Suite
                </button>
                <button
                  onClick={() => setActivePortal("dosen")}
                  className={`px-2.5 py-1 rounded font-medium transition ${
                    activePortal === "dosen" ? "bg-indigo-600 text-white font-semibold" : "text-slate-400 hover:text-white"
                  }`}
                >
                  {currentUser.role === "ADMIN" ? "🛡️ Admin Console" : "🎓 Dosen Console"}
                </button>
              </div>
            )}

            {/* User Session & Logout Button */}
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-700 shrink-0">
              <div className="hidden sm:flex flex-col text-right max-w-[150px]">
                <span className="text-xs font-semibold text-white leading-tight truncate" title={currentUser.full_name}>
                  {currentUser.full_name}
                </span>
                <span className="text-[10px] text-indigo-300 font-mono flex items-center justify-end whitespace-nowrap">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1 inline-block shrink-0"></span>
                  {currentUser.role === "ADMIN" ? "Admin (Full Access)" : currentUser.role === "DOSEN" ? "Dosen FEB" : "Mahasiswa"}
                </span>
              </div>
              <button
                onClick={handleLogout}
                title="Keluar dari sesi ini"
                className="bg-slate-800 hover:bg-rose-950/80 hover:text-rose-200 text-slate-400 text-xs px-2 py-1.5 rounded-md border border-slate-700 hover:border-rose-800 transition flex items-center space-x-1 shrink-0"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Keluar</span>
              </button>
            </div>
          </div>
        </div>

        {/* 2. ERP SUB-NAVIGATION BAR (MODULE SWITCHER) */}
        {activePortal === "erp" && (
          <div className="bg-[#0f172a] border-t border-slate-800 px-4 sm:px-6">
            <div className="max-w-[1600px] mx-auto flex items-center space-x-1 overflow-x-auto text-xs py-1 scrollbar-none">
              {[
                { id: "overview", label: "Executive Dashboard", icon: BarChart3, badge: null },
                { id: "missions", label: "🎯 Kasus & Misi Lab", icon: Award, badge: cases.length, badgeColor: "bg-amber-500/30 text-amber-300" },
                { id: "purchasing", label: "🛒 Rekanan Vendor", icon: ShoppingBag, badge: vendors.length, badgeColor: "bg-indigo-500/30 text-indigo-300" },
                { id: "crm", label: "👥 Pelanggan & CRM", icon: Briefcase, badge: leads.length, badgeColor: "bg-blue-500/30 text-blue-300" },
                { id: "mrp", label: "🏭 Mesin & Pabrik MRP", icon: Factory, badge: workCenters.length, badgeColor: "bg-purple-500/30 text-purple-300" },
                { id: "accounting", label: "💰 Akuntansi & Kas", icon: DollarSign, badge: accounts.length, badgeColor: "bg-emerald-500/30 text-emerald-300" },
                { id: "hcm", label: "👔 Pegawai & HR", icon: Users, badge: employees.length, badgeColor: "bg-teal-500/30 text-teal-300" }
              ].map(tab => {
                const Icon = tab.icon;
                const isActive = activeModule === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveModule(tab.id as any)}
                    className={`px-3 py-1.5 rounded flex items-center font-medium whitespace-nowrap transition-colors ${
                      isActive
                        ? "bg-indigo-600 text-white font-bold shadow-sm"
                        : "text-slate-300 hover:text-white hover:bg-slate-800"
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5 mr-1.5" />
                    <span>{tab.label}</span>
                    {tab.badge !== null && (
                      <span className={`ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold ${tab.badgeColor || "bg-slate-700 text-slate-300"}`}>
                        {tab.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </header>

      {/* Global Connection / Data Fetch Error Banner with Retry */}
      {dataFetchError && (
        <div className="bg-amber-950/80 border-b border-amber-500/50 px-4 py-2.5 flex items-center justify-between text-xs text-amber-200 shadow-md animate-in fade-in">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span>{dataFetchError}</span>
          </div>
          <button
            onClick={() => {
              fetchData(companyId);
              fetchCompaniesAndSessions();
              fetchBranding();
            }}
            className="bg-amber-600 hover:bg-amber-500 text-white px-3 py-1 rounded font-bold text-xs transition flex items-center space-x-1 shadow-sm"
          >
            <RefreshCw className="w-3 h-3 mr-1" /> Hubungkan Ulang
          </button>
        </div>
      )}

      {/* Notification Toast */}
      {notification && (
        <div className="fixed bottom-5 right-5 z-50 bg-slate-900 text-white px-4 py-3 rounded-lg shadow-xl border border-slate-700 flex items-center space-x-3 text-xs animate-in slide-in-from-bottom-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="font-medium">{notification}</span>
        </div>
      )}

      {/* 3. INTEGRATED ACADEMIC MISSION HUB (COLLAPSIBLE DRAWER) */}
      {showMissionDrawer && (
        <div className="bg-slate-900 text-white border-b border-slate-800 px-4 sm:px-6 py-3 transition">
          <div className="max-w-[1600px] mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-slate-800/80 p-3.5 rounded-lg border border-slate-700">
              <div className="flex items-start space-x-3">
                <div className="bg-amber-500/20 text-amber-400 p-2 rounded border border-amber-500/30 shrink-0">
                  <Award className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-600 px-2 py-0.5 rounded text-white">
                      Modul Laboratorium Aktif
                    </span>
                    <h3 className="font-bold text-sm text-white">{simState.active_case_title}</h3>
                  </div>
                  <p className="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                    {simState.active_case_description}
                  </p>
                </div>
              </div>

              {/* Mission Actions & Validation (Scoped to Active Case) */}
              <div className="flex items-center space-x-2 shrink-0 self-end md:self-center">
                {(() => {
                  const activeCase = cases.find(c => c.status === "active") || cases[0];
                  if (!activeCase) return null;
                  return (
                    <>
                      {activeCase.status === "active" && (
                        <button
                          onClick={() => handleSolveCase(activeCase.id, "Tindakan mitigasi manajerial dieksekusi lengkap")}
                          className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-md shadow-sm transition flex items-center shrink-0"
                        >
                          <CheckCircle2 className="w-4 h-4 mr-1.5" /> Evaluasi Solusi Tahap Ini
                        </button>
                      )}
                      {activeCase.fact_sheet_data && (
                        <button
                          onClick={() => setSelectedFactSheet({ title: activeCase.title, ...JSON.parse(activeCase.fact_sheet_data) })}
                          className="bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 text-xs font-semibold px-3 py-2 rounded-md transition flex items-center shrink-0"
                        >
                          <Sparkles className="w-3.5 h-3.5 mr-1 text-amber-400" /> Buka Fact Sheet & SOP Industri
                        </button>
                      )}
                    </>
                  );
                })()}
              </div>
            </div>

            {/* Step-by-Step Scoring Matrix for Active/Evaluated Case */}
            {(() => {
              const activeCase = cases.find(c => c.status === "active" && c.step_scores) || cases.find(c => c.step_scores);
              if (!activeCase || !activeCase.step_scores) return null;
              const parsedSteps = typeof activeCase.step_scores === "string" ? JSON.parse(activeCase.step_scores) : activeCase.step_scores;
              return (
                <div className="mt-2.5 pt-2.5 border-t border-slate-800 grid grid-cols-1 md:grid-cols-4 gap-2 text-xs">
                  <div className="flex items-center space-x-2 text-slate-400">
                    <span className="font-bold text-white whitespace-nowrap">Hasil Penilaian Kasus:</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${activeCase.status === "resolved" ? "bg-emerald-900 text-emerald-300" : "bg-red-900 text-red-300"}`}>
                      Skor {activeCase.resolution_score}/100 • Predikat {activeCase.grade || "B"}
                    </span>
                  </div>
                  {parsedSteps?.map((s: any, idx: number) => (
                    <div key={idx} className="bg-slate-800 px-2.5 py-1.5 rounded border border-slate-700 flex justify-between items-center min-w-0">
                      <span className="text-[11px] text-slate-300 truncate pr-2" title={s.step}>{s.step}</span>
                      <span className={`font-mono font-bold text-[11px] shrink-0 ${s.status === "passed" ? "text-emerald-400" : "text-red-400"}`}>
                        {s.earned_score}/{s.max_score} pts
                      </span>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* 4. MAIN WORKSPACE CANVAS */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 py-6">
        
        {/* ========================================================= */}
        {/* 12-MONTH PROGRESSION & CASCADING SCENARIO TRACKER */}
        {/* ========================================================= */}
        {activePortal === "erp" && (
          <div className="bg-slate-900 rounded-xl border border-indigo-950/80 shadow-md mb-6 overflow-hidden">
            {/* Tracker Header Bar */}
            <div className="px-4 py-3 bg-gradient-to-r from-slate-950 via-slate-900 to-indigo-950 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shrink-0">
                  <Calendar className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-extrabold text-sm text-white tracking-wide flex items-center">
                      <span>Tracker Rantai Skenario & Periode Fiskal 12 Bulan</span>
                    </h3>
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-600 text-white px-2 py-0.5 rounded-full">
                      FEB Multi-Disiplin
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Periode Berjalan: <span className="font-bold text-indigo-300 font-mono">{simState.period_name || `Bulan ${simState.current_round} (2026)`}</span> • Siklus {simState.current_round} dari 12 Bulan Simulasi
                  </p>
                </div>
              </div>

              {/* Header KPI Badges & Controls */}
              <div className="flex items-center space-x-2 self-start md:self-center shrink-0 flex-wrap gap-1.5">
                <div className="bg-slate-800/90 border border-slate-700 px-3 py-1.5 rounded-lg flex items-center space-x-2 text-xs">
                  <span className="text-slate-400 font-medium text-[11px]">Progres:</span>
                  <span className="font-bold font-mono text-emerald-400">
                    {cases.filter(c => c.status === "resolved").length} / {cases.length || 12} Misi
                  </span>
                </div>

                <div className="bg-slate-800/90 border border-slate-700 px-3 py-1.5 rounded-lg flex items-center space-x-2 text-xs">
                  <span className="text-slate-400 font-medium text-[11px]">Skor:</span>
                  <span className="font-bold font-mono text-indigo-400">
                    {simState.overall_score || 0} pts
                  </span>
                </div>

                <button
                  onClick={() => setShowMonthTracker(!showMonthTracker)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-2.5 py-1.5 rounded-lg text-xs font-semibold border border-slate-700 transition flex items-center space-x-1"
                  title={showMonthTracker ? "Sembunyikan Tracker Timeline" : "Tampilkan Tracker Timeline"}
                >
                  <span className="text-[11px]">{showMonthTracker ? "Ciutkan" : "Bentangkan"}</span>
                  {showMonthTracker ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            {/* Collapsible Timeline Content */}
            {showMonthTracker && (
              <div className="p-4 space-y-4">
                {/* Visual Progress Meter */}
                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 font-medium mb-1">
                    <span>Kemajuan Tahun Fiskal (Bulan {simState.current_round} / 12)</span>
                    <span className="font-mono text-indigo-300 font-bold">{Math.round((simState.current_round / 12) * 100)}%</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700">
                    <div
                      className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 h-2 transition-all duration-500 rounded-full"
                      style={{ width: `${Math.min(100, Math.max(8, (simState.current_round / 12) * 100))}%` }}
                    />
                  </div>
                </div>

                {/* 12-Month Interactive Grid (3 Discipline Blocks) */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
                  {[
                    { blockIdx: 1, range: [1, 2, 3, 4], defaultLabel: "Blok 1: Fase Awal Disiplin", color: "indigo" },
                    { blockIdx: 2, range: [5, 6, 7, 8], defaultLabel: "Blok 2: Fase Konsolidasi", color: "purple" },
                    { blockIdx: 3, range: [9, 10, 11, 12], defaultLabel: "Blok 3: Fase Ekspansi & Finale", color: "emerald" },
                  ].map((block) => {
                    const blockCases = cases.filter(c => block.range.includes(c.stage_order));
                    // Determine dominant category in this block for dynamic header label
                    let blockLabel = block.defaultLabel;
                    if (blockCases.length > 0) {
                      const cats = blockCases.map(c => c.category);
                      if (cats.includes("mrp") || cats.includes("hr")) blockLabel = `Blok ${block.blockIdx}: SDM & Manufaktur MRP (Bulan ${block.range[0]}-${block.range[3]})`;
                      else if (cats.includes("accounting") || cats.includes("purchasing")) blockLabel = `Blok ${block.blockIdx}: Keuangan & Pengadaan SCM (Bulan ${block.range[0]}-${block.range[3]})`;
                      else if (cats.includes("crm")) blockLabel = `Blok ${block.blockIdx}: Pemasaran & Pelanggan CRM (Bulan ${block.range[0]}-${block.range[3]})`;
                    }

                    return (
                      <div key={block.blockIdx} className="bg-slate-950/60 border border-slate-800 rounded-lg p-3 space-y-2.5">
                        <div className="flex items-center justify-between border-b border-slate-800/80 pb-1.5">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 font-mono">
                            {blockLabel}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {blockCases.filter(c => c.status === "resolved").length}/4 Selesai
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          {block.range.map((monthNum) => {
                            const c = cases.find(item => item.stage_order === monthNum);
                            const isCurrent = simState.current_round === monthNum;
                            const isPast = simState.current_round > monthNum;
                            const isResolved = c?.status === "resolved";
                            const isActive = c?.status === "active" || isCurrent;

                            return (
                              <div
                                key={monthNum}
                                onClick={() => c && setPreviewMonthCase(c)}
                                className={`p-2 rounded-lg border text-left cursor-pointer transition-all flex flex-col justify-between min-h-[72px] ${
                                  isResolved
                                    ? "bg-emerald-950/40 border-emerald-600/50 hover:bg-emerald-950/60 text-emerald-200"
                                    : isActive
                                    ? "bg-indigo-900/60 border-indigo-400 shadow-md shadow-indigo-950/50 ring-2 ring-indigo-500/40 text-white animate-pulse"
                                    : "bg-slate-900/50 border-slate-800/80 hover:border-slate-700 text-slate-400 hover:text-slate-300"
                                }`}
                              >
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-mono font-bold">
                                    Bln {monthNum}
                                  </span>
                                  <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded font-mono ${
                                    isResolved
                                      ? "bg-emerald-800/80 text-emerald-200"
                                      : isActive
                                      ? "bg-indigo-600 text-white"
                                      : "bg-slate-800 text-slate-500"
                                  }`}>
                                    {c?.code || `M-${monthNum}`}
                                  </span>
                                </div>

                                <div className="text-[11px] font-bold line-clamp-1 mt-1">
                                  {c ? c.title.replace(/^Bulan \d+:\s*/, "") : `Misi Bulan ${monthNum}`}
                                </div>

                                <div className="flex items-center justify-between mt-1 text-[9px]">
                                  <span className="text-slate-400 capitalize">
                                    {c?.category === "mrp" ? "🏭 MRP" : c?.category === "hr" ? "👥 HR" : c?.category === "accounting" ? "💰 Akuntansi" : c?.category === "crm" ? "👥 CRM" : c?.category === "purchasing" ? "🛒 SCM" : "Umum"}
                                  </span>
                                  <span className="font-bold">
                                    {isResolved ? "✓ Selesai" : isActive ? "⚡ Aktif" : "🔒 Pending"}
                                  </span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Active Month Quick-Action Banner */}
                {(() => {
                  const activeCase = cases.find(c => c.status === "active") || cases.find(c => c.stage_order === simState.current_round);
                  if (!activeCase) return null;

                  const moduleTabMap: Record<string, string> = {
                    mrp: "mrp", manufacturing: "mrp",
                    accounting: "accounting", finance: "accounting",
                    crm: "crm", marketing: "crm", sales: "crm",
                    hr: "hcm", sdm: "hcm",
                    purchasing: "purchasing", procurement: "purchasing", scm: "purchasing"
                  };
                  const targetModule = moduleTabMap[activeCase.category || ""] || "missions";

                  return (
                    <div className="bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-950 p-3.5 rounded-lg border border-indigo-800/60 flex flex-col md:flex-row md:items-center justify-between gap-3">
                      <div className="flex items-start space-x-2.5">
                        <div className="p-1.5 rounded bg-indigo-600 text-white shrink-0 mt-0.5">
                          <Zap className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-600/60 text-indigo-200 px-2 py-0.5 rounded">
                              Fokus Bulan {activeCase.stage_order} [{activeCase.code}]
                            </span>
                            <span className="text-xs font-bold text-white">{activeCase.title}</span>
                          </div>
                          <p className="text-[11px] text-slate-300 mt-1 line-clamp-2 leading-relaxed">
                            {activeCase.description}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 shrink-0 self-end md:self-center">
                        <button
                          onClick={() => setActiveModule(targetModule as any)}
                          className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition flex items-center space-x-1 shadow-sm"
                        >
                          <span>🛠️ Buka Modul {targetModule.toUpperCase()}</span>
                        </button>
                        <button
                          onClick={handleAdvanceRound}
                          className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition flex items-center space-x-1 shadow-sm"
                          title="Tutup buku bulan ini dan lanjut ke bulan berikutnya"
                        >
                          <RotateCcw className="w-3.5 h-3.5 mr-1" />
                          <span>Tutup Buku Bln {simState.current_round}</span>
                        </button>
                      </div>
                    </div>
                  );
                })()}
              </div>
            )}
          </div>
        )}

        {/* Modal: Month Scenario Detail & Preview */}
        {previewMonthCase && (
          <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-xs flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-700 text-white rounded-xl max-w-2xl w-full p-6 space-y-4 shadow-2xl animate-in zoom-in-95">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-600 text-white px-2.5 py-0.5 rounded-full font-mono">
                    Bulan {previewMonthCase.stage_order} • [{previewMonthCase.code}]
                  </span>
                  <span className="text-xs text-slate-400 capitalize">
                    Modul: {previewMonthCase.category?.toUpperCase()}
                  </span>
                </div>
                <button
                  onClick={() => setPreviewMonthCase(null)}
                  className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div>
                <h3 className="text-base font-extrabold text-white">{previewMonthCase.title}</h3>
                <p className="text-xs text-slate-300 mt-2 leading-relaxed bg-slate-950/80 p-3.5 rounded-lg border border-slate-800">
                  {previewMonthCase.description}
                </p>
              </div>

              {previewMonthCase.trigger_hint && (
                <div className="text-xs bg-amber-950/40 border border-amber-600/40 p-3 rounded-lg text-amber-200">
                  <div className="font-bold flex items-center mb-1 text-[11px] text-amber-300">
                    <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-400 shrink-0" />
                    Indikator Krisis & Panduan Mitigasi:
                  </div>
                  <p className="text-[11px] leading-relaxed text-amber-200/90">{previewMonthCase.trigger_hint}</p>
                </div>
              )}

              {previewMonthCase.solvable_workflow && (
                <div className="text-xs bg-slate-950/60 border border-slate-800 p-3 rounded-lg text-slate-300 space-y-1">
                  <span className="font-bold text-indigo-300 block text-[11px]">SOP Penanganan Kasus:</span>
                  <p className="text-[11px] whitespace-pre-line leading-relaxed text-slate-400">{previewMonthCase.solvable_workflow}</p>
                </div>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                <span className={`text-xs font-bold px-2.5 py-1 rounded font-mono ${
                  previewMonthCase.status === "resolved"
                    ? "bg-emerald-900/80 text-emerald-300 border border-emerald-700"
                    : previewMonthCase.status === "active"
                    ? "bg-indigo-900/80 text-indigo-300 border border-indigo-700 animate-pulse"
                    : "bg-slate-800 text-slate-400 border border-slate-700"
                }`}>
                  Status: {previewMonthCase.status === "resolved" ? `✓ Terselesaikan (${previewMonthCase.resolution_score} pts)` : previewMonthCase.status === "active" ? "⚡ Aktif Sekarang" : "🔒 Menunggu Tahap Sebelumnya"}
                </span>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      const modMap: Record<string, string> = {
                        mrp: "mrp", hr: "hcm", accounting: "accounting", crm: "crm", purchasing: "purchasing"
                      };
                      const target = modMap[previewMonthCase.category || ""] || "missions";
                      setActiveModule(target as any);
                      setPreviewMonthCase(null);
                    }}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs px-4 py-2 rounded-lg transition"
                  >
                    Buka Modul {previewMonthCase.category?.toUpperCase()}
                  </button>
                  <button
                    onClick={() => setPreviewMonthCase(null)}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs px-3 py-2 rounded-lg transition"
                  >
                    Tutup
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* ========================================================= */}
        {/* VIEW: EXECUTIVE OVERVIEW & ENTERPRISE KPI DASHBOARD */}
        {/* ========================================================= */}

        {activePortal === "erp" && activeModule === "overview" && (
          <div className="space-y-6">
            {/* Top Corporate Summary Ribbon */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-sm">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">Saldo Kas & Bank</span>
                <p className="text-base font-bold font-mono text-slate-900 mt-1">
                  Rp {(simState.cash || 500000000).toLocaleString("id-ID")}
                </p>
                <div className="flex items-center text-[10px] text-emerald-600 font-semibold mt-1">
                  <ArrowUpRight className="w-3 h-3 mr-0.5" /> Likuiditas Aman
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-sm">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">Pendapatan Fiskal</span>
                <p className="text-base font-bold font-mono text-slate-900 mt-1">
                  Rp {(simState.revenue || 45000000).toLocaleString("id-ID")}
                </p>
                <div className="flex items-center text-[10px] text-slate-500 mt-1">
                  <span>Realisasi Penjualan Q1</span>
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-sm">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">Beban Operasional</span>
                <p className="text-base font-bold font-mono text-red-600 mt-1">
                  -Rp {(simState.expenses || 25000000).toLocaleString("id-ID")}
                </p>
                <div className="flex items-center text-[10px] text-slate-500 mt-1">
                  <span>Beban Gaji, Listrik, Sewa</span>
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-sm">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">Laba Bersih Berjalan</span>
                <p className="text-base font-bold font-mono text-emerald-700 mt-1">
                  +Rp {(simState.net_profit || 20000000).toLocaleString("id-ID")}
                </p>
                <div className="flex items-center text-[10px] text-emerald-600 font-semibold mt-1">
                  Margin: {Math.round(((simState.net_profit || 20000000) / (simState.revenue || 45000000)) * 100)}%
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-sm">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">CSAT Indeks Pelanggan</span>
                <p className="text-base font-bold font-mono text-slate-900 mt-1">
                  {simState.csat_score}%
                </p>
                <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2">
                  <div className="bg-indigo-600 h-1.5 rounded-full" style={{ width: `${simState.csat_score}%` }}></div>
                </div>
              </div>

              <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-sm">
                <span className="text-[11px] font-medium text-slate-500 uppercase tracking-wide">Efisiensi Manufaktur (OEE)</span>
                <p className="text-base font-bold font-mono text-slate-900 mt-1">
                  {simState.machine_health}%
                </p>
                <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2">
                  <div className={`h-1.5 rounded-full ${simState.machine_health < 70 ? "bg-red-500" : "bg-emerald-500"}`} style={{ width: `${simState.machine_health}%` }}></div>
                </div>
              </div>
            </div>

            {/* Odoo-style ERP Quick-Launch App Tiles (Direct Access to Operational Modules) */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
              <button
                onClick={() => setActiveModule("purchasing")}
                className="bg-white hover:bg-indigo-50/60 p-4 rounded-xl border border-slate-200 shadow-sm hover:border-indigo-300 transition text-left flex flex-col justify-between group"
              >
                <div>
                  <div className="w-10 h-10 rounded-lg bg-indigo-50 group-hover:bg-indigo-600 text-indigo-600 group-hover:text-white flex items-center justify-center transition mb-3">
                    <ShoppingBag className="w-5 h-5" />
                  </div>
                  <h4 className="font-bold text-slate-900 text-xs group-hover:text-indigo-600 transition">Pemasok & Vendor</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">{vendors.length} Vendor Aktif</p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-100 flex justify-between items-center text-[10px] font-semibold text-indigo-600">
                  <span>Buka Modul</span>
                  <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition" />
                </div>
              </button>

              <button
                onClick={() => setActiveModule("crm")}
                className="bg-white hover:bg-blue-50/60 p-4 rounded-xl border border-slate-200 shadow-sm hover:border-blue-300 transition text-left flex flex-col justify-between group"
              >
                <div>
                  <div className="w-10 h-10 rounded-lg bg-blue-50 group-hover:bg-blue-600 text-blue-600 group-hover:text-white flex items-center justify-center transition mb-3">
                    <Briefcase className="w-5 h-5" />
                  </div>
                  <h4 className="font-bold text-slate-900 text-xs group-hover:text-blue-600 transition">Pelanggan & CRM</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">{leads.length} Prospek & Keluhan VIP</p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-100 flex justify-between items-center text-[10px] font-semibold text-blue-600">
                  <span>Buka Modul</span>
                  <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition" />
                </div>
              </button>

              <button
                onClick={() => setActiveModule("mrp")}
                className="bg-white hover:bg-purple-50/60 p-4 rounded-xl border border-slate-200 shadow-sm hover:border-purple-300 transition text-left flex flex-col justify-between group"
              >
                <div>
                  <div className="w-10 h-10 rounded-lg bg-purple-50 group-hover:bg-purple-600 text-purple-600 group-hover:text-white flex items-center justify-center transition mb-3">
                    <Factory className="w-5 h-5" />
                  </div>
                  <h4 className="font-bold text-slate-900 text-xs group-hover:text-purple-600 transition">Mesin SMT & Pabrik</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">{workCenters.length} Stasiun Mesin</p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-100 flex justify-between items-center text-[10px] font-semibold text-purple-600">
                  <span>Buka Modul</span>
                  <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition" />
                </div>
              </button>

              <button
                onClick={() => setActiveModule("hcm")}
                className="bg-white hover:bg-teal-50/60 p-4 rounded-xl border border-slate-200 shadow-sm hover:border-teal-300 transition text-left flex flex-col justify-between group"
              >
                <div>
                  <div className="w-10 h-10 rounded-lg bg-teal-50 group-hover:bg-teal-600 text-teal-600 group-hover:text-white flex items-center justify-center transition mb-3">
                    <Users className="w-5 h-5" />
                  </div>
                  <h4 className="font-bold text-slate-900 text-xs group-hover:text-teal-600 transition">Pegawai & Payroll</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">{employees.length} Pegawai Tetap</p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-100 flex justify-between items-center text-[10px] font-semibold text-teal-600">
                  <span>Buka Modul</span>
                  <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition" />
                </div>
              </button>

              <button
                onClick={() => setActiveModule("accounting")}
                className="bg-white hover:bg-emerald-50/60 p-4 rounded-xl border border-slate-200 shadow-sm hover:border-emerald-300 transition text-left flex flex-col justify-between group"
              >
                <div>
                  <div className="w-10 h-10 rounded-lg bg-emerald-50 group-hover:bg-emerald-600 text-emerald-600 group-hover:text-white flex items-center justify-center transition mb-3">
                    <DollarSign className="w-5 h-5" />
                  </div>
                  <h4 className="font-bold text-slate-900 text-xs group-hover:text-emerald-600 transition">Keuangan & Kas</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">{accounts.length} Akun Buku Besar</p>
                </div>
                <div className="mt-3 pt-2 border-t border-slate-100 flex justify-between items-center text-[10px] font-semibold text-emerald-600">
                  <span>Buka Modul</span>
                  <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition" />
                </div>
              </button>
            </div>

            {/* Middle Section: Financial Chart & Operational Alerts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Financial Trend Visualizer */}
              <div className="lg:col-span-2 bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">Kinerja Arus Kas & Laba Operasional Bulanan</h3>
                    <p className="text-xs text-slate-500">Perbandingan riil pendapatan kotor dan pengeluaran beban usaha</p>
                  </div>
                  <span className="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded font-mono font-bold">
                    FY2026 Run-rate
                  </span>
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={[
                        { period: "Bulan -2", Revenue: 40000000, Expenses: 22000000, Profit: 18000000 },
                        { period: "Bulan -1", Revenue: 42000000, Expenses: 24000000, Profit: 18000000 },
                        { period: "Bulan Berjalan", Revenue: simState.revenue || 45000000, Expenses: simState.expenses || 25000000, Profit: simState.net_profit || 20000000 }
                      ]}
                      margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="period" stroke="#64748b" fontSize={11} />
                      <YAxis stroke="#64748b" fontSize={11} tickFormatter={(v) => `Rp${v/1000000}M`} />
                      <Tooltip formatter={(val: any) => [`Rp ${Number(val).toLocaleString("id-ID")}`, ""]} />
                      <Legend />
                      <Bar dataKey="Revenue" name="Pendapatan (Revenue)" fill="#4f46e5" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Expenses" name="Beban Usaha (Expenses)" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Profit" name="Laba Bersih (Net Profit)" fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Operational System Alerts & Enterprise Audit */}
              <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
                    <h3 className="text-sm font-bold text-slate-900 flex items-center">
                      <Bell className="w-4 h-4 mr-1.5 text-indigo-600" /> Audit Log & Status Divisi
                    </h3>
                    <span className="text-[10px] bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-bold">
                      Real-time
                    </span>
                  </div>

                  <div className="space-y-3 text-xs">
                    <div className="flex items-start space-x-2.5 p-2 rounded bg-slate-50 border border-slate-100">
                      <div className="w-2 h-2 rounded-full bg-emerald-500 mt-1"></div>
                      <div>
                        <span className="font-bold text-slate-800">Lini SMT Perakitan:</span>
                        <p className="text-slate-600 mt-0.5">Operasional normal. Tingkat kesiapan komponen 95%.</p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-2.5 p-2 rounded bg-slate-50 border border-slate-100">
                      <div className={`w-2 h-2 rounded-full mt-1 ${simState.is_strike_active ? "bg-red-500 animate-ping" : "bg-emerald-500"}`}></div>
                      <div>
                        <span className="font-bold text-slate-800">Ketenagakerjaan & Serikat:</span>
                        <p className="text-slate-600 mt-0.5">
                          {simState.is_strike_active ? "Mogok kerja sedang aktif! Negosiasi bipartit diperlukan." : "Suasana kerja kondusif. Moral kerja berada di level prima."}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-2.5 p-2 rounded bg-slate-50 border border-slate-100">
                      <div className="w-2 h-2 rounded-full bg-indigo-500 mt-1"></div>
                      <div>
                        <span className="font-bold text-slate-800">Pengadaan & Pembelian:</span>
                        <p className="text-slate-600 mt-0.5">{vendors.length} vendor terdaftar aktif dalam katalog direktori ERP.</p>
                      </div>
                    </div>

                    <div className="flex items-start space-x-2.5 p-2 rounded bg-slate-50 border border-slate-100">
                      <div className="w-2 h-2 rounded-full bg-amber-500 mt-1"></div>
                      <div>
                        <span className="font-bold text-slate-800">Pipeline Penjualan & CRM:</span>
                        <p className="text-slate-600 mt-0.5">{leads.length} dokumen prospek aktif dalam database.</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
                  <span>Database: SQLite 3 (ACID)</span>
                  <span className="font-mono text-emerald-600 font-bold">Latency: &lt;5ms</span>
                </div>
              </div>
            </div>

            {/* 4-PILLAR OPERATIONAL DOMAINS PREVIEW GRID (VENDORS, CUSTOMERS, MACHINES, EMPLOYEES) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Pillar 1: Rekanan Pemasok Utama */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center pb-2.5 mb-2.5 border-b border-slate-100">
                    <h4 className="text-xs font-bold text-slate-900 flex items-center">
                      <ShoppingBag className="w-4 h-4 mr-1.5 text-indigo-600" /> Rekanan Vendor ({vendors.length})
                    </h4>
                    <button
                      onClick={() => setActiveModule("purchasing")}
                      className="text-[11px] text-indigo-600 font-bold hover:underline"
                    >
                      Buka ➔
                    </button>
                  </div>
                  <div className="space-y-2 text-xs">
                    {vendors.slice(0, 4).map((v) => (
                      <div key={v.id} className="p-2 rounded bg-slate-50 border border-slate-100 flex justify-between items-center">
                        <div className="truncate pr-2">
                          <span className="font-semibold text-slate-900 block truncate">{v.name}</span>
                          <span className="text-[10px] text-slate-500">Lead time: {v.lead_time_days} hr • Defect: {v.defect_rate}%</span>
                        </div>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded font-mono ${v.defect_rate > 5.0 ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"}`}>
                          {v.fulfillment_rate}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => setActiveModule("purchasing")}
                  className="mt-3 w-full py-1.5 bg-slate-100 hover:bg-indigo-50 text-indigo-700 rounded font-semibold text-[11px] transition text-center"
                >
                  Kelola Pengadaan & Terbitkan PO
                </button>
              </div>

              {/* Pillar 2: Pelanggan & Tiket CRM Kritis */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center pb-2.5 mb-2.5 border-b border-slate-100">
                    <h4 className="text-xs font-bold text-slate-900 flex items-center">
                      <Briefcase className="w-4 h-4 mr-1.5 text-blue-600" /> Pelanggan & CRM ({leads.length})
                    </h4>
                    <button
                      onClick={() => setActiveModule("crm")}
                      className="text-[11px] text-blue-600 font-bold hover:underline"
                    >
                      Buka ➔
                    </button>
                  </div>
                  <div className="space-y-2 text-xs">
                    {leads.slice(0, 3).map((l) => (
                      <div key={l.id} className={`p-2 rounded border flex justify-between items-center ${l.is_complaint ? "bg-red-50/70 border-red-200" : "bg-slate-50 border-slate-100"}`}>
                        <div className="truncate pr-2">
                          <span className="font-semibold text-slate-900 block truncate flex items-center">
                            {l.is_complaint && <AlertTriangle className="w-3 h-3 text-red-600 mr-1 shrink-0" />}
                            {l.customer_name}
                          </span>
                          <span className="text-[10px] text-slate-500">{l.title}</span>
                        </div>
                        <span className="text-[10px] font-mono font-bold text-slate-700 shrink-0">
                          Rp {(l.expected_revenue / 1000000).toFixed(0)}M
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => setActiveModule("crm")}
                  className="mt-3 w-full py-1.5 bg-slate-100 hover:bg-blue-50 text-blue-700 rounded font-semibold text-[11px] transition text-center"
                >
                  Buka Pipeline CRM & Tiket Keluhan
                </button>
              </div>

              {/* Pillar 3: Status Mesin Pabrik & Risiko Breakdown */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center pb-2.5 mb-2.5 border-b border-slate-100">
                    <h4 className="text-xs font-bold text-slate-900 flex items-center">
                      <Factory className="w-4 h-4 mr-1.5 text-purple-600" /> Mesin Pabrik & MRP ({workCenters.length})
                    </h4>
                    <button
                      onClick={() => setActiveModule("mrp")}
                      className="text-[11px] text-purple-600 font-bold hover:underline"
                    >
                      Buka ➔
                    </button>
                  </div>
                  <div className="space-y-2 text-xs">
                    {workCenters.map((wc) => {
                      const isBreakdown = wc.status === "breakdown";
                      return (
                        <div key={wc.id} className={`p-2 rounded border flex justify-between items-center ${isBreakdown ? "bg-red-50 border-red-200" : "bg-slate-50 border-slate-100"}`}>
                          <div>
                            <span className="font-semibold text-slate-900 block">{wc.name}</span>
                            <span className="text-[10px] text-slate-500">Kapasitas: {wc.capacity_units_per_hour} unit/jam • {wc.code}</span>
                          </div>
                          <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase ${isBreakdown ? "bg-red-600 text-white animate-pulse" : "bg-emerald-100 text-emerald-800"}`}>
                            {wc.status}
                          </span>
                        </div>
                      );
                    })}
                    <div className="p-2 bg-slate-50 rounded border border-slate-100 text-[11px] flex justify-between items-center">
                      <span className="text-slate-600 font-medium">Kesehatan Mesin SMT:</span>
                      <span className={`font-mono font-bold ${simState.machine_health < 70 ? "text-red-600" : "text-emerald-600"}`}>
                        {simState.machine_health}%
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setActiveModule("mrp")}
                  className="mt-3 w-full py-1.5 bg-slate-100 hover:bg-purple-50 text-purple-700 rounded font-semibold text-[11px] transition text-center"
                >
                  Eksekusi Work Order & Maintenance
                </button>
              </div>

              {/* Pillar 4: Direktori Pegawai & Serikat Buruh */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center pb-2.5 mb-2.5 border-b border-slate-100">
                    <h4 className="text-xs font-bold text-slate-900 flex items-center">
                      <Users className="w-4 h-4 mr-1.5 text-teal-600" /> Pegawai & HR ({employees.length})
                    </h4>
                    <button
                      onClick={() => setActiveModule("hcm")}
                      className="text-[11px] text-teal-600 font-bold hover:underline"
                    >
                      Buka ➔
                    </button>
                  </div>
                  <div className="space-y-1.5 text-xs">
                    {employees.slice(0, 3).map((e) => (
                      <div key={e.id} className="p-1.5 rounded bg-slate-50 border border-slate-100 flex justify-between items-center">
                        <div className="truncate pr-2">
                          <span className="font-semibold text-slate-900 block truncate">{e.name}</span>
                          <span className="text-[10px] text-slate-500">{e.department} • {e.role}</span>
                        </div>
                        <span className="text-[10px] font-mono font-bold text-teal-700 shrink-0">
                          {e.morale_score}%
                        </span>
                      </div>
                    ))}
                    <div className="pt-1 flex justify-between text-[11px] text-slate-500">
                      <span>Beban Payroll Gaji:</span>
                      <span className="font-mono font-bold text-slate-800">Rp 30.400.000</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setActiveModule("hcm")}
                  className="mt-3 w-full py-1.5 bg-slate-100 hover:bg-teal-50 text-teal-700 rounded font-semibold text-[11px] transition text-center"
                >
                  Kelola Pegawai & Dialog Bipartit
                </button>
              </div>
            </div>

            {/* ========================================================= */}
            {/* EXECUTIVE SCENARIO & STRATEGIC DECISION RADAR */}
            {/* ========================================================= */}


            {/* ========================================================= */}
            {/* ENTERPRISE LIVE OPERATIONS AUDIT TRAIL & CROSS-MODULE FEED */}
            {/* ========================================================= */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-5 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-gradient-to-r from-slate-900 to-indigo-950 text-white">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="flex h-2.5 w-2.5 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                    </span>
                    <h3 className="font-bold text-sm text-white tracking-wide flex items-center">
                      <Activity className="w-4 h-4 mr-2 text-indigo-400" />
                      Enterprise Live Operations Audit Trail & Cross-Module Log Feed
                    </h3>
                  </div>
                  <p className="text-xs text-slate-300 mt-1">
                    Pencatatan real-time seluruh aktivitas operasional, jurnal akuntansi, rantai otomasi (CRM ➔ MRP ➔ Akuntansi ➔ HR), dan histori keputusan mengikat.
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-[11px] bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 px-3 py-1 rounded-full font-mono">
                    Total Aktivitas: {companyStoryline.length}
                  </span>
                  <button
                    onClick={() => fetchData()}
                    className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white rounded-lg text-xs font-semibold flex items-center space-x-1 transition"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    <span>Sinkronisasi</span>
                  </button>
                </div>
              </div>

              {/* Department Domain Filter Tabs */}
              <div className="bg-slate-50 border-b border-slate-200 px-5 py-2.5 flex flex-wrap items-center gap-2 text-xs">
                <span className="font-bold text-slate-500 text-[11px] uppercase mr-1">Filter Divisi:</span>
                {[
                  { id: "all", label: `Semua Divisi (${companyStoryline.length})` },
                  { id: "accounting", label: `💰 Akuntansi & Kas (${companyStoryline.filter(e => e.domain === 'accounting').length})` },
                  { id: "manufacturing", label: `🏭 Pabrik & MRP (${companyStoryline.filter(e => e.domain === 'manufacturing').length})` },
                  { id: "crm", label: `👥 CRM & Penjualan (${companyStoryline.filter(e => e.domain === 'crm' || e.domain === 'sales' || e.domain === 'marketing').length})` },
                  { id: "purchasing", label: `🛒 Pengadaan SCM (${companyStoryline.filter(e => e.domain === 'purchasing' || e.domain === 'scm').length})` },
                  { id: "hr", label: `👔 SDM & Payroll (${companyStoryline.filter(e => e.domain === 'hr' || e.domain === 'hcm').length})` }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setAuditDomainFilter(tab.id)}
                    className={`px-3 py-1 rounded-lg font-semibold transition ${
                      auditDomainFilter === tab.id
                        ? "bg-indigo-600 text-white shadow-sm"
                        : "bg-white text-slate-600 hover:bg-slate-200/70 border border-slate-200"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Events List Feed */}
              <div className="p-5">
                {(() => {
                  const filtered = (companyStoryline || []).filter((ev: any) => {
                    if (auditDomainFilter === "all") return true;
                    if (auditDomainFilter === "accounting") return ev.domain === "accounting";
                    if (auditDomainFilter === "manufacturing") return ev.domain === "manufacturing";
                    if (auditDomainFilter === "crm") return ev.domain === "crm" || ev.domain === "sales" || ev.domain === "marketing";
                    if (auditDomainFilter === "purchasing") return ev.domain === "purchasing" || ev.domain === "scm";
                    if (auditDomainFilter === "hr") return ev.domain === "hr" || ev.domain === "hcm";
                    return true;
                  });

                  if (filtered.length === 0) {
                    return (
                      <div className="py-10 text-center text-slate-400 text-xs">
                        <Activity className="w-8 h-8 mx-auto text-slate-300 mb-2" />
                        <p className="font-semibold text-slate-600">Belum ada aktivitas tercatat untuk kategori ini.</p>
                        <p className="text-slate-400 text-[11px] mt-0.5">Lakukan transaksi PO di modul Pengadaan, konversi Sales Order di CRM, atau ambil keputusan strategis di Pohon Keputusan.</p>
                      </div>
                    );
                  }

                  return (
                    <div className="space-y-3.5">
                      {filtered.map((ev: any) => {
                        const domainColors: Record<string, { bg: string; text: string; border: string; label: string }> = {
                          crm: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200", label: "👥 CRM & Penjualan" },
                          sales: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200", label: "👥 CRM & Penjualan" },
                          marketing: { bg: "bg-sky-50", text: "text-sky-700", border: "border-sky-200", label: "📢 Pemasaran" },
                          purchasing: { bg: "bg-indigo-50", text: "text-indigo-700", border: "border-indigo-200", label: "🛒 Pengadaan SCM" },
                          scm: { bg: "bg-indigo-50", text: "text-indigo-700", border: "border-indigo-200", label: "🛒 Pengadaan SCM" },
                          manufacturing: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200", label: "🏭 Pabrik & MRP" },
                          accounting: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", label: "💰 Akuntansi & Kas" },
                          hr: { bg: "bg-teal-50", text: "text-teal-700", border: "border-teal-200", label: "👔 SDM & HR" },
                          general: { bg: "bg-slate-50", text: "text-slate-700", border: "border-slate-200", label: "🌐 Korporat" }
                        };
                        const style = domainColors[ev.domain?.toLowerCase()] || domainColors.general;

                        return (
                          <div
                            key={ev.id}
                            className="bg-white rounded-xl border border-slate-200 p-4 hover:border-slate-300 hover:shadow-sm transition space-y-2.5"
                          >
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 border-b border-slate-100 pb-2.5">
                              <div className="flex items-center space-x-2">
                                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${style.bg} ${style.text} ${style.border}`}>
                                  {style.label}
                                </span>
                                <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                                  {ev.period_name || `Bulan ${ev.round_number || 1}`}
                                </span>
                                <h4 className="font-bold text-slate-900 text-xs">{ev.title}</h4>
                              </div>
                              <span className="text-[10px] text-slate-400 font-mono">
                                {new Date(ev.created_at).toLocaleString("id-ID")}
                              </span>
                            </div>

                            <p className="text-xs text-slate-600 leading-relaxed">
                              {ev.description}
                            </p>

                            {/* Cascading Ripples Tags */}
                            {ev.ripples && ev.ripples.length > 0 && (
                              <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-100 space-y-1.5">
                                <div className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                                  ⚡ Dampak Berantai Lintas Departemen (Cascading Ripples):
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-1.5">
                                  {ev.ripples.map((rip: any, rIdx: number) => {
                                    const ripText = rip.impact || rip.effect || `${rip.dept}: ${rip.effect || ''}`;
                                    return (
                                      <div key={rIdx} className="text-[11px] bg-white p-1.5 rounded border border-slate-200/80 flex items-start space-x-1.5 text-slate-700">
                                        <span className="text-xs shrink-0">{rip.icon || "📌"}</span>
                                        <span>
                                          <strong className="text-slate-900 font-semibold">{rip.dept}: </strong>
                                          {ripText}
                                        </span>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            )}

                            {/* Document View Button */}
                            {ev.document && (
                              <div className="pt-1 flex justify-end">
                                <button
                                  onClick={() => handleViewDocument(ev.document)}
                                  className="px-3 py-1 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 text-indigo-700 font-bold rounded-lg text-xs transition flex items-center space-x-1.5 shadow-sm"
                                >
                                  <FileText className="w-3.5 h-3.5 text-indigo-600" />
                                  <span>Buka Dokumen Resmi / Voucher Bukti</span>
                                </button>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  );
                })()}
              </div>
            </div>

            {/* Bottom Quick-Access ERP Ledger Summary */}
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center">
                  <FileText className="w-4 h-4 mr-1.5 text-indigo-600" /> Ringkasan Kode Akun Buku Besar (Chart of Accounts - COA)
                </h4>
                <button onClick={() => setActiveModule("accounting")} className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold">
                  Buka Modul Akuntansi Lengkap →
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                {accounts.slice(0, 4).map((acc) => (
                  <div key={acc.id} className="p-2.5 bg-slate-50 rounded border border-slate-100 flex justify-between items-center">
                    <div>
                      <span className="font-mono text-slate-500 block text-[10px]">{acc.code}</span>
                      <span className="font-bold text-slate-800">{acc.name}</span>
                    </div>
                    <span className="font-mono font-bold text-slate-900">
                      Rp {acc.balance.toLocaleString("id-ID")}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* ========================================================= */}
        {/* VIEW: ACADEMIC MISSIONS & SCENARIO PROBLEMS HUB */}
        {/* ========================================================= */}
        {activePortal === "erp" && activeModule === "missions" && (
          <div className="space-y-6">
            {/* Top Mission Progression Executive Banner */}
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-xl border border-indigo-900/60 shadow-lg">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider bg-indigo-600 text-white px-2.5 py-0.5 rounded-full">
                      Smart Python Brain Engine
                    </span>
                    <span className="text-xs text-indigo-300 font-mono">
                      {companies.find(c => c.id === companyId)?.name || "PT Inovasi Cipta Mandiri"} ({companies.find(c => c.id === companyId)?.group_label || "Kelompok 1"})
                    </span>
                  </div>
                  <h2 className="text-xl font-extrabold mt-2 text-white flex items-center">
                    <Award className="w-5 h-5 mr-2 text-amber-400" />
                    Pusat Simulasi Skenario, Misi & Diagnostik Strategis
                  </h2>
                  <p className="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                    Laboratorium simulasi keputusan manajerial FEB terintegrasi: Misi Kurikulum Bertahap, 20 Pohon Keputusan Multi-Skenario dengan Efek Domino Lintas Departemen, Analisis DuPont & Altman Z-Score oleh Smart CFO, serta Penerbitan Dokumen Resmi Bisnis.
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2.5 shrink-0 self-start md:self-center">
                  <div className="bg-slate-800/90 border border-slate-700 p-3 rounded-lg text-center">
                    <div className="text-[10px] uppercase text-slate-400 font-semibold">Skor Akumulasi</div>
                    <div className="text-xl font-black text-indigo-400 font-mono mt-0.5">
                      {(() => {
                        const resolvedList = cases.filter(c => c.status === "resolved");
                        if (resolvedList.length === 0) return 0;
                        const avg = Math.round(resolvedList.reduce((acc, c) => acc + (c.resolution_score || 0), 0) / resolvedList.length);
                        return (simState.overall_score && simState.overall_score > 0) ? simState.overall_score : avg;
                      })()} / 100
                    </div>
                  </div>
                  <div className="bg-slate-800/90 border border-slate-700 p-3 rounded-lg text-center">
                    <div className="text-[10px] uppercase text-slate-400 font-semibold">Status Tahap</div>
                    <div className="text-xs font-bold text-emerald-400 mt-1.5 flex items-center">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-400" />
                      {cases.filter(c => c.status === "resolved").length} dari {cases.length} Selesai
                    </div>
                  </div>
                  {currentUser?.role !== "MAHASISWA" && (
                    <button
                      onClick={() => handleResetCompanyMissions(companyId)}
                      className="bg-rose-900/60 hover:bg-rose-800 border border-rose-500/60 text-white text-xs font-bold px-3 py-3 rounded-lg transition flex items-center space-x-1.5 shadow"
                      title="Kosongkan seluruh jawaban & skor misi kelompok ini ke kondisi awal"
                    >
                      <RotateCcw className="w-4 h-4 text-rose-300" />
                      <span>Reset Jawaban Misi</span>
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Sub-Tabs Switcher */}
            <div className="flex items-center space-x-2 border-b border-slate-200 pb-2 overflow-x-auto">
              <button
                onClick={() => setMissionsSubTab("cases")}
                className={`px-4 py-2 rounded-lg font-bold text-xs transition flex items-center space-x-2 ${
                  missionsSubTab === "cases"
                    ? "bg-indigo-600 text-white shadow"
                    : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                <Award className="w-4 h-4" />
                <span>Misi Kurikulum Terarah ({cases.length})</span>
              </button>

              {currentUser?.role !== "MAHASISWA" && (
                <button
                  onClick={() => setMissionsSubTab("scenarios")}
                  className={`px-4 py-2 rounded-lg font-bold text-xs transition flex items-center space-x-2 ${
                    missionsSubTab === "scenarios"
                      ? "bg-indigo-600 text-white shadow"
                      : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
                  }`}
                >
                  <Layers className="w-4 h-4" />
                  <span>Pohon Keputusan Multi-Skenario ({scenarioMatrix.length || 20})</span>
                </button>
              )}

              <button
                onClick={() => setMissionsSubTab("cfo")}
                className={`px-4 py-2 rounded-lg font-bold text-xs transition flex items-center space-x-2 ${
                  missionsSubTab === "cfo"
                    ? "bg-indigo-600 text-white shadow"
                    : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                <TrendingUp className="w-4 h-4" />
                <span>Smart CFO: DuPont & Altman Z-Score</span>
              </button>

              <button
                onClick={() => setMissionsSubTab("storyline")}
                className={`px-4 py-2 rounded-lg font-bold text-xs transition flex items-center space-x-2 ${
                  missionsSubTab === "storyline"
                    ? "bg-indigo-600 text-white shadow"
                    : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span>Log Kronologi & Dokumen Resmi ({companyStoryline.length})</span>
              </button>
            </div>

            {/* TAB 1: CASES (STEP-BY-STEP PROBLEM SOLVING) */}
            {missionsSubTab === "cases" && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {cases.map((c) => {
                  const isResolved = c.status === "resolved";
                  const isActive = c.status === "active";
                  const isPending = c.status === "pending";
                  const parsedSteps = c.step_scores ? (typeof c.step_scores === "string" ? JSON.parse(c.step_scores) : c.step_scores) : null;
                  const parsedFactSheet = c.fact_sheet_data ? (typeof c.fact_sheet_data === "string" ? JSON.parse(c.fact_sheet_data) : c.fact_sheet_data) : null;

                  return (
                    <div
                      key={c.id}
                      className={`bg-white rounded-xl border shadow-sm p-5 flex flex-col justify-between transition-all ${
                        isActive
                          ? "border-indigo-500 ring-2 ring-indigo-500/20 shadow-md"
                          : isResolved
                          ? "border-emerald-300 bg-emerald-50/10"
                          : "border-slate-200 opacity-90"
                      }`}
                    >
                      <div>
                        {/* Top Header & Badges */}
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-1.5 flex-wrap gap-1">
                            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                              Tahap {c.stage_order} • {c.category === "procurement" || c.category === "purchasing" ? "Pengadaan & Gudang" : c.category === "crm" || c.category === "marketing" ? "CRM & Pelanggan" : c.category === "accounting" || c.category === "finance" ? "Akuntansi & Kas" : c.category === "hr" ? "SDM & Bipartit" : "Produksi & Pabrik"}
                            </span>
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 flex items-center">
                              🌐 Open Path
                            </span>
                          </div>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded flex items-center ${
                              isResolved
                                ? "bg-emerald-100 text-emerald-800 border border-emerald-300"
                                : isActive
                                ? "bg-indigo-100 text-indigo-800 border border-indigo-300 animate-pulse"
                                : "bg-slate-100 text-slate-500 border border-slate-200"
                            }`}
                          >
                            {isResolved ? `✓ Selesai (${c.resolution_score}/100 • ${c.grade || "A"})` : isActive ? "⚡ Misi Aktif" : "🔒 Belum Terbuka"}
                          </span>
                        </div>

                        {/* Title & Problem Description */}
                        <h3 className="font-bold text-slate-900 text-sm mb-2">{c.title}</h3>
                        <p className="text-xs text-slate-600 leading-relaxed mb-4 bg-slate-50 p-3 rounded-lg border border-slate-100">
                          {c.description}
                        </p>

                        {/* Problem Indicators & Trigger Hints */}
                        {c.trigger_hint && (
                          <div className="mb-3 text-xs bg-amber-50/80 border border-amber-200/80 p-2.5 rounded-lg text-amber-900">
                            <div className="font-bold flex items-center mb-1 text-[11px] text-amber-800">
                              <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600 shrink-0" />
                              Indikator / Petunjuk Masalah:
                            </div>
                            <p className="text-[11px] text-amber-800 leading-relaxed">{c.trigger_hint}</p>
                          </div>
                        )}

                        {/* Solvable Workflow Guide */}
                        <div className="mb-4 text-xs">
                          <div className="font-bold text-slate-800 mb-1 flex items-center text-[11px]">
                            <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-indigo-600 shrink-0" />
                            Langkah Penyelesaian Manajerial (SOP & Open Path):
                          </div>
                          <div className="text-[11px] text-slate-600 whitespace-pre-line leading-relaxed bg-slate-50 p-2.5 rounded border border-slate-200">
                            {c.solvable_workflow}
                          </div>
                        </div>

                        {/* Executed Action Display if Resolved */}
                        {isResolved && parsedFactSheet?.student_actions_taken && (
                          <div className="mb-3 text-[11px] bg-emerald-50 text-emerald-900 p-2.5 rounded-lg border border-emerald-200">
                            <span className="font-bold block text-emerald-800 mb-0.5">🎯 Keputusan Manajerial Terpilih:</span>
                            <span className="italic">{parsedFactSheet.student_actions_taken}</span>
                          </div>
                        )}

                        {/* Dynamic Step-by-Step Scoring Breakdown */}
                        {parsedSteps && (
                          <div className="mb-4 space-y-1.5 pt-3 border-t border-slate-200">
                            <div className="text-[11px] font-bold text-slate-700 mb-1">Matriks Penilaian Langkah:</div>
                            {parsedSteps.map((s: any, idx: number) => (
                              <div key={idx} className="flex justify-between items-center text-[11px] bg-slate-100 px-2.5 py-1 rounded">
                                <span className="text-slate-700 truncate pr-2">{s.step}</span>
                                <span className={`font-mono font-bold shrink-0 ${s.status === "passed" ? "text-emerald-700" : "text-red-700"}`}>
                                  {s.earned_score}/{s.max_score} pts
                                </span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Action Buttons */}
                      <div className="pt-3 border-t border-slate-200 flex flex-col space-y-2">
                        {isActive && (
                          <>
                            <button
                              onClick={() => {
                                setActivePortal("erp");
                                if (c.category === "procurement" || c.category === "purchasing") setActiveModule("purchasing");
                                else if (c.category === "crm" || c.category === "marketing") setActiveModule("crm");
                                else if (c.category === "accounting" || c.category === "finance") setActiveModule("accounting");
                                else if (c.category === "hr") setActiveModule("hcm");
                                else if (c.category === "mrp") setActiveModule("mrp");
                              }}
                              className="w-full bg-slate-50 hover:bg-indigo-50 text-indigo-700 border border-indigo-200 font-semibold py-1.5 px-3 rounded-lg text-xs transition flex items-center justify-center space-x-1"
                            >
                              <span>🛠️ Buka Modul Terkait Untuk Eksekusi</span>
                            </button>
                            <button
                              onClick={() => handleSolveCase(c.id, "Tindakan mitigasi manajerial dieksekusi lengkap")}
                              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-3 rounded-lg text-xs shadow-sm transition flex items-center justify-center space-x-1.5"
                            >
                              <CheckCircle2 className="w-4 h-4 text-white" />
                              <span>Validasi & Selesaikan Kasus</span>
                            </button>
                          </>
                        )}
                        {isResolved && (
                          <div className="space-y-1.5">
                            <div className="w-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold py-1.5 px-3 rounded-lg text-xs text-center">
                              Terselesaikan dengan Nilai {c.resolution_score}/100
                            </div>
                            {currentUser?.role !== "MAHASISWA" && (
                              <button
                                onClick={() => handleResetSingleCase(c.id)}
                                className="w-full bg-slate-50 hover:bg-rose-50 text-slate-600 hover:text-rose-700 border border-slate-200 hover:border-rose-300 font-medium py-1 px-2.5 rounded text-[11px] transition flex items-center justify-center space-x-1"
                              >
                                <RotateCcw className="w-3.5 h-3.5" />
                                <span>Reset Misi Ini Saja</span>
                              </button>
                            )}
                          </div>
                        )}
                        {isPending && (
                          <div>
                            <div className="w-full bg-slate-100 text-slate-400 font-medium py-2 px-3 rounded-lg text-xs text-center border border-slate-200 mb-1.5">
                              Selesaikan tahap sebelumnya untuk membuka misi ini
                            </div>
                            <button
                              onClick={() => {
                                setActivePortal("erp");
                                if (c.category === "procurement" || c.category === "purchasing") setActiveModule("purchasing");
                                else if (c.category === "crm" || c.category === "marketing") setActiveModule("crm");
                                else if (c.category === "accounting" || c.category === "finance") setActiveModule("accounting");
                                else if (c.category === "hr") setActiveModule("hcm");
                                else if (c.category === "mrp") setActiveModule("mrp");
                              }}
                              className="w-full bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 font-medium py-1 px-2.5 rounded text-[11px] transition flex items-center justify-center space-x-1"
                            >
                              <span>🚀 Pratinjau Modul ERP Terkait</span>
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* TAB 2: MULTI-SCENARIO BRANCHING DECISION TREE */}
            {missionsSubTab === "scenarios" && (
              <div className="space-y-6">
                {/* Domain Filter Pills */}
                <div className="flex flex-wrap items-center gap-2 bg-white p-3 rounded-xl border border-slate-200 shadow-sm">
                  <span className="text-xs font-bold text-slate-700 mr-2 flex items-center">
                    <Filter className="w-3.5 h-3.5 mr-1 text-indigo-600" /> Filter Domain:
                  </span>
                  {[
                    { key: "all", label: "Semua Domain (20)" },
                    { key: "purchasing", label: "Pengadaan & Rantai Pasok" },
                    { key: "manufacturing", label: "Produksi & Kualitas" },
                    { key: "crm", label: "CRM & Hubungan Pelanggan" },
                    { key: "hr", label: "SDM & Serikat Buruh" },
                    { key: "accounting", label: "Akuntansi & Keuangan" }
                  ].map((f) => (
                    <button
                      key={f.key}
                      onClick={() => setSelectedScenarioDomain(f.key)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                        selectedScenarioDomain === f.key
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>

                {/* Scenario Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {scenarioMatrix
                    .filter((sc) => selectedScenarioDomain === "all" || sc.domain === selectedScenarioDomain)
                    .map((sc) => {
                      const domainColors: { [key: string]: { bg: string; text: string; border: string } } = {
                        purchasing: { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200" },
                        manufacturing: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200" },
                        crm: { bg: "bg-purple-50", text: "text-purple-700", border: "border-purple-200" },
                        hr: { bg: "bg-teal-50", text: "text-teal-700", border: "border-teal-200" },
                        accounting: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200" }
                      };
                      const col = domainColors[sc.domain] || { bg: "bg-slate-50", text: "text-slate-700", border: "border-slate-200" };
                      const executed = executedDecisionsMap[sc.id];

                      return (
                        <div
                          key={sc.id}
                          className={`bg-white rounded-xl border shadow-sm hover:shadow-md transition p-5 flex flex-col justify-between ${
                            executed ? "border-emerald-300 ring-2 ring-emerald-500/15" : "border-slate-200"
                          }`}
                        >
                          <div>
                            {/* Card Header */}
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center space-x-2">
                                <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${col.bg} ${col.text} border ${col.border}`}>
                                  {sc.domain_label}
                                </span>
                                <span className="font-mono text-xs font-bold text-slate-500">[{sc.id}]</span>
                              </div>
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                                  sc.urgency === "CRITICAL"
                                    ? "bg-rose-100 text-rose-800 border border-rose-300 animate-pulse"
                                    : sc.urgency === "HIGH"
                                    ? "bg-amber-100 text-amber-800 border border-amber-300"
                                    : "bg-blue-100 text-blue-800 border border-blue-300"
                                }`}
                              >
                                {sc.urgency}
                              </span>
                            </div>

                            {/* Binding Decision Seal Badge if already executed */}
                            {executed && (
                              <div className="mb-3 p-2.5 bg-emerald-50 border border-emerald-300 rounded-lg flex items-center justify-between text-emerald-900 text-xs shadow-xs">
                                <div className="flex items-center space-x-1.5">
                                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                                  <div>
                                    <span className="font-bold block">Keputusan Resmi Dewan Direksi Disahkan:</span>
                                    <span className="text-[11px] text-emerald-800 font-medium">{executed.decision_taken || `Pilihan ${executed.choice_id}`}</span>
                                  </div>
                                </div>
                                <span className="text-[10px] font-mono font-bold bg-emerald-200 text-emerald-900 px-2 py-0.5 rounded shrink-0">
                                  TERKUNCI
                                </span>
                              </div>
                            )}

                            {/* Title & Context */}
                            <h3 className="font-bold text-slate-900 text-sm mb-2">{sc.title}</h3>
                            <p className="text-xs text-slate-600 leading-relaxed mb-4 bg-slate-50 p-3 rounded-lg border border-slate-100">
                              {sc.context}
                            </p>

                            {/* Branches */}
                            <div className="space-y-3 mb-4">
                              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-700 flex items-center">
                                <Sparkles className="w-3.5 h-3.5 mr-1 text-indigo-600" /> Pilihan Cabang Strategis & Efek Domino:
                              </div>
                              {sc.branches.map((b: any) => {
                                const isThisChosen = executed && executed.choice_id === b.choice_id;
                                const isOtherChosen = executed && executed.choice_id !== b.choice_id;

                                return (
                                  <div
                                    key={b.choice_id}
                                    className={`p-3 rounded-lg border transition space-y-2 ${
                                      isThisChosen
                                        ? "bg-emerald-50/80 border-emerald-400 ring-1 ring-emerald-400 shadow-xs"
                                        : isOtherChosen
                                        ? "bg-slate-100/60 border-slate-200 opacity-60"
                                        : "border-slate-200 bg-slate-50/50 hover:bg-slate-50"
                                    }`}
                                  >
                                    <div className="flex items-start justify-between gap-2">
                                      <div className="flex items-start space-x-2">
                                        <span className={`w-5 h-5 rounded font-bold font-mono text-xs flex items-center justify-center shrink-0 mt-0.5 ${
                                          isThisChosen
                                            ? "bg-emerald-600 text-white"
                                            : "bg-indigo-100 text-indigo-700"
                                        }`}>
                                          {b.choice_id}
                                        </span>
                                        <div>
                                          <div className={`text-xs font-bold ${isThisChosen ? "text-emerald-950" : "text-slate-900"}`}>
                                            {b.label}
                                          </div>
                                          <div className="text-[11px] text-slate-500 mt-0.5">{b.rationale}</div>
                                        </div>
                                      </div>
                                      <div className="text-right shrink-0">
                                        <span className="text-[10px] font-mono font-bold text-slate-700 block">
                                          {b.immediate_cost > 0 ? `Rp ${b.immediate_cost.toLocaleString("id-ID")}` : "Rp 0 (Kas Aman)"}
                                        </span>
                                      </div>
                                    </div>

                                    {/* Ripple Badges */}
                                    {b.ripples && (
                                      <div className="flex flex-wrap gap-1 pt-1.5 border-t border-slate-200/60">
                                        {b.ripples.map((rip: any, rIdx: number) => (
                                          <span
                                            key={rIdx}
                                            className={`text-[9px] font-semibold px-2 py-0.5 rounded-full ${
                                              rip.type === "positive"
                                                ? "bg-emerald-100 text-emerald-800"
                                                : rip.type === "negative"
                                                ? "bg-rose-100 text-rose-800"
                                                : "bg-slate-200 text-slate-700"
                                            }`}
                                          >
                                            {rip.dept}: {rip.effect}
                                          </span>
                                        ))}
                                      </div>
                                    )}

                                    {/* Execute Branch Button with Binding Lock Guard */}
                                    <div className="pt-1 flex justify-end">
                                      {isThisChosen ? (
                                        <div className="px-3 py-1.5 bg-emerald-700 text-white font-bold rounded-lg text-[11px] flex items-center space-x-1 shadow-xs">
                                          <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                                          <span>✓ Telah Ditetapkan & Mengikat</span>
                                        </div>
                                      ) : isOtherChosen ? (
                                        <div className="px-3 py-1.5 bg-slate-200 text-slate-500 font-medium rounded-lg text-[11px] flex items-center space-x-1">
                                          <span>🔒 Opsi Gugur (Pilihan {executed.choice_id} Telah Disahkan)</span>
                                        </div>
                                      ) : (
                                        <button
                                          disabled={executingBranchChoice || !!executed}
                                          onClick={() => handleExecuteBranchDecision(sc.id, b.choice_id)}
                                          className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg text-[11px] transition flex items-center space-x-1 shadow-sm"
                                        >
                                          <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                                          <span>Pilih Cabang {b.choice_id}</span>
                                        </button>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* TAB 3: SMART CFO DIAGNOSTICS & DUPONT/ALTMAN Z */}
            {missionsSubTab === "cfo" && cfoDiagnostics && (
              <div className="space-y-6">
                {/* Executive Balance Sheet & Working Capital Meter */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-100 pb-4">
                    <div>
                      <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full">
                        Smart CFO Engine
                      </span>
                      <h3 className="text-lg font-extrabold text-slate-900 mt-1 flex items-center">
                        <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" />
                        Diagnostik Kesehatan Keuangan & Modal Kerja
                      </h3>
                      <p className="text-xs text-slate-500">
                        Evaluasi otomatis posisi likuiditas, solvabilitas, dan efisiensi modal per tanggal {cfoDiagnostics.as_of_date}.
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="text-right">
                        <span className="text-[10px] text-slate-400 uppercase font-semibold">Net Working Capital</span>
                        <div className="text-lg font-black text-slate-900 font-mono">
                          Rp {cfoDiagnostics.balance_sheet_summary?.working_capital?.toLocaleString("id-ID")}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* 4 Working Capital KPIs */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">Current Ratio</span>
                      <div className="text-2xl font-black text-slate-900 font-mono mt-1">
                        {cfoDiagnostics.ratios?.current_ratio}x
                      </div>
                      <span className="text-[10px] text-slate-500 mt-1 block">Batas aman industri: &gt; 1.5x</span>
                    </div>

                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">Quick Ratio (Acid-Test)</span>
                      <div className="text-2xl font-black text-indigo-600 font-mono mt-1">
                        {cfoDiagnostics.ratios?.quick_ratio}x
                      </div>
                      <span className="text-[10px] text-slate-500 mt-1 block">Batas aman: &gt; 1.0x</span>
                    </div>

                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">Cash Ratio Likuid</span>
                      <div className="text-2xl font-black text-emerald-600 font-mono mt-1">
                        {cfoDiagnostics.ratios?.cash_ratio}x
                      </div>
                      <span className="text-[10px] text-slate-500 mt-1 block">Batas kas darurat: &gt; 0.5x</span>
                    </div>

                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">Return on Equity (ROE)</span>
                      <div className="text-2xl font-black text-purple-600 font-mono mt-1">
                        {cfoDiagnostics.ratios?.return_on_equity_pct}%
                      </div>
                      <span className="text-[10px] text-slate-500 mt-1 block">Imbal hasil atas modal disetor</span>
                    </div>
                  </div>
                </div>

                {/* DuPont Analysis Breakdown Grid */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div>
                      <h4 className="font-extrabold text-slate-900 text-sm flex items-center">
                        <BarChart3 className="w-4 h-4 mr-2 text-indigo-600" />
                        Model Analisis DuPont 3-Faktor (Decomposition of ROE)
                      </h4>
                      <p className="text-xs text-slate-500 mt-0.5">
                        ROE = Profit Margin (Efisiensi Operasi) × Asset Turnover (Efisiensi Aset) × Equity Multiplier (Leverage Keuangan)
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-200 space-y-2">
                      <div className="text-xs font-bold text-indigo-900 uppercase">1. Net Profit Margin</div>
                      <div className="text-2xl font-black text-indigo-700 font-mono">
                        {cfoDiagnostics.ratios?.net_profit_margin_pct}%
                      </div>
                      <p className="text-[11px] text-indigo-950 leading-relaxed">
                        Kemampuan perusahaan mengubah pendapatan kotor menjadi laba bersih setelah HPP dan beban operasional.
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-purple-50/60 border border-purple-200 space-y-2">
                      <div className="text-xs font-bold text-purple-900 uppercase">2. Total Asset Turnover</div>
                      <div className="text-2xl font-black text-purple-700 font-mono">
                        {cfoDiagnostics.ratios?.asset_turnover}x
                      </div>
                      <p className="text-[11px] text-purple-950 leading-relaxed">
                        Perputaran seluruh aset perusahaan dalam menghasilkan penjualan produk jadi di pasar.
                      </p>
                    </div>

                    <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-2">
                      <div className="text-xs font-bold text-emerald-900 uppercase">3. Equity Multiplier (Leverage)</div>
                      <div className="text-2xl font-black text-emerald-700 font-mono">
                        {cfoDiagnostics.ratios?.equity_multiplier}x
                      </div>
                      <p className="text-[11px] text-emerald-950 leading-relaxed">
                        Rasio total aset terhadap ekuitas pemegang saham yang menggambarkan tingkat ketergantungan utang.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Altman Z-Score Predictor Gauge */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                    <div>
                      <h4 className="font-extrabold text-slate-900 text-sm flex items-center">
                        <ShieldAlert className="w-4 h-4 mr-2 text-rose-600" />
                        Altman Z-Score Financial Distress Predictor (Model Manufaktur Swasta)
                      </h4>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {cfoDiagnostics.altman_z_score?.interpretation}
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-bold border ${
                      cfoDiagnostics.altman_z_score?.status.includes("SAFE")
                        ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                        : cfoDiagnostics.altman_z_score?.status.includes("GREY")
                        ? "bg-amber-100 text-amber-800 border-amber-300"
                        : "bg-rose-100 text-rose-800 border-rose-300"
                    }`}>
                      {cfoDiagnostics.altman_z_score?.status}
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-900 text-white flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase font-semibold">Skor Altman Z-Score Saat Ini</span>
                      <div className="text-3xl font-black font-mono text-emerald-400 mt-1">
                        Z = {cfoDiagnostics.altman_z_score?.score}
                      </div>
                      <div className="text-xs text-slate-300 mt-1">
                        Skor &gt; 2.90 = Zona Aman • 1.23 - 2.90 = Zona Abu-abu • &lt; 1.23 = Zona Bahaya Likuidasi
                      </div>
                    </div>
                  </div>
                </div>

                {/* Smart Strategic Recommendations & Risk Flags */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Risk Flags */}
                  <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                    <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-1.5 text-amber-500" /> Indikator Risiko Likuiditas & Operasi
                    </h4>
                    <div className="space-y-2">
                      {cfoDiagnostics.risk_flags?.map((rf: any, idx: number) => (
                        <div key={idx} className="p-3 bg-amber-50/80 rounded-lg border border-amber-200 text-xs">
                          <div className="font-bold text-amber-900">{rf.title}</div>
                          <div className="text-[11px] text-amber-800 mt-0.5">{rf.detail}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                    <h4 className="font-bold text-slate-900 text-xs uppercase tracking-wider flex items-center">
                      <Sparkles className="w-4 h-4 mr-1.5 text-indigo-600" /> Rekomendasi Tindakan Manajerial CFO
                    </h4>
                    <div className="space-y-2">
                      {cfoDiagnostics.cfo_recommendations?.map((rec: string, idx: number) => (
                        <div key={idx} className="p-3 bg-indigo-50/60 rounded-lg border border-indigo-200 text-xs flex items-start space-x-2">
                          <CheckCircle2 className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                          <span className="text-indigo-950 font-medium">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: STORYLINE & OFFICIAL LEGAL DOCUMENTS LOG */}
            {missionsSubTab === "storyline" && (
              <div className="space-y-4">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <h3 className="font-bold text-slate-900 text-sm flex items-center mb-1">
                    <BookOpen className="w-4 h-4 mr-2 text-indigo-600" />
                    Log Kronologis Keputusan & Penerbitan Dokumen Bisnis
                  </h3>
                  <p className="text-xs text-slate-500">
                    Histori lengkap seluruh keputusan cabang, biaya kas, konsekuensi antar departemen, dan dokumen hukum/komersial yang diterbitkan perusahaan.
                  </p>
                </div>

                {companyStoryline.length === 0 ? (
                  <div className="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-500 text-xs">
                    Belum ada riwayat keputusan cabang yang dieksekusi. Buka tab <strong className="text-indigo-600">Pohon Keputusan Multi-Skenario</strong> untuk mengambil keputusan strategis pertama!
                  </div>
                ) : (
                  <div className="space-y-3">
                    {companyStoryline.map((ev) => (
                      <div
                        key={ev.id}
                        className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition space-y-3"
                      >
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                          <div className="flex items-center space-x-2">
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 border border-indigo-200">
                              {ev.domain}
                            </span>
                            <span className="font-bold text-slate-900 text-sm">{ev.title}</span>
                          </div>
                          <span className="text-[11px] text-slate-400 font-mono">
                            {new Date(ev.created_at).toLocaleString("id-ID")}
                          </span>
                        </div>

                        <div className="text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-100">
                          {ev.description}
                        </div>

                        {/* Ripples display */}
                        {ev.ripples && ev.ripples.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {ev.ripples.map((rip: any, rIdx: number) => (
                              <span
                                key={rIdx}
                                className={`text-[10px] font-medium px-2.5 py-0.5 rounded-full ${
                                  rip.type === "positive"
                                    ? "bg-emerald-100 text-emerald-800"
                                    : rip.type === "negative"
                                    ? "bg-rose-100 text-rose-800"
                                    : "bg-slate-200 text-slate-700"
                                }`}
                              >
                                {rip.dept}: {rip.effect}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Document button if present */}
                        {ev.document && (
                          <div className="pt-2 flex justify-end">
                            <button
                              onClick={() => setActiveDocument(ev.document)}
                              className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 text-indigo-700 font-bold rounded-lg text-xs transition flex items-center space-x-1.5 shadow-sm"
                            >
                              <FileText className="w-3.5 h-3.5 text-indigo-600" />
                              <span>Lihat Dokumen: {ev.document.title}</span>
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW: PURCHASING & VENDOR PROCUREMENT MANAGEMENT */}
        {/* ========================================================= */}
        {activePortal === "erp" && activeModule === "purchasing" && (
          <div className="space-y-5">
            {/* Action & Filter Toolbar */}
            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex items-center space-x-3 flex-1">
                <div className="relative flex-1 max-w-md">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Cari pemasok berdasarkan nama perusahaan atau kategori..."
                    value={vendorSearch}
                    onChange={(e) => setVendorSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-md text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
                <span className="text-xs text-slate-500">Menampilkan {filteredVendors.length} dari {vendors.length} Rekanan</span>
              </div>
              <div className="flex items-center space-x-2">
                {currentUser.role !== "MAHASISWA" && (
                  <button
                    onClick={() => setShowAddVendorModal(true)}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition flex items-center"
                    title="Hanya Instruktur: Daftarkan Rekanan Pemasok Baru"
                  >
                    <Plus className="w-3.5 h-3.5 mr-1" /> Rekanan Pemasok Baru
                  </button>
                )}
              </div>
            </div>

            {/* Split View: Master Table & Inspection Detail Drawer */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Vendor Master Grid (Dense ERP Table) */}
              <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-3.5 border-b border-slate-200 bg-slate-50/70 flex justify-between items-center">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Katalog Rekanan Pemasok (Vendor Master)</h3>
                  <span className="text-[11px] text-slate-500">Klik baris untuk memuat audit scorecard</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200 text-xs">
                    <thead className="bg-slate-50 text-slate-500 font-semibold">
                      <tr>
                        <th className="px-3 py-2 text-left">Nama Pemasok</th>
                        <th className="px-3 py-2 text-left">Kategori Pasokan</th>
                        <th className="px-3 py-2 text-center">Fulfillment</th>
                        <th className="px-3 py-2 text-center">Ketaatan</th>
                        <th className="px-3 py-2 text-center">Defect Rate</th>
                        <th className="px-3 py-2 text-center">Indeks Harga</th>
                        <th className="px-3 py-2 text-center">Aksi PO</th>
                        {currentUser.role !== "MAHASISWA" && <th className="px-3 py-2 text-center">Hapus</th>}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredVendors.map((v) => {
                        const isSelected = selectedVendorForDetail?.id === v.id;
                        return (
                          <tr
                            key={v.id}
                            onClick={() => setSelectedVendorForDetail(v)}
                            className={`cursor-pointer hover:bg-indigo-50/50 transition ${
                              isSelected ? "bg-indigo-50/80 font-medium" : ""
                            }`}
                          >
                            <td className="px-3 py-2.5 font-bold text-slate-900">{v.name}</td>
                            <td className="px-3 py-2.5 text-slate-600">{v.category}</td>
                            <td className="px-3 py-2.5 text-center font-mono font-semibold">{v.fulfillment_rate}%</td>
                            <td className="px-3 py-2.5 text-center font-mono font-semibold">{v.on_time_rate}%</td>
                            <td className="px-3 py-2.5 text-center">
                              <span className={`px-2 py-0.5 rounded font-mono font-bold ${
                                v.defect_rate > 5.0 ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-800"
                              }`}>
                                {v.defect_rate}%
                              </span>
                            </td>
                            <td className="px-3 py-2.5 text-center font-mono font-bold text-slate-700">x{v.price_multiplier}</td>
                            <td className="px-3 py-2.5 text-center" onClick={(e) => e.stopPropagation()}>
                              <div className="flex items-center justify-center space-x-1">
                                <input
                                  type="number"
                                  min="10"
                                  step="10"
                                  value={poQty[v.id] || 50}
                                  onChange={(e) => setPoQty({ ...poQty, [v.id]: parseInt(e.target.value) || 10 })}
                                  className="w-12 border rounded px-1 py-0.5 text-center font-mono text-xs"
                                />
                                <button
                                  onClick={() => handleInitiatePO(v.id)}
                                  className="bg-indigo-600 hover:bg-indigo-500 text-white px-2 py-0.5 rounded text-[11px] font-semibold transition flex items-center space-x-1 shadow-xs"
                                >
                                  <span>Terbitkan PO</span>
                                </button>
                              </div>
                            </td>
                            {currentUser.role !== "MAHASISWA" && (
                              <td className="px-3 py-2.5 text-center" onClick={(e) => e.stopPropagation()}>
                                <button
                                  onClick={() => handleDeleteVendor(v.id)}
                                  title="Hapus Master Data Rekanan (Instruktur Only)"
                                  className="text-slate-400 hover:text-red-600 p-1 transition"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </td>
                            )}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Vendor Detail Inspection Drawer */}
              {selectedVendorForDetail ? (
                <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start pb-3 mb-3 border-b border-slate-100">
                      <div>
                        <h4 className="font-bold text-sm text-slate-900">{selectedVendorForDetail.name}</h4>
                        <p className="text-xs text-slate-500">{selectedVendorForDetail.category}</p>
                      </div>
                      <span className="text-[10px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono font-bold">
                        Tempo: {selectedVendorForDetail.credit_terms_days} hari
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                      <div className="p-2 bg-slate-50 rounded border border-slate-100">
                        <span className="text-slate-500 block text-[10px]">Waktu Kirim (Lead Time):</span>
                        <span className="font-bold text-slate-800">{selectedVendorForDetail.lead_time_days} Hari Kerja</span>
                      </div>
                      <div className="p-2 bg-slate-50 rounded border border-slate-100">
                        <span className="text-slate-500 block text-[10px]">Harga Patokan:</span>
                        <span className="font-bold text-slate-800">x{selectedVendorForDetail.price_multiplier} dari HPP Standar</span>
                      </div>
                    </div>

                    {/* Recharts Historical Trend */}
                    <div className="mb-3">
                      <span className="text-[11px] font-bold text-slate-700 block mb-1">Tren Scorecard Historis (Bulan -3 s/d Bulan -1):</span>
                      <div className="h-44 w-full bg-slate-50 rounded p-1 border border-slate-100">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={selectedVendorForDetail.metrics}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                            <XAxis dataKey="period_label" stroke="#94a3b8" fontSize={10} />
                            <YAxis stroke="#94a3b8" fontSize={10} domain={[0, 100]} />
                            <Tooltip formatter={(val: any) => [`${val}%`, ""]} />
                            <Line type="monotone" dataKey="fulfillment_rate" name="Fulfillment %" stroke="#4f46e5" strokeWidth={2} dot={{ r: 2 }} />
                            <Line type="monotone" dataKey="on_time_rate" name="Ketaatan %" stroke="#10b981" strokeWidth={2} dot={{ r: 2 }} />
                            <Line type="monotone" dataKey="defect_rate" name="Cacat %" stroke="#ef4444" strokeWidth={2} dot={{ r: 2 }} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    <div className="p-2.5 rounded bg-slate-50 border border-slate-100 text-xs">
                      <span className="font-bold text-slate-700 block mb-0.5">Catatan Audit Internal Vendor:</span>
                      <p className="text-slate-600 italic">"{selectedVendorForDetail.notes}"</p>
                    </div>
                  </div>

                  <div className="pt-3 mt-3 border-t border-slate-100 flex justify-between items-center text-[11px] text-slate-500">
                    <span>Terverifikasi Departemen QA</span>
                    <span className="text-indigo-600 font-semibold">ISO 9001:2015</span>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-lg border border-slate-200 p-8 text-center text-slate-400 text-xs flex flex-col items-center justify-center">
                  <ShoppingBag className="w-8 h-8 mb-2 text-slate-300" />
                  Pilih rekanan pemasok pada tabel di sebelah kiri untuk melihat rekam jejak audit historis.
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW: SALES & CRM PIPELINE (KANBAN & ESCALATIONS) */}
        {/* ========================================================= */}
        {activePortal === "erp" && activeModule === "crm" && (
          <div className="space-y-5">
            {/* Header Toolbar */}
            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex items-center space-x-3 flex-1">
                <div className="relative flex-1 max-w-md">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Cari prospek penjualan atau nama institusi klien..."
                    value={leadSearch}
                    onChange={(e) => setLeadSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-md text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
                <span className="text-xs text-slate-500">{filteredLeads.length} Prospek Aktif</span>
              </div>
              <div className="flex items-center space-x-2">
                {currentUser?.role !== "MAHASISWA" && (
                  <button
                    onClick={() => handleResetCompanyMissions(companyId)}
                    title="Reset Status Jawaban & Evaluasi Misi Kelompok Ini"
                    className="bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 text-xs font-semibold px-2.5 py-1.5 rounded-md shadow-sm transition flex items-center"
                  >
                    <RotateCcw className="w-3.5 h-3.5 mr-1 text-slate-500" />
                    <span className="hidden sm:inline">Reset Misi Kasus</span>
                    <span className="sm:hidden">Reset Misi</span>
                  </button>
                )}

                <button
                  onClick={() => setShowAddLeadModal(true)}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition flex items-center"
                >
                  <Plus className="w-3.5 h-3.5 mr-1" /> Buat Prospek Penjualan Baru
                </button>
              </div>
            </div>

            {/* Urgent Customer Incident Tickets (Customer Care Escalation) */}
            {filteredLeads.filter(l => l.is_complaint && l.stage !== "won").map(complaint => (
              <div key={complaint.id} className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
                    <div>
                      <h4 className="font-bold text-sm text-red-900">{complaint.title}</h4>
                      <p className="text-xs text-red-700">Akun: <strong className="text-red-900">{complaint.customer_name}</strong> • Nilai Kontrak Terancam: <strong>Rp {complaint.expected_revenue.toLocaleString("id-ID")}</strong></p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {currentUser.role !== "MAHASISWA" && (
                      <button
                        onClick={() => handleRandomizeCustomer(complaint.id)}
                        title="Simulasikan Respon Pelanggan Lain (Instruktur Only)"
                        className="bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 text-[11px] font-semibold px-2.5 py-1 rounded transition"
                      >
                        🎲 Respon Baru
                      </button>
                    )}
                    {currentUser.role !== "MAHASISWA" && (
                      <button
                        onClick={() => handleDeleteLead(complaint.id)}
                        title="Hapus Tiket (Instruktur Only)"
                        className="text-slate-400 hover:text-red-600 p-1"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>

                <div className="my-2.5 bg-white p-3 rounded border border-red-200 text-xs">
                  <span className="font-bold text-red-900 block mb-0.5">Kutipan Pernyataan Keluhan Resmi:</span>
                  <p className="text-red-800 italic">"{complaint.complaint_details || complaint.notes}"</p>
                </div>

                {complaint.stage === "proposition" ? (
                  <div className="bg-amber-50 border border-amber-300 p-3 rounded-lg mt-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
                    <div className="text-xs text-amber-900">
                      <span className="font-bold block text-sm mb-0.5">🤝 Mediasi Tingkat Direksi Sedang Berlangsung</span>
                      <span>Klien bersedia menunda pembatalan kontrak. Buka Notulensi Mediasi untuk memilih opsi kesepakatan akhir (open path):</span>
                    </div>
                    <button
                      onClick={() => {
                        setActiveMediationComplaint(complaint);
                        setShowMediationModal(true);
                      }}
                      className="bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold px-3.5 py-1.5 rounded-md shadow-sm transition whitespace-nowrap flex items-center space-x-1"
                    >
                      <span>📝</span>
                      <span>Buka Notulensi & Sepakati Solusi</span>
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <span className="text-xs font-semibold text-slate-700 mr-2">Mitigasi Layanan:</span>
                    <button
                      onClick={() => setConfirmingComplaintAction({
                        leadId: complaint.id,
                        actionType: "replace_with_discount",
                        title: "Penggantian 15 Unit Baru + Voucher Diskon 10% (SOP Standar)",
                        customerName: complaint.customer_name,
                        cost: "HPP Rp 3.150.000 + Potong 15 Unit Stok Barang Jadi",
                        impact: "Memulihkan CSAT ke 92% dan menyelamatkan kontrak Rp 150.000.000."
                      })}
                      className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-1 rounded transition shadow-xs flex items-center space-x-1"
                    >
                      <span>✅ Ganti Unit Baru + Diskon 10% (SOP Standar)</span>
                    </button>
                    <button
                      onClick={() => {
                        setActiveMediationComplaint(complaint);
                        setShowMediationModal(true);
                      }}
                      className="bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold px-3 py-1 rounded transition shadow-xs flex items-center space-x-1"
                    >
                      <span>🤝 Mediasi Tingkat Direksi</span>
                    </button>
                    <button
                      onClick={() => setConfirmingComplaintAction({
                        leadId: complaint.id,
                        actionType: "ignore",
                        title: "Abaikan & Tolak Klaim Kompensasi Klien VIP",
                        customerName: complaint.customer_name,
                        cost: "Biaya Kas Rp 0",
                        impact: "⚠️ Klien membatalkan kontrak Rp 150.000.000, CSAT jatuh drastis ke 20%, dan timbul risiko somasi hukum!",
                        isDangerous: true
                      })}
                      className="bg-slate-200 hover:bg-red-100 text-slate-700 hover:text-red-700 text-xs font-semibold px-3 py-1 rounded transition"
                    >
                      Abaikan Keluhan
                    </button>
                  </div>
                )}
              </div>
            ))}

            {/* Standard ERP Pipeline Kanban Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                { stage: "new", title: "1. Prospek Baru (New)" },
                { stage: "qualified", title: "2. Kualifikasi Kebutuhan" },
                { stage: "proposition", title: "3. Penawaran / Proposal" },
                { stage: "won", title: "4. Closing Berhasil (Won)" }
              ].map(column => {
                const stageLeads = filteredLeads.filter(l => l.stage === column.stage);
                const stageTotal = stageLeads.reduce((acc, curr) => acc + (curr.expected_revenue || 0), 0);
                return (
                  <div key={column.stage} className="bg-slate-100 rounded-lg p-3 border border-slate-200 flex flex-col">
                    <div className="flex justify-between items-center pb-2 mb-2 border-b border-slate-200">
                      <div>
                        <h4 className="text-xs font-bold text-slate-800">{column.title}</h4>
                        <span className="text-[10px] font-mono text-slate-500">Total: Rp {(stageTotal/1000000).toFixed(0)}M</span>
                      </div>
                      <span className="bg-slate-200 text-slate-700 text-xs font-bold px-2 py-0.5 rounded-full">
                        {stageLeads.length}
                      </span>
                    </div>

                    <div className="space-y-2.5 flex-1">
                      {stageLeads.map(lead => (
                        <div key={lead.id} className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm space-y-2">
                          <div className="flex justify-between items-start mb-1">
                            <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
                              lead.priority === "urgent" ? "bg-red-100 text-red-700" : "bg-blue-100 text-blue-700"
                            }`}>
                              {lead.priority}
                            </span>
                            {currentUser.role !== "MAHASISWA" && (
                              <div className="flex items-center space-x-1">
                                <button
                                  onClick={() => handleRandomizeCustomer(lead.id)}
                                  title="Simulasikan Respon Lain (Instruktur Only)"
                                  className="text-slate-400 hover:text-amber-600 text-xs p-0.5"
                                >
                                  🎲
                                </button>
                                <button
                                  onClick={() => handleDeleteLead(lead.id)}
                                  title="Hapus Dokumen Prospek (Instruktur Only)"
                                  className="text-slate-400 hover:text-red-600 p-0.5"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            )}
                          </div>
                          <div>
                            <h5 className="font-bold text-xs text-slate-900">{lead.title}</h5>
                            <p className="text-[11px] text-slate-600">{lead.customer_name}</p>
                          </div>
                          <p className="text-xs font-mono font-bold text-indigo-700">
                            Rp {lead.expected_revenue.toLocaleString("id-ID")}
                          </p>
                          {lead.notes && (
                            <p className="text-[10px] text-slate-500 italic bg-slate-50 p-1.5 rounded border border-slate-100 line-clamp-2">
                              "{lead.notes}"
                            </p>
                          )}
                          {lead.is_complaint ? (
                            lead.stage === "proposition" ? (
                              <button
                                onClick={() => {
                                  setActiveMediationComplaint(lead);
                                  setShowMediationModal(true);
                                }}
                                className="w-full bg-amber-600 hover:bg-amber-500 text-white text-[11px] font-semibold py-1.5 px-2 rounded shadow-sm transition flex items-center justify-center space-x-1"
                              >
                                <span>📝</span>
                                <span>Sepakati Solusi Mediasi</span>
                              </button>
                            ) : lead.stage === "won" ? (
                              <div className="text-[10px] bg-emerald-50 text-emerald-700 p-1.5 rounded border border-emerald-200 font-semibold text-center">
                                ✅ Tiket Keluhan Tuntas ({lead.resolution_action || "Selesai"})
                              </div>
                            ) : (
                              <button
                                onClick={() => {
                                  setActiveMediationComplaint(lead);
                                  setShowMediationModal(true);
                                }}
                                className="w-full bg-red-600 hover:bg-red-500 text-white text-[11px] font-semibold py-1.5 px-2 rounded shadow-sm transition flex items-center justify-center space-x-1"
                              >
                                <span>⚠️</span>
                                <span>Tindak Lanjuti Keluhan</span>
                              </button>
                            )
                          ) : (
                            lead.stage === "new" ? (
                              <div className="space-y-1.5 pt-1">
                                <button
                                  onClick={() => handleAdvanceLeadStage(lead.id, "qualified")}
                                  className="w-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-semibold py-1 px-2 rounded border border-indigo-200 transition flex items-center justify-center space-x-1"
                                >
                                  <span>➡️</span>
                                  <span>Kualifikasi Kebutuhan</span>
                                </button>
                                <button
                                  onClick={() => {
                                    setConvertingLead(lead);
                                    setSoQuantity(100);
                                    setSoPaymentTerms("Tempo 30 Hari");
                                  }}
                                  className="w-full bg-slate-50 hover:bg-slate-100 text-slate-700 text-[10px] py-1 px-2 rounded border border-slate-200 transition flex items-center justify-center space-x-1"
                                >
                                  <span>📄</span>
                                  <span>Langsung Terbitkan SO</span>
                                </button>
                              </div>
                            ) : lead.stage === "qualified" ? (
                              <div className="space-y-1.5 pt-1">
                                <button
                                  onClick={() => handleAdvanceLeadStage(lead.id, "proposition")}
                                  className="w-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-[11px] font-semibold py-1 px-2 rounded border border-indigo-200 transition flex items-center justify-center space-x-1"
                                >
                                  <span>➡️</span>
                                  <span>Kirim Proposal / Penawaran</span>
                                </button>
                                <button
                                  onClick={() => {
                                    setConvertingLead(lead);
                                    setSoQuantity(100);
                                    setSoPaymentTerms("Tempo 30 Hari");
                                  }}
                                  className="w-full bg-slate-50 hover:bg-slate-100 text-slate-700 text-[10px] py-1 px-2 rounded border border-slate-200 transition flex items-center justify-center space-x-1"
                                >
                                  <span>📄</span>
                                  <span>Terbitkan Sales Order</span>
                                </button>
                              </div>
                            ) : lead.stage === "proposition" ? (
                              <button
                                onClick={() => {
                                  setConvertingLead(lead);
                                  setSoQuantity(100);
                                  setSoPaymentTerms("Tempo 30 Hari");
                                }}
                                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-semibold py-1.5 px-2 rounded shadow-sm transition flex items-center justify-center space-x-1"
                              >
                                <span>📄</span>
                                <span>Finalisasi & Terbitkan SO</span>
                              </button>
                            ) : (
                              <div className="text-[10px] bg-emerald-50 text-emerald-700 p-1.5 rounded border border-emerald-200 font-semibold text-center">
                                ✅ Kontrak Berhasil (Won)
                              </div>
                            )
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW: MANUFACTURING & MRP (WORK CENTERS & BOM RECIPE) */}
        {/* ========================================================= */}
        {activePortal === "erp" && activeModule === "mrp" && (
          <div className="space-y-6">
            {/* Live Operational & Engineering Decision Panel */}
            <div className={`p-4 rounded-xl border shadow-sm transition-all ${
              (simState.machine_health < 80 || workCenters.some(w => w.status === "breakdown" || w.is_broken))
                ? "bg-rose-50 border-rose-400 text-rose-900 ring-2 ring-rose-500/20"
                : "bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white border-indigo-900/60"
            }`}>
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                      (simState.machine_health < 80 || workCenters.some(w => w.status === "breakdown" || w.is_broken))
                        ? "bg-rose-600 text-white animate-pulse"
                        : "bg-indigo-600 text-white"
                    }`}>
                      {(simState.machine_health < 80 || workCenters.some(w => w.status === "breakdown" || w.is_broken))
                        ? "Peringatan Darurat Mesin SMT"
                        : "Rekayasa Pabrik SMT & Mutu QC"}
                    </span>
                    <span className={`text-xs font-mono font-bold ${
                      (simState.machine_health < 80 || workCenters.some(w => w.status === "breakdown" || w.is_broken))
                        ? "text-rose-700"
                        : "text-indigo-300"
                    }`}>
                      Kesehatan Mesin: {simState.machine_health}% • Kapasitas: {simState.machine_health < 80 ? "0 unit/jam (Mogok)" : "30 unit/jam (Aktif)"}
                    </span>
                  </div>
                  <h4 className="font-bold text-sm mt-1">
                    {(simState.machine_health < 80 || workCenters.some(w => w.status === "breakdown" || w.is_broken))
                      ? "Mesin SMT Mengalami Korsleting Inverter (Lini Terhenti Total)"
                      : "Mitigasi Downtime Mesin & Kontrol Mutu Batch QC"}
                  </h4>
                  <p className={`text-xs mt-0.5 max-w-2xl ${
                    (simState.machine_health < 80 || workCenters.some(w => w.status === "breakdown" || w.is_broken))
                      ? "text-rose-800"
                      : "text-slate-300"
                  }`}>
                    {(simState.machine_health < 80 || workCenters.some(w => w.status === "breakdown" || w.is_broken))
                      ? "Lini perakitan tidak dapat memproses Work Order sampai perbaikan atau overhaul dieksekusi. Pilih solusi teknis di samping:"
                      : "Ambil keputusan teknis untuk menjaga efisiensi perakitan dan mencegah lolosnya produk cacat ke tangan pelanggan:"}
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-2 shrink-0">
                  {(() => {
                    const mfg01 = executedDecisionsMap["MFG-01"];
                    const mfg02 = executedDecisionsMap["MFG-02"];

                    return (
                      <>
                        {mfg01?.choice_id === "A" ? (
                          <div className="bg-emerald-700 text-white text-xs font-bold px-3 py-2 rounded-lg shadow-xs flex items-center space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-200" />
                            <span>✓ Overhaul Disahkan (A)</span>
                          </div>
                        ) : mfg01?.choice_id === "B" ? (
                          <div className="bg-slate-800 text-slate-400 text-xs font-medium px-3 py-2 rounded-lg border border-slate-700">
                            🔒 Opsi Gugur (Maklon Dipilih)
                          </div>
                        ) : (
                          <button
                            onClick={() => handleExecuteBranchDecision("MFG-01", "A")}
                            disabled={executingBranchChoice || !!mfg01}
                            className="bg-rose-700 hover:bg-rose-800 text-white text-xs font-bold px-3 py-2 rounded-lg shadow-sm transition flex items-center"
                            title="Panggil teknisi ekspres, overhaul tuntas 24 jam (Rp 28 Jt)"
                          >
                            <Wrench className="w-3.5 h-3.5 mr-1" /> Overhaul Kilat (Rp 28 Jt)
                          </button>
                        )}

                        {mfg01?.choice_id === "B" ? (
                          <div className="bg-emerald-700 text-white text-xs font-bold px-3 py-2 rounded-lg shadow-xs flex items-center space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-200" />
                            <span>✓ Maklon Disahkan (B)</span>
                          </div>
                        ) : mfg01?.choice_id === "A" ? (
                          <div className="bg-slate-800 text-slate-400 text-xs font-medium px-3 py-2 rounded-lg border border-slate-700">
                            🔒 Opsi Gugur (Overhaul Dipilih)
                          </div>
                        ) : (
                          <button
                            onClick={() => handleExecuteBranchDecision("MFG-01", "B")}
                            disabled={executingBranchChoice || !!mfg01}
                            className="bg-white hover:bg-slate-100 text-slate-800 border border-slate-300 text-xs font-semibold px-3 py-2 rounded-lg shadow-sm transition"
                            title="Alihkan perakitan ke pabrik rekanan maklon (Rp 12 Jt)"
                          >
                            Sub-Kontrak Maklon (Rp 12 Jt)
                          </button>
                        )}

                        {mfg02?.choice_id === "A" ? (
                          <div className="bg-emerald-700 text-white text-xs font-bold px-3 py-2 rounded-lg shadow-xs flex items-center space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-200" />
                            <span>✓ Rework QC Selesai (A)</span>
                          </div>
                        ) : (
                          <button
                            onClick={() => handleExecuteBranchDecision("MFG-02", "A")}
                            disabled={executingBranchChoice || !!mfg02}
                            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-lg shadow-sm transition flex items-center"
                            title="Tahan batch cacat QC & flashing firmware ulang (Rp 6 Jt)"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Rework QC (Rp 6 Jt)
                          </button>
                        )}
                      </>
                    );
                  })()}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Work Centers Status Table */}
              <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-200 bg-slate-50/80 flex justify-between items-center">
                  <div>
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">Stasiun Kerja Pabrik (Work Centers)</h3>
                    <p className="text-[11px] text-slate-500">Lini Manufaktur Cikarang • Kapasitas Riil & Status Operasional</p>
                  </div>
                  <span className="text-xs font-mono font-bold bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded border border-indigo-200">
                    Total: {workCenters.length} Stasiun
                  </span>
                </div>
                <div className="p-4 space-y-3">
                  {workCenters.map(wc => {
                    const isBroken = wc.status === "breakdown" || wc.is_broken || (wc.code.includes("SMT") && simState.machine_health < 80);
                    const capacity = isBroken ? 0 : (wc.capacity_units_per_hour || wc.capacity_per_hour || 30);
                    const hourlyCost = wc.hourly_cost || 180000;
                    const defectRate = wc.failure_rate || wc.failure_risk || 3.5;

                    return (
                      <div key={wc.id} className={`p-3.5 rounded-lg border flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition ${
                        isBroken ? "bg-rose-50/50 border-rose-300" : "bg-slate-50/50 border-slate-200"
                      }`}>
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-mono text-xs bg-slate-200 px-1.5 py-0.5 rounded font-bold text-slate-700">{wc.code}</span>
                            <h4 className="font-bold text-sm text-slate-900">{wc.name}</h4>
                            <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                              isBroken ? "bg-rose-100 text-rose-800 animate-pulse border border-rose-300" : "bg-emerald-100 text-emerald-800"
                            }`}>
                              {isBroken ? "MOGOK / BREAKDOWN" : "OPERATIONAL NORMAL"}
                            </span>
                          </div>
                          <div className="flex items-center space-x-4 text-xs text-slate-500 mt-1.5 flex-wrap gap-y-1">
                            <span>Kapasitas: <strong className={isBroken ? "text-rose-600" : "text-slate-800"}>{capacity} unit/jam</strong></span>
                            <span>Biaya Operasi: <strong className="font-mono">Rp {hourlyCost.toLocaleString("id-ID")}/jam</strong></span>
                            <span>Probabilitas Aus: <strong className={defectRate > 5 ? "text-amber-600" : "text-slate-700"}>{defectRate}%</strong></span>
                          </div>
                        </div>
                        <div className="shrink-0">
                          {isBroken ? (
                            <button
                              onClick={() => handleRepairMachine(wc.id)}
                              className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold px-3 py-1.5 rounded-md shadow-sm transition flex items-center"
                            >
                              <Wrench className="w-3.5 h-3.5 mr-1" /> Servis Mesin (Rp 5.000.000)
                            </button>
                          ) : (
                            <span className="text-xs text-emerald-600 font-semibold flex items-center bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded">
                              <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" /> Siap Produksi
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* BOM Recipe & Work Order Release */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex flex-col justify-between">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 pb-2 mb-3 border-b border-slate-100">
                    Bill of Materials (BOM): Smartwatch VLab Pro
                  </h3>

                  <div className="space-y-2 text-xs mb-4">
                    <div className="flex justify-between py-1 border-b border-slate-100">
                      <span>1x Chipset Processor MCU-X</span>
                      <span className="font-mono text-slate-600">Rp 75.000</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-100">
                      <span>1x Modul Layar AMOLED 1.4"</span>
                      <span className="font-mono text-slate-600">Rp 60.000</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-100">
                      <span>1x Baterai Lithium-Polymer 450mAh</span>
                      <span className="font-mono text-slate-600">Rp 35.000</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-slate-100">
                      <span>1x Casing Logam Aluminium CNC</span>
                      <span className="font-mono text-slate-600">Rp 40.000</span>
                    </div>
                    <div className="pt-2 flex justify-between font-bold text-indigo-700">
                      <span>Total HPP Bahan per Unit:</span>
                      <span className="font-mono">Rp 210.000</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
                    <label className="text-xs font-bold text-slate-700 block">Kuantitas Produksi (Work Order):</label>
                    <div className="flex items-center space-x-2">
                      <input
                        type="number"
                        min="10"
                        step="10"
                        value={woQty}
                        onChange={(e) => setWoQty(parseInt(e.target.value) || 10)}
                        className="w-24 border rounded p-1.5 text-center font-mono font-bold text-xs"
                      />
                      <span className="text-xs text-slate-500">Unit Barang Jadi</span>
                    </div>
                  </div>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-100">
                  {(() => {
                    const hasBrokenMachine = simState.machine_health < 80 || workCenters.some(w => w.status === "breakdown" || w.is_broken);
                    return (
                      <button
                        onClick={handleCreateWO}
                        disabled={hasBrokenMachine}
                        className={`w-full text-xs font-semibold py-2.5 rounded-md transition shadow-sm flex items-center justify-center ${
                          hasBrokenMachine
                            ? "bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300"
                            : "bg-emerald-600 hover:bg-emerald-500 text-white"
                        }`}
                        title={hasBrokenMachine ? "Perbaiki mesin SMT terlebih dahulu sebelum merilis Work Order" : "Rilis Work Order ke lantai pabrik"}
                      >
                        <Factory className="w-4 h-4 mr-1.5" />
                        {hasBrokenMachine ? "Lini Terhenti - Perbaiki Mesin Dahulu" : "Eksekusi Work Order Perakitan"}
                      </button>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW: FINANCIAL ACCOUNTING & BUDGET CONTROL */}
        {/* ========================================================= */}
        {activePortal === "erp" && activeModule === "accounting" && (
          <div className="space-y-6">
            {/* Header Toolbar & Direct Accounting Actions */}
            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Buku Besar & Kontrol Anggaran Perusahaan</h3>
                <p className="text-xs text-slate-500">Sistem pembukuan berpasangan (Double-Entry Ledger) & Pemantauan Realisasi Divisi</p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleAdvanceRound}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-1.5 rounded-md shadow-sm transition flex items-center"
                  title="Tutup buku periode ini dan kalkulasi laba/rugi bersih"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Tutup Buku Bulanan
                </button>
                <button
                  onClick={() => {
                    setActiveModule("missions");
                    setMissionsSubTab("cfo");
                  }}
                  className="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 text-xs font-bold px-3 py-1.5 rounded-md shadow-sm transition flex items-center"
                  title="Buka Analisis DuPont 3-Stage & Altman Z-Score"
                >
                  <TrendingUp className="w-3.5 h-3.5 mr-1" /> Diagnostik CFO
                </button>
                {currentUser.role !== "MAHASISWA" && (
                  <button
                    onClick={() => setShowAddBudgetModal(true)}
                    className="bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition flex items-center"
                    title="Hanya Instruktur: Atur Plafon Anggaran Departemen"
                  >
                    <Plus className="w-3.5 h-3.5 mr-1" /> Pagu Divisi
                  </button>
                )}
              </div>
            </div>

            {/* In-Situ Interactive Accounting & Fiscal Decision Bar */}
            <div className="bg-gradient-to-r from-slate-900 to-indigo-950 text-white p-4 rounded-xl border border-indigo-900/60 shadow-sm">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-emerald-600 text-white px-2 py-0.5 rounded">
                      Keputusan Strategis Keuangan
                    </span>
                    <span className="text-xs font-mono text-indigo-300 font-bold">
                      Saldo Kas: Rp {simState.cash.toLocaleString("id-ID")}
                    </span>
                  </div>
                  <h4 className="font-bold text-sm text-white mt-1">Dilema Fiskal & Kebijakan Likuiditas Kas</h4>
                  <p className="text-xs text-slate-300 mt-0.5 max-w-2xl">
                    Pilih kebijakan mitigasi pajak atau penambahan modal kerja jangka pendek untuk menjaga Altman Z-Score di zona aman:
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {(() => {
                    const acc01 = executedDecisionsMap["ACC-01"];
                    const acc02 = executedDecisionsMap["ACC-02"];

                    return (
                      <>
                        {acc01?.choice_id === "A" ? (
                          <div className="bg-emerald-700 text-white text-xs font-bold px-3 py-2 rounded-lg shadow-xs flex items-center space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-200" />
                            <span>✓ Keberatan Pajak Disahkan (A)</span>
                          </div>
                        ) : acc01?.choice_id === "B" ? (
                          <div className="bg-slate-800 text-slate-400 text-xs font-medium px-3 py-2 rounded-lg border border-slate-700">
                            🔒 Opsi Gugur (Bayar Pokok Dipilih)
                          </div>
                        ) : (
                          <button
                            onClick={() => handleExecuteBranchDecision("ACC-01", "A")}
                            disabled={executingBranchChoice || !!acc01}
                            className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-lg shadow-sm transition flex items-center"
                            title="Ajukan Keberatan Pajak via Konsultan Resmi (Biaya Rp 15 Jt, +5 Pts Skor Audit)"
                          >
                            <FileText className="w-3.5 h-3.5 mr-1" /> Keberatan Pajak (Rp 15 Jt)
                          </button>
                        )}

                        {acc02?.choice_id === "B" || acc02?.choice_id === "A" ? (
                          <div className="bg-emerald-700 text-white text-xs font-bold px-3 py-2 rounded-lg shadow-xs flex items-center space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-200" />
                            <span>✓ Modal Disahkan</span>
                          </div>
                        ) : (
                          <button
                            onClick={() => handleExecuteBranchDecision("ACC-02", "B")}
                            disabled={executingBranchChoice || !!acc02}
                            className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-3 py-2 rounded-lg shadow-sm transition flex items-center"
                            title="Tarik Pinjaman Modal Kerja (+Rp 50 Jt Kas)"
                          >
                            <DollarSign className="w-3.5 h-3.5 mr-1" /> Tambah Modal (+Rp 50 Jt)
                          </button>
                        )}

                        {acc01?.choice_id === "B" ? (
                          <div className="bg-emerald-700 text-white text-xs font-bold px-3 py-2 rounded-lg shadow-xs flex items-center space-x-1">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-200" />
                            <span>✓ Pokok Pajak Dilunasi (B)</span>
                          </div>
                        ) : acc01?.choice_id === "A" ? (
                          <div className="bg-slate-800 text-slate-400 text-xs font-medium px-3 py-2 rounded-lg border border-slate-700">
                            🔒 Opsi Gugur (Keberatan Pajak Dipilih)
                          </div>
                        ) : (
                          <button
                            onClick={() => handleExecuteBranchDecision("ACC-01", "B")}
                            disabled={executingBranchChoice || !!acc01}
                            className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-3 py-2 rounded-lg transition"
                            title="Bayar Penuh Denda & Pokok Pajak (Rp 42 Jt)"
                          >
                            Bayar Pokok Pajak (Rp 42 Jt)
                          </button>
                        )}
                      </>
                    );
                  })()}
                </div>
              </div>
            </div>

            {/* Black Swan Emergency Alert */}
            {blackSwanAlert && (
              <div className="bg-amber-50 border-l-4 border-amber-500 rounded-lg p-4 shadow-sm">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-sm font-bold text-amber-900 flex items-center">
                      <AlertCircle className="w-4 h-4 mr-1.5 text-amber-600" /> {blackSwanAlert.shock_title}
                    </h4>
                    <p className="text-xs text-amber-800 mt-1 leading-relaxed">{blackSwanAlert.shock_description}</p>
                    <div className="mt-2 text-xs font-mono font-bold text-red-700">
                      Kerugian Bersih Langsung: -Rp {blackSwanAlert.financial_loss?.toLocaleString("id-ID")}
                    </div>
                  </div>
                  <button onClick={() => setBlackSwanAlert(null)} className="text-amber-700 hover:text-amber-900 text-xs font-bold">✕ Tutup</button>
                </div>
              </div>
            )}

            {/* General Ledger & Department Budgets Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Chart of Accounts Balance Table */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-3.5 border-b border-slate-200 bg-slate-50/80">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">Neraca Saldo Buku Besar (Chart of Accounts)</h4>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200 text-xs">
                    <thead className="bg-slate-50 text-slate-500 font-semibold">
                      <tr>
                        <th className="px-3 py-2 text-left">Kode Akun</th>
                        <th className="px-3 py-2 text-left">Nama Akun</th>
                        <th className="px-3 py-2 text-left">Golongan</th>
                        <th className="px-3 py-2 text-right">Saldo Buku</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {accounts.map(acc => (
                        <tr key={acc.id} className="hover:bg-slate-50">
                          <td className="px-3 py-2 font-mono text-slate-500 font-bold">{acc.code}</td>
                          <td className="px-3 py-2 font-semibold text-slate-800">{acc.name}</td>
                          <td className="px-3 py-2 text-xs">
                            {acc.account_type === "asset" && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">ASET LANCAR</span>}
                            {acc.account_type === "liability" && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">UTANG USAHA (AP)</span>}
                            {acc.account_type === "equity" && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-50 text-purple-700 border border-purple-200">EKUITAS / MODAL</span>}
                            {acc.account_type === "revenue" && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">PENDAPATAN</span>}
                            {acc.account_type === "expense" && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">BEBAN USAHA</span>}
                            {!acc.account_type && <span className="text-slate-400 font-mono text-[10px]">-</span>}
                          </td>
                          <td className="px-3 py-2 text-right font-mono font-bold text-slate-900">
                            Rp {acc.balance.toLocaleString("id-ID")}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Departmental Budgets Monitor & AP Quick Pay */}
              <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center pb-2 mb-3 border-b border-slate-100">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                      Realisasi Anggaran Departemen (Budget vs Actual)
                    </h4>
                    <span className="text-[10px] text-slate-500 font-mono">Pagu Anggaran Q1</span>
                  </div>
                  <div className="space-y-4">
                    {budgets.map(b => {
                      const pct = Math.min(100, Math.round((b.spent_amount / b.allocated_amount) * 100));
                      return (
                        <div key={b.id} className="p-2.5 rounded bg-slate-50 border border-slate-100 text-xs">
                          <div className="flex justify-between items-center mb-1">
                            <span className="font-bold text-slate-800">{b.department}</span>
                            <div className="flex items-center space-x-2">
                              <span className="font-mono text-slate-600 font-medium">
                                Rp {b.spent_amount.toLocaleString("id-ID")} / Rp {b.allocated_amount.toLocaleString("id-ID")} ({pct}%)
                              </span>
                              {currentUser.role !== "MAHASISWA" && (
                                <button onClick={() => handleDeleteBudget(b.id)} title="Hapus Pagu (Instruktur Only)" className="text-slate-400 hover:text-red-600 p-0.5">
                                  <Trash2 className="w-3 h-3" />
                                </button>
                              )}
                            </div>
                          </div>
                          <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all ${pct > 80 ? "bg-red-500" : "bg-indigo-600"}`}
                              style={{ width: `${pct}%` }}
                            ></div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Quick AP Pay Action Card */}
                {(() => {
                  const apAcc = accounts.find(a => a.code === "2010");
                  const apBal = apAcc?.balance || 0;
                  if (apBal <= 0) return null;
                  return (
                    <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-center justify-between">
                      <div>
                        <div className="text-xs font-bold text-rose-900 flex items-center">
                          <DollarSign className="w-3.5 h-3.5 mr-1 text-rose-600" />
                          Tagihan Utang Usaha (AP): Rp {apBal.toLocaleString("id-ID")}
                        </div>
                        <p className="text-[10px] text-rose-600 mt-0.5">
                          Kewajiban pembayaran PO ke vendor rekanan.
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={async () => {
                          try {
                            const res = await fetch(`${API_BASE}/vendors/ap/pay`, {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({ company_id: companyId, amount: apBal })
                            });
                            const data = await res.json();
                            if (res.ok) {
                              showNotification(`💸 ${data.message}`);
                              fetchData(companyId);
                            } else {
                              showNotification(`❌ ${data.detail || "Gagal lunasi utang"}`);
                            }
                          } catch (err) {
                            showNotification("❌ Gagal menghubungi server");
                          }
                        }}
                        className="px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold transition shadow-sm"
                      >
                        Lunasi Utang via Kas
                      </button>
                    </div>
                  );
                })()}
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW: HUMAN CAPITAL & BIPARTITE NEGOTIATIONS */}
        {/* ========================================================= */}
        {activePortal === "erp" && activeModule === "hcm" && (
          <div className="space-y-6">
            {/* Header Toolbar */}
            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center space-x-3 flex-1">
                <div className="relative flex-1 max-w-md">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Cari pegawai berdasarkan nama atau departemen..."
                    value={employeeSearch}
                    onChange={(e) => setEmployeeSearch(e.target.value)}
                    className="w-full pl-9 pr-3 py-1.5 border border-slate-300 rounded-md text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
                <span className="text-xs text-slate-500">{filteredEmployees.length} Pegawai Aktif</span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowAddEmployeeModal(true)}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-1.5 rounded-md shadow-sm transition flex items-center"
                >
                  <Plus className="w-3.5 h-3.5 mr-1" /> Rekrut Pegawai Baru
                </button>
              </div>
            </div>

            {/* Industrial Relations (Bipartite Dialog Card & Interactive Negotiation Table) */}
            {unionProfile && (
              <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 shadow-lg space-y-4">
                {/* Header Profile */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-700 to-indigo-500 flex items-center justify-center font-bold text-sm shadow-md">
                      {unionProfile.rep_name?.charAt(0) || "A"}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className="font-bold text-sm text-white">{unionProfile.rep_name}</h4>
                        <span className="text-[10px] bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/30 font-medium">
                          {unionProfile.label}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">Dewan Pengurus Ketenagakerjaan Bipartit • Lini Pabrik & Manufaktur</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {simState.is_strike_active ? (
                      <span className="bg-rose-950/80 text-rose-300 border border-rose-500/40 px-3 py-1 rounded-full text-xs font-bold flex items-center space-x-1.5 animate-pulse">
                        <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                        <span>Mogok Kerja Aktif</span>
                      </span>
                    ) : (
                      <span className="bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 px-3 py-1 rounded-full text-xs font-semibold flex items-center space-x-1.5">
                        <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                        <span>Meja Perundingan Terbuka</span>
                      </span>
                    )}
                  </div>
                </div>

                {/* Strike Warning Banner if active */}
                {simState.is_strike_active && (
                  <div className="bg-rose-950/70 border border-rose-600/60 rounded-lg p-3.5 text-xs text-rose-200 flex items-start space-x-2.5">
                    <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-rose-100 text-sm block">PERINGATAN: Mogok Kerja Sedang Berlangsung!</span>
                      <p className="mt-0.5 text-rose-300">
                        Alasan: <strong>{simState.strike_reason || "Tuntutan penyesuaian uang saku darurat dan upah kerja."}</strong> Lini pabrik terhenti sampai kesepakatan bipartit ditandatangani.
                      </p>
                    </div>
                  </div>
                )}

                {/* Quote Statement */}
                <div className="bg-slate-950/80 p-3.5 rounded-lg border border-slate-800 text-xs">
                  <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1">
                    Pernyataan Resmi Perwakilan Buruh:
                  </span>
                  <p className="text-indigo-200 italic leading-relaxed">
                    "{unionProfile.speech}"
                  </p>
                </div>

                {/* Live Negotiation Feedback Result (Accepted / Rejected speech) */}
                {strikeNegotiationResult && (
                  <div className={`p-4 rounded-lg border text-xs space-y-1.5 animate-in fade-in duration-200 ${
                    strikeNegotiationResult.accepted
                      ? "bg-emerald-950/90 border-emerald-500/50 text-emerald-100"
                      : "bg-amber-950/90 border-amber-500/50 text-amber-100"
                  }`}>
                    <div className="flex items-center space-x-2 font-bold text-sm">
                      {strikeNegotiationResult.accepted ? (
                        <>
                          <Check className="w-4 h-4 text-emerald-400" />
                          <span className="text-emerald-300">Kesepakatan Bipartit Diterima!</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-4 h-4 text-amber-400" />
                          <span className="text-amber-300">Tawaran Ditolak oleh {unionProfile.rep_name}</span>
                        </>
                      )}
                    </div>
                    <p className="italic text-slate-200">"{strikeNegotiationResult.speech}"</p>
                    {strikeNegotiationResult.accepted ? (
                      <div className="pt-2 border-t border-emerald-800/60 flex flex-wrap gap-4 text-[11px] text-emerald-300">
                        <span>Total Kompensasi Dibayarkan: <strong>Rp {(strikeNegotiationResult.bonus_total_paid || 0).toLocaleString("id-ID")}</strong></span>
                        <span>Indeks Moral Pekerja Baru: <strong>{strikeNegotiationResult.new_worker_morale || 95}%</strong></span>
                        <span className="text-emerald-400 font-semibold">✓ Operasional Pabrik Normal Kembali</span>
                      </div>
                    ) : (
                      <p className="text-[11px] text-amber-300 pt-1">
                        Saran: Tingkatkan tawaran bonus damai atau persentase kenaikan gaji agar tuntutan kaum pekerja terpenuhi.
                      </p>
                    )}
                  </div>
                )}

                {/* Interactive Negotiation Form */}
                <div className="bg-slate-800/70 border border-slate-700/60 rounded-xl p-4 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 border-b border-slate-700/50 pb-2">
                    <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                      <span>🤝 Formulir Pengajuan Kesepakatan Manajemen (Bipartit Accord)</span>
                    </span>
                    <span className="text-[10px] text-slate-400">Pilih besaran tawaran untuk diajukan ke perwakilan buruh</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                    {/* Offer 1: Wage Raise % */}
                    <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-700 space-y-2">
                      <div className="flex justify-between items-center">
                        <label className="font-semibold text-slate-300">Tawaran Kenaikan Gaji / Uang Lembur (%):</label>
                        <span className="font-bold text-indigo-400 text-sm">{wageRaise}%</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="25"
                        step="1"
                        value={wageRaise}
                        onChange={(e) => setWageRaise(parseFloat(e.target.value) || 0)}
                        className="w-full accent-indigo-500 cursor-pointer"
                      />
                      <div className="flex space-x-1.5">
                        {[0, 5, 8, 10, 15].map((pct) => (
                          <button
                            key={pct}
                            type="button"
                            onClick={() => setWageRaise(pct)}
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold transition ${
                              wageRaise === pct
                                ? "bg-indigo-600 text-white"
                                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                            }`}
                          >
                            +{pct}%
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Offer 2: Worker Bonus (Rp) */}
                    <div className="bg-slate-900/90 p-3 rounded-lg border border-slate-700 space-y-2">
                      <div className="flex justify-between items-center">
                        <label className="font-semibold text-slate-300">Uang Saku Darurat / Bonus Damai (Rp/Buruh):</label>
                        <span className="font-bold text-emerald-400 text-sm">
                          Rp {workerBonus.toLocaleString("id-ID")}
                        </span>
                      </div>
                      <div className="flex space-x-1.5">
                        {[500000, 1000000, 1500000, 2000000].map((bVal) => (
                          <button
                            key={bVal}
                            type="button"
                            onClick={() => setWorkerBonus(bVal)}
                            className={`flex-1 py-1 rounded text-[10px] font-semibold transition text-center ${
                              workerBonus === bVal
                                ? "bg-emerald-600 text-white"
                                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                            }`}
                          >
                            Rp {(bVal / 1000000).toFixed(1)} Jt
                          </button>
                        ))}
                      </div>
                      <input
                        type="number"
                        step="100000"
                        value={workerBonus}
                        onChange={(e) => setWorkerBonus(parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1 text-white font-mono text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                        placeholder="Ketik nominal kustom..."
                      />
                    </div>
                  </div>

                  {/* Negotiation Action Bar */}
                  <div className="pt-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t border-slate-700/50">
                    <div className="text-[11px] text-slate-300 flex items-center space-x-4">
                      <span>Pekerja: <strong className="text-white">{employees.length} Orang</strong></span>
                      <span>Total Kas Berkurang: <strong className="text-emerald-400">Rp {(workerBonus * employees.length).toLocaleString("id-ID")}</strong></span>
                    </div>
                    <button
                      type="button"
                      onClick={handleResolveStrike}
                      className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold px-5 py-2.5 rounded-lg shadow-md shadow-indigo-600/30 transition flex items-center justify-center space-x-2 text-xs"
                    >
                      <Check className="w-4 h-4" />
                      <span>Ajukan Kesepakatan ke {unionProfile.rep_name}</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Employee Master Table */}
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-3.5 border-b border-slate-200 bg-slate-50/80">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">Master Data Pegawai & Beban Payroll</h4>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-xs">
                  <thead className="bg-slate-50 text-slate-500 font-semibold">
                    <tr>
                      <th className="px-3 py-2 text-left">Nama Lengkap</th>
                      <th className="px-3 py-2 text-left">Departemen</th>
                      <th className="px-3 py-2 text-left">Jabatan</th>
                      <th className="px-3 py-2 text-right">Gaji Bulanan</th>
                      <th className="px-3 py-2 text-center">Indeks Moral</th>
                      <th className="px-3 py-2 text-center">Status</th>
                      {currentUser.role !== "MAHASISWA" && <th className="px-3 py-2 text-center">Aksi</th>}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filteredEmployees.map(emp => (
                      <tr key={emp.id} className="hover:bg-slate-50">
                        <td className="px-3 py-2 font-bold text-slate-900">{emp.name}</td>
                        <td className="px-3 py-2 text-slate-600">{emp.department}</td>
                        <td className="px-3 py-2 text-slate-500">{emp.role}</td>
                        <td className="px-3 py-2 text-right font-mono font-bold text-slate-800">
                          Rp {emp.monthly_salary.toLocaleString("id-ID")}
                        </td>
                        <td className="px-3 py-2 text-center font-bold text-indigo-600">{emp.morale_score}%</td>
                        <td className="px-3 py-2 text-center">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            emp.status === "active" ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"
                          }`}>
                            {emp.status}
                          </span>
                        </td>
                        {currentUser.role !== "MAHASISWA" && (
                          <td className="px-3 py-2 text-center">
                            <button
                              onClick={() => handleDeleteEmployee(emp.id)}
                              title="Nonaktifkan Pegawai (Instruktur Only)"
                              className="text-slate-400 hover:text-red-600 p-1"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW: DOSEN COMMAND CENTER (SLIDERS & MULTI-TENANT MANAGEMENT) */}
        {/* ========================================================= */}
        {activePortal === "dosen" && (
          <div className="space-y-6">
            {/* ========================================================= */}
            {/* MULTI-CLASS & TEAM TEACHING FEB CONTROL CENTER */}
            {/* ========================================================= */}
            <div className="bg-gradient-to-r from-slate-900 via-[#0f172a] to-slate-900 text-white p-5 rounded-xl border border-indigo-500/30 shadow-xl space-y-4">
              {/* Full Access Super Admin Badge Banner */}
              {currentUser.role === "ADMIN" && (
                <div className="bg-gradient-to-r from-rose-950/80 via-slate-900 to-indigo-950/80 border border-rose-500/40 p-3 rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-inner">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-1.5 rounded-md bg-rose-600/30 border border-rose-500/50 text-rose-300 shrink-0">
                      <ShieldCheck className="w-4 h-4 text-rose-400" />
                    </div>
                    <div>
                      <div className="font-bold text-xs text-rose-200 flex items-center">
                        <span>Mode Super Administrator (Full System Access)</span>
                        <span className="ml-2 px-1.5 py-0.2 text-[9px] bg-rose-600 text-white rounded font-mono uppercase font-black tracking-wider">
                          Full Access
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-300 mt-0.5">
                        Anda memiliki hak akses tertinggi untuk mengelola seluruh kelas FEB, mengatur profil 3 Dosen Pengampu, rolling skenario, reset sistem, serta membuka semua tenant perusahaan mahasiswa.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 shrink-0 self-start sm:self-center">
                    <button
                      type="button"
                      onClick={() => {
                        fetchUsers();
                        setDosenSubTab("users");
                      }}
                      className="bg-indigo-950/90 hover:bg-indigo-900 text-indigo-200 hover:text-white border border-indigo-700/60 text-xs px-3 py-1.5 rounded-md transition font-semibold flex items-center space-x-1.5 shadow-sm"
                      title="Buka manajemen username & kata sandi seluruh pengguna"
                    >
                      <KeyRound className="w-3.5 h-3.5 text-indigo-400" />
                      <span>🔐 Ubah User & Password</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setBrandingForm(branding);
                        setShowBrandingModal(true);
                      }}
                      className="bg-rose-900/60 hover:bg-rose-800 text-rose-200 hover:text-white border border-rose-700/60 text-xs px-3 py-1.5 rounded-md transition font-semibold flex items-center space-x-1.5 shadow-sm"
                    >
                      <Settings className="w-3.5 h-3.5" />
                      <span>Konfigurasi Branding</span>
                    </button>
                  </div>
                </div>
              )}

              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-700/60 pb-3">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="bg-indigo-600 text-white font-extrabold text-[10px] px-2.5 py-0.5 rounded uppercase tracking-wider shadow">
                      Multi-Team Dosen & Multi-Class Hub
                    </span>
                    <span className="text-indigo-300 text-xs font-mono">Fakultas Ekonomi & Bisnis (FEB)</span>
                  </div>
                  <h2 className="text-lg font-bold text-white mt-1 flex items-center">
                    <GraduationCap className="w-5 h-5 mr-2 text-indigo-400" />
                    Manajemen Kelas & Kolaborasi Tim Dosen Pengampu
                  </h2>
                  <p className="text-xs text-slate-300 mt-0.5">
                    Kelola banyak sesi kelas perkuliahan paralel secara fleksibel dengan penugasan Tim Dosen lintas rumpun ilmu (Pemasaran, SDM, Keuangan & Akuntansi, Manufaktur).
                  </p>
                </div>
                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    type="button"
                    onClick={handleOpenAddSession}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-3.5 py-2 rounded-lg shadow transition flex items-center space-x-1.5"
                  >
                    <Plus className="w-4 h-4" />
                    <span>+ Buat Sesi Kelas Baru</span>
                  </button>
                </div>
              </div>

              {/* Class Switcher Selector */}
              <div className="space-y-2">
                <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                  <span>Pilih Sesi Kelas yang Sedang Dikelola ({sessions.length} Kelas Terdaftar):</span>
                  <span className="text-[11px] font-normal text-indigo-300 font-mono">
                    Kelas Aktif: <strong className="text-white">{sessions.find(s => s.id === selectedSessionId)?.name || "Kelas FEB A"}</strong>
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {sessions.map((s) => {
                    const isSelected = s.id === selectedSessionId;
                    const teamCount = s.team_lecturers ? s.team_lecturers.length : 1;
                    return (
                      <div
                        key={s.id}
                        onClick={() => handleSelectSession(s.id)}
                        className={`text-left p-3 rounded-xl border transition cursor-pointer flex flex-col justify-between ${
                          isSelected
                            ? "bg-indigo-600/25 border-indigo-400 ring-2 ring-indigo-500/50 shadow-lg shadow-indigo-950/50"
                            : "bg-slate-950/60 border-slate-800 hover:bg-slate-900 hover:border-slate-700"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center space-x-2.5 min-w-0">
                            <div className={`p-2 rounded-lg shrink-0 ${isSelected ? "bg-indigo-600 text-white shadow" : "bg-slate-800 text-slate-400"}`}>
                              <Building2 className="w-4 h-4" />
                            </div>
                            <div className="min-w-0">
                              <div className="font-bold text-xs text-white truncate">{s.name}</div>
                              <div className="text-[10px] text-slate-400 font-mono flex items-center space-x-1.5 mt-0.5">
                                <span className="text-indigo-300 font-bold">{s.code}</span>
                                <span>•</span>
                                <span>{s.company_count || 0} Kelompok</span>
                              </div>
                            </div>
                          </div>
                          {isSelected ? (
                            <span className="bg-emerald-500 text-white text-[9px] font-extrabold px-2 py-0.5 rounded-full shrink-0 shadow-sm">
                              AKTIF
                            </span>
                          ) : (
                            <span className="text-[9px] font-mono text-slate-500 border border-slate-800 px-1.5 py-0.5 rounded shrink-0">
                              {s.status === "archived" ? "Arsip" : "Standby"}
                            </span>
                          )}
                        </div>

                        {/* Team Dosen & Term Info Tags */}
                        <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                          <div className="text-slate-400 truncate flex items-center space-x-1">
                            <Users className="w-3 h-3 text-indigo-400 shrink-0" />
                            <span className="truncate">Tim: <strong className="text-slate-200">{teamCount} Dosen</strong></span>
                          </div>
                          <span className="text-indigo-300/80 text-[9px] font-mono truncate max-w-[120px]">
                            {s.academic_term || "Ganjil 2026/2027"}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* 1-Click Problem Rolling Engine Bar */}
              <div className="bg-slate-950/90 p-4 rounded-lg border border-slate-800 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
                  <div>
                    <span className="text-xs font-bold text-amber-400 flex items-center">
                      <Zap className="w-4 h-4 mr-1.5" />
                      1-Klik Rolling Urutan Masalah ({sessions.find(s => s.id === selectedSessionId)?.code || "ERP-FEB"}):
                    </span>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Klik salah satu tombol untuk mengatur giliran dosen yang masuk duluan. Misi Tahap 1 seluruh kelompok di kelas ini otomatis langsung berganti seketika.
                    </p>
                  </div>
                  {rollingLoading && (
                    <span className="text-xs font-bold text-indigo-400 flex items-center">
                      <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" /> Sedang mensinkronkan misi kelompok...
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
                  <button
                    type="button"
                    disabled={rollingLoading}
                    onClick={() => handleRollCases("marketing_first")}
                    className="text-left bg-gradient-to-br from-blue-950/80 via-slate-900 to-slate-950 border border-blue-600/40 hover:border-blue-400 p-3 rounded-lg transition group shadow-sm disabled:opacity-50"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-xs text-blue-300 group-hover:text-white flex items-center">
                        <Briefcase className="w-4 h-4 mr-1.5 text-blue-400" />
                        Pemasaran Masuk Duluan
                      </span>
                      <span className="text-[9px] bg-blue-900/80 text-blue-200 px-1.5 py-0.5 rounded font-mono font-bold">MKT</span>
                    </div>
                    <div className="text-[11px] text-slate-300 leading-tight">
                      <strong>Misi 1:</strong> Skandal Retur VIP & Penyelamatan Omset<br/>
                      <span className="text-slate-500 text-[10px]">Rotasi Lanjut: SDM (Lembur) → Keuangan (Kas)</span>
                    </div>
                  </button>

                  <button
                    type="button"
                    disabled={rollingLoading}
                    onClick={() => handleRollCases("finance_first")}
                    className="text-left bg-gradient-to-br from-emerald-950/80 via-slate-900 to-slate-950 border border-emerald-600/40 hover:border-emerald-400 p-3 rounded-lg transition group shadow-sm disabled:opacity-50"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-xs text-emerald-300 group-hover:text-white flex items-center">
                        <DollarSign className="w-4 h-4 mr-1.5 text-emerald-400" />
                        Keuangan Masuk Duluan
                      </span>
                      <span className="text-[9px] bg-emerald-900/80 text-emerald-200 px-1.5 py-0.5 rounded font-mono font-bold">AKUN</span>
                    </div>
                    <div className="text-[11px] text-slate-300 leading-tight">
                      <strong>Misi 1:</strong> Mitigasi Piutang Macet & Likuiditas Kas<br/>
                      <span className="text-slate-500 text-[10px]">Rotasi Lanjut: Pemasaran → SDM</span>
                    </div>
                  </button>

                  <button
                    type="button"
                    disabled={rollingLoading}
                    onClick={() => handleRollCases("hr_first")}
                    className="text-left bg-gradient-to-br from-teal-950/80 via-slate-900 to-slate-950 border border-teal-600/40 hover:border-teal-400 p-3 rounded-lg transition group shadow-sm disabled:opacity-50"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-xs text-teal-300 group-hover:text-white flex items-center">
                        <Users className="w-4 h-4 mr-1.5 text-teal-400" />
                        SDM & Pabrik MRP Masuk Duluan
                      </span>
                      <span className="text-[9px] bg-teal-900/80 text-teal-200 px-1.5 py-0.5 rounded font-mono font-bold">MRP/HR</span>
                    </div>
                    <div className="text-[11px] text-slate-300 leading-tight">
                      <strong>Misi 1:</strong> Kerusakan Mesin SMT, Mogok & Mediasi Bipartit<br/>
                      <span className="text-slate-500 text-[10px]">Rotasi Lanjut: Keuangan → Pemasaran</span>
                    </div>
                  </button>
                </div>
              </div>

              {/* 3 Lecturers of Discipline Profile Cards with Direct CRUD Edit Trigger */}
              <div className="space-y-2 pt-1">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center">
                    <Users className="w-3.5 h-3.5 mr-1.5 text-indigo-400" /> Profil 3 Dosen Rumpun Ilmu (Team Teaching):
                  </span>
                  <div className="flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={() => {
                        fetchUsers();
                        setDosenSubTab("users");
                      }}
                      className="text-[11px] font-semibold text-emerald-300 hover:text-white bg-emerald-950/90 hover:bg-emerald-900 border border-emerald-700/60 hover:border-emerald-500 px-3 py-1 rounded-md transition flex items-center space-x-1.5 shadow-sm"
                      title="Buka panel manajemen password dan username akun dosen & mahasiswa"
                    >
                      <KeyRound className="w-3 h-3 text-emerald-400" />
                      <span>🔐 Ubah Password Akun</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setBrandingForm(branding);
                        setShowBrandingModal(true);
                      }}
                      className="text-[11px] font-semibold text-indigo-300 hover:text-white bg-indigo-950/90 hover:bg-indigo-900 border border-indigo-700/60 hover:border-indigo-500 px-3 py-1 rounded-md transition flex items-center space-x-1.5 shadow-sm group"
                      title="Buka form CRUD untuk mengubah nama dan gelar ketiga dosen pengampu FEB"
                    >
                      <Settings className="w-3 h-3 text-indigo-400 group-hover:rotate-45 transition-transform" />
                      <span>✏️ Ubah Profil Dosen</span>
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div 
                    onClick={() => {
                      setBrandingForm(branding);
                      setShowBrandingModal(true);
                    }}
                    className="bg-slate-950/60 hover:bg-slate-900/80 border border-slate-800 hover:border-blue-500/50 p-2.5 rounded-lg flex items-center space-x-2.5 cursor-pointer transition group"
                    title="Klik untuk mengubah nama dosen pemasaran"
                  >
                    <div className="w-8 h-8 rounded-full bg-blue-600/30 border border-blue-400/30 flex items-center justify-center font-bold text-blue-300 shrink-0 group-hover:scale-105 transition-transform">
                      MKT
                    </div>
                    <div className="min-w-0">
                      <div className="font-bold text-slate-200 group-hover:text-blue-300 transition truncate">
                        {branding.lecturer_marketing_name || "Dr. Maya Indah, S.E., M.M."}
                      </div>
                      <div className="text-[10px] text-blue-400 font-medium flex items-center">
                        <span>Dosen Pemasaran & CRM</span>
                        <span className="ml-1 opacity-0 group-hover:opacity-100 text-[9px] text-slate-400">✏️</span>
                      </div>
                    </div>
                  </div>

                  <div 
                    onClick={() => {
                      setBrandingForm(branding);
                      setShowBrandingModal(true);
                    }}
                    className="bg-slate-950/60 hover:bg-slate-900/80 border border-slate-800 hover:border-teal-500/50 p-2.5 rounded-lg flex items-center space-x-2.5 cursor-pointer transition group"
                    title="Klik untuk mengubah nama dosen SDM"
                  >
                    <div className="w-8 h-8 rounded-full bg-teal-600/30 border border-teal-400/30 flex items-center justify-center font-bold text-teal-300 shrink-0 group-hover:scale-105 transition-transform">
                      HR
                    </div>
                    <div className="min-w-0">
                      <div className="font-bold text-slate-200 group-hover:text-teal-300 transition truncate">
                        {branding.lecturer_hr_name || "Drs. Bambang Prakoso, M.Psi."}
                      </div>
                      <div className="text-[10px] text-teal-400 font-medium flex items-center">
                        <span>Dosen SDM & Organisasi</span>
                        <span className="ml-1 opacity-0 group-hover:opacity-100 text-[9px] text-slate-400">✏️</span>
                      </div>
                    </div>
                  </div>

                  <div 
                    onClick={() => {
                      setBrandingForm(branding);
                      setShowBrandingModal(true);
                    }}
                    className="bg-slate-950/60 hover:bg-slate-900/80 border border-slate-800 hover:border-emerald-500/50 p-2.5 rounded-lg flex items-center space-x-2.5 cursor-pointer transition group"
                    title="Klik untuk mengubah nama dosen keuangan"
                  >
                    <div className="w-8 h-8 rounded-full bg-emerald-600/30 border border-emerald-400/30 flex items-center justify-center font-bold text-emerald-300 shrink-0 group-hover:scale-105 transition-transform">
                      AKN
                    </div>
                    <div className="min-w-0">
                      <div className="font-bold text-slate-200 group-hover:text-emerald-300 transition truncate">
                        {branding.lecturer_finance_name || "Dr. Ir. Budi Santoso, Ak."}
                      </div>
                      <div className="text-[10px] text-emerald-400 font-medium flex items-center">
                        <span>Dosen Keuangan & Akuntansi</span>
                        <span className="ml-1 opacity-0 group-hover:opacity-100 text-[9px] text-slate-400">✏️</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Dosen Sub-Navigation Tabs */}
            <div className="bg-white px-4 pt-3 rounded-lg border border-slate-200 shadow-sm flex space-x-4 text-xs font-semibold">
              <button
                onClick={() => setDosenSubTab("sliders")}
                className={`pb-3 flex items-center border-b-2 transition ${
                  dosenSubTab === "sliders"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                <Sliders className="w-4 h-4 mr-1.5" />
                <span>Parameter Simulasi & Disrupsi Makro</span>
              </button>
              <button
                onClick={() => setDosenSubTab("tenants")}
                className={`pb-3 flex items-center border-b-2 transition ${
                  dosenSubTab === "tenants"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                <Building2 className="w-4 h-4 mr-1.5" />
                <span>Manajemen Multi-Tenant & Sesi Kelas</span>
                <span className="ml-2 bg-indigo-100 text-indigo-700 text-[10px] px-2 py-0.5 rounded-full font-bold">
                  {companies.length} Kelompok
                </span>
              </button>
              <button
                onClick={() => {
                  setDosenSubTab("cases");
                  if (companies.length > 0 && !selectedCompanyForCases) {
                    setSelectedCompanyForCases(companies[0].id);
                  }
                }}
                className={`pb-3 flex items-center border-b-2 transition ${
                  dosenSubTab === "cases"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                <Award className="w-4 h-4 mr-1.5" />
                <span>🎯 Editor & Diferensiasi Kasus Masalah</span>
              </button>
              <button
                onClick={() => {
                  setBrandingForm(branding);
                  setDosenSubTab("branding");
                }}
                className={`pb-3 flex items-center border-b-2 transition whitespace-nowrap ${
                  dosenSubTab === "branding"
                    ? "border-indigo-600 text-indigo-600"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                <Settings className="w-4 h-4 mr-1.5" />
                <span>🎨 Kustomisasi Branding & Identitas Kampus</span>
              </button>
              <button
                onClick={() => {
                  fetchUsers();
                  setDosenSubTab("users");
                }}
                className={`pb-3 flex items-center border-b-2 transition whitespace-nowrap ${
                  dosenSubTab === "users"
                    ? "border-indigo-600 text-indigo-600 font-bold"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                <KeyRound className="w-4 h-4 mr-1.5 text-indigo-500" />
                <span>🔐 Manajemen Akun & Password</span>
                <span className="ml-2 bg-indigo-50 text-indigo-700 text-[10px] px-2 py-0.5 rounded-full font-bold border border-indigo-200/60">
                  {usersList.length || 13} User
                </span>
              </button>
            </div>

            {/* TAB 1: SLIDERS & PARAMETRIC CONTROL */}
            {dosenSubTab === "sliders" && (
              <>
                <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 flex items-center">
                      <Sliders className="w-4 h-4 mr-2 text-indigo-600" /> Konsol Dosen: Parameter Simulasi & Disrupsi Makro
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Ubah parameter risiko secara real-time untuk menguji kemampuan resiliensi dan pengambilan keputusan manajerial mahasiswa.
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button onClick={() => applyPreset("tutorial")} className="text-xs px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium">
                      Preset Tutorial
                    </button>
                    <button onClick={() => applyPreset("supply_shock")} className="text-xs px-2.5 py-1 rounded bg-amber-100 hover:bg-amber-200 text-amber-800 font-semibold">
                      Krisis Suplai
                    </button>
                    <button onClick={() => applyPreset("labor_strike")} className="text-xs px-2.5 py-1 rounded bg-red-100 hover:bg-red-200 text-red-800 font-semibold">
                      Mogok Kerja
                    </button>
                    <button onClick={() => applyPreset("chaos")} className="text-xs px-2.5 py-1 rounded bg-purple-100 hover:bg-purple-200 text-purple-800 font-semibold">
                      Chaos Mode
                    </button>
                    <button
                      onClick={handleTriggerBlackSwan}
                      className="text-xs px-3 py-1 rounded bg-amber-600 hover:bg-amber-500 text-white font-bold flex items-center shadow-sm transition"
                      title="Picu Kejutan Finansial Mendadak (Black Swan) untuk Menguji Kelompok Ini"
                    >
                      <Flame className="w-3.5 h-3.5 mr-1" /> Picu Black Swan
                    </button>
                  </div>
                </div>

            {/* Sliders Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { key: "supply_disruption", label: "Disrupsi Rantai Pasok (Supply Chain)", icon: ShoppingBag },
                { key: "machine_breakdown_risk", label: "Risiko Kerusakan Mesin SMT", icon: Factory },
                { key: "market_volatility", label: "Volatilitas Permintaan Pasar", icon: TrendingUp },
                { key: "labor_strike_risk", label: "Tekanan Mogok Serikat Buruh", icon: Users },
                { key: "bad_debt_risk", label: "Risiko Gagal Bayar Piutang (Bad Debt)", icon: DollarSign },
                { key: "competitor_price_war", label: "Perang Harga Kompetitor", icon: ShieldAlert }
              ].map(s => {
                const Icon = s.icon;
                const val = sliders[s.key] || 0;
                return (
                  <div key={s.key} className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold text-slate-800 flex items-center">
                        <Icon className="w-3.5 h-3.5 mr-1.5 text-slate-500" /> {s.label}
                      </span>
                      <span className="font-mono font-bold text-indigo-600">{val}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={val}
                      onChange={(e) => setSliders({ ...sliders, [s.key]: parseFloat(e.target.value) })}
                      onMouseUp={() => handleUpdateSliders(sliders)}
                      onTouchEnd={() => handleUpdateSliders(sliders)}
                      className="w-full accent-indigo-600"
                    />
                  </div>
                );
              })}
            </div>

            {/* Live Class Leaderboard with Discipline Metric Filter */}
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-200 bg-slate-50/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center">
                    <Award className="w-4 h-4 mr-1.5 text-amber-500" />
                    Papan Peringkat Tim Mahasiswa (Live Leaderboard)
                  </h4>
                  <span className="text-[11px] text-slate-500">Kelas: {sessions.find(s => s.id === selectedSessionId)?.name || "Kelas FEB A"}</span>
                </div>
                
                {/* Discipline Filter Pills */}
                <div className="flex flex-wrap items-center gap-1.5">
                  {[
                    { id: "all", label: "Semua Metrik", color: "bg-indigo-600 text-white" },
                    { id: "marketing", label: "🎯 Fokus Pemasaran (CSAT)", color: "bg-blue-600 text-white" },
                    { id: "finance", label: "💰 Fokus Keuangan (Kas/Laba)", color: "bg-emerald-600 text-white" },
                    { id: "hr", label: "👥 Fokus SDM (Moral)", color: "bg-teal-600 text-white" },
                  ].map(f => (
                    <button
                      key={f.id}
                      type="button"
                      onClick={() => setLecturerDiscipline(f.id as any)}
                      className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition ${
                        lecturerDiscipline === f.id
                          ? f.color
                          : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
                      }`}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-xs">
                  <thead className="bg-slate-50 text-slate-500 font-semibold">
                    <tr>
                      <th className="px-3 py-2 text-center">Rank</th>
                      <th className="px-3 py-2 text-left">Nama Kelompok Mahasiswa</th>
                      <th className="px-3 py-2 text-right">Saldo Kas</th>
                      <th className="px-3 py-2 text-right">Laba Bersih</th>
                      <th className="px-3 py-2 text-center">CSAT</th>
                      <th className="px-3 py-2 text-center">Moral</th>
                      <th className="px-3 py-2 text-center">Total Skor</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {leaderboard.map(lb => (
                      <tr key={lb.rank} className={lb.rank === 1 ? "bg-amber-50/40" : ""}>
                        <td className="px-3 py-2.5 text-center font-bold font-mono">#{lb.rank}</td>
                        <td className="px-3 py-2.5 font-bold text-slate-900">{lb.name}</td>
                        <td className="px-3 py-2.5 text-right font-mono">Rp {lb.cash.toLocaleString("id-ID")}</td>
                        <td className="px-3 py-2.5 text-right font-mono font-bold text-emerald-700">+Rp {lb.net_profit.toLocaleString("id-ID")}</td>
                        <td className="px-3 py-2.5 text-center font-mono">{lb.csat_score}%</td>
                        <td className="px-3 py-2.5 text-center font-mono">{lb.worker_morale}%</td>
                        <td className="px-3 py-2.5 text-center font-mono font-extrabold text-indigo-700 text-sm">
                          {lb.overall_score} pts
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}

        {/* TAB 2: MULTI-TENANT & CLASS SESSION ADMINISTRATION */}
        {dosenSubTab === "tenants" && (
          <div className="space-y-6">
            {/* Master Sesi Kelas Perkuliahan & Kolaborasi Tim Dosen Pengampu */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden space-y-4 p-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3.5">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="bg-indigo-600 text-white font-extrabold text-[10px] px-2 py-0.5 rounded uppercase tracking-wider">
                      Multi-Class & Team Teaching
                    </span>
                    <span className="text-xs text-slate-500 font-mono">Total {sessions.length} Sesi Kelas Perkuliahan</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mt-1 flex items-center">
                    <GraduationCap className="w-5 h-5 mr-2 text-indigo-600" />
                    Daftar Master Sesi Kelas & Kolaborasi Tim Dosen FEB
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Setiap kelas dapat diajar bersama oleh tim dosen multidisiplin (Pemasaran, SDM, Keuangan, Manufaktur) dengan isolasi data kelompok dan rotasi masalah mandiri.
                  </p>
                </div>
                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    type="button"
                    onClick={handleOpenAddSession}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-sm transition flex items-center space-x-1.5"
                  >
                    <Plus className="w-4 h-4" />
                    <span>+ Buat Sesi Kelas Baru</span>
                  </button>
                </div>
              </div>

              {/* Grid of Class Sessions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {sessions.map((s) => {
                  const isCurrent = s.id === selectedSessionId;
                  const teamMembers = s.team_lecturers || [];
                  return (
                    <div
                      key={s.id}
                      className={`rounded-xl border p-4 transition flex flex-col justify-between ${
                        isCurrent
                          ? "bg-indigo-50/40 border-indigo-300 ring-2 ring-indigo-500/30 shadow-md"
                          : "bg-slate-50/60 border-slate-200 hover:border-slate-300"
                      }`}
                    >
                      <div className="space-y-3">
                        {/* Header: Status, Code, Title */}
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-1">
                            <div className="flex items-center space-x-2">
                              <span className="font-mono font-bold text-xs bg-slate-900 text-white px-2 py-0.5 rounded">
                                {s.code}
                              </span>
                              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                s.status === "archived"
                                  ? "bg-amber-100 text-amber-800"
                                  : "bg-emerald-100 text-emerald-800"
                              }`}>
                                {s.status === "archived" ? "Diarsipkan" : "Aktif"}
                              </span>
                              <span className="text-[10px] text-slate-500 font-medium">
                                {s.company_count || 0} Kelompok
                              </span>
                            </div>
                            <h4 className="font-bold text-sm text-slate-900">{s.name}</h4>
                          </div>

                          {isCurrent && (
                            <span className="bg-indigo-600 text-white text-[10px] font-extrabold px-2.5 py-1 rounded-full shrink-0 shadow-sm flex items-center space-x-1">
                              <Check className="w-3 h-3" />
                              <span>Kelas Aktif</span>
                            </span>
                          )}
                        </div>

                        {/* Metadata badges */}
                        <div className="flex flex-wrap gap-1.5 text-[11px] text-slate-600">
                          <span className="bg-white border border-slate-200 px-2 py-0.5 rounded text-slate-700 font-medium">
                            🏛️ {s.department || "S1 Manajemen & Bisnis Digital FEB"}
                          </span>
                          <span className="bg-white border border-slate-200 px-2 py-0.5 rounded text-slate-700 font-medium">
                            📅 {s.academic_term || "Semester Ganjil 2026/2027"}
                          </span>
                        </div>

                        {/* Team Dosen Pengampu List */}
                        <div className="bg-white rounded-lg border border-slate-200/80 p-3 space-y-2">
                          <div className="text-[11px] font-bold text-slate-700 flex items-center justify-between">
                            <span className="flex items-center space-x-1.5">
                              <Users className="w-3.5 h-3.5 text-indigo-600" />
                              <span>Tim Dosen Pengampu ({teamMembers.length} Dosen):</span>
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {teamMembers.length > 0 ? (
                              teamMembers.map((tm: any, idx: number) => {
                                const isCoord = tm.is_primary || tm.role_title?.toLowerCase().includes("koordinator") || tm.role_title?.toLowerCase().includes("utama");
                                const isMkt = tm.role_title?.toLowerCase().includes("pemasaran") || tm.role_title?.toLowerCase().includes("mkt");
                                const isSdm = tm.role_title?.toLowerCase().includes("sdm") || tm.role_title?.toLowerCase().includes("hr");
                                const isFin = tm.role_title?.toLowerCase().includes("keuangan") || tm.role_title?.toLowerCase().includes("akuntansi");

                                const colorClass = isCoord
                                  ? "bg-amber-50 text-amber-900 border-amber-200"
                                  : isMkt
                                  ? "bg-blue-50 text-blue-900 border-blue-200"
                                  : isSdm
                                  ? "bg-teal-50 text-teal-900 border-teal-200"
                                  : isFin
                                  ? "bg-emerald-50 text-emerald-900 border-emerald-200"
                                  : "bg-slate-50 text-slate-800 border-slate-200";

                                return (
                                  <div
                                    key={idx}
                                    className={`text-[10px] px-2 py-1 rounded-md border flex items-center space-x-1 font-medium ${colorClass}`}
                                    title={tm.email}
                                  >
                                    <span>👤 <strong>{tm.full_name}</strong></span>
                                    <span className="text-[9px] opacity-75 font-normal">({tm.role_title})</span>
                                  </div>
                                );
                              })
                            ) : (
                              <span className="text-xs text-slate-500 italic">
                                {s.lecturer_name || "Tim Dosen FEB"}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="mt-4 pt-3 border-t border-slate-200/80 flex items-center justify-between gap-2">
                        <div>
                          {!isCurrent ? (
                            <button
                              type="button"
                              onClick={() => handleSelectSession(s.id)}
                              className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold px-3 py-1.5 rounded-md shadow-sm transition flex items-center space-x-1"
                            >
                              <span>Pilih & Kelola Kelas Ini</span>
                              <ChevronRight className="w-3.5 h-3.5" />
                            </button>
                          ) : (
                            <span className="text-xs font-bold text-emerald-700 flex items-center space-x-1">
                              <Check className="w-4 h-4 text-emerald-600" />
                              <span>Sedang Dikelola di Konsol</span>
                            </span>
                          )}
                        </div>

                        <div className="flex items-center space-x-1.5">
                          <button
                            type="button"
                            onClick={() => handleOpenEditSession(s)}
                            className="text-xs text-slate-600 hover:text-indigo-700 bg-white hover:bg-slate-100 border border-slate-200 px-2.5 py-1.5 rounded-md transition font-medium flex items-center space-x-1 shadow-sm"
                            title="Edit data kelas dan susunan tim dosen"
                          >
                            <Edit3 className="w-3.5 h-3.5 text-slate-500" />
                            <span>Edit / Tim Dosen</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => handleOpenCloneSession(s)}
                            className="text-xs text-slate-600 hover:text-indigo-700 bg-white hover:bg-slate-100 border border-slate-200 px-2.5 py-1.5 rounded-md transition font-medium flex items-center space-x-1 shadow-sm"
                            title="Duplikasi struktur kelas ini ke kelas baru"
                          >
                            <Copy className="w-3.5 h-3.5 text-slate-500" />
                            <span>Clone</span>
                          </button>
                          {sessions.length > 1 && (
                            <button
                              type="button"
                              onClick={() => handleDeleteSession(s)}
                              className="text-xs text-rose-600 hover:text-rose-800 bg-white hover:bg-rose-50 border border-rose-200 px-2 py-1.5 rounded-md transition font-medium shadow-sm"
                              title="Hapus sesi kelas ini"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Batch Multi-Tenant Generator Card (Sliders for Group Count & Initial Capital) */}
            <div className="bg-gradient-to-br from-slate-900 via-[#0f172a] to-slate-900 text-white p-6 rounded-xl border border-indigo-500/30 shadow-xl space-y-5">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-700/60 pb-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="bg-indigo-600 text-white font-extrabold text-[10px] px-2.5 py-0.5 rounded uppercase tracking-wider shadow">
                      Batch Generator Engine
                    </span>
                    <span className="text-indigo-300 text-xs font-mono">Automated Multi-Tenant Provisioner</span>
                  </div>
                  <h3 className="text-base sm:text-lg font-bold text-white mt-1 flex items-center">
                    <Sliders className="w-5 h-5 mr-2 text-indigo-400" />
                    Generator Kelompok & Neraca Awal Praktikum (Slider-Based)
                  </h3>
                  <p className="text-xs text-slate-300 mt-0.5">
                    Buat hingga 12 kelompok perusahaan sekaligus, tentukan pagu modal awal kas, dan aktifkan diferensiasi masalah kasus agar tiap kelompok menghadapi tantangan yang berbeda.
                  </p>
                </div>
                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={handleBatchGenerateTenants}
                    disabled={batchLoading}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow-lg shadow-emerald-900/40 transition flex items-center space-x-2 disabled:opacity-60"
                  >
                    {batchLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Memproses Provisioning...</span>
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4" />
                        <span>Eksekusi Buat & Sinkronkan {batchGroupCount} Kelompok</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Sliders Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-1">
                {/* Slider 1: Group Count */}
                <div className="bg-slate-950/70 p-4 rounded-lg border border-slate-800 space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-200 flex items-center">
                      <Users className="w-4 h-4 mr-2 text-indigo-400" />
                      Jumlah Kelompok Praktikan:
                    </span>
                    <span className="font-mono font-extrabold text-sm text-indigo-400 bg-indigo-950/80 px-2.5 py-1 rounded border border-indigo-500/30">
                      {batchGroupCount} Kelompok
                    </span>
                  </div>
                  <input
                    type="range"
                    min="2"
                    max="12"
                    step="1"
                    value={batchGroupCount}
                    onChange={(e) => setBatchGroupCount(parseInt(e.target.value))}
                    className="w-full accent-indigo-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>Min: 2 Kelompok</span>
                    <span>Default: 4 Kelompok</span>
                    <span>Max: 12 Kelompok</span>
                  </div>
                  {/* Visual Preview of Groups */}
                  <div className="pt-2 flex flex-wrap gap-1.5">
                    {Array.from({ length: batchGroupCount }).map((_, idx) => (
                      <span key={idx} className="text-[10px] font-mono bg-indigo-600/30 text-indigo-200 px-2 py-0.5 rounded border border-indigo-500/20">
                        K-{idx + 1}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Slider 2: Initial Capital */}
                <div className="bg-slate-950/70 p-4 rounded-lg border border-slate-800 space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-200 flex items-center">
                      <DollarSign className="w-4 h-4 mr-2 text-emerald-400" />
                      Modal Awal Kas Tiap Perusahaan:
                    </span>
                    <span className="font-mono font-extrabold text-sm text-emerald-400 bg-emerald-950/80 px-2.5 py-1 rounded border border-emerald-500/30">
                      Rp {batchInitialCapital.toLocaleString("id-ID")}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="100000000"
                    max="2000000000"
                    step="50000000"
                    value={batchInitialCapital}
                    onChange={(e) => setBatchInitialCapital(parseFloat(e.target.value))}
                    className="w-full accent-emerald-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>Rp 100 Juta (Ketat)</span>
                    <span>Rp 500 Juta (Standar)</span>
                    <span>Rp 2 Miliar (Ekspansi)</span>
                  </div>
                  {/* Quick Preset Buttons */}
                  <div className="pt-1 flex space-x-2">
                    {[
                      { label: "Rp 250 Jt", val: 250000000 },
                      { label: "Rp 500 Jt", val: 500000000 },
                      { label: "Rp 750 Jt", val: 750000000 },
                      { label: "Rp 1 Miliar", val: 1000000000 }
                    ].map(p => (
                      <button
                        key={p.val}
                        type="button"
                        onClick={() => setBatchInitialCapital(p.val)}
                        className={`text-[10px] px-2 py-0.5 rounded font-mono transition ${
                          batchInitialCapital === p.val
                            ? "bg-emerald-600 text-white font-bold"
                            : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Differentiation Option Banner */}
              <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <label className="flex items-center space-x-3 cursor-pointer text-xs">
                  <input
                    type="checkbox"
                    checked={batchDifferentiate}
                    onChange={(e) => setBatchDifferentiate(e.target.checked)}
                    className="w-4 h-4 accent-indigo-600 rounded cursor-pointer"
                  />
                  <div>
                    <span className="font-bold text-white">
                      Aktifkan Diferensiasi Skenario Masalah Otomatis
                    </span>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Tiap kelompok otomatis diberikan paket kasus unik (Krisis Suplier, Retur Mutu VIP, Mogok Serikat, Gagal Bayar Piutang, Kerusakan Mesin SMT, dll) sehingga tidak dapat saling meniru solusi.
                    </p>
                  </div>
                </label>
                <div className="text-right shrink-0">
                  <span className="text-[10px] font-mono text-indigo-400 bg-indigo-950/60 px-2 py-1 rounded border border-indigo-500/30">
                    {batchDifferentiate ? "✓ Skenario Berbeda Aktif" : "Skenario Seragam"}
                  </span>
                </div>
              </div>
            </div>

            {/* Tenant Companies Master Grid */}
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-200 bg-slate-50/80 flex flex-col md:flex-row md:items-center justify-between gap-2">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                    Daftar Tenant Perusahaan Mahasiswa (Isolated DB Sandboxes)
                  </h4>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Tiap kelompok memiliki database transaksi, COA, Vendor, BOM, dan evaluasi misi mandiri.
                  </p>
                </div>
                <span className="text-xs font-semibold text-slate-600">
                  Total: {companies.length} Kelompok Terdaftar
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-xs">
                  <thead className="bg-slate-50 text-slate-600 font-semibold">
                    <tr>
                      <th className="px-3.5 py-3 text-left">Kelompok & Entitas Perusahaan</th>
                      <th className="px-3.5 py-3 text-left">Sektor Industri</th>
                      <th className="px-3.5 py-3 text-right">Saldo Kas</th>
                      <th className="px-3.5 py-3 text-right">Laba Bersih</th>
                      <th className="px-3.5 py-3 text-center">CSAT</th>
                      <th className="px-3.5 py-3 text-center">Moral</th>
                      <th className="px-3.5 py-3 text-center">Skor Evaluasi</th>
                      <th className="px-3.5 py-3 text-center">Misi Aktif</th>
                      <th className="px-3.5 py-3 text-center">Aksi Manajemen</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {companies.map((c) => (
                      <tr key={c.id} className={c.id === companyId ? "bg-indigo-50/40" : "hover:bg-slate-50"}>
                        <td className="px-3.5 py-3">
                          <div className="font-bold text-slate-900 flex items-center">
                            {c.name}
                            {c.id === companyId && (
                              <span className="ml-2 bg-indigo-600 text-white text-[10px] px-1.5 py-0.5 rounded font-normal">
                                Aktif
                              </span>
                            )}
                          </div>
                          <div className="text-[11px] text-indigo-600 font-medium">{c.group_label}</div>
                        </td>
                        <td className="px-3.5 py-3 text-slate-600">{c.industry}</td>
                        <td className="px-3.5 py-3 text-right font-mono font-bold text-slate-800">
                          Rp {(c.current_cash || 500000000).toLocaleString("id-ID")}
                        </td>
                        <td className="px-3.5 py-3 text-right font-mono font-bold text-emerald-600">
                          +Rp {(c.net_profit || 20000000).toLocaleString("id-ID")}
                        </td>
                        <td className="px-3.5 py-3 text-center font-mono">{c.csat_score || 88.5}%</td>
                        <td className="px-3.5 py-3 text-center font-mono">{c.worker_morale || 90.0}%</td>
                        <td className="px-3.5 py-3 text-center font-mono font-bold text-indigo-700 text-sm">
                          {c.overall_score !== undefined ? c.overall_score : 0.0} pts
                        </td>
                        <td className="px-3.5 py-3 text-center">
                          <span className="text-[10px] bg-slate-100 border border-slate-200 px-2 py-0.5 rounded font-medium text-slate-700 truncate max-w-[140px] inline-block">
                            {c.active_case_title || "Misi 1: Evaluasi Vendor"}
                          </span>
                        </td>
                        <td className="px-3.5 py-3 text-center">
                          <div className="flex items-center justify-center space-x-1.5">
                            <button
                              onClick={() => {
                                setCompanyId(c.id);
                                setActivePortal("erp");
                                showNotification(`Beralih ke ERP dari sudut pandang ${c.name}`);
                              }}
                              title="Beralih ke lingkungan ERP kelompok ini"
                              className="px-2 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded font-semibold text-[11px] transition"
                            >
                              Beralih
                            </button>
                            <button
                              onClick={() => handleResetCompany(c.id)}
                              title="Reset data transaksi kelompok ke kondisi awal"
                              className="px-2 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 rounded font-semibold text-[11px] transition"
                            >
                              Reset
                            </button>
                            <button
                              onClick={() => handleDeleteCompany(c.id)}
                              title="Hapus tenant ini"
                              className="px-2 py-1 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded font-semibold text-[11px] transition"
                            >
                              Hapus
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Multi-Tenant Cross-Group Benchmark Summary */}
            <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                Benchmarking Multi-Tenant: Komparasi Kinerja Antar Kelompok
              </h4>
              <p className="text-xs text-slate-500 mb-4">
                Pantau disparitas performa likuiditas kas, kepuasan konsumen (CSAT), dan resiliensi serikat buruh secara komparatif.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {companies.map((c) => (
                  <div key={c.id} className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 text-xs">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className="font-bold text-slate-900 block">{c.name}</span>
                        <span className="text-[10px] text-indigo-600 font-semibold">{c.group_label}</span>
                      </div>
                      <span className="font-mono font-bold text-indigo-700 text-sm">{c.overall_score !== undefined ? c.overall_score : 0} pts</span>
                    </div>
                    <div className="space-y-1.5 pt-2 border-t border-slate-200 text-[11px]">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Saldo Kas:</span>
                        <span className="font-mono font-semibold">Rp {(c.current_cash ?? 500000000).toLocaleString("id-ID")}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">CSAT Pelanggan:</span>
                        <span className="font-mono font-semibold">{c.csat_score ?? 88}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Moral Karyawan:</span>
                        <span className="font-mono font-semibold">{c.worker_morale ?? 90}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: CASE SCENARIO EDITOR & DIFFERENTIAL PROBLEM ENGINE */}
        {dosenSubTab === "branding" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-indigo-900 to-slate-900 rounded-xl p-6 text-white border border-indigo-800 shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center space-x-2 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-1">
                  <Sparkles className="w-4 h-4" />
                  <span>White-Label & Custom Branding Engine</span>
                </div>
                <h2 className="text-2xl font-black">Kustomisasi Branding & Identitas Kampus</h2>
                <p className="text-slate-300 text-xs mt-1 max-w-2xl leading-relaxed">
                  Bebas atur dan ubah nama sistem, fakultas, jurusan, nama dosen pengampu, gelar, peran, dan teks footer secara dinamis. Seluruh teks akan tersimpan ke database dan otomatis langsung berlaku di layar login maupun dasbor mahasiswa.
                </p>
              </div>
              <div className="flex items-center space-x-3 shrink-0">
                <button
                  type="button"
                  onClick={handleResetBranding}
                  disabled={isSavingBranding}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold px-4 py-2.5 rounded-lg transition flex items-center space-x-1.5 shadow-sm"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Reset Default</span>
                </button>
                <button
                  type="button"
                  onClick={handleSaveBranding}
                  disabled={isSavingBranding}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-5 py-2.5 rounded-lg transition flex items-center space-x-2 shadow-lg shadow-indigo-600/30"
                >
                  {isSavingBranding ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                  <span>{isSavingBranding ? "Menyimpan..." : "Simpan Perubahan"}</span>
                </button>
              </div>
            </div>

            {/* Live Form & Preview */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Column: Form Settings */}
              <div className="lg:col-span-7 bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                <h3 className="font-bold text-slate-800 text-sm flex items-center space-x-2 border-b border-slate-100 pb-3">
                  <Settings className="w-4 h-4 text-indigo-600" />
                  <span>Parameter Identitas & Institusi</span>
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Nama Aplikasi / Judul Platform (App Title)
                    </label>
                    <input
                      type="text"
                      value={brandingForm.app_title}
                      onChange={(e) => setBrandingForm({ ...brandingForm, app_title: e.target.value })}
                      className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      placeholder="Contoh: VLab-ERP Enterprise Edition"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Nama Jurusan / Fakultas / Institusi Pendidikan
                    </label>
                    <input
                      type="text"
                      value={brandingForm.department_name}
                      onChange={(e) => setBrandingForm({ ...brandingForm, department_name: e.target.value })}
                      className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      placeholder="Contoh: Fakultas Ekonomi dan Bisnis (FEB) • Manajemen Bisnis & Akuntansi"
                    />
                  </div>

                  {/* 3 Discipline Lecturers FEB */}
                  <div className="sm:col-span-2 pt-2 border-t border-slate-100">
                    <div className="flex items-center space-x-1.5 text-xs font-bold text-indigo-900 mb-3">
                      <Users className="w-4 h-4 text-indigo-600" />
                      <span>Profil 3 Dosen Rumpun Ilmu Khusus FEB (Team Teaching):</span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <div className="bg-blue-50/60 p-3 rounded-lg border border-blue-200/80">
                        <label className="block text-[11px] font-bold text-blue-900 mb-1">
                          🎯 Dosen Pemasaran & CRM
                        </label>
                        <input
                          type="text"
                          value={brandingForm.lecturer_marketing_name || ""}
                          onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_marketing_name: e.target.value })}
                          className="w-full text-xs px-2.5 py-1.5 bg-white border border-blue-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
                          placeholder="Dr. Maya Indah, S.E., M.M."
                        />
                        <span className="text-[10px] text-blue-600 mt-1 block">Rumpun Pemasaran & Retur VIP</span>
                      </div>

                      <div className="bg-teal-50/60 p-3 rounded-lg border border-teal-200/80">
                        <label className="block text-[11px] font-bold text-teal-900 mb-1">
                          👥 Dosen SDM & Organisasi
                        </label>
                        <input
                          type="text"
                          value={brandingForm.lecturer_hr_name || ""}
                          onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_hr_name: e.target.value })}
                          className="w-full text-xs px-2.5 py-1.5 bg-white border border-teal-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:outline-none"
                          placeholder="Drs. Bambang Prakoso, M.Psi."
                        />
                        <span className="text-[10px] text-teal-600 mt-1 block">Rumpun SDM & Serikat Buruh</span>
                      </div>

                      <div className="bg-emerald-50/60 p-3 rounded-lg border border-emerald-200/80">
                        <label className="block text-[11px] font-bold text-emerald-900 mb-1">
                          💰 Dosen Keuangan & Akuntansi
                        </label>
                        <input
                          type="text"
                          value={brandingForm.lecturer_finance_name || ""}
                          onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_finance_name: e.target.value })}
                          className="w-full text-xs px-2.5 py-1.5 bg-white border border-emerald-300 rounded-md focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                          placeholder="Dr. Ir. Budi Santoso, Ak."
                        />
                        <span className="text-[10px] text-emerald-600 mt-1 block">Rumpun Kas & Piutang Macet</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-100">
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Nama Koordinator Tim / Dosen Utama
                    </label>
                    <input
                      type="text"
                      value={brandingForm.lecturer_name}
                      onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_name: e.target.value })}
                      className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      placeholder="Contoh: Tim Dosen Pengampu FEB"
                    />
                  </div>

                  <div className="pt-2 border-t border-slate-100">
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Label Jabatan / Peran Pengampu
                    </label>
                    <input
                      type="text"
                      value={brandingForm.lecturer_role_label}
                      onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_role_label: e.target.value })}
                      className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      placeholder="Contoh: Tim Pengampu FEB"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Badge Supervisi / Sub-teks
                    </label>
                    <input
                      type="text"
                      value={brandingForm.supervision_badge}
                      onChange={(e) => setBrandingForm({ ...brandingForm, supervision_badge: e.target.value })}
                      className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      placeholder="Contoh: Supervisi & Skenario"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Semester / Periode Akademik
                    </label>
                    <input
                      type="text"
                      value={brandingForm.academic_term}
                      onChange={(e) => setBrandingForm({ ...brandingForm, academic_term: e.target.value })}
                      className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      placeholder="Contoh: Semester Ganjil 2026/2027"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Sub-judul / Tagline Portal Akses
                    </label>
                    <input
                      type="text"
                      value={brandingForm.portal_subtitle}
                      onChange={(e) => setBrandingForm({ ...brandingForm, portal_subtitle: e.target.value })}
                      className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      placeholder="Contoh: Simulasi Bisnis & Praktikum Enterprise Resource Planning Terintegrasi"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Teks Footer Sistem (Hak Cipta / Informasi Server)
                    </label>
                    <textarea
                      rows={2}
                      value={brandingForm.footer_text}
                      onChange={(e) => setBrandingForm({ ...brandingForm, footer_text: e.target.value })}
                      className="w-full text-xs px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                      placeholder="Teks footer di bagian bawah layar"
                    />
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-end space-x-3">
                  <button
                    type="button"
                    onClick={handleResetBranding}
                    className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 border border-slate-300 rounded-lg hover:bg-slate-50 transition"
                  >
                    Reset Bawaan
                  </button>
                  <button
                    type="button"
                    onClick={handleSaveBranding}
                    disabled={isSavingBranding}
                    className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition shadow-sm flex items-center space-x-1.5"
                  >
                    {isSavingBranding ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                    <span>Terapkan Branding</span>
                  </button>
                </div>
              </div>

              {/* Right Column: Live Visual Preview */}
              <div className="lg:col-span-5 space-y-4">
                <div className="bg-slate-900 text-white p-5 rounded-xl border border-slate-800 shadow-sm space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-400 flex items-center">
                      <Eye className="w-3.5 h-3.5 mr-1" />
                      Live Preview di Layar Login
                    </span>
                    <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded">Preview</span>
                  </div>

                  {/* Header preview */}
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                    <div className="text-xs font-bold text-white flex items-center space-x-1.5">
                      <span>{brandingForm.app_title || "VLab-ERP Enterprise"}</span>
                      <span className="text-[9px] bg-indigo-500/20 text-indigo-300 px-1.5 py-0.2 rounded border border-indigo-500/30">
                        {brandingForm.academic_term}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {brandingForm.portal_subtitle} • <strong className="text-indigo-300">{brandingForm.department_name}</strong>
                    </div>
                  </div>

                  {/* Card quick demo preview */}
                  <div className="bg-slate-800/80 p-3 rounded-lg border border-amber-500/30">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{brandingForm.lecturer_role_label || "Dosen Pengampu"}</span>
                      <span className="text-[10px] font-semibold text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full">
                        {brandingForm.supervision_badge || "Supervisi & Skenario"}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-amber-300 mt-1">
                      {brandingForm.lecturer_name || "Dr. Ir. Hendra Gunawan, M.T."}
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5 font-mono">
                      Username: dosen • Password: dosen123
                    </div>
                  </div>

                  {/* Footer preview */}
                  <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-center">
                    <span className="text-[10px] text-slate-400">
                      {brandingForm.footer_text || "VLab-ERP Enterprise Edition"}
                    </span>
                  </div>
                </div>

                <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl text-emerald-900 text-xs space-y-1.5">
                  <div className="font-bold flex items-center space-x-1 text-emerald-800">
                    <Check className="w-4 h-4 text-emerald-600" />
                    <span>Kebebasan Penuh (Full Freedom White-Label)</span>
                  </div>
                  <p className="text-emerald-700 leading-relaxed text-[11px]">
                    Anda bebas mengganti nama universitas, nama prodi, maupun nama dosen pengampu kapan saja tanpa harus restart server atau mengubah source code. Sistem menyimpannya secara persisten ke database backend.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {dosenSubTab === "cases" && (
          <div className="space-y-6">
            {/* Header & Target Company Selector Bar */}
            <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="bg-amber-600 text-white font-extrabold text-[10px] px-2.5 py-0.5 rounded uppercase tracking-wider shadow">
                    Problem-Based Learning Lab
                  </span>
                  <span className="text-amber-800 text-xs font-mono">Differential Case Injection</span>
                </div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900 mt-1 flex items-center">
                  <Award className="w-5 h-5 mr-2 text-amber-600" />
                  Editor & Diferensiasi Kasus Masalah Perusahaan
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Pilih entitas kelompok untuk memeriksa, mengedit, atau menyuntikkan skenario tantangan bisnis khusus agar tiap kelompok tidak saling mencontek.
                </p>
              </div>

              {/* Target Company Selector & Action Buttons */}
              <div className="flex flex-wrap items-center gap-2">
                <div className="flex items-center space-x-1.5 bg-slate-100 px-3 py-1.5 rounded-md border border-slate-200 text-xs">
                  <Building2 className="w-4 h-4 text-indigo-600 shrink-0" />
                  <span className="text-slate-600 font-medium">Pilih Tenant:</span>
                  <select
                    value={selectedCompanyForCases}
                    onChange={(e) => setSelectedCompanyForCases(parseInt(e.target.value))}
                    className="bg-white border border-slate-300 font-bold text-slate-800 rounded px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  >
                    {companies.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} ({c.group_label})
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={() => handleRandomizeSingleCompanyCases(selectedCompanyForCases)}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3 py-2 rounded-md shadow-sm transition flex items-center space-x-1"
                  title="Acak paket skenario masalah unik untuk perusahaan ini"
                >
                  <RotateCcw className="w-3.5 h-3.5 mr-1 text-amber-400" />
                  <span>Acak Kasus Kelompok Ini</span>
                </button>

                <button
                  onClick={() => handleResetCompanyMissions(selectedCompanyForCases)}
                  className="bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold px-3 py-2 rounded-md shadow-sm transition flex items-center space-x-1"
                  title="Kosongkan jawaban & skor tersimpan kelompok ini agar mahasiswa dapat memecahkan masalah dari awal"
                >
                  <RotateCcw className="w-3.5 h-3.5 mr-1 text-white" />
                  <span>Reset Jawaban Kelompok Ini</span>
                </button>

                <button
                  onClick={handleResetAllCompaniesMissions}
                  className="bg-rose-700 hover:bg-rose-600 text-white text-xs font-bold px-3 py-2 rounded-md shadow-sm transition flex items-center space-x-1"
                  title="Reset seluruh status misi untuk SEMUA kelompok mahasiswa ke kondisi awal"
                >
                  <RotateCcw className="w-3.5 h-3.5 mr-1 text-white" />
                  <span>Reset Misi Semua Kelompok</span>
                </button>

                <button
                  onClick={() => setShowAddCustomCaseModal(true)}
                  className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-2 rounded-md shadow-sm transition flex items-center space-x-1"
                >
                  <Plus className="w-3.5 h-3.5 mr-1" />
                  <span>Buat Kasus Kustom</span>
                </button>
              </div>
            </div>

            {/* Quick 1-Click Problem Injector Shelf */}
            <div className="bg-slate-900 text-white p-4 rounded-xl border border-slate-800 shadow-md space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center">
                  <Zap className="w-4 h-4 mr-1.5 text-amber-400" />
                  Pustaka Masalah Cepat (1-Klik Injeksi Kasus ke {companies.find(c => c.id === selectedCompanyForCases)?.group_label || "Kelompok Terpilih"}):
                </span>
                <span className="text-[10px] text-slate-400 font-mono">Klik untuk menyuntikkan masalah</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                {[
                  { type: "scm_defect", label: "Krisis Suplier Cacat", cat: "SCM", icon: ShoppingBag, color: "hover:border-indigo-500 hover:bg-indigo-950/40" },
                  { type: "crm_recall", label: "Skandal Retur VIP", cat: "CRM", icon: Briefcase, color: "hover:border-blue-500 hover:bg-blue-950/40" },
                  { type: "hr_strike", label: "Ancaman Mogok Buruh", cat: "HR", icon: Users, color: "hover:border-teal-500 hover:bg-teal-950/40" },
                  { type: "accounting_baddebt", label: "Piutang Macet Retail", cat: "Kas", icon: DollarSign, color: "hover:border-emerald-500 hover:bg-emerald-950/40" },
                  { type: "mrp_breakdown", label: "Breakdown Motor SMT", cat: "MRP", icon: Factory, color: "hover:border-purple-500 hover:bg-purple-950/40" },
                  { type: "price_war", label: "Perang Harga Global", cat: "Pasar", icon: TrendingUp, color: "hover:border-amber-500 hover:bg-amber-950/40" },
                ].map((preset) => {
                  const Icon = preset.icon;
                  return (
                    <button
                      key={preset.type}
                      type="button"
                      onClick={() => handleInjectQuickCase(preset.type)}
                      className={`text-left bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 transition text-xs group ${preset.color}`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <Icon className="w-3.5 h-3.5 text-slate-400 group-hover:text-white transition" />
                        <span className="text-[9px] font-mono bg-slate-800 text-slate-300 px-1 rounded">
                          {preset.cat}
                        </span>
                      </div>
                      <div className="font-bold text-slate-200 group-hover:text-white truncate">
                        {preset.label}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Active Problem Cases for Selected Company */}
            <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-200 bg-slate-50/80 flex justify-between items-center">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800 flex items-center">
                    <span>Kasus Masalah Aktif:</span>
                    <span className="ml-2 font-extrabold text-indigo-600">
                      {companies.find(c => c.id === selectedCompanyForCases)?.name || "Kelompok Terpilih"}
                    </span>
                    <span className="ml-2 bg-indigo-100 text-indigo-800 text-[10px] px-2 py-0.5 rounded font-mono">
                      {companyCases.length} Skenario
                    </span>
                  </h4>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Kasus-kasus di bawah adalah tantangan yang harus diselesaikan oleh kelompok ini di antarmuka ERP mereka.
                  </p>
                </div>
              </div>

              {companyCases.length === 0 ? (
                <div className="p-8 text-center text-slate-500 text-xs">
                  <HelpCircle className="w-8 h-8 mx-auto text-slate-400 mb-2" />
                  <p className="font-semibold text-slate-700">Belum ada skenario masalah untuk kelompok ini.</p>
                  <p className="mt-1">Gunakan Pustaka Masalah Cepat di atas atau klik "Acak Kasus Kelompok Ini".</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {companyCases.map((cs, idx) => (
                    <div key={cs.id} className="p-5 hover:bg-slate-50/70 transition space-y-3">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center space-x-2">
                          <span className="bg-slate-900 text-white font-mono text-[10px] font-bold px-2 py-0.5 rounded">
                            {cs.code || `CASE-0${idx + 1}`}
                          </span>
                          <span className="bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold text-[10px] px-2 py-0.5 rounded uppercase">
                            Tahap {cs.stage_order || idx + 1}
                          </span>
                          <span className="bg-amber-50 text-amber-800 border border-amber-200 font-semibold text-[10px] px-2 py-0.5 rounded uppercase">
                            Modul: {cs.category?.toUpperCase()}
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                            cs.status === "passed" ? "bg-emerald-100 text-emerald-800" :
                            cs.status === "active" ? "bg-blue-100 text-blue-800 animate-pulse" : "bg-slate-100 text-slate-600"
                          }`}>
                            Status: {cs.status?.toUpperCase() || "PENDING"}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleDeleteCase(cs.id)}
                            className="text-slate-400 hover:text-red-600 p-1 rounded hover:bg-red-50 text-xs flex items-center space-x-1"
                            title="Hapus Kasus dari Perusahaan Ini"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                            <span className="text-[11px]">Hapus</span>
                          </button>
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-bold text-slate-900">{cs.title}</h4>
                        <p className="text-xs text-slate-600 mt-1 leading-relaxed">{cs.description}</p>
                      </div>

                      {/* Details Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs">
                        <div>
                          <span className="font-bold text-slate-700 block mb-0.5 flex items-center">
                            <Zap className="w-3 h-3 mr-1 text-amber-500" /> Petunjuk Pemicu (Trigger Hint):
                          </span>
                          <p className="text-slate-600 text-[11px]">{cs.trigger_hint || "-"}</p>
                        </div>
                        <div>
                          <span className="font-bold text-slate-700 block mb-0.5 flex items-center">
                            <Sliders className="w-3 h-3 mr-1 text-indigo-500" /> Alur Penyelesaian SOP:
                          </span>
                          <p className="text-slate-600 text-[11px] whitespace-pre-line">{cs.solvable_workflow || "-"}</p>
                        </div>
                        <div>
                          <span className="font-bold text-slate-700 block mb-0.5 flex items-center">
                            <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-500" /> Kriteria Keberhasilan:
                          </span>
                          <p className="text-slate-600 text-[11px]">{cs.resolution_criteria || "-"}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* SUBTAB 5: MANAJEMEN PENGGUNA & PASSWORD (CRUD LENGKAP) */}
        {dosenSubTab === "users" && (
          <div className="space-y-6 animate-in fade-in duration-200">
            {/* Top Banner */}
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-900/50 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden">
              <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/10 via-transparent to-transparent pointer-events-none" />
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
                <div className="flex items-start space-x-4">
                  <div className="w-12 h-12 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300 shrink-0">
                    <KeyRound className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h2 className="text-xl font-black tracking-tight text-white">Manajemen Akun Pengguna & Password (CRUD)</h2>
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[11px] font-bold border border-emerald-500/30">
                        {usersList.length} Akun Aktif
                      </span>
                    </div>
                    <p className="text-slate-300 text-xs mt-1 max-w-2xl leading-relaxed">
                      Kelola hak akses, nama lengkap, username login, role, penugasan kelas perkuliahan, dan reset password mandiri/massal untuk seluruh civitas FEB.
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2 shrink-0">
                  <button
                    onClick={fetchUsers}
                    disabled={usersLoading}
                    className="px-3.5 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-1.5"
                    title="Muat ulang daftar pengguna"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${usersLoading ? "animate-spin text-indigo-400" : ""}`} />
                    <span>Segarkan</span>
                  </button>
                  <button
                    onClick={() => {
                      setNewUserForm({ username: "", full_name: "", email: "", role: "MAHASISWA", password: "", company_id: 0, session_id: 0 });
                      setShowCreateUserModal(true);
                    }}
                    className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition flex items-center space-x-2"
                  >
                    <Plus className="w-4 h-4" />
                    <span>+ Tambah Pengguna Baru</span>
                  </button>
                </div>
              </div>

              {/* Quick 4 Stats Grid */}
              <div className="mt-5 pt-4 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/50">
                  <div className="text-slate-400 text-[11px]">Total Pengguna</div>
                  <div className="text-xl font-black text-white mt-0.5">{usersList.length}</div>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/50">
                  <div className="text-slate-400 text-[11px]">Mahasiswa / Kelompok</div>
                  <div className="text-xl font-black text-emerald-400 mt-0.5">
                    {usersList.filter((u: any) => u.role === "MAHASISWA").length}
                  </div>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/50">
                  <div className="text-slate-400 text-[11px]">Dosen Pengampu FEB</div>
                  <div className="text-xl font-black text-indigo-400 mt-0.5">
                    {usersList.filter((u: any) => u.role === "DOSEN").length}
                  </div>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/50">
                  <div className="text-slate-400 text-[11px]">Administrator Sistem</div>
                  <div className="text-xl font-black text-purple-400 mt-0.5">
                    {usersList.filter((u: any) => u.role === "ADMIN").length}
                  </div>
                </div>
              </div>
            </div>

            {/* Filter & Search Bar */}
            <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold text-slate-500 flex items-center mr-1">
                  <Filter className="w-3.5 h-3.5 mr-1" /> Filter:
                </span>
                {[
                  { id: "ALL", label: "Semua Akun" },
                  { id: "ADMIN", label: "Admin", icon: ShieldAlert },
                  { id: "DOSEN", label: "Dosen / Pengajar", icon: GraduationCap },
                  { id: "MAHASISWA", label: "Mahasiswa / Kelompok", icon: Users }
                ].map(tab => {
                  const isActive = userRoleFilter === tab.id;
                  const count = tab.id === "ALL" 
                    ? usersList.length 
                    : usersList.filter((u: any) => u.role && u.role.toUpperCase() === tab.id).length;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setUserRoleFilter(tab.id)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition flex items-center space-x-1.5 ${
                        isActive
                          ? "bg-indigo-600 text-white shadow-sm"
                          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}
                    >
                      {tab.icon && <tab.icon className="w-3 h-3" />}
                      <span>{tab.label}</span>
                      <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                        isActive ? "bg-white/20 text-white" : "bg-slate-200 text-slate-700"
                      }`}>
                        {count}
                      </span>
                    </button>
                  );
                })}

                {/* Sesi Filter Dropdown */}
                <div className="flex items-center space-x-1 ml-2">
                  <BookOpen className="w-3.5 h-3.5 text-slate-400" />
                  <select
                    value={userSessionFilter}
                    onChange={(e) => setUserSessionFilter(e.target.value)}
                    className="text-xs bg-slate-100 border border-slate-300 rounded-lg px-2.5 py-1.5 text-slate-700 font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="ALL">Semua Sesi Kelas</option>
                    {sessions.map(s => (
                      <option key={s.id} value={s.id.toString()}>
                        {s.name} ({s.code})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="relative w-full lg:w-72">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Cari username, nama, atau tenant..."
                  value={userSearchTerm}
                  onChange={(e) => setUserSearchTerm(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition"
                />
              </div>
            </div>

            {/* Batch Actions Toolbar (if users selected) */}
            {selectedUserIds.length > 0 && (
              <div className="bg-amber-50 border border-amber-300 rounded-xl p-3 flex flex-col sm:flex-row items-center justify-between gap-3 animate-in fade-in">
                <div className="flex items-center space-x-2 text-xs text-amber-900 font-bold">
                  <KeyRound className="w-4 h-4 text-amber-600" />
                  <span>{selectedUserIds.length} akun pengguna dipilih</span>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleBatchResetPassword("mhs123")}
                    disabled={isSavingUser}
                    className="px-3 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold shadow-sm transition"
                  >
                    Reset ke &apos;mhs123&apos;
                  </button>
                  <button
                    onClick={() => handleBatchResetPassword("dosen123")}
                    disabled={isSavingUser}
                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm transition"
                  >
                    Reset ke &apos;dosen123&apos;
                  </button>
                  <button
                    onClick={() => setSelectedUserIds([])}
                    className="px-2.5 py-1.5 rounded-lg border border-amber-300 text-amber-800 text-xs font-semibold hover:bg-amber-100 transition"
                  >
                    Batal Pilih
                  </button>
                </div>
              </div>
            )}

            {/* Users Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              {usersLoading && usersList.length === 0 ? (
                <div className="py-16 text-center text-slate-400 space-y-2">
                  <RefreshCw className="w-8 h-8 mx-auto animate-spin text-indigo-500" />
                  <p className="text-xs font-semibold">Memuat data kredensial akun...</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-slate-600">
                    <thead className="bg-slate-50 text-slate-700 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
                      <tr>
                        <th className="px-4 py-3 w-10 text-center">
                          <input
                            type="checkbox"
                            checked={usersList.length > 0 && selectedUserIds.length === usersList.length}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedUserIds(usersList.map((u: any) => u.id));
                              } else {
                                setSelectedUserIds([]);
                              }
                            }}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                          />
                        </th>
                        <th className="px-4 py-3">Pengguna & Nama Lengkap</th>
                        <th className="px-4 py-3">Username (Login ID)</th>
                        <th className="px-4 py-3">Role / Hak Akses</th>
                        <th className="px-4 py-3">Tenant / Kelompok Bisnis</th>
                        <th className="px-4 py-3">Sesi Kelas</th>
                        <th className="px-4 py-3 text-right">Aksi CRUD</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {(() => {
                        const filtered = usersList.filter((u: any) => {
                          const matchesRole = userRoleFilter === "ALL" || (u.role && u.role.toUpperCase() === userRoleFilter);
                          const matchesSession = userSessionFilter === "ALL" || (u.session_id && u.session_id.toString() === userSessionFilter);
                          const q = userSearchTerm.toLowerCase();
                          const matchesSearch = !userSearchTerm ||
                            (u.username && u.username.toLowerCase().includes(q)) ||
                            (u.full_name && u.full_name.toLowerCase().includes(q)) ||
                            (u.email && u.email.toLowerCase().includes(q)) ||
                            (u.company_name && u.company_name.toLowerCase().includes(q)) ||
                            (u.session_name && u.session_name.toLowerCase().includes(q));
                          return matchesRole && matchesSession && matchesSearch;
                        });

                        if (filtered.length === 0) {
                          return (
                            <tr>
                              <td colSpan={7} className="text-center py-12 text-slate-400">
                                <Users className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                                <p className="font-semibold">Tidak ada akun yang sesuai dengan pencarian atau filter.</p>
                              </td>
                            </tr>
                          );
                        }

                        return filtered.map((u: any) => {
                          const isCurrentUser = currentUser && currentUser.username === u.username;
                          const isSelected = selectedUserIds.includes(u.id);
                          const roleColor =
                            u.role === "ADMIN"
                              ? "bg-purple-100 text-purple-800 border-purple-200"
                              : u.role === "DOSEN"
                              ? "bg-indigo-100 text-indigo-800 border-indigo-200"
                              : "bg-emerald-100 text-emerald-800 border-emerald-200";

                          return (
                            <tr key={u.id} className={`hover:bg-slate-50/80 transition group ${isSelected ? "bg-indigo-50/40" : ""}`}>
                              <td className="px-4 py-3.5 text-center">
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={(e) => {
                                    if (e.target.checked) {
                                      setSelectedUserIds([...selectedUserIds, u.id]);
                                    } else {
                                      setSelectedUserIds(selectedUserIds.filter(id => id !== u.id));
                                    }
                                  }}
                                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                                />
                              </td>
                              <td className="px-4 py-3.5">
                                <div className="flex items-center space-x-3">
                                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                                    u.role === "ADMIN"
                                      ? "bg-purple-600 text-white"
                                      : u.role === "DOSEN"
                                      ? "bg-indigo-600 text-white"
                                      : "bg-emerald-600 text-white"
                                  }`}>
                                    {u.full_name ? u.full_name.charAt(0).toUpperCase() : u.username.charAt(0).toUpperCase()}
                                  </div>
                                  <div>
                                    <div className="font-bold text-slate-900 flex items-center space-x-1.5">
                                      <span>{u.full_name || u.username}</span>
                                      {isCurrentUser && (
                                        <span className="px-1.5 py-0.2 text-[9px] rounded bg-amber-100 text-amber-800 font-bold border border-amber-300">
                                          Anda
                                        </span>
                                      )}
                                    </div>
                                    <div className="text-slate-400 text-[11px]">{u.email || `${u.username}@vlab.edu`}</div>
                                  </div>
                                </div>
                              </td>
                              <td className="px-4 py-3.5 font-mono text-xs font-bold text-slate-800">
                                <span className="bg-slate-100 px-2 py-1 rounded border border-slate-200">
                                  {u.username}
                                </span>
                              </td>
                              <td className="px-4 py-3.5">
                                <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold border ${roleColor}`}>
                                  {u.role === "ADMIN" && <ShieldAlert className="w-3 h-3 mr-1" />}
                                  {u.role === "DOSEN" && <GraduationCap className="w-3 h-3 mr-1" />}
                                  {u.role === "MAHASISWA" && <Users className="w-3 h-3 mr-1" />}
                                  {u.role}
                                </span>
                              </td>
                              <td className="px-4 py-3.5 text-slate-700">
                                {u.company_name ? (
                                  <div className="font-medium text-slate-800 flex items-center space-x-1">
                                    <Building2 className="w-3 h-3 text-slate-400 shrink-0" />
                                    <span className="truncate max-w-[180px]">{u.company_name}</span>
                                  </div>
                                ) : (
                                  <span className="text-slate-400 italic">Umum / Semua Tenant</span>
                                )}
                              </td>
                              <td className="px-4 py-3.5 text-slate-600">
                                {u.session_name ? (
                                  <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded text-[11px] font-medium border border-indigo-100 truncate max-w-[150px] inline-block">
                                    {u.session_name}
                                  </span>
                                ) : (
                                  <span className="text-slate-400 italic">-</span>
                                )}
                              </td>
                              <td className="px-4 py-3.5 text-right">
                                <div className="flex items-center justify-end space-x-1.5">
                                  <button
                                    onClick={() => handleOpenEditUser(u)}
                                    className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-lg border border-slate-300 text-xs transition flex items-center space-x-1"
                                    title="Edit Data Pengguna Lengkap"
                                  >
                                    <span>✏️ Edit</span>
                                  </button>
                                  <button
                                    onClick={() => handleOpenQuickPassword(u)}
                                    className="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold rounded-lg border border-indigo-200 text-xs transition flex items-center space-x-1"
                                    title="Ganti Password Cepat"
                                  >
                                    <KeyRound className="w-3 h-3" />
                                    <span>Password</span>
                                  </button>
                                  {u.role !== "ADMIN" && (
                                    <button
                                      onClick={() => setUserToDelete(u)}
                                      className="p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                                      title="Hapus Akun Pengguna"
                                    >
                                      <Trash2 className="w-3.5 h-3.5" />
                                    </button>
                                  )}
                                </div>
                              </td>
                            </tr>
                          );
                        });
                      })()}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    )}

      </main>

      {/* MODAL: NOTULENSI MEDIASI DIREKSI (OPEN-WORLD MULTI-PATH) */}
      {showMediationModal && activeMediationComplaint && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-xl w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-2xl">🤝</span>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Notulensi Rapat Mediasi Tingkat Direksi</h3>
                  <p className="text-[11px] text-slate-500">Negosiasi B2B Mitigasi Komplain Akun Enterprise VIP</p>
                </div>
              </div>
              <button onClick={() => setShowMediationModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>

            <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs mb-4 space-y-1.5">
              <div className="flex justify-between">
                <span className="text-slate-500">Klien Enterprise:</span>
                <span className="font-bold text-slate-900">{activeMediationComplaint.customer_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Nilai Kontrak Terancam:</span>
                <span className="font-bold text-indigo-700 font-mono">Rp {activeMediationComplaint.expected_revenue.toLocaleString("id-ID")}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Status Pembatalan:</span>
                <span className="text-amber-700 font-semibold">Ditunda Sementara Menunggu Solusi Final</span>
              </div>
              <div className="p-2.5 bg-white rounded border border-slate-200 text-slate-700 italic">
                "{activeMediationComplaint.complaint_details || activeMediationComplaint.notes}"
              </div>
            </div>

            <div className="mb-4">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">
                Pilih Kesepakatan Strategis Hasil Mediasi (Open Path):
              </h4>
              <div className="space-y-3">
                {/* Opsi 1: Addendum Diskon 15% */}
                <div className="border border-emerald-200 bg-emerald-50/50 hover:bg-emerald-50 rounded-lg p-3.5 transition flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-xs text-emerald-900 flex items-center">
                        💰 Opsi 1: Addendum Diskon 15% (Selamatkan Kas & Tanpa Potong Stok)
                      </span>
                      <span className="text-[10px] font-bold bg-emerald-200 text-emerald-800 px-1.5 py-0.5 rounded">
                        CSAT: 88%
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 mb-2.5">
                      Klien bersedia mempertahankan kontrak dengan kompensasi diskon 15% pada termin berjalan. <strong>Kas operasional tetap utuh</strong> dan tidak mengurangi persediaan fisik gudang.
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      await handleResolveComplaint(activeMediationComplaint.id, "mediation_discount_addendum");
                      setShowMediationModal(false);
                    }}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold py-1.5 rounded transition shadow-sm"
                  >
                    Sepakati Addendum Diskon 15%
                  </button>
                </div>

                {/* Opsi 2: Penggantian 15 Unit Fisik */}
                <div className="border border-blue-200 bg-blue-50/50 hover:bg-blue-50 rounded-lg p-3.5 transition flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-xs text-blue-900 flex items-center">
                        📦 Opsi 2: Penggantian 15 Unit Fisik Bergaransi Pabrik (Customer-First)
                      </span>
                      <span className="text-[10px] font-bold bg-blue-200 text-blue-800 px-1.5 py-0.5 rounded">
                        CSAT: 96%
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 mb-2.5">
                      Memotong 15 unit barang jadi dari gudang (HPP Rp 3.150.000). Jika stok gudang menipis, wajib menjalankan <em>Emergency Work Order</em> di modul MRP. Klien sangat puas dan loyalitas pulih maksimal.
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      await handleResolveComplaint(activeMediationComplaint.id, "mediation_emergency_replace");
                      setShowMediationModal(false);
                    }}
                    className="w-full bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold py-1.5 rounded transition shadow-sm"
                  >
                    Eksekusi Penggantian 15 Unit Fisik
                  </button>
                </div>

                {/* Opsi 3: Servis Lapangan & Audit Vendor Cacat */}
                <div className="border border-amber-200 bg-amber-50/50 hover:bg-amber-50 rounded-lg p-3.5 transition flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-xs text-amber-900 flex items-center">
                        🔧 Opsi 3: Kirim Tim Servis Lapangan & Audit Cacat Vendor (Pragmatis)
                      </span>
                      <span className="text-[10px] font-bold bg-amber-200 text-amber-800 px-1.5 py-0.5 rounded">
                        CSAT: 82%
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 mb-2.5">
                      Mengirim tim teknisi untuk perbaikan di lokasi klien (biaya operasional Rp 1.500.000). Mengonfirmasi bahwa kerusakan akibat cacat komponen dari supplier (CV Mitra Bahari).
                    </p>
                  </div>
                  <button
                    onClick={async () => {
                      await handleResolveComplaint(activeMediationComplaint.id, "mediation_qc_investigation");
                      setShowMediationModal(false);
                    }}
                    className="w-full bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold py-1.5 rounded transition shadow-sm"
                  >
                    Kirim Tim Servis & Investigasi QC
                  </button>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t flex justify-end">
              <button
                type="button"
                onClick={() => setShowMediationModal(false)}
                className="px-4 py-1.5 border rounded text-slate-600 text-xs hover:bg-slate-50"
              >
                Tutup Notulensi
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: KONVERSI PROSPEK KE SALES ORDER (OPEN-PATH) */}
      {convertingLead && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-xl">📄</span>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Konversi Prospek ke Sales Order Resmi</h3>
                  <p className="text-[11px] text-slate-500">{convertingLead.title}</p>
                </div>
              </div>
              <button onClick={() => setConvertingLead(null)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>

            <form onSubmit={handleExecuteConvertSO} className="space-y-3.5 text-xs">
              <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
                <div className="flex justify-between mb-1">
                  <span className="text-slate-500">Nama Klien:</span>
                  <span className="font-bold text-slate-900">{convertingLead.customer_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Credit Rating:</span>
                  <span className={`font-bold uppercase ${convertingLead.credit_rating === 'high_risk' ? 'text-red-600' : 'text-emerald-700'}`}>
                    {convertingLead.credit_rating || 'Normal Risk'}
                  </span>
                </div>
              </div>

              <div>
                <label className="text-slate-700 font-semibold block mb-1">Pilih Produk Barang Jadi:</label>
                <select
                  value={soProductId}
                  onChange={(e) => setSoProductId(Number(e.target.value))}
                  className="w-full border rounded p-2 text-xs"
                >
                  {products.filter(p => p.product_type === "finished_good").length > 0 ? (
                    products.filter(p => p.product_type === "finished_good").map(p => (
                      <option key={p.id} value={p.id}>
                        {p.name} — Rp {p.list_price.toLocaleString("id-ID")} (Stok: {p.current_stock})
                      </option>
                    ))
                  ) : (
                    <option value={1}>Smartwatch Pro Series 5 — Rp 1.250.000</option>
                  )}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Jumlah Unit Pesanan:</label>
                  <input
                    type="number"
                    min="1"
                    max="10000"
                    required
                    value={soQuantity}
                    onChange={(e) => setSoQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                    className="w-full border rounded p-2 font-mono font-bold text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Termin Pembayaran:</label>
                  <select
                    value={soPaymentTerms}
                    onChange={(e) => setSoPaymentTerms(e.target.value)}
                    className="w-full border rounded p-2 text-xs"
                  >
                    <option value="Tunai / Cash on Delivery">Tunai / COD (Kas Langsung Masuk)</option>
                    <option value="Tempo 30 Hari">Tempo 30 Hari</option>
                    <option value="Tempo 60 Hari">Tempo 60 Hari</option>
                  </select>
                </div>
              </div>

              {/* Credit Risk Warning */}
              {convertingLead.credit_rating === "high_risk" && soPaymentTerms.includes("Tempo") && (
                <div className="bg-red-50 border border-red-200 text-red-800 p-2.5 rounded text-[11px] space-y-1">
                  <div className="font-bold flex items-center">
                    <AlertTriangle className="w-3.5 h-3.5 mr-1 text-red-600 shrink-0" />
                    Peringatan Risiko Kredit Macet (Bad Debt Risk)
                  </div>
                  <p>
                    Klien ini memiliki reputasi kredit berisiko. Memberikan fasilitas tempo pembayaran tanpa DP berisiko gagal bayar saat Tutup Buku Bulanan!
                  </p>
                </div>
              )}

              <div className="bg-indigo-50/60 p-2.5 rounded border border-indigo-100 flex justify-between items-center">
                <span className="text-slate-600 text-xs">Total Nilai Sales Order:</span>
                <span className="font-mono font-bold text-sm text-indigo-700">
                  Rp {(
                    (products.find(p => p.id === soProductId)?.list_price || 1250000) * soQuantity
                  ).toLocaleString("id-ID")}
                </span>
              </div>

              <div className="pt-3 border-t flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setConvertingLead(null)}
                  className="px-3 py-1.5 border rounded text-slate-600 text-xs hover:bg-slate-50"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold text-xs shadow-sm transition"
                >
                  Konfirmasi & Terbitkan SO
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: KONFIRMASI RESMI PENERBITAN PURCHASE ORDER (PO) */}
      {confirmingPOVendor && (
        <div className="fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 space-y-4">
            <div className="flex items-start justify-between border-b pb-3">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-indigo-100 text-indigo-700">
                  <ShoppingBag className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">Konfirmasi Penerbitan Purchase Order</h3>
                  <p className="text-[11px] text-slate-500">Surat Pesanan Pembelian Bahan Baku Resmi ke Rekanan</p>
                </div>
              </div>
              <button
                disabled={isSubmittingPO}
                onClick={() => setConfirmingPOVendor(null)}
                className="text-slate-400 hover:text-slate-700 font-bold text-lg p-1"
              >
                ✕
              </button>
            </div>

            {/* Vendor & Order Breakdown */}
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2 text-xs">
              <div className="flex justify-between items-center border-b border-slate-200 pb-2">
                <span className="text-slate-500 font-medium">Rekanan Pemasok:</span>
                <span className="font-bold text-slate-900">{confirmingPOVendor.vendor.name}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-200 pb-2">
                <span className="text-slate-500 font-medium">Kategori Bahan Baku:</span>
                <span className="font-bold text-slate-900">{confirmingPOVendor.product?.name || confirmingPOVendor.vendor.category}</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-200 pb-2">
                <span className="text-slate-500 font-medium">Kuantitas Dipesan:</span>
                <span className="font-bold font-mono text-indigo-700">{confirmingPOVendor.quantity} Unit</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-200 pb-2">
                <span className="text-slate-500 font-medium">Harga Satuan Efektif:</span>
                <span className="font-mono text-slate-700">Rp {Math.round(confirmingPOVendor.unitCost).toLocaleString("id-ID")} / unit (x{confirmingPOVendor.vendor.price_multiplier})</span>
              </div>
              <div className="flex justify-between items-center pt-1 text-sm font-bold">
                <span className="text-slate-800">Total Komitmen Kas (AP):</span>
                <span className="font-mono text-indigo-700">Rp {Math.round(confirmingPOVendor.totalCost).toLocaleString("id-ID")}</span>
              </div>
            </div>

            {/* Payment Method & Terms Breakdown */}
            <div className="space-y-2 text-xs">
              <span className="font-bold text-slate-700 block">Pilih Metode Pembayaran Pengadaan:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setPoPaymentMethod("tempo")}
                  className={`p-3 rounded-xl border text-left transition ${
                    poPaymentMethod === "tempo"
                      ? "bg-indigo-50 border-indigo-500 ring-2 ring-indigo-500/20 text-indigo-950"
                      : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  <div className="font-bold flex items-center justify-between text-xs">
                    <span>💳 Tempo {confirmingPOVendor.vendor.credit_terms_days || 30} Hari</span>
                    {poPaymentMethod === "tempo" && <Check className="w-3.5 h-3.5 text-indigo-600" />}
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">
                    Kas tetap utuh sekarang. Dicatat sebagai <strong>Utang Usaha (AP Akun 2010)</strong> sampai tanggal pelunasan.
                  </p>
                </button>

                <button
                  type="button"
                  onClick={() => setPoPaymentMethod("cash")}
                  className={`p-3 rounded-xl border text-left transition ${
                    poPaymentMethod === "cash"
                      ? "bg-emerald-50 border-emerald-500 ring-2 ring-emerald-500/20 text-emerald-950"
                      : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  <div className="font-bold flex items-center justify-between text-xs">
                    <span>💵 Tunai Langsung (Cash)</span>
                    {poPaymentMethod === "cash" && <Check className="w-3.5 h-3.5 text-emerald-600" />}
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">
                    Saldo <strong>Kas & Bank (Akun 1010)</strong> dipotong langsung seketika Rp {Math.round(confirmingPOVendor.totalCost).toLocaleString("id-ID")}.
                  </p>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-500 block text-[10px]">Estimasi Waktu Kirim:</span>
                <span className="font-bold text-slate-800">{confirmingPOVendor.vendor.lead_time_days} Hari Kerja</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-500 block text-[10px]">Status Pembayaran Terpilih:</span>
                <span className={`font-bold ${poPaymentMethod === 'cash' ? 'text-emerald-700' : 'text-indigo-700'}`}>
                  {poPaymentMethod === 'cash' ? 'Tunai (Kas Berkurang)' : `Kredit Tempo (${confirmingPOVendor.vendor.credit_terms_days || 30} Hari)`}
                </span>
              </div>
            </div>

            <div className="text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
              💡 <strong>Dampak Finansial & Operasional:</strong> Dokumen PO ini mengikat secara hukum. {poPaymentMethod === 'cash' ? 'Kas riil berkurang seketika.' : 'Kewajiban dicatat ke Utang Usaha (AP) dan kas baru berkurang saat dilakukan pelunasan utang.'}
            </div>

            {/* Action Buttons */}
            <div className="pt-2 border-t flex justify-end space-x-2">
              <button
                disabled={isSubmittingPO}
                onClick={() => setConfirmingPOVendor(null)}
                className="px-4 py-2 border rounded-lg text-slate-600 text-xs hover:bg-slate-50 font-semibold transition"
              >
                Batal / Tinjau Ulang
              </button>
              <button
                disabled={isSubmittingPO}
                onClick={handleConfirmPO}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-bold text-xs shadow-sm transition flex items-center space-x-1.5"
              >
                {isSubmittingPO ? (
                  <span>Menerbitkan Dokumen...</span>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Setujui & Terbitkan PO Resmi</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: KONFIRMASI KEPUTUSAN MITIGASI KELUHAN CRM */}
      {confirmingComplaintAction && (
        <div className="fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 space-y-4">
            <div className="flex items-start justify-between border-b pb-3">
              <div className="flex items-center space-x-2">
                <div className={`p-2 rounded-lg ${confirmingComplaintAction.isDangerous ? "bg-rose-100 text-rose-700" : "bg-indigo-100 text-indigo-700"}`}>
                  <MessageSquare className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-extrabold text-slate-900">Konfirmasi Mitigasi Layanan Klien VIP</h3>
                  <p className="text-[11px] text-slate-500">Akun: {confirmingComplaintAction.customerName}</p>
                </div>
              </div>
              <button
                onClick={() => setConfirmingComplaintAction(null)}
                className="text-slate-400 hover:text-slate-700 font-bold text-lg p-1"
              >
                ✕
              </button>
            </div>

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2.5 text-xs">
              <div>
                <span className="text-slate-500 font-medium block text-[11px]">Tindakan Mitigasi Terpilih:</span>
                <h4 className="font-extrabold text-slate-900 text-sm mt-0.5">{confirmingComplaintAction.title}</h4>
              </div>

              <div className="pt-2 border-t border-slate-200 flex justify-between items-center">
                <span className="text-slate-500 font-medium">Beban Biaya / Alokasi Stok:</span>
                <span className="font-bold text-indigo-700 font-mono">{confirmingComplaintAction.cost}</span>
              </div>

              <div className="pt-2 border-t border-slate-200">
                <span className="text-slate-500 font-medium block text-[11px]">Dampak Terhadap Kepuasan (CSAT) & Kontrak:</span>
                <p className="font-semibold text-slate-800 mt-0.5">{confirmingComplaintAction.impact}</p>
              </div>
            </div>

            {confirmingComplaintAction.isDangerous ? (
              <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-300 text-rose-900 text-xs space-y-1">
                <div className="font-bold flex items-center text-rose-800">
                  <AlertTriangle className="w-4 h-4 mr-1 text-rose-600 shrink-0 animate-pulse" />
                  PERINGATAN DIREKSI: KEPUTUSAN BERISIKO TINGGI
                </div>
                <p className="text-[11px] leading-relaxed text-rose-800/90">
                  Menolak kompensasi klien VIP berisiko langsung memicu pemutusan kontrak dagang bernilai ratusan juta rupiah dan menurunkan skor audit reputasi perusahaan!
                </p>
              </div>
            ) : (
              <div className="text-[11px] text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                💡 Keputusan mitigasi ini bersifat mengikat dan akan segera memperbarui status tiket keluhan di sistem CRM serta memulihkan indeks loyalitas konsumen.
              </div>
            )}

            <div className="pt-2 border-t flex justify-end space-x-2">
              <button
                onClick={() => setConfirmingComplaintAction(null)}
                className="px-4 py-2 border rounded-lg text-slate-600 text-xs hover:bg-slate-50 font-semibold transition"
              >
                Batal / Tinjau Kembali
              </button>
              <button
                onClick={() => handleResolveComplaint(confirmingComplaintAction.leadId, confirmingComplaintAction.actionType)}
                className={`px-4 py-2 rounded-lg font-bold text-xs shadow-sm transition flex items-center space-x-1.5 ${
                  confirmingComplaintAction.isDangerous
                    ? "bg-rose-600 hover:bg-rose-700 text-white"
                    : "bg-indigo-600 hover:bg-indigo-700 text-white"
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Sahkan & Eksekusi Solusi</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: LAPORAN AKHIR & MULTIPLE ENDINGS PERUSAHAAN */}
      {showEndingModal && endingData && (
        <div className="fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b pb-4 mb-4">
              <div>
                <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${endingData.ending.badge_color}`}>
                  {endingData.ending.badge} • Predikat: {endingData.ending.grade}
                </span>
                <h2 className="text-base sm:text-lg font-extrabold text-slate-900 mt-2">
                  {endingData.ending.title}
                </h2>
                <p className="text-xs text-slate-500 font-medium">{endingData.ending.subtitle}</p>
              </div>
              <button onClick={() => setShowEndingModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-xl">✕</button>
            </div>

            {/* Verdict Box */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-4">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center">
                <FileText className="w-3.5 h-3.5 mr-1.5 text-indigo-600" /> Putusan Manajemen & Narasi Akhir
              </h4>
              <p className="text-xs text-slate-800 leading-relaxed font-serif">
                "{endingData.ending.verdict}"
              </p>
            </div>

            {/* Metrics Snapshot */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-4">
              <div className="bg-slate-100 p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Saldo Kas Akhir</span>
                <span className={`text-xs font-mono font-bold ${endingData.metrics.cash < 0 ? 'text-red-600' : 'text-slate-900'}`}>
                  Rp {endingData.metrics.cash.toLocaleString("id-ID")}
                </span>
              </div>
              <div className="bg-slate-100 p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Kepuasan Klien (CSAT)</span>
                <span className="text-xs font-mono font-bold text-indigo-700">
                  {endingData.metrics.csat_score.toFixed(1)}%
                </span>
              </div>
              <div className="bg-slate-100 p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Moral Buruh SDM</span>
                <span className={`text-xs font-mono font-bold ${endingData.metrics.worker_morale < 50 ? 'text-red-600' : 'text-emerald-700'}`}>
                  {endingData.metrics.worker_morale.toFixed(1)}%
                </span>
              </div>
              <div className="bg-slate-100 p-2.5 rounded-lg border border-slate-200">
                <span className="text-[10px] text-slate-500 block uppercase font-bold">Misi Terpecahkan</span>
                <span className="text-xs font-mono font-bold text-slate-800">
                  {endingData.metrics.resolved_cases} / {endingData.metrics.total_cases}
                </span>
              </div>
            </div>

            {/* Autopsy / Key Lessons */}
            <div className="border border-slate-200 rounded-xl p-4 mb-4 bg-white shadow-xs">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 flex items-center">
                <Award className="w-3.5 h-3.5 mr-1.5 text-amber-500" /> Evaluasi & Autopsi Manajerial
              </h4>
              <ul className="space-y-1.5 text-xs text-slate-700">
                {endingData.ending.autopsy.map((item: string, idx: number) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-indigo-500 mr-2 shrink-0 font-bold">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="pt-3 border-t flex justify-between items-center">
              <span className="text-[11px] text-slate-400 italic">
                Evaluasi Periode: {endingData.period_name} (Siklus {endingData.round})
              </span>
              <button
                type="button"
                onClick={() => setShowEndingModal(false)}
                className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition shadow-sm"
              >
                Tutup Laporan
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. FACT SHEET & BENCHMARK SOLUSI MODAL */}
      {selectedFactSheet && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <div className="bg-indigo-100 text-indigo-800 p-2 rounded-lg">
                  <Sparkles className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Fact Sheet Pembelajaran & Solusi Standar Industri</h3>
                  <p className="text-xs text-slate-500">{selectedFactSheet.title}</p>
                </div>
              </div>
              <button onClick={() => setSelectedFactSheet(null)} className="text-slate-400 hover:text-slate-700 font-bold text-lg p-1">✕</button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="bg-red-50 p-3.5 rounded-lg border border-red-200">
                <h4 className="font-bold text-red-900 flex items-center mb-1">
                  <AlertTriangle className="w-4 h-4 mr-1.5 text-red-600" /> Analisis Akar Masalah (Root Cause):
                </h4>
                <p className="text-red-800 leading-relaxed">{selectedFactSheet.root_cause}</p>
              </div>

              <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200">
                <h4 className="font-bold text-slate-900 mb-1">Evaluasi Aksi yang Diambil Tim Mahasiswa:</h4>
                <p className="text-slate-700 leading-relaxed">{selectedFactSheet.why_evaluation || selectedFactSheet.student_actions_taken}</p>
              </div>

              <div className="bg-emerald-50 p-3.5 rounded-lg border border-emerald-200">
                <h4 className="font-bold text-emerald-900 flex items-center mb-1">
                  <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-600" /> Solusi Problem Solving yang Benar (Standard Industry SOP):
                </h4>
                <p className="text-emerald-800 whitespace-pre-line leading-relaxed font-medium">
                  {selectedFactSheet.benchmark_solution || selectedFactSheet.best_practice}
                </p>
              </div>

              <div className="bg-indigo-50 p-3.5 rounded-lg border border-indigo-200">
                <h4 className="font-bold text-indigo-900 flex items-center mb-1">
                  <Award className="w-4 h-4 mr-1.5 text-indigo-600" /> Pelajaran Bisnis Kunci (Takeaway Manajerial):
                </h4>
                <p className="text-indigo-800 italic leading-relaxed">
                  "{selectedFactSheet.key_takeaway}"
                </p>
              </div>
            </div>

            <div className="mt-6 pt-3 border-t flex justify-end">
              <button
                onClick={() => setSelectedFactSheet(null)}
                className="bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs py-2 px-5 rounded-lg transition"
              >
                Tutup Fact Sheet
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 6. MODAL: TAMBAH PROSPEK CRM */}
      {showAddLeadModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center">
                <Briefcase className="w-4 h-4 mr-2 text-indigo-600" /> Dokumen Peluang Penjualan Baru
              </h3>
              <button onClick={() => setShowAddLeadModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>
            <form onSubmit={handleCreateLead} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Judul Peluang / Proyek:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Pengadaan Smartwatch 100 Unit"
                  value={newLeadForm.title}
                  onChange={(e) => setNewLeadForm({ ...newLeadForm, title: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Nama Klien / Instansi:</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. PT Maju Jaya Sentosa"
                    value={newLeadForm.customer_name}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, customer_name: e.target.value })}
                    className="w-full border rounded p-2 text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Email Kontak:</label>
                  <input
                    type="email"
                    placeholder="purchasing@majujaya.com"
                    value={newLeadForm.customer_email}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, customer_email: e.target.value })}
                    className="w-full border rounded p-2 text-xs"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Nilai Kontrak (Rp):</label>
                  <input
                    type="number"
                    step="1000000"
                    required
                    value={newLeadForm.expected_revenue}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, expected_revenue: parseFloat(e.target.value) || 0 })}
                    className="w-full border rounded p-2 font-mono font-bold text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Prioritas:</label>
                  <select
                    value={newLeadForm.priority}
                    onChange={(e) => setNewLeadForm({ ...newLeadForm, priority: e.target.value })}
                    className="w-full border rounded p-2 text-xs"
                  >
                    <option value="low">Rendah (Low)</option>
                    <option value="medium">Sedang (Medium)</option>
                    <option value="high">Tinggi (High)</option>
                    <option value="urgent">Mendesak (Urgent)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Catatan Negosiasi:</label>
                <textarea
                  rows={2}
                  placeholder="Kebutuhan khusus atau catatan diskusi komersial..."
                  value={newLeadForm.notes}
                  onChange={(e) => setNewLeadForm({ ...newLeadForm, notes: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div className="pt-3 border-t flex justify-end space-x-2">
                <button type="button" onClick={() => setShowAddLeadModal(false)} className="px-3 py-1.5 border rounded text-slate-600 text-xs">
                  Batal
                </button>
                <button type="submit" className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold text-xs">
                  Simpan Dokumen
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 7. MODAL: TAMBAH VENDOR */}
      {showAddVendorModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center">
                <ShoppingBag className="w-4 h-4 mr-2 text-indigo-600" /> Pendaftaran Master Rekanan Pemasok
              </h3>
              <button onClick={() => setShowAddVendorModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>
            <form onSubmit={handleCreateVendor} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Nama Perusahaan / Supplier:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. PT Micro Precision Components"
                  value={newVendorForm.name}
                  onChange={(e) => setNewVendorForm({ ...newVendorForm, name: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Kategori Pasokan Bahan:</label>
                <input
                  type="text"
                  required
                  value={newVendorForm.category}
                  onChange={(e) => setNewVendorForm({ ...newVendorForm, category: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Lead Time (Hari):</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={newVendorForm.lead_time_days}
                    onChange={(e) => setNewVendorForm({ ...newVendorForm, lead_time_days: parseInt(e.target.value) || 1 })}
                    className="w-full border rounded p-2 text-center font-bold text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Defect Rate (%):</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    required
                    value={newVendorForm.defect_rate}
                    onChange={(e) => setNewVendorForm({ ...newVendorForm, defect_rate: parseFloat(e.target.value) || 0 })}
                    className="w-full border rounded p-2 text-center font-bold text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Pengali Harga:</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0.5"
                    required
                    value={newVendorForm.price_multiplier}
                    onChange={(e) => setNewVendorForm({ ...newVendorForm, price_multiplier: parseFloat(e.target.value) || 1 })}
                    className="w-full border rounded p-2 text-center font-bold text-xs"
                  />
                </div>
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Catatan Evaluasi / Legalitas:</label>
                <textarea
                  rows={2}
                  placeholder="Informasi legalitas, sertifikasi mutu, atau catatan audit..."
                  value={newVendorForm.notes}
                  onChange={(e) => setNewVendorForm({ ...newVendorForm, notes: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div className="pt-3 border-t flex justify-end space-x-2">
                <button type="button" onClick={() => setShowAddVendorModal(false)} className="px-3 py-1.5 border rounded text-slate-600 text-xs">
                  Batal
                </button>
                <button type="submit" className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold text-xs">
                  Simpan Master Data
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 8. MODAL: TAMBAH ANGGARAN DEPARTEMEN */}
      {showAddBudgetModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-sm w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center">
                <DollarSign className="w-4 h-4 mr-2 text-indigo-600" /> Penetapan Pagu Anggaran
              </h3>
              <button onClick={() => setShowAddBudgetModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>
            <form onSubmit={handleCreateBudget} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Nama Departemen / Divisi:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Riset & Rekayasa Produk (R&D)"
                  value={newBudgetForm.department}
                  onChange={(e) => setNewBudgetForm({ ...newBudgetForm, department: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Alokasi Pagu Anggaran (Rp):</label>
                <input
                  type="number"
                  step="5000000"
                  required
                  value={newBudgetForm.allocated_amount}
                  onChange={(e) => setNewBudgetForm({ ...newBudgetForm, allocated_amount: parseFloat(e.target.value) || 0 })}
                  className="w-full border rounded p-2 font-mono font-bold text-xs"
                />
              </div>
              <div className="pt-3 border-t flex justify-end space-x-2">
                <button type="button" onClick={() => setShowAddBudgetModal(false)} className="px-3 py-1.5 border rounded text-slate-600 text-xs">
                  Batal
                </button>
                <button type="submit" className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold text-xs">
                  Tetapkan Pagu
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 10. MODAL: PENDAFTARAN TENANT / KELOMPOK BARU */}
      {showAddCompanyModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center">
                <Building2 className="w-4 h-4 mr-2 text-indigo-600" /> Daftarkan Kelompok / Tenant Perusahaan Baru
              </h3>
              <button onClick={() => setShowAddCompanyModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>
            <form onSubmit={handleCreateCompany} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Nama Entitas Perusahaan (PT):</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. PT Sinergi Robotika Indonesia"
                  value={newCompanyForm.name}
                  onChange={(e) => setNewCompanyForm({ ...newCompanyForm, name: e.target.value })}
                  className="w-full border rounded p-2 text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Sektor / Lini Industri Bisnis:</label>
                <select
                  value={newCompanyForm.industry}
                  onChange={(e) => setNewCompanyForm({ ...newCompanyForm, industry: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                >
                  <option value="Manufaktur Elektronik Smart Device">Manufaktur Elektronik Smart Device</option>
                  <option value="Komponen IoT & Sensor Pintar">Komponen IoT & Sensor Pintar</option>
                  <option value="Alat Kesehatan & Monitoring Digital">Alat Kesehatan & Monitoring Digital</option>
                  <option value="Penyimpanan Energi & Battery Pack">Penyimpanan Energi & Battery Pack</option>
                  <option value="Perakitan Otomotif & Mikromobilitas">Perakitan Otomotif & Mikromobilitas</option>
                </select>
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Modal Awal Disetor (Rp):</label>
                <input
                  type="number"
                  step="50000000"
                  required
                  value={newCompanyForm.initial_capital}
                  onChange={(e) => setNewCompanyForm({ ...newCompanyForm, initial_capital: parseFloat(e.target.value) || 0 })}
                  className="w-full border rounded p-2 font-mono font-bold text-xs"
                />
                <p className="text-[10px] text-slate-500 mt-1">
                  Sistem akan otomatis mem-provisioning Chart of Accounts (Kas Rp {newCompanyForm.initial_capital.toLocaleString("id-ID")}), 4 Vendor dengan riwayat metrik, Master Produk, BOM, Work Center, CRM Leads, dan Misi Kasus mandiri.
                </p>
              </div>
              <div className="pt-3 border-t flex justify-end space-x-2">
                <button type="button" onClick={() => setShowAddCompanyModal(false)} className="px-3 py-1.5 border rounded text-slate-600 text-xs">
                  Batal
                </button>
                <button type="submit" className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold text-xs shadow-sm">
                  + Buat & Provisioning Sandbox Tenant
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 9. MODAL: REKRUT PEGAWAI BARU */}
      {showAddEmployeeModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center">
                <Users className="w-4 h-4 mr-2 text-indigo-600" /> Master Data Pegawai Baru
              </h3>
              <button onClick={() => setShowAddEmployeeModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>
            <form onSubmit={handleCreateEmployee} className="space-y-3 text-xs">
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Nama Lengkap:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Siti Nurhaliza"
                  value={newEmployeeForm.name}
                  onChange={(e) => setNewEmployeeForm({ ...newEmployeeForm, name: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Departemen:</label>
                  <select
                    value={newEmployeeForm.department}
                    onChange={(e) => setNewEmployeeForm({ ...newEmployeeForm, department: e.target.value })}
                    className="w-full border rounded p-2 text-xs"
                  >
                    <option value="Produksi">Produksi</option>
                    <option value="Quality Control">Quality Control</option>
                    <option value="Logistik & Gudang">Logistik & Gudang</option>
                    <option value="Sales & Marketing">Sales & Marketing</option>
                    <option value="Finance & Accounting">Finance & Accounting</option>
                    <option value="HR & Legal">HR & Legal</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Jabatan:</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Inspector QC"
                    value={newEmployeeForm.role}
                    onChange={(e) => setNewEmployeeForm({ ...newEmployeeForm, role: e.target.value })}
                    className="w-full border rounded p-2 text-xs"
                  />
                </div>
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Gaji Pokok Bulanan (Rp):</label>
                <input
                  type="number"
                  step="500000"
                  required
                  value={newEmployeeForm.monthly_salary}
                  onChange={(e) => setNewEmployeeForm({ ...newEmployeeForm, monthly_salary: parseFloat(e.target.value) || 0 })}
                  className="w-full border rounded p-2 font-mono font-bold text-xs"
                />
              </div>
              <div className="pt-3 border-t flex justify-end space-x-2">
                <button type="button" onClick={() => setShowAddEmployeeModal(false)} className="px-3 py-1.5 border rounded text-slate-600 text-xs">
                  Batal
                </button>
                <button type="submit" className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold text-xs">
                  Daftarkan Pegawai
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 10. MODAL: BUAT SKENARIO KASUS MASALAH KUSTOM */}
      {showAddCustomCaseModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b pb-3 mb-4">
              <h3 className="text-sm font-bold text-slate-900 flex items-center">
                <Award className="w-4 h-4 mr-2 text-indigo-600" /> Buat Skenario Masalah Kustom
              </h3>
              <button onClick={() => setShowAddCustomCaseModal(false)} className="text-slate-400 hover:text-slate-700 font-bold text-lg">✕</button>
            </div>
            <form onSubmit={handleCreateCustomCase} className="space-y-3 text-xs">
              <div className="bg-indigo-50 p-2.5 rounded text-indigo-800 text-[11px] mb-2">
                Target Perusahaan: <strong>{companies.find(c => c.id === selectedCompanyForCases)?.name || "Kelompok Terpilih"}</strong>
              </div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Kode Kasus:</label>
                  <input
                    type="text"
                    required
                    value={newCustomCaseForm.code}
                    onChange={(e) => setNewCustomCaseForm({ ...newCustomCaseForm, code: e.target.value })}
                    className="w-full border rounded p-2 text-xs font-mono font-bold"
                  />
                </div>
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Urutan Tahap:</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    required
                    value={newCustomCaseForm.stage_order}
                    onChange={(e) => setNewCustomCaseForm({ ...newCustomCaseForm, stage_order: parseInt(e.target.value) || 1 })}
                    className="w-full border rounded p-2 text-xs text-center font-bold"
                  />
                </div>
                <div>
                  <label className="text-slate-700 font-semibold block mb-1">Modul Target:</label>
                  <select
                    value={newCustomCaseForm.category}
                    onChange={(e) => setNewCustomCaseForm({ ...newCustomCaseForm, category: e.target.value })}
                    className="w-full border rounded p-2 text-xs font-bold"
                  >
                    <option value="purchasing">Pengadaan (SCM)</option>
                    <option value="crm">Pelanggan (CRM)</option>
                    <option value="mrp">Pabrik (MRP)</option>
                    <option value="hr">Pegawai (HR)</option>
                    <option value="accounting">Akuntansi & Kas</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Judul Masalah Bisnis:</label>
                <input
                  type="text"
                  required
                  placeholder="misal: Krisis Kenaikan Harga Bahan Baku Logam 30%"
                  value={newCustomCaseForm.title}
                  onChange={(e) => setNewCustomCaseForm({ ...newCustomCaseForm, title: e.target.value })}
                  className="w-full border rounded p-2 text-xs font-bold"
                />
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Deskripsi Narasi Masalah:</label>
                <textarea
                  rows={3}
                  required
                  placeholder="Jelaskan kondisi krisis bisnis yang dihadapi perusahaan kelompok ini..."
                  value={newCustomCaseForm.description}
                  onChange={(e) => setNewCustomCaseForm({ ...newCustomCaseForm, description: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Petunjuk Pemicu (Trigger Hint):</label>
                <input
                  type="text"
                  placeholder="misal: Buka modul CRM -> Cek riwayat tiket komplain..."
                  value={newCustomCaseForm.trigger_hint}
                  onChange={(e) => setNewCustomCaseForm({ ...newCustomCaseForm, trigger_hint: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Alur Solusi SOP yang Diharapkan:</label>
                <textarea
                  rows={2}
                  placeholder="Langkah 1.. Langkah 2.. Langkah 3.."
                  value={newCustomCaseForm.solvable_workflow}
                  onChange={(e) => setNewCustomCaseForm({ ...newCustomCaseForm, solvable_workflow: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div>
                <label className="text-slate-700 font-semibold block mb-1">Kriteria Keberhasilan & Skor:</label>
                <input
                  type="text"
                  placeholder="misal: PO berhasil dialihkan, CSAT di atas 80%, margin terjaga."
                  value={newCustomCaseForm.resolution_criteria}
                  onChange={(e) => setNewCustomCaseForm({ ...newCustomCaseForm, resolution_criteria: e.target.value })}
                  className="w-full border rounded p-2 text-xs"
                />
              </div>
              <div className="pt-3 border-t flex justify-end space-x-2">
                <button type="button" onClick={() => setShowAddCustomCaseModal(false)} className="px-3 py-1.5 border rounded text-slate-600 text-xs">
                  Batal
                </button>
                <button type="submit" className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-bold text-xs shadow-sm">
                  + Suntikkan Masalah ke Tenant
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* GLOBAL BRANDING CUSTOMIZATION MODAL */}
      {showBrandingModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-2xl w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 px-6 py-4 text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center space-x-2.5">
                <div className="bg-indigo-600 p-1.5 rounded-lg">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">🎨 Kustomisasi Bebas Branding & Identitas</h3>
                  <p className="text-[11px] text-indigo-300">Ubah nama kampus, jurusan, dosen pengampu, dan footer secara dinamis</p>
                </div>
              </div>
              <button
                onClick={() => setShowBrandingModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              <div className="bg-indigo-50 border border-indigo-200 p-3 rounded-lg text-indigo-900 text-[11px] flex items-start space-x-2">
                <ShieldCheck className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                <span>
                  Perubahan branding ini langsung aktif dan tersimpan ke database backend. Siapapun yang mengakses VLab-ERP akan melihat identitas kampus & dosen yang Anda tentukan di sini.
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="sm:col-span-2">
                  <label className="block font-bold text-slate-700 mb-1">Nama Aplikasi / Judul Platform (App Title)</label>
                  <input
                    type="text"
                    value={brandingForm.app_title}
                    onChange={(e) => setBrandingForm({ ...brandingForm, app_title: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="Contoh: VLab-ERP Enterprise Edition"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block font-bold text-slate-700 mb-1">Nama Jurusan / Fakultas / Kampus</label>
                  <input
                    type="text"
                    value={brandingForm.department_name}
                    onChange={(e) => setBrandingForm({ ...brandingForm, department_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="Contoh: Fakultas Ekonomi dan Bisnis (FEB) • Manajemen Bisnis & Akuntansi"
                  />
                </div>

                {/* 3 Discipline Lecturers FEB */}
                <div className="sm:col-span-2 pt-2 border-t border-slate-100">
                  <div className="flex items-center space-x-1.5 font-bold text-indigo-900 mb-2.5">
                    <Users className="w-4 h-4 text-indigo-600" />
                    <span>Profil 3 Dosen Rumpun Ilmu FEB (Team Teaching):</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="bg-blue-50/70 p-2.5 rounded-lg border border-blue-200">
                      <label className="block font-bold text-blue-900 mb-1">
                        🎯 Dosen Pemasaran & CRM
                      </label>
                      <input
                        type="text"
                        value={brandingForm.lecturer_marketing_name || ""}
                        onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_marketing_name: e.target.value })}
                        className="w-full px-2 py-1.5 bg-white border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                        placeholder="Dr. Maya Indah, S.E., M.M."
                      />
                      <span className="text-[10px] text-blue-600 mt-0.5 block">Misi Pemasaran & Retur VIP</span>
                    </div>

                    <div className="bg-teal-50/70 p-2.5 rounded-lg border border-teal-200">
                      <label className="block font-bold text-teal-900 mb-1">
                        👥 Dosen SDM & Organisasi
                      </label>
                      <input
                        type="text"
                        value={brandingForm.lecturer_hr_name || ""}
                        onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_hr_name: e.target.value })}
                        className="w-full px-2 py-1.5 bg-white border border-teal-300 rounded focus:ring-2 focus:ring-teal-500 focus:outline-none"
                        placeholder="Drs. Bambang Prakoso, M.Psi."
                      />
                      <span className="text-[10px] text-teal-600 mt-0.5 block">Misi SDM & Serikat Buruh</span>
                    </div>

                    <div className="bg-emerald-50/70 p-2.5 rounded-lg border border-emerald-200">
                      <label className="block font-bold text-emerald-900 mb-1">
                        💰 Dosen Keuangan & Akun
                      </label>
                      <input
                        type="text"
                        value={brandingForm.lecturer_finance_name || ""}
                        onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_finance_name: e.target.value })}
                        className="w-full px-2 py-1.5 bg-white border border-emerald-300 rounded focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                        placeholder="Dr. Ir. Budi Santoso, Ak."
                      />
                      <span className="text-[10px] text-emerald-600 mt-0.5 block">Misi Likuiditas & Piutang</span>
                    </div>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100">
                  <label className="block font-bold text-slate-700 mb-1">Koordinator / Tim Dosen Pengampu</label>
                  <input
                    type="text"
                    value={brandingForm.lecturer_name}
                    onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_name: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="Contoh: Tim Dosen Pengampu FEB"
                  />
                </div>

                <div className="pt-2 border-t border-slate-100">
                  <label className="block font-bold text-slate-700 mb-1">Label Peran Dosen</label>
                  <input
                    type="text"
                    value={brandingForm.lecturer_role_label}
                    onChange={(e) => setBrandingForm({ ...brandingForm, lecturer_role_label: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="Contoh: Tim Pengampu FEB"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Badge Skenario / Supervisi</label>
                  <input
                    type="text"
                    value={brandingForm.supervision_badge}
                    onChange={(e) => setBrandingForm({ ...brandingForm, supervision_badge: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="Contoh: Supervisi & Skenario"
                  />
                </div>

                <div>
                  <label className="block font-bold text-slate-700 mb-1">Semester / Tahun Akademik</label>
                  <input
                    type="text"
                    value={brandingForm.academic_term}
                    onChange={(e) => setBrandingForm({ ...brandingForm, academic_term: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="Contoh: Semester Ganjil 2026/2027"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block font-bold text-slate-700 mb-1">Teks Lengkap Footer</label>
                  <textarea
                    rows={2}
                    value={brandingForm.footer_text}
                    onChange={(e) => setBrandingForm({ ...brandingForm, footer_text: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    placeholder="Teks footer di bagian bawah portal"
                  />
                </div>
              </div>
            </div>

            <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex items-center justify-between">
              <button
                type="button"
                onClick={handleResetBranding}
                disabled={isSavingBranding}
                className="text-xs font-semibold text-rose-600 hover:text-rose-700 hover:underline"
              >
                Reset Standar Bawaan
              </button>
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={() => setShowBrandingModal(false)}
                  className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-800 border border-slate-300 rounded-lg hover:bg-slate-100 transition"
                >
                  Batal
                </button>
                <button
                  type="button"
                  onClick={handleSaveBranding}
                  disabled={isSavingBranding}
                  className="px-5 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition shadow-md shadow-indigo-600/20 flex items-center space-x-1.5"
                >
                  {isSavingBranding ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                  <span>Simpan & Terapkan</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 1: BUAT SESI KELAS BARU FEB & ATUR TIM DOSEN */}
      {showAddSessionModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-2xl w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 px-6 py-4 text-white flex items-center justify-between border-b border-slate-800 shrink-0">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                  <GraduationCap className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">Buat Sesi Kelas Baru & Konfigurasi Tim Dosen</h3>
                  <p className="text-[11px] text-indigo-300">Fakultas Ekonomi dan Bisnis (FEB) • Multi-Class Management</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowAddSessionModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSession} className="p-6 space-y-5 overflow-y-auto text-xs flex-1">
              {/* Bagian 1: Data Identitas Kelas */}
              <div className="space-y-3">
                <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center">
                  <Building2 className="w-4 h-4 mr-1.5 text-indigo-600" />
                  Informasi Utama Kelas Perkuliahan
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div className="sm:col-span-2">
                    <label className="block font-bold text-slate-700 mb-1">Nama Sesi Kelas Perkuliahan *</label>
                    <input
                      type="text"
                      required
                      value={newSessionForm.name}
                      onChange={(e) => setNewSessionForm({ ...newSessionForm, name: e.target.value })}
                      placeholder="Contoh: Praktikum ERP & Simulasi Bisnis - Kelas FEB C"
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Kode Sesi Kelas (Unik) *</label>
                    <input
                      type="text"
                      required
                      value={newSessionForm.code}
                      onChange={(e) => setNewSessionForm({ ...newSessionForm, code: e.target.value.toUpperCase() })}
                      placeholder="Contoh: ERP-FEB-C"
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono font-bold focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Semester / Tahun Akademik</label>
                    <input
                      type="text"
                      value={newSessionForm.academic_term}
                      onChange={(e) => setNewSessionForm({ ...newSessionForm, academic_term: e.target.value })}
                      placeholder="Contoh: Semester Ganjil 2026/2027"
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block font-bold text-slate-700 mb-1">Program Studi / Jurusan</label>
                    <input
                      type="text"
                      value={newSessionForm.department}
                      onChange={(e) => setNewSessionForm({ ...newSessionForm, department: e.target.value })}
                      placeholder="Contoh: S1 Manajemen & Bisnis Digital FEB"
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Mode Pembelajaran</label>
                    <select
                      value={newSessionForm.progression_mode}
                      onChange={(e) => setNewSessionForm({ ...newSessionForm, progression_mode: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    >
                      <option value="problem_based">Problem-Based Learning & Kasus Terintegrasi</option>
                      <option value="turn_based">Turn-Based Simulation (Ronde Bulanan Terjadwal)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Total Target Ronde Simulasi</label>
                    <input
                      type="number"
                      min="1"
                      max="24"
                      value={newSessionForm.total_rounds}
                      onChange={(e) => setNewSessionForm({ ...newSessionForm, total_rounds: parseInt(e.target.value) || 12 })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Bagian 2: Penugasan Tim Dosen Pengampu (Team Teaching) */}
              <div className="space-y-3 pt-2 border-t border-slate-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center">
                      <Users className="w-4 h-4 mr-1.5 text-indigo-600" />
                      Penugasan Tim Dosen Pengampu (Team Teaching)
                    </h4>
                    <p className="text-[11px] text-slate-500">Tentukan dosen pengampu dan perannya dalam mengajar kelas ini.</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      const firstDosen = dosenList.length > 0 ? dosenList[0] : null;
                      if (firstDosen) {
                        setNewSessionForm({
                          ...newSessionForm,
                          lecturers: [
                            ...newSessionForm.lecturers,
                            { user_id: firstDosen.id, role_title: "Dosen Pengampu", is_primary: false }
                          ]
                        });
                      }
                    }}
                    className="text-[11px] bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold px-2.5 py-1 rounded-lg border border-indigo-200 transition flex items-center space-x-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Tambah Dosen</span>
                  </button>
                </div>

                <div className="space-y-2.5">
                  {newSessionForm.lecturers.map((lec, idx) => (
                    <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2">
                      <div className="grid grid-cols-1 sm:grid-cols-12 gap-2 items-center">
                        <div className="sm:col-span-5">
                          <label className="block text-[10px] font-bold text-slate-600 mb-0.5">Pilih Dosen:</label>
                          <select
                            value={lec.user_id}
                            onChange={(e) => {
                              const updated = [...newSessionForm.lecturers];
                              updated[idx].user_id = parseInt(e.target.value);
                              setNewSessionForm({ ...newSessionForm, lecturers: updated });
                            }}
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-md text-xs bg-white focus:ring-1 focus:ring-indigo-500"
                          >
                            {dosenList.map((d) => (
                              <option key={d.id} value={d.id}>
                                {d.full_name} ({d.username})
                              </option>
                            ))}
                          </select>
                        </div>

                        <div className="sm:col-span-5">
                          <label className="block text-[10px] font-bold text-slate-600 mb-0.5">Peran / Bidang Dosen:</label>
                          <input
                            type="text"
                            value={lec.role_title}
                            onChange={(e) => {
                              const updated = [...newSessionForm.lecturers];
                              updated[idx].role_title = e.target.value;
                              setNewSessionForm({ ...newSessionForm, lecturers: updated });
                            }}
                            placeholder="Contoh: Dosen Bidang Pemasaran"
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-md text-xs bg-white focus:ring-1 focus:ring-indigo-500"
                          />
                        </div>

                        <div className="sm:col-span-2 flex items-center justify-between sm:justify-end space-x-2 pt-3 sm:pt-4">
                          <label className="flex items-center space-x-1 cursor-pointer text-[11px] text-slate-700" title="Jadikan Koordinator Utama">
                            <input
                              type="radio"
                              name="primary_dosen_add"
                              checked={lec.is_primary}
                              onChange={() => {
                                const updated = newSessionForm.lecturers.map((item, i) => ({
                                  ...item,
                                  is_primary: i === idx
                                }));
                                setNewSessionForm({ ...newSessionForm, lecturers: updated });
                              }}
                              className="w-3.5 h-3.5 text-indigo-600"
                            />
                            <span className="text-[10px] font-semibold">Utama</span>
                          </label>

                          {newSessionForm.lecturers.length > 1 && (
                            <button
                              type="button"
                              onClick={() => {
                                const updated = newSessionForm.lecturers.filter((_, i) => i !== idx);
                                if (lec.is_primary && updated.length > 0) {
                                  updated[0].is_primary = true;
                                }
                                setNewSessionForm({ ...newSessionForm, lecturers: updated });
                              }}
                              className="text-rose-600 hover:text-rose-800 p-1 rounded hover:bg-rose-50"
                              title="Hapus dosen dari tim"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Quick preset role chips */}
                      <div className="flex flex-wrap gap-1 pt-1">
                        <span className="text-[10px] text-slate-400 self-center mr-1">Preset:</span>
                        {[
                          "Koordinator Matakuliah",
                          "Dosen Bidang Pemasaran",
                          "Dosen Bidang SDM",
                          "Dosen Bidang Keuangan & Akuntansi",
                          "Dosen Bidang Manufaktur & Operasional"
                        ].map((rolePreset) => (
                          <button
                            key={rolePreset}
                            type="button"
                            onClick={() => {
                              const updated = [...newSessionForm.lecturers];
                              updated[idx].role_title = rolePreset;
                              setNewSessionForm({ ...newSessionForm, lecturers: updated });
                            }}
                            className="text-[9px] bg-slate-200/70 hover:bg-indigo-100 hover:text-indigo-800 text-slate-700 px-1.5 py-0.5 rounded transition font-mono"
                          >
                            {rolePreset}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bagian 3: Auto-Provisioning Kelompok Praktikan */}
              <div className="space-y-3 pt-2 border-t border-slate-200">
                <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center">
                  <Sliders className="w-4 h-4 mr-1.5 text-emerald-600" />
                  Opsi Otomatisasi Provisioning Kelompok Praktikan
                </h4>

                <div className="bg-emerald-50/50 border border-emerald-200 rounded-lg p-3 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-bold text-emerald-900">Generate Kelompok Mahasiswa Otomatis</span>
                      <p className="text-[11px] text-emerald-700">Langsung siapkan entitas perusahaan sandbox lengkap untuk kelas ini.</p>
                    </div>
                    <span className="font-mono font-bold text-sm bg-emerald-700 text-white px-2.5 py-1 rounded">
                      {newSessionForm.auto_provision_groups} Kelompok
                    </span>
                  </div>

                  <input
                    type="range"
                    min="0"
                    max="12"
                    step="1"
                    value={newSessionForm.auto_provision_groups}
                    onChange={(e) => setNewSessionForm({ ...newSessionForm, auto_provision_groups: parseInt(e.target.value) })}
                    className="w-full accent-emerald-600 cursor-pointer h-2 bg-slate-200 rounded-lg"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                    <span>0 (Kelas Kosong)</span>
                    <span>4 Kelompok (Standar FEB)</span>
                    <span>12 Kelompok (Besar)</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-200 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowAddSessionModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-100 font-semibold"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={isSavingSession}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-md transition flex items-center space-x-1.5 disabled:opacity-60"
                >
                  {isSavingSession ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                  <span>{isSavingSession ? "Memproses..." : "Buat & Simpan Sesi Kelas"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: EDIT SESI KELAS & SUSUNAN TIM DOSEN */}
      {showEditSessionModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-2xl w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 px-6 py-4 text-white flex items-center justify-between border-b border-slate-800 shrink-0">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                  <Edit3 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">Edit Sesi Kelas & Susunan Tim Dosen</h3>
                  <p className="text-[11px] text-indigo-300">Ubah konfigurasi, status kelas, dan penugasan dosen pengampu</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowEditSessionModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateSession} className="p-6 space-y-5 overflow-y-auto text-xs flex-1">
              <div className="space-y-3">
                <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center">
                  <Building2 className="w-4 h-4 mr-1.5 text-indigo-600" />
                  Data Pokok Sesi Kelas
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  <div className="sm:col-span-2">
                    <label className="block font-bold text-slate-700 mb-1">Nama Sesi Kelas *</label>
                    <input
                      type="text"
                      required
                      value={editSessionForm.name}
                      onChange={(e) => setEditSessionForm({ ...editSessionForm, name: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Kode Sesi Kelas *</label>
                    <input
                      type="text"
                      required
                      value={editSessionForm.code}
                      onChange={(e) => setEditSessionForm({ ...editSessionForm, code: e.target.value.toUpperCase() })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono font-bold focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Status Sesi Kelas</label>
                    <select
                      value={editSessionForm.status}
                      onChange={(e) => setEditSessionForm({ ...editSessionForm, status: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none font-bold"
                    >
                      <option value="active">🟢 Aktif (Sedang Berjalan)</option>
                      <option value="archived">🟡 Diarsipkan (Selesai / Non-Aktif)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Semester / Tahun Akademik</label>
                    <input
                      type="text"
                      value={editSessionForm.academic_term}
                      onChange={(e) => setEditSessionForm({ ...editSessionForm, academic_term: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block font-bold text-slate-700 mb-1">Program Studi / Jurusan</label>
                    <input
                      type="text"
                      value={editSessionForm.department}
                      onChange={(e) => setEditSessionForm({ ...editSessionForm, department: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Tim Dosen Editor */}
              <div className="space-y-3 pt-2 border-t border-slate-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center">
                      <Users className="w-4 h-4 mr-1.5 text-indigo-600" />
                      Tim Dosen Pengampu Terdaftar
                    </h4>
                    <p className="text-[11px] text-slate-500">Sesuaikan peran dan anggota dosen untuk sesi kelas ini.</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      const firstDosen = dosenList.length > 0 ? dosenList[0] : null;
                      if (firstDosen) {
                        setEditSessionForm({
                          ...editSessionForm,
                          lecturers: [
                            ...editSessionForm.lecturers,
                            { user_id: firstDosen.id, role_title: "Dosen Pengampu", is_primary: false }
                          ]
                        });
                      }
                    }}
                    className="text-[11px] bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold px-2.5 py-1 rounded-lg border border-indigo-200 transition flex items-center space-x-1"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Tambah Dosen</span>
                  </button>
                </div>

                <div className="space-y-2.5">
                  {editSessionForm.lecturers.map((lec, idx) => (
                    <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2">
                      <div className="grid grid-cols-1 sm:grid-cols-12 gap-2 items-center">
                        <div className="sm:col-span-5">
                          <label className="block text-[10px] font-bold text-slate-600 mb-0.5">Dosen Pengampu:</label>
                          <select
                            value={lec.user_id}
                            onChange={(e) => {
                              const updated = [...editSessionForm.lecturers];
                              updated[idx].user_id = parseInt(e.target.value);
                              setEditSessionForm({ ...editSessionForm, lecturers: updated });
                            }}
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-md text-xs bg-white focus:ring-1 focus:ring-indigo-500"
                          >
                            {dosenList.map((d) => (
                              <option key={d.id} value={d.id}>
                                {d.full_name} ({d.username})
                              </option>
                            ))}
                          </select>
                        </div>

                        <div className="sm:col-span-5">
                          <label className="block text-[10px] font-bold text-slate-600 mb-0.5">Peran / Spesialisasi:</label>
                          <input
                            type="text"
                            value={lec.role_title}
                            onChange={(e) => {
                              const updated = [...editSessionForm.lecturers];
                              updated[idx].role_title = e.target.value;
                              setEditSessionForm({ ...editSessionForm, lecturers: updated });
                            }}
                            className="w-full px-2.5 py-1.5 border border-slate-300 rounded-md text-xs bg-white focus:ring-1 focus:ring-indigo-500"
                          />
                        </div>

                        <div className="sm:col-span-2 flex items-center justify-between sm:justify-end space-x-2 pt-3 sm:pt-4">
                          <label className="flex items-center space-x-1 cursor-pointer text-[11px] text-slate-700">
                            <input
                              type="radio"
                              name="primary_dosen_edit"
                              checked={lec.is_primary}
                              onChange={() => {
                                const updated = editSessionForm.lecturers.map((item, i) => ({
                                  ...item,
                                  is_primary: i === idx
                                }));
                                setEditSessionForm({ ...editSessionForm, lecturers: updated });
                              }}
                              className="w-3.5 h-3.5 text-indigo-600"
                            />
                            <span className="text-[10px] font-semibold">Utama</span>
                          </label>

                          {editSessionForm.lecturers.length > 1 && (
                            <button
                              type="button"
                              onClick={() => {
                                const updated = editSessionForm.lecturers.filter((_, i) => i !== idx);
                                if (lec.is_primary && updated.length > 0) {
                                  updated[0].is_primary = true;
                                }
                                setEditSessionForm({ ...editSessionForm, lecturers: updated });
                              }}
                              className="text-rose-600 hover:text-rose-800 p-1 rounded hover:bg-rose-50"
                              title="Hapus dosen dari tim"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Quick preset role chips */}
                      <div className="flex flex-wrap gap-1 pt-1">
                        <span className="text-[10px] text-slate-400 self-center mr-1">Preset:</span>
                        {[
                          "Koordinator Matakuliah",
                          "Dosen Bidang Pemasaran",
                          "Dosen Bidang SDM",
                          "Dosen Bidang Keuangan & Akuntansi",
                          "Dosen Bidang Manufaktur & Operasional"
                        ].map((rolePreset) => (
                          <button
                            key={rolePreset}
                            type="button"
                            onClick={() => {
                              const updated = [...editSessionForm.lecturers];
                              updated[idx].role_title = rolePreset;
                              setEditSessionForm({ ...editSessionForm, lecturers: updated });
                            }}
                            className="text-[9px] bg-slate-200/70 hover:bg-indigo-100 hover:text-indigo-800 text-slate-700 px-1.5 py-0.5 rounded transition font-mono"
                          >
                            {rolePreset}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-3 border-t border-slate-200 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowEditSessionModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-100 font-semibold"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={isSavingSession}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-md transition flex items-center space-x-1.5 disabled:opacity-60"
                >
                  {isSavingSession ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                  <span>{isSavingSession ? "Menyimpan..." : "Simpan Perubahan Sesi"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: DUPLIKASI / CLONE SESI KELAS */}
      {showCloneSessionModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col">
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 px-6 py-4 text-white flex items-center justify-between border-b border-slate-800 shrink-0">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                  <Copy className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">Duplikasi / Clone Sesi Kelas</h3>
                  <p className="text-[11px] text-indigo-300">Gandakan kurikulum, konfigurasi, dan kelompok ke kelas baru</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowCloneSessionModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCloneSession} className="p-6 space-y-4 text-xs">
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-3">
                <span className="text-[10px] uppercase font-bold text-indigo-600 tracking-wider">Sesi Sumber yang Diduplikasi:</span>
                <div className="font-bold text-sm text-indigo-950 mt-0.5">{cloneSessionForm.source_name}</div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Nama Sesi Kelas Baru *</label>
                <input
                  type="text"
                  required
                  value={cloneSessionForm.new_name}
                  onChange={(e) => setCloneSessionForm({ ...cloneSessionForm, new_name: e.target.value })}
                  placeholder="Contoh: Praktikum ERP - Kelas FEB C (Paralel)"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none font-medium"
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Kode Sesi Kelas Baru (Unik) *</label>
                <input
                  type="text"
                  required
                  value={cloneSessionForm.new_code}
                  onChange={(e) => setCloneSessionForm({ ...cloneSessionForm, new_code: e.target.value.toUpperCase() })}
                  placeholder="Contoh: ERP-FEB-C-PARALEL"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono font-bold focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Semester / Tahun</label>
                  <input
                    type="text"
                    value={cloneSessionForm.academic_term}
                    onChange={(e) => setCloneSessionForm({ ...cloneSessionForm, academic_term: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Program Studi</label>
                  <input
                    type="text"
                    value={cloneSessionForm.department}
                    onChange={(e) => setCloneSessionForm({ ...cloneSessionForm, department: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="space-y-2 pt-2 border-t border-slate-200">
                <label className="flex items-center space-x-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={cloneSessionForm.clone_companies}
                    onChange={(e) => setCloneSessionForm({ ...cloneSessionForm, clone_companies: e.target.checked })}
                    className="w-4 h-4 accent-indigo-600 rounded cursor-pointer"
                  />
                  <div>
                    <span className="font-bold text-slate-800">Duplikasi Kelompok Perusahaan Mahasiswa</span>
                    <p className="text-[10px] text-slate-500">Membuat kelompok sandbox mandiri dengan jumlah yang sama seperti kelas sumber.</p>
                  </div>
                </label>

                <label className="flex items-center space-x-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={cloneSessionForm.differentiate_cases}
                    onChange={(e) => setCloneSessionForm({ ...cloneSessionForm, differentiate_cases: e.target.checked })}
                    className="w-4 h-4 accent-indigo-600 rounded cursor-pointer"
                  />
                  <div>
                    <span className="font-bold text-slate-800">Aktifkan Diferensiasi Masalah Kasus Unik</span>
                    <p className="text-[10px] text-slate-500">Mengacak skenario kasus antar kelompok agar tidak dapat saling meniru jawaban.</p>
                  </div>
                </label>
              </div>

              <div className="pt-3 border-t border-slate-200 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowCloneSessionModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-100 font-semibold"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={isSavingSession}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-md transition flex items-center space-x-1.5 disabled:opacity-60"
                >
                  {isSavingSession ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{isSavingSession ? "Menduplikasi..." : "Eksekusi Duplikasi Kelas"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: EDIT USER & UBAH PASSWORD */}
      {showEditUserModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="px-6 py-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                  <KeyRound className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold">Ubah Username & Password</h3>
                  <p className="text-[11px] text-slate-300">ID Pengguna: #{editUserForm.id}</p>
                </div>
              </div>
              <button
                onClick={() => setShowEditUserModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveUser} className="p-6 space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Username (Login ID) <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={editUserForm.username}
                  onChange={(e) => setEditUserForm({ ...editUserForm, username: e.target.value })}
                  placeholder="Contoh: dosen.marketing / kelompok1"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono font-bold focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                <p className="text-[10px] text-slate-400 mt-1">Username digunakan untuk masuk (login) ke platform.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Nama Lengkap Pengguna</label>
                  <input
                    type="text"
                    value={editUserForm.full_name}
                    onChange={(e) => setEditUserForm({ ...editUserForm, full_name: e.target.value })}
                    placeholder="Contoh: Dr. Budi Santoso, M.M."
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Role / Hak Akses</label>
                  <select
                    value={editUserForm.role}
                    onChange={(e) => setEditUserForm({ ...editUserForm, role: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none font-semibold"
                  >
                    <option value="MAHASISWA">MAHASISWA (Kelompok Bisnis)</option>
                    <option value="DOSEN">DOSEN (Dosen Pengampu FEB)</option>
                    <option value="ADMIN">ADMIN (Super Administrator)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Email Pengguna</label>
                <input
                  type="email"
                  value={editUserForm.email}
                  onChange={(e) => setEditUserForm({ ...editUserForm, email: e.target.value })}
                  placeholder="email@vlab.edu"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Penugasan Sesi Kelas</label>
                  <select
                    value={editUserForm.session_id}
                    onChange={(e) => setEditUserForm({ ...editUserForm, session_id: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value={0}>Tidak Ditugaskan / Umum</option>
                    {sessions.map(s => (
                      <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Perusahaan Tenant Kelompok</label>
                  <select
                    value={editUserForm.company_id}
                    onChange={(e) => setEditUserForm({ ...editUserForm, company_id: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value={0}>Tanpa Tenant / Akun Umum</option>
                    {companies.map(c => (
                      <option key={c.id} value={c.id}>{c.name} (Sesi #{c.session_id})</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-200">
                <div className="flex items-center justify-between mb-1">
                  <label className="block font-bold text-slate-900">
                    Password Baru (Opsional)
                  </label>
                  <span className="text-[10px] text-slate-500">Kosongkan jika tidak ingin mengubah password</span>
                </div>
                <div className="relative">
                  <input
                    type={showPasswordInModal ? "text" : "password"}
                    value={editUserForm.password}
                    onChange={(e) => setEditUserForm({ ...editUserForm, password: e.target.value })}
                    placeholder="Ketik password baru untuk akun ini..."
                    className="w-full pl-3 pr-10 py-2 border border-slate-300 rounded-lg font-mono focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswordInModal(!showPasswordInModal)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                    title={showPasswordInModal ? "Sembunyikan password" : "Lihat password"}
                  >
                    {showPasswordInModal ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>

                {/* Quick Presets */}
                <div className="mt-2 flex items-center space-x-2 text-[11px]">
                  <span className="text-slate-500">Preset cepat:</span>
                  <button
                    type="button"
                    onClick={() => setEditUserForm({ ...editUserForm, password: "admin123" })}
                    className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100 font-mono font-bold"
                  >
                    admin123
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditUserForm({ ...editUserForm, password: "dosen123" })}
                    className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 font-mono font-bold"
                  >
                    dosen123
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditUserForm({ ...editUserForm, password: "mhs123" })}
                    className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 font-mono font-bold"
                  >
                    mhs123
                  </button>
                </div>
              </div>

              <div className="pt-4 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowEditUserModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={isSavingUser}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-md transition flex items-center space-x-1.5"
                >
                  {isSavingUser ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Menyimpan...</span>
                    </>
                  ) : (
                    <>
                      <Check className="w-4 h-4" />
                      <span>Simpan Perubahan</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: BUAT PENGGUNA BARU */}
      {showCreateUserModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="px-6 py-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                  <Plus className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold">Buat Akun Pengguna Baru</h3>
                  <p className="text-[11px] text-slate-300">Tambah Dosen, Asisten, atau Kelompok Mahasiswa</p>
                </div>
              </div>
              <button
                onClick={() => setShowCreateUserModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="p-6 space-y-4 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Username (Login ID) <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={newUserForm.username}
                  onChange={(e) => setNewUserForm({ ...newUserForm, username: e.target.value.toLowerCase() })}
                  placeholder="Contoh: dosen.sdm / kelompok7"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono font-bold focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Nama Lengkap Pengguna</label>
                  <input
                    type="text"
                    value={newUserForm.full_name}
                    onChange={(e) => setNewUserForm({ ...newUserForm, full_name: e.target.value })}
                    placeholder="Contoh: Tim Kelompok 7 Bisnis"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Role / Hak Akses</label>
                  <select
                    value={newUserForm.role}
                    onChange={(e) => setNewUserForm({ ...newUserForm, role: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none font-semibold"
                  >
                    <option value="MAHASISWA">MAHASISWA (Kelompok Bisnis)</option>
                    <option value="DOSEN">DOSEN (Dosen Pengampu FEB)</option>
                    <option value="ADMIN">ADMIN (Super Administrator)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-bold text-slate-700 mb-1">Email (Opsional)</label>
                <input
                  type="email"
                  value={newUserForm.email}
                  onChange={(e) => setNewUserForm({ ...newUserForm, email: e.target.value })}
                  placeholder="kelompok7@vlab.edu"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Penugasan Sesi Kelas</label>
                  <select
                    value={newUserForm.session_id}
                    onChange={(e) => setNewUserForm({ ...newUserForm, session_id: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value={0}>Tidak Ditugaskan / Umum</option>
                    {sessions.map(s => (
                      <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block font-bold text-slate-700 mb-1">Perusahaan Tenant Kelompok</label>
                  <select
                    value={newUserForm.company_id}
                    onChange={(e) => setNewUserForm({ ...newUserForm, company_id: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  >
                    <option value={0}>Tanpa Tenant / Akun Umum</option>
                    {companies.map(c => (
                      <option key={c.id} value={c.id}>{c.name} (Sesi #{c.session_id})</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block font-bold text-slate-700">
                    Password <span className="text-rose-500">*</span>
                  </label>
                  <span className="text-[10px] text-slate-500">Minimal 4 karakter</span>
                </div>
                <div className="relative">
                  <input
                    type={showPasswordInModal ? "text" : "password"}
                    required
                    value={newUserForm.password}
                    onChange={(e) => setNewUserForm({ ...newUserForm, password: e.target.value })}
                    placeholder="Masukkan password awal..."
                    className="w-full pl-3 pr-10 py-2 border border-slate-300 rounded-lg font-mono focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswordInModal(!showPasswordInModal)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                  >
                    {showPasswordInModal ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {/* Quick Presets */}
                <div className="mt-2 flex items-center space-x-2 text-[11px]">
                  <span className="text-slate-500">Preset cepat:</span>
                  <button
                    type="button"
                    onClick={() => setNewUserForm({ ...newUserForm, password: "mhs123" })}
                    className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 font-mono font-bold"
                  >
                    mhs123
                  </button>
                  <button
                    type="button"
                    onClick={() => setNewUserForm({ ...newUserForm, password: "dosen123" })}
                    className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 font-mono font-bold"
                  >
                    dosen123
                  </button>
                </div>
              </div>

              <div className="pt-4 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowCreateUserModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={isSavingUser}
                  className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-md transition flex items-center space-x-1.5"
                >
                  {isSavingUser ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Menyimpan...</span>
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      <span>Buat Akun</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: QUICK RESET PASSWORD */}
      {showQuickPasswordModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-sm w-full overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="px-5 py-3.5 bg-gradient-to-r from-slate-900 to-indigo-950 text-white flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <KeyRound className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-bold">Ganti Password: {quickPasswordForm.username}</h3>
              </div>
              <button
                onClick={() => setShowQuickPasswordModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleSaveQuickPassword} className="p-5 space-y-3 text-xs">
              <div>
                <label className="block font-bold text-slate-700 mb-1">Password Baru</label>
                <input
                  type="text"
                  required
                  value={quickPasswordForm.password}
                  onChange={(e) => setQuickPasswordForm({ ...quickPasswordForm, password: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg font-mono focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  placeholder="Masukkan password baru..."
                />
                <div className="mt-2 flex items-center space-x-1.5 text-[10px]">
                  <span className="text-slate-500">Preset:</span>
                  <button
                    type="button"
                    onClick={() => setQuickPasswordForm({ ...quickPasswordForm, password: "mhs123" })}
                    className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-mono font-bold"
                  >
                    mhs123
                  </button>
                  <button
                    type="button"
                    onClick={() => setQuickPasswordForm({ ...quickPasswordForm, password: "dosen123" })}
                    className="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 font-mono font-bold"
                  >
                    dosen123
                  </button>
                  <button
                    type="button"
                    onClick={() => setQuickPasswordForm({ ...quickPasswordForm, password: "admin123" })}
                    className="px-2 py-0.5 rounded bg-purple-50 text-purple-700 border border-purple-200 font-mono font-bold"
                  >
                    admin123
                  </button>
                </div>
              </div>
              <div className="pt-3 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowQuickPasswordModal(false)}
                  className="px-3 py-1.5 border border-slate-300 rounded-lg text-slate-600 font-semibold"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={isSavingUser}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg shadow-sm transition"
                >
                  {isSavingUser ? "Menyimpan..." : "Simpan Password"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: DELETE CONFIRMATION DIALOG */}
      {userToDelete && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-start space-x-3.5">
              <div className="w-10 h-10 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center shrink-0">
                <Trash2 className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <h3 className="text-base font-bold text-slate-900">Konfirmasi Hapus Akun</h3>
                <p className="text-xs text-slate-500 mt-1">
                  Apakah Anda yakin ingin menghapus permanen akun pengguna berikut?
                </p>
                <div className="mt-3 bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-1.5 text-xs">
                  <div><span className="font-bold text-slate-700">Username:</span> <span className="font-mono text-slate-900 font-bold">{userToDelete.username}</span></div>
                  <div><span className="font-bold text-slate-700">Nama:</span> <span className="text-slate-900">{userToDelete.full_name || "-"}</span></div>
                  <div><span className="font-bold text-slate-700">Role:</span> <span className="text-slate-900 font-semibold">{userToDelete.role}</span></div>
                  {userToDelete.company_name && (
                    <div><span className="font-bold text-slate-700">Tenant:</span> <span className="text-slate-900">{userToDelete.company_name}</span></div>
                  )}
                </div>
                <p className="text-[11px] text-rose-600 font-medium mt-2">
                  ⚠️ Tindakan ini akan menghapus akun dari sistem dan tidak dapat dibatalkan.
                </p>
              </div>
            </div>
            <div className="mt-6 flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setUserToDelete(null)}
                className="px-4 py-2 border border-slate-300 rounded-xl text-slate-600 hover:bg-slate-100 font-semibold text-xs"
              >
                Batal
              </button>
              <button
                type="button"
                disabled={isDeletingUser}
                onClick={handleConfirmDeleteUser}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white font-bold rounded-xl text-xs shadow-md transition flex items-center space-x-1.5"
              >
                {isDeletingUser ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Menghapus...</span>
                  </>
                ) : (
                  <>
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Ya, Hapus Akun Ini</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* MODAL: INTERACTIVE OFFICIAL BUSINESS DOCUMENT VIEWER */}
      {/* ========================================================= */}
      {activeDocument && (
        <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full border border-slate-300 p-8 animate-in fade-in zoom-in-95 text-slate-900 space-y-6">
            {/* Formal Indonesian Corporate / Legal Kop Surat */}
            <div className="border-b-4 border-double border-slate-900 pb-4 text-center">
              <div className="text-[11px] font-black uppercase tracking-widest text-slate-500">
                REPUBLIK INDONESIA • LEMBAR DOKUMEN RESMI KORPORASI
              </div>
              <h2 className="text-lg font-black tracking-tight text-slate-900 uppercase mt-1">
                {activeDocument.title || "DOKUMEN RESMI KESEPAKATAN BISNIS"}
              </h2>
              <div className="text-xs text-slate-600 font-serif italic mt-0.5">
                VLab-ERP Enterprise Legal & Compliance Repository • FEB
              </div>
            </div>

            {/* Meta Information Bar */}
            <div className="grid grid-cols-2 gap-3 text-xs bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <div>
                <span className="font-bold text-slate-500 block text-[10px] uppercase">Pihak Dituju / Penerima:</span>
                <span className="font-bold text-slate-900">{activeDocument.recipient || "Direksi & Manajemen Terkait"}</span>
              </div>
              <div>
                <span className="font-bold text-slate-500 block text-[10px] uppercase">Klasifikasi Dokumen:</span>
                <span className="font-mono font-bold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
                  {activeDocument.type || "LEGAL_AGREEMENT"}
                </span>
              </div>
            </div>

            {/* Document Content / Klausul */}
            <div className="space-y-3 text-xs leading-relaxed font-serif text-slate-800 bg-amber-50/20 p-4 rounded-xl border border-amber-200/50">
              <div className="font-sans font-bold text-slate-900 text-xs mb-1 uppercase tracking-wider">
                Ringkasan Klausul & Ketetapan Manajerial:
              </div>
              <p className="whitespace-pre-line text-justify">
                {activeDocument.summary || "Dokumen ini menetapkan kesepakatan resmi dan komitmen operasional yang mengikat antara para pihak sesuai regulasi yang berlaku."}
              </p>
            </div>

            {/* Digital Stamp & Signatures */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200 text-xs text-center">
              <div className="space-y-12">
                <span className="text-[11px] text-slate-500 font-semibold block">Pihak Pertama / Pemohon</span>
                <div>
                  <div className="font-bold text-slate-900 underline">Direksi Operasional</div>
                  <div className="text-[10px] text-slate-500 font-mono">PT Inovasi Cipta Mandiri</div>
                </div>
              </div>
              <div className="space-y-12 relative">
                <span className="text-[11px] text-slate-500 font-semibold block">Pihak Kedua / Pengesah</span>
                {/* Visual Stamp Watermark */}
                <div className="absolute top-4 left-1/2 -translate-x-1/2 w-20 h-20 border-2 border-emerald-600/60 rounded-full flex items-center justify-center rotate-[-12deg] pointer-events-none">
                  <span className="text-[9px] font-black text-emerald-700 uppercase tracking-tighter text-center">
                    TERVERIFIKASI<br />LEGAL DIGITAL
                  </span>
                </div>
                <div>
                  <div className="font-bold text-slate-900 underline">{activeDocument.recipient || "Mitra / Otoritas Terkait"}</div>
                  <div className="text-[10px] text-slate-500 font-mono">Tanda Tangan Elektronik Sah</div>
                </div>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="pt-4 flex justify-between items-center border-t border-slate-200">
              <button
                type="button"
                onClick={() => window.print()}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold rounded-xl text-xs transition flex items-center space-x-1.5"
              >
                <Download className="w-4 h-4 text-slate-600" />
                <span>Cetak / Simpan PDF (Print Preview)</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveDocument(null)}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl text-xs shadow-md transition"
              >
                Tutup Dokumen
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* MODAL: DYNAMIC DOMINO RIPPLE EFFECT VISUALIZER */}
      {/* ========================================================= */}
      {activeRippleEvent && (
        <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-xl w-full border border-slate-200 p-6 animate-in fade-in zoom-in-95 space-y-5">
            <div className="flex items-start space-x-3.5 border-b border-slate-100 pb-4">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center shrink-0">
                <Sparkles className="w-6 h-6 animate-pulse" />
              </div>
              <div className="flex-1">
                <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-200">
                  Causality & Multi-Order Ripple Engine
                </span>
                <h3 className="text-base font-extrabold text-slate-900 mt-1">
                  Dampak Domino Keputusan Lintas Departemen
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {activeRippleEvent.scenario_title || "Keputusan Cabang Manajerial"}
                </p>
              </div>
              <button
                onClick={() => setActiveRippleEvent(null)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Rationale & CFO Verdict */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2 text-xs">
              <div>
                <span className="font-bold text-slate-700 block">Pilihan Cabang:</span>
                <span className="font-semibold text-slate-900">{activeRippleEvent.choice_label}</span>
              </div>
              <div>
                <span className="font-bold text-slate-700 block">Evaluasi Strategis Smart CFO:</span>
                <span className="text-slate-600 italic">{activeRippleEvent.cfo_verdict || activeRippleEvent.summary}</span>
              </div>
            </div>

            {/* Department Domino Impact Grid */}
            <div className="space-y-2">
              <div className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Rantai Konsekuensi Departemen:
              </div>
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {activeRippleEvent.ripples?.map((rip: any, idx: number) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-xl border text-xs flex items-center justify-between ${
                      rip.type === "positive"
                        ? "bg-emerald-50/80 border-emerald-200 text-emerald-950"
                        : rip.type === "negative"
                        ? "bg-rose-50/80 border-rose-200 text-rose-950"
                        : "bg-slate-100 border-slate-200 text-slate-900"
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className={`w-2.5 h-2.5 rounded-full ${
                        rip.type === "positive" ? "bg-emerald-500" : rip.type === "negative" ? "bg-rose-500" : "bg-slate-500"
                      }`} />
                      <span className="font-bold">{rip.dept}:</span>
                      <span>{rip.effect}</span>
                    </div>
                    <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                      rip.type === "positive" ? "bg-emerald-100 text-emerald-800" : rip.type === "negative" ? "bg-rose-100 text-rose-800" : "bg-slate-200 text-slate-700"
                    }`}>
                      {rip.type}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="pt-3 flex justify-between items-center border-t border-slate-200">
              {activeRippleEvent.document ? (
                <button
                  type="button"
                  onClick={() => {
                    const doc = activeRippleEvent.document;
                    setActiveRippleEvent(null);
                    setActiveDocument(doc);
                  }}
                  className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 text-indigo-700 font-bold rounded-xl text-xs transition flex items-center space-x-1.5 shadow-sm"
                >
                  <FileText className="w-4 h-4 text-indigo-600" />
                  <span>Lihat Dokumen Resmi Diterbitkan</span>
                </button>
              ) : <div />}
              <button
                type="button"
                onClick={() => setActiveRippleEvent(null)}
                className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-xs transition"
              >
                Tutup Notifikasi
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

```


---
# FILE: frontend/src/app/layout.tsx
---
```tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VLab-ERP: Virtual Lab & Business Simulation Platform",
  description: "Platform simulasi modular ERP terpadu untuk pembelajaran mahasiswa",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <body className="antialiased min-h-screen flex flex-col bg-slate-100 text-slate-900">
        {children}
      </body>
    </html>
  );
}

```


---
# FILE: frontend/next.config.mjs
---
```tsx
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://127.0.0.1:8281';
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;

```


---
# FILE: docker-compose.yml
---
```tsx
name: vlaberp

# CasaOS Application Metadata
x-casaos:
  architectures:
    - amd64
    - arm64
    - arm
  main: frontend
  author: VLab-ERP
  category: Educational
  description:
    en_us: "VLab-ERP: Virtual Lab & Business Simulation Platform for Enterprise Resource Planning (FastAPI + Next.js)."
  developer: VLab-ERP FEB
  icon: https://cdn-icons-png.flaticon.com/512/9167/9167018.png
  index: /
  port_map: "8280"
  scheme: http
  title:
    en_us: VLab-ERP

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      network: host
    image: vlaberp-backend:latest
    container_name: vlaberp-backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=sqlite:////app/data/vlaberp.db
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
    ports:
      - "8281:8281"
    networks:
      - vlaberp-net

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      network: host
    image: vlaberp-frontend:latest
    container_name: vlaberp-frontend
    restart: unless-stopped
    environment:
      - BACKEND_URL=http://backend:8281
      - NODE_ENV=production
    ports:
      - "8280:8280"
    depends_on:
      - backend
    networks:
      - vlaberp-net

networks:
  vlaberp-net:
    driver: bridge

```
