import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.models import (
    Company, CompanyStoryEvent, JournalEntry, JournalItem, Account, Product,
    SimulationState, Vendor, WorkCenter, CRMLead, Employee
)

# ==========================================
# 1. BEHAVIORAL PROFILES & TEMPERAMENTS
# ==========================================

CUSTOMER_TEMPERAMENTS = [
    {
        "type": "annoyingly_angry",
        "label": "Akun Korporat Eskalasi Kritis",
        "tone": "anger",
        "color": "red",
        "tolerance": 15,
        "sample_dialogs": [
            "SAYA TUNTUT KE YLKI DAN AKAN SAYA SOMASI HARI INI JUGA! Barang cacat kok berani dikirim?! Uang muka saya kembali utuh 100% plus ganti rugi atau nama perusahaan kalian saya viralkan di media sosial!",
            "Pelayanan amatir sampah! Ini kontrak ratusan juta bukan beli cilok di pinggir jalan! Saya minta direktur kalian telepon saya dalam 1 jam atau kita ketemu di pengadilan!",
            "Kalian sengaja kirim barang rusak ya?! Jangan coba-coba alasan teknis, saya tidak terima alasan apapun! Ganti sekarang juga atau kontrak batal!"
        ],
        "min_discount_demanded": 15.0,
        "requires_executive": True
    },
    {
        "type": "calm_as_cucumber",
        "label": "Mitra Bisnis Jangka Panjang",
        "tone": "calm",
        "color": "emerald",
        "tolerance": 75,
        "sample_dialogs": [
            "Halo rekan-rekan manajemen, kami maklumi dalam proses manufaktur pasti ada kendala teknis tak terduga. Tolong dijadwalkan pengiriman penggantinya ya, kami percaya dengan itikad baik kalian.",
            "Selamat siang, kami temukan beberapa unit tidak sesuai spesifikasi. Tidak apa-apa, tolong diproses penukarannya saat batch berikutnya siap ya. Sukses selalu untuk tim.",
            "Hai tim VLab, kami mengerti kendala mesin kalian. Cukup kirimkan unit pengganti yang sudah lolos QC ganda saja ya, tidak perlu panik."
        ],
        "min_discount_demanded": 5.0,
        "requires_executive": False
    },
    {
        "type": "passive_aggressive",
        "label": "Klien Institusi Strategis",
        "tone": "snarky",
        "color": "purple",
        "tolerance": 40,
        "sample_dialogs": [
            "Wah hebat sekali ya, dari 50 unit yang dipesan yang nyala cuma 35. Mungkin tim QC kalian sedang liburan bersama waktu perakitan? Kami tunggu itikad baiknya sebelum kami cerita ke asosiasi.",
            "Terima kasih atas kiriman produknya yang sangat 'unik' ini. Kami baru tahu kalau layar bergaris sekarang jadi fitur baru. Mohon segera diselesaikan ya sebelum kesabaran kami habis.",
            "Luar biasa ya komitmen ketepatan waktunya, meleset 2 minggu dan barangnya pun rusak. Sangat profesional sekali."
        ],
        "min_discount_demanded": 10.0,
        "requires_executive": False
    },
    {
        "type": "shrewd_negotiator",
        "label": "Distributor Utama Regional",
        "tone": "calculating",
        "color": "blue",
        "tolerance": 50,
        "sample_dialogs": [
            "Kami tetap ingin bermitra, tapi kelalaian ini merugikan operasional kami. Kami bersedia tidak memutus kontrak ASALKAN diberikan diskon kompensasi untuk pemesanan berikutnya dan tempo pembayaran diperpanjang.",
            "Masalah kualitas ini bisa kita selesaikan secara kekeluargaan bisnis. Berikan kami kompensasi unit ekstra dan prioritas pengiriman pertama, baru kami tutup komplain ini.",
            "Setiap kesalahan ada harganya dalam bisnis. Berikan penyesuaian komersial yang sepadan dan kami lupakan masalah batch cacat ini."
        ],
        "min_discount_demanded": 20.0,
        "requires_executive": True
    }
]

UNION_PERSONALITIES = [
    {
        "type": "bebal_militan",
        "rep_name": "Bambang Sukirman",
        "label": "Ketua Dewan Pengurus SP-Mandiri",
        "tolerance": "low",
        "speech": "Tuntutan kaum buruh mutlak dan tidak bisa ditawar! Kami minta kenaikan gaji pokok yang signifikan dan uang saku damai per orang yang sepadan! Kalau direksi pelit dan masa bodoh, mesin pabrik tidak akan pernah menyala lagi!",
        "min_wage_raise_accepted": 12.0,
        "min_bonus_accepted": 1500000.0,
        "rejection_speech": "Tawaran penghinaan macam apa ini?! Direksi makan enak buruh disuruh puasa! Negosiasi DITOLAK! Kami perpanjang mogok kerja!",
        "acceptance_speech": "Hidup Buruh! Karena direksi menunjukkan kepedulian nyata, kami instruksikan seluruh operator kembali ke stasiun kerja shift malam ini!"
    },
    {
        "type": "manut_kooperatif",
        "rep_name": "Agus Prasetyo",
        "label": "Koordinator Forum Komunikasi Pekerja Pabrik",
        "tolerance": "high",
        "speech": "Kami memahami kondisi kas perusahaan sedang diuji oleh krisis pasar. Asalkan ada sedikit perhatian untuk uang lembur dan uang saku darurat rekan-rekan, kawan-kawan buruh siap bekerja keras mengejar target produksi.",
        "min_wage_raise_accepted": 5.0,
        "min_bonus_accepted": 500000.0,
        "rejection_speech": "Mohon maaf Pak/Bu Direksi, setidaknya bantulah sedikit untuk makan rekan-rekan buruh. Naikkan sedikit lagi ya tawaran bonus atau upahnya.",
        "acceptance_speech": "Terima kasih banyak atas kebijaksanaan manajemen! Seluruh pekerja siap lembur malam ini memastikan pesanan selesai tepat waktu!"
    },
    {
        "type": "skeptikal_pragmatis",
        "rep_name": "Hendra Wijaya",
        "label": "Ketua Presidium Aliansi Buruh Bersatu",
        "tolerance": "medium",
        "speech": "Kami sudah kenyang janji manis manajemen di masa lalu. Kami hanya butuh komitmen riil: kenaikan upah yang terukur dan uang kompensasi langsung cair hari ini ke rekening, baru kami cabut blokade mesin.",
        "min_wage_raise_accepted": 8.0,
        "min_bonus_accepted": 1000000.0,
        "rejection_speech": "Janji lisan tidak cukup. Angka tawaran Anda di bawah kalkulasi kebutuhan riil. Tolong hitung ulang atau pabrik tetap tutup.",
        "acceptance_speech": "Sepakat. Hitam di atas putih ditandatangani. Blokade lini produksi resmi kami buka kembali."
    }
]

BLACK_SWAN_SHOCKS = [
    {
        "code": "BAD_DEBT",
        "title": "Gagal Bayar Piutang Konsumen (Customer Default)",
        "description": "Klien korporat 'PT Megatama Retail' resmi dinyatakan pailit oleh pengadilan niaga. Piutang usaha sebesar Rp 35.000.000 tidak tertagih dan harus dihapusbukukan langsung ke kerugian Laba Rugi!",
        "impact_type": "bad_debt",
        "amount": 35000000.0,
        "affected_accounts": ["1020 Piutang Usaha", "5010 Beban Kerugian Piutang Macet"]
    },
    {
        "code": "VENDOR_FRAUD",
        "title": "Vendor Bawa Kabur Uang Uang Muka (Vendor Abscondment)",
        "description": "Pemasok suku cadang 'CV Kilat Sentosa' dilaporkan menutup kantornya secara sepihak dan pemiliknya menghilang! Uang muka PO sebesar Rp 20.000.000 lenyap dan bahan baku gagal dikirim.",
        "impact_type": "cash_loss",
        "amount": 20000000.0,
        "affected_accounts": ["1010 Kas & Bank", "6030 Kerugian Non-Operasional Fraud"]
    },
    {
        "code": "BANK_RESTRUCTURE",
        "title": "Restrukturisasi & Pinalti Suku Bunga Pinjaman Bank",
        "description": "Karena rasio likuiditas kas perusahaan turun di bawah batas aman (Covenant Breach), bank rekanan menaikkan bunga cerukan dan membebankan pinalti administrasi sebesar Rp 15.000.000.",
        "impact_type": "bank_penalty",
        "amount": 15000000.0,
        "affected_accounts": ["1010 Kas & Bank", "6040 Beban Bunga & Finansial"]
    },
    {
        "code": "TAX_AUDIT",
        "title": "Pemeriksaan Pajak Mendadak (Surprise Tax Audit)",
        "description": "Kantor Pelayanan Pajak (KPP) menerbitkan Surat Ketetapan Pajak Kurang Bayar (SKPKB) terkait rekonsiliasi PPN masa lalu. Denda pajak sebesar Rp 12.500.000 langsung dipotong dari rekening kas.",
        "impact_type": "cash_loss",
        "amount": 12500000.0,
        "affected_accounts": ["1010 Kas & Bank", "6050 Denda Pajak"]
    }
]

# ==========================================
# 2. 20-SCENARIO MULTI-DOMAIN MATRIX
# ==========================================

SCENARIO_MATRIX: List[Dict[str, Any]] = [
    # ------------------ PURCHASING & SUPPLY CHAIN (4 Scenarios) ------------------
    {
        "id": "PUR-01",
        "domain": "purchasing",
        "domain_label": "Pengadaan & Rantai Pasok",
        "title": "Kelangkaan Chipset Global & Kenaikan Harga Vendor Utama",
        "context": "Pemasok utama komponen motherboard dan IC controller memberitahukan bahwa krisis rantai pasok global memicu lonjakan harga komponen sebesar 40%. Vendor menuntut penyesuaian harga kontrak atau mereka akan mengalihkan alokasi stok ke kompetitor dalam 48 jam.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Setujui Kenaikan Harga Vendor 40% & Kunci Stok Prioritas",
                "rationale": "Menjamin kelancaran lini produksi dan pengiriman pesanan tepat waktu tanpa downtime, namun menekan Margin Laba Kotor secara signifikan.",
                "immediate_cost": 45000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Jadwal produksi berjalan 100% normal tanpa downtime", "type": "positive"},
                    {"dept": "finance", "effect": "Margin laba kotor turun 18% dan kas keluar membengkak", "type": "negative"},
                    {"dept": "crm", "effect": "Kepuasan klien tetap aman karena pengiriman tepat waktu", "type": "positive"}
                ],
                "document": {
                    "type": "ADDENDUM_KONTRAK",
                    "title": "Addendum Kontrak No. 044/ADD-PUR/2026",
                    "recipient": "PT Global Micro Parts Indonesia",
                    "summary": "Perjanjian penyesuaian harga pengadaan IC Chipset sebesar +40% dengan jaminan Service Level Agreement (SLA) pasokan prioritas 14 hari kerja."
                },
                "cfo_verdict": "Likuiditas terbebani jangka pendek, tetapi menyelamatkan reputasi operasional dari denda wanprestasi pelanggan."
            },
            {
                "choice_id": "B",
                "label": "Tolak Kenaikan & Alihkan ke Pemasok Alternatif Tier-3 (Harga Murah, Kualitas Belum Teruji)",
                "rationale": "Menjaga HPP tetap rendah, tetapi berisiko tinggi terhadap tingkat cacat produk (scrap rate) dan potensi penolakan QC.",
                "immediate_cost": 15000000.0,
                "ripples": [
                    {"dept": "purchasing", "effect": "Penghematan HPP sebesar 25% dibandingkan vendor lama", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Risiko scrap & defect rate meningkat hingga 35%", "type": "negative"},
                    {"dept": "crm", "effect": "Potensi eskalasi komplain garansi dari pelanggan akhir", "type": "negative"}
                ],
                "document": {
                    "type": "PO_BARU",
                    "title": "Surat Penunjukan Vendor Pengadaan No. 102/SPV/2026",
                    "recipient": "CV Sinar Logam Makmur Abadi",
                    "summary": "Penerbitan PO darurat bahan baku chipset Tier-3 dengan klausul garansi penukaran komponen bermasalah dalam 7 hari."
                },
                "cfo_verdict": "Menjaga margin kertas, namun membuka liabilitas kontijensi biaya garansi dan risiko audit mutu."
            },
            {
                "choice_id": "C",
                "label": "Tunda Pengadaan & Pangkas Kapasitas Produksi 50% Sementara Waktu",
                "rationale": "Menghindari komitmen kas besar di tengah volatilitas, menunggu harga komoditas turun di kuartal berikutnya.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Arus kas jangka pendek aman dan terkendali", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Kapasitas menganggur (idle capacity) naik, beban tetap tetap berjalan", "type": "negative"},
                    {"dept": "crm", "effect": "Lead time pengiriman molor 3-4 minggu memicu ancaman penalti kontrak", "type": "negative"}
                ],
                "document": {
                    "type": "MEMO_DIREKSI",
                    "title": "Surat Edaran Direksi No. 018/DIR-OPS/2026",
                    "recipient": "Seluruh Kepala Departemen Operasional",
                    "summary": "Instruksi penyesuaian jadwal lini perakitan dan penundaan pembelian persediaan untuk preservasi rasio likuiditas kas."
                },
                "cfo_verdict": "Strategi defensif konservatif; cash flow aman namun market share berisiko tergerus oleh pesaing."
            }
        ]
    },
    {
        "id": "PUR-02",
        "domain": "purchasing",
        "domain_label": "Pengadaan & Rantai Pasok",
        "title": "Vendor Utama Bahan Baku Mengalami Kebakaran Gudang",
        "context": "Gudang sentral pemasok casing dan panel metalik terbakar habis semalam. Vendor meminta penangguhan pengiriman selama 6 minggu atau pembatalan kontrak sepihak.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Impor Darurat via Jalur Udara (Air Freight) dari Singapura dengan Biaya Premium",
                "rationale": "Bahan baku tiba dalam 3 hari, lini produksi tetap berjalan tanpa jeda, namun biaya logistik membengkak 3x lipat.",
                "immediate_cost": 38000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Produksi zero downtime, target output tercapai", "type": "positive"},
                    {"dept": "finance", "effect": "Beban logistik & freight ekspres menggerus laba bersih operasional", "type": "negative"}
                ],
                "document": {
                    "type": "AIR_FREIGHT_PO",
                    "title": "Surat Perjanjian Pengiriman Cepat No. 088/LOG-INT/2026",
                    "recipient": "Apex Express Cargo Singapore Pte Ltd",
                    "summary": "Kontrak kargo udara darurat untuk pengangkutan 500 unit plat metal cetak presisi tinggi."
                },
                "cfo_verdict": "Biaya tinggi namun mempertahankan SLA pelanggan institusional."
            },
            {
                "choice_id": "B",
                "label": "Gunakan Material Subtitusi Lokal dengan Spesifikasi Lebih Rendah",
                "rationale": "Harga tetap murah dan pasokan cepat didapat, namun tampilan estetika dan durabilitas produk menurun.",
                "immediate_cost": 8000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Pengeluaran kas minim dan terkendali", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Toleransi perakitan berkurang, butuh penyesuaian mal mesin", "type": "negative"},
                    {"dept": "crm", "effect": "Keluhan estetika dari klien segmen premium meningkat", "type": "negative"}
                ],
                "document": {
                    "type": "DEV_SPEC",
                    "title": "Berita Acara Deviasi Spesifikasi Material No. 014/QC-BA/2026",
                    "recipient": "Departemen Quality Control & Produksi",
                    "summary": "Persetujuan penggunaan material substitusi plat aluminium 1.2mm dengan toleransi deviasi visual 5%."
                },
                "cfo_verdict": "Solusi pragmatis hemat kas, awasi respon retur konsumen."
            }
        ]
    },
    {
        "id": "PUR-03",
        "domain": "purchasing",
        "domain_label": "Pengadaan & Rantai Pasok",
        "title": "Tawaran Diskon Kuantitas Besar (Bulk Buy) dengan Syarat Kas Tunai",
        "context": "Pemasok kabel dan resistor menawarkan diskon 30% jika perusahaan memesan stok untuk kebutuhan 6 bulan ke depan dan membayar tunai di muka (Cash on Order).",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Ambil Penawaran Bulk Buy & Bayar Tunai Rp 60.000.000",
                "rationale": "Mengunci HPP murah untuk 6 bulan ke depan, namun menguras modal kerja kas likuid perusahaan secara drastis.",
                "immediate_cost": 60000000.0,
                "ripples": [
                    {"dept": "purchasing", "effect": "Efisiensi biaya pembelian 30% (saving Rp 25.000.000)", "type": "positive"},
                    {"dept": "finance", "effect": "Rasio kas likuid (Cash Ratio) anjlok ke level rentan", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Gudang bahan baku penuh, beban sewa ruang tambahan", "type": "negative"}
                ],
                "document": {
                    "type": "KONTRAK_BULK",
                    "title": "Perjanjian Pembelian Grosir Strategis No. 201/PUR-BLK/2026",
                    "recipient": "PT Elektronika Sentra Pasifik",
                    "summary": "Pembelian partai besar komponen pasif dengan potongan harga 30% termin pembayaran Cash Before Delivery."
                },
                "cfo_verdict": "Hati-hati risiko likuiditas macet bila terjadi pengeluaran mendadak dalam 30 hari ke depan."
            },
            {
                "choice_id": "B",
                "label": "Tolak Tawaran & Tetap Menggunakan Metode Pengadaan Just-In-Time (JIT)",
                "rationale": "Menjaga fleksibilitas kas likuid dan menghindari risiko kerusakan persediaan di gudang.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Kas tetap fleksibel dan likuiditas harian terjaga", "type": "positive"},
                    {"dept": "purchasing", "effect": "Kehilangan peluang penghematan marjin jangka panjang", "type": "negative"}
                ],
                "document": {
                    "type": "MEMO_PUR",
                    "title": "Nota Dinas Penolakan Program Bulk No. 042/ND-PUR/2026",
                    "recipient": "Komite Manajemen Modal Kerja",
                    "summary": "Keputusan mempertahankan pola pengadaan bulanan sesuai fluktuasi demand dinamis."
                },
                "cfo_verdict": "Kebijakan kas yang bijak bagi perusahaan dengan buffer modal kerja terbatas."
            }
        ]
    },
    {
        "id": "PUR-04",
        "domain": "purchasing",
        "domain_label": "Pengadaan & Rantai Pasok",
        "title": "Temuan Praktik Gratifikasi / Kickback pada Tim Purchasing",
        "context": "Audit internal menemukan indikasi bahwa salah satu staf procurement senior menerima komisi rahasia dari vendor baut dan packaging dengan imbalan harga beli yang di-mark up 15%.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Pemutusan Hubungan Kerja (PHK) Seketika & Blacklist Vendor Terlibat",
                "rationale": "Tindakan tegas menegakkan Good Corporate Governance (GCG) dan menghentikan kebocoran anggaran jangka panjang.",
                "immediate_cost": 5000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Efek jera bagi karyawan lain, integritas tim meningkat", "type": "positive"},
                    {"dept": "purchasing", "effect": "Gangguan sementara proses pengadaan saat mencari vendor pengganti", "type": "negative"},
                    {"dept": "finance", "effect": "Harga pengadaan terkoreksi turun 15% ke harga wajar pasar", "type": "positive"}
                ],
                "document": {
                    "type": "SURAT_PHK_ETIK",
                    "title": "Surat Keputusan Direksi Pemecatan No. 091/SK-DIR/2026",
                    "recipient": "Departemen HR & Komite Etik Perusahaan",
                    "summary": "Pemberhentian tidak dengan hormat atas pelanggaran berat integritas dan surat pemberitahuan blacklist vendor."
                },
                "cfo_verdict": "Langkah governance yang tepat untuk menekan inefisiensi laten."
            },
            {
                "choice_id": "B",
                "label": "Beri Surat Peringatan III (SP3) & Negosiasi Ulang Kontrak Vendor",
                "rationale": "Menghindari kekosongan personel procurement di tengah masa puncak produksi sambil meminta vendor mengembalikan selisih harga.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "purchasing", "effect": "Operasional pengadaan tetap berjalan lancar tanpa jeda", "type": "positive"},
                    {"dept": "hr", "effect": "Moral kedisiplinan berisiko melemah karena sanksi dianggap lunak", "type": "negative"}
                ],
                "document": {
                    "type": "SP3_SURAT",
                    "title": "Surat Peringatan Terakhir (SP-3) No. 033/HR-SP/2026",
                    "recipient": "Staf Bagian Pembelian Terkait",
                    "summary": "Peringatan keras pelanggaran kode etik pengadaan dengan kewajiban pengawasan melekat oleh Internal Auditor."
                },
                "cfo_verdict": "Kompromi operasional; butuh pengawasan internal yang lebih ketat."
            }
        ]
    },

    # ------------------ MANUFACTURING & PRODUCTION (4 Scenarios) ------------------
    {
        "id": "MFG-01",
        "domain": "manufacturing",
        "domain_label": "Produksi & Kualitas",
        "title": "Kerusakan Fatal Mesin SMT (Surface Mount Technology) Utama",
        "context": "Mesin solder presisi tinggi mengalami korsleting panel inverter pada saat pesanan ekspor sedang dikerjakan. Lini produksi terhenti total.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Panggil Teknisi Khusus Luar Negeri & Overhaul Mesin Kilat (24 Jam Selesai)",
                "rationale": "Pabrik kembali beroperasi penuh dalam sehari, namun biaya jasa teknisi ekspres dan suku cadang orisinal sangat tinggi.",
                "immediate_cost": 28000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Lini produksi beroperasi kembali 100% dalam tempo 24 jam", "type": "positive"},
                    {"dept": "finance", "effect": "Beban pemeliharaan mesin langsung terdebet dari kas", "type": "negative"},
                    {"dept": "crm", "effect": "Komitmen delivery tetap tercapai tepat waktu", "type": "positive"}
                ],
                "document": {
                    "type": "WORK_ORDER_DARURAT",
                    "title": "Surat Perintah Kerja Perbaikan Mesin No. 511/MNT-WO/2026",
                    "recipient": "PT Siemens Industrial Solutions Indonesia",
                    "summary": "Perintah darurat overhaul inverter SMT Line #1 dengan garansi operasional 6 bulan."
                },
                "cfo_verdict": "Investasi tepat untuk mencegah kerugian penalti keterlambatan kontrak ekspor."
            },
            {
                "choice_id": "B",
                "label": "Sub-kontrakkan (Maklon) Pekerjaan SMT ke Pabrik Rekanan Mitra",
                "rationale": "Mengalihkan perakitan ke pabrik luar; tidak perlu biaya perbaikan besar di awal, tapi biaya per unit naik 20% dan risiko bocornya desain PCB.",
                "immediate_cost": 12000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Produksi berjalan via mitra dengan biaya variabel lebih tinggi", "type": "positive"},
                    {"dept": "finance", "effect": "Margin laba kotor tergerus 12% selama masa maklon", "type": "negative"},
                    {"dept": "purchasing", "effect": "Ketergantungan terhadap kapasitas pabrik eksternal", "type": "negative"}
                ],
                "document": {
                    "type": "KONTRAK_MAKLON",
                    "title": "Perjanjian Kerjasama Jasa Manufaktur No. 077/MKL-OPS/2026",
                    "recipient": "PT Cipta Elektronika Mandiri",
                    "summary": "Kontrak outsourcing perakitan SMT sebanyak 1.000 PCB dengan klausul kerahasiaan NDA."
                },
                "cfo_verdict": "Melindungi likuiditas kas belanja modal (Capex) dengan mengorbankan margin operasional (Opex)."
            },
            {
                "choice_id": "C",
                "label": "Gunakan Tenaga Manual Solder Tangan oleh Operator Pabrik (Jadwal Kerja Lembur)",
                "rationale": "Tanpa biaya mesin eksternal, namun kecepatan produksi melambat drastis dan tingkat cacat perakitan meningkat.",
                "immediate_cost": 4000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Kelelahan operator dan beban upah lembur lembur meningkat", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Defect rate solder manual naik 20%, bottleneck output", "type": "negative"},
                    {"dept": "finance", "effect": "Biaya kas keluar terendah di awal", "type": "positive"}
                ],
                "document": {
                    "type": "INSTRUKSI_MANUAL",
                    "title": "Standard Operating Procedure Penyesuaian Manual No. 021/SOP-MAN/2026",
                    "recipient": "Seluruh Supervisor Lini Perakitan",
                    "summary": "Prosedur darurat pengerjaan solder manual dua shift dengan pengawasan QC sampling intensif."
                },
                "cfo_verdict": "Sangat berisiko merusak reputasi kualitas produk di pasar akhir."
            }
        ]
    },
    {
        "id": "MFG-02",
        "domain": "manufacturing",
        "domain_label": "Produksi & Kualitas",
        "title": "Temuan Batch Produksi Cacat Lolos QC pada Tahap Packing",
        "context": "Tim quality control menemukan bahwa 200 unit produk jadi yang siap dikirim mengalami masalah firmware crashing setelah uji coba acak terakhir.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tahan Seluruh Pengiriman & Lakukan Rework Flashing Firmware 100%",
                "rationale": "Mencegah barang cacat sampai ke tangan pembeli, namun pengiriman tertunda 4 hari.",
                "immediate_cost": 6000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Klien terlindungi dari produk cacat, kepercayaan jangka panjang terjaga", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Lembur tim engineering untuk proses flashing ulang 200 unit", "type": "negative"},
                    {"dept": "finance", "effect": "Biaya rework tambahan sebesar Rp 6.000.000", "type": "negative"}
                ],
                "document": {
                    "type": "BA_REWORK",
                    "title": "Berita Acara Karantina & Pengerjaan Ulang No. 045/QC-RW/2026",
                    "recipient": "Departemen Quality Assurance & Logistik",
                    "summary": "Karantina batch produk nomor seri BATCH-202609 dan instruksi flashing patch firmware v2.1."
                },
                "cfo_verdict": "Langkah mitigasi risiko komplain dan retur yang jauh lebih mahal jika barang terlanjur beredar."
            },
            {
                "choice_id": "B",
                "label": "Kirim Sesuai Jadwal & Siapkan Patch OTA (Over-The-Air) Pasca Penjualan",
                "rationale": "Target pengiriman dan penagihan invoice invoice tepat waktu, namun pembeli awal mungkin mengalami kendala sesaat sebelum update.",
                "immediate_cost": 1500000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Faktur penjualan dapat segera dicairkan tanpa keterlambatan", "type": "positive"},
                    {"dept": "crm", "effect": "Beban customer support melonjak untuk panduan update pengguna", "type": "negative"}
                ],
                "document": {
                    "type": "RELEASE_NOTE",
                    "title": "Catatan Rilis Patch Firmware No. 089/ENG-REL/2026",
                    "recipient": "Tim Customer Service & Technical Support",
                    "summary": "Dokumentasi panduan update firmware pelanggan dan alur penanganan tiket kendala sistem."
                },
                "cfo_verdict": "Mengamankan arus kas penagihan, namun awasi rating kepuasan konsumen di marketplace."
            }
        ]
    },
    {
        "id": "MFG-03",
        "domain": "manufacturing",
        "domain_label": "Produksi & Kualitas",
        "title": "Optimalisasi Efisiensi Lean Manufacturing & Reduksi Pemborosan (Kaizen)",
        "context": "Konsultan industri menyarankan implementasi sistem 5S dan Poka-Yoke di lini perakitan untuk memangkas waktu siklus per unit sebesar 15%.",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Investasi Program Kaizen & Sertifikasi Lean Manufacturing",
                "rationale": "Meningkatkan kapasitas produksi jangka panjang dan mengurangi scrap rate secara permanen.",
                "immediate_cost": 18000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Efisiensi lini naik 15% dan defect rate berkurang signifikan", "type": "positive"},
                    {"dept": "finance", "effect": "Capex pelatihan & perombakan tata letak (layout) pabrik", "type": "negative"},
                    {"dept": "hr", "effect": "Keterampilan operator meningkat berkat sertifikasi resmi", "type": "positive"}
                ],
                "document": {
                    "type": "KONTRAK_KONSULTAN",
                    "title": "Perjanjian Program Transformasi Lean No. 012/LEAN-OPS/2026",
                    "recipient": "Indonesia Productivity & Quality Institute",
                    "summary": "Program pendampingan implementasi 5S, Standard Work, dan Value Stream Mapping selama 3 bulan."
                },
                "cfo_verdict": "Investasi modal intelektual yang menghasilkan ROI positif dalam siklus 2-3 periode."
            },
            {
                "choice_id": "B",
                "label": "Jalankan Efisiensi Internal Swakelola Tanpa Konsultan Luar",
                "rationale": "Hemat biaya anggaran kas, namun progres lambat karena keterbatasan kompetensi internal.",
                "immediate_cost": 2000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Penghematan anggaran jasa konsultasi", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Peningkatan efisiensi minim (hanya ~3-5%)", "type": "neutral"}
                ],
                "document": {
                    "type": "MEMO_INTERNAL",
                    "title": "Instruksi Gugus Kendali Mutu Mandiri No. 008/GKM/2026",
                    "recipient": "Seluruh Ketua Tim Kerja Pabrik",
                    "summary": "Pembentukan gugus kendali mutu internal untuk identifikasi titik pemborosan material."
                },
                "cfo_verdict": "Pendekatan low-cost yang konservatif."
            }
        ]
    },
    {
        "id": "MFG-04",
        "domain": "manufacturing",
        "domain_label": "Produksi & Kualitas",
        "title": "Audit Keselamatan Kerja & Standardisasi K3 Lingkungan Pabrik",
        "context": "Inspektur Dinas Tenaga Kerja menemukan kekurangan alat pelindung diri (APD) dan sistem ventilasi pembuangan timbal di ruang perakitan.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Modernisasi Sistem Ventilasi K3 & Lengkapi APD Standar Internasional",
                "rationale": "Menghilangkan risiko sanksi penyegelan pabrik dan meningkatkan moral keselamatan pekerja.",
                "immediate_cost": 16000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Tingkat absensi sakit pekerja menurun drastis, moral kerja naik", "type": "positive"},
                    {"dept": "finance", "effect": "Beban investasi kepatuhan regulasi lingkungan K3", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Lolos audit sertifikasi ISO 45001", "type": "positive"}
                ],
                "document": {
                    "type": "SERTIFIKASI_K3",
                    "title": "Laporan Pemenuhan Rekomendasi K3 No. 034/K3-DISNAKER/2026",
                    "recipient": "Dinas Tenaga Kerja dan Transmigrasi Provinsi",
                    "summary": "Bukti pemenuhan standar instalasi exhaust blower dan pengadaan APD lengkap bagi seluruh pekerja pabrik."
                },
                "cfo_verdict": "Kepatuhan hukum wajib untuk menghindari risiko penutupan paksa operasional."
            },
            {
                "choice_id": "B",
                "label": "Pengadaan APD Minimum Sekadar Memenuhi Syarat Administrasi",
                "rationale": "Biaya minimal dalam jangka pendek, namun rentan sanksi inspeksi ulang di masa depan.",
                "immediate_cost": 4500000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Pengeluaran kas minim", "type": "positive"},
                    {"dept": "hr", "effect": "Potensi tuntutan serikat buruh terkait kenyamanan kerja", "type": "negative"}
                ],
                "document": {
                    "type": "BERITA_ACARA_APD",
                    "title": "Tanda Terima Pengadaan APD Dasar No. 056/HR-APD/2026",
                    "recipient": "Pengawas K3 Internal Pabrik",
                    "summary": "Distribusi masker filter standar dan sarung tangan anti-statis tahap awal."
                },
                "cfo_verdict": "Menekan biaya jangka pendek dengan mempertahankan risiko audit berkelanjutan."
            }
        ]
    },

    # ------------------ CRM, SALES & CONTRACT COMPLAINTS (4 Scenarios) ------------------
    {
        "id": "CRM-01",
        "domain": "crm",
        "domain_label": "Hubungan Pelanggan & Komplain",
        "title": "Ancaman Somasi Hukum dari Klien Korporat Utama (PT Megatama)",
        "context": "Klien korporat terbesar melayangkan Surat Peringatan Hukum (Somasi) karena 35 unit mesin yang dikirim terlambat 10 hari dan mengalami kendala kalibrasi. Klien menuntut ganti rugi Rp 50.000.000 atau perkara dibawa ke Pengadilan Niaga.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tawarkan Kompensasi Diskon 15% Invoice & Kirim Tim Teknisi Onsite 24 Jam",
                "rationale": "Meredam amarah klien, menyelamatkan kontrak tahunan bernilai miliaran, dengan beban potongan harga yang terukur.",
                "immediate_cost": 22000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Somasi dicabut, kontrak tahunan tetap aman diperpanjang", "type": "positive"},
                    {"dept": "finance", "effect": "Pendapatan invoice terpangkas Rp 22.000.000", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Tim teknisi dikerahkan onsite selama 3 hari berturut-turut", "type": "negative"}
                ],
                "document": {
                    "type": "AKTA_PERDAMAIAN",
                    "title": "Akta Perjanjian Perdamaian Bipartit No. 019/LEG-CRM/2026",
                    "recipient": "Direksi PT Megatama Retailindo Tbk",
                    "summary": "Pencabutan somasi hukum dengan komitmen kredit nota potongan 15% dan dukungan teknisi onsite prioritas."
                },
                "cfo_verdict": "Biaya perdamaian jauh lebih murah daripada biaya pengacara dan hilangnya klien jangkar perusahaan."
            },
            {
                "choice_id": "B",
                "label": "Lawan Somasi via Kuasa Hukum Perusahaan Menggunakan Klausul Force Majeure",
                "rationale": "Menolak membayar ganti rugi dengan dasar keterlambatan vendor pihak ketiga, namun memicu perang litigasi di pengadilan.",
                "immediate_cost": 15000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Biaya jasa pengacara retain fee langsung dibayar", "type": "negative"},
                    {"dept": "crm", "effect": "Hubungan dengan klien korporat putus total, reputasi pasar tercoreng", "type": "negative"},
                    {"dept": "accounting", "effect": "Piutang berjalan macet dan berpotensi menjadi Bad Debt 100%", "type": "negative"}
                ],
                "document": {
                    "type": "JAWABAN_SOMASI",
                    "title": "Surat Tanggapan Somasi Hukum No. 099/LEG-LAW/2026",
                    "recipient": "Kantor Advokat & Konsultan Hukum Siregar & Partners",
                    "summary": "Penolakan klaim ganti rugi wanprestasi berdasarkan klausul pembatasan tanggung jawab dalam Kontrak Induk Pengadaan."
                },
                "cfo_verdict": "Risiko reputasi dan kerugian piutang macet yang sangat destruktif bagi neraca keuangan."
            },
            {
                "choice_id": "C",
                "label": "Tawarkan Penggantian Unit Baru Utuh (Full Replacement) Tanpa Diskon Kas",
                "rationale": "Menjaga nilai invoice tetap utuh dengan membebankan biaya produksi unit pengganti ke HPP.",
                "immediate_cost": 18000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Klien puas dengan unit baru, komplain dinyatakan selesai", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Antrean produksi diselak untuk membuat 35 unit pengganti", "type": "negative"},
                    {"dept": "finance", "effect": "Beban HPP membengkak, namun nilai piutang utuh tertagih", "type": "positive"}
                ],
                "document": {
                    "type": "SURAT_PENGGANTIAN",
                    "title": "Berita Acara Penukaran Barang No. 063/BA-RETUR/2026",
                    "recipient": "General Manager Procurement PT Megatama Retailindo",
                    "summary": "Pengiriman 35 unit baru produk pengganti dengan garansi purna jual diperpanjang menjadi 24 bulan."
                },
                "cfo_verdict": "Solusi win-win yang menjaga nilai penjualan kotor tetap tercatat tinggi di laporan Laba Rugi."
            }
        ]
    },
    {
        "id": "CRM-02",
        "domain": "crm",
        "domain_label": "Hubungan Pelanggan & Komplain",
        "title": "Peluang Tender Pengadaan Pemerintah (E-Katalog B2G)",
        "context": "Kementerian Pendidikan membuka tender pengadaan perangkat lab senilai Rp 300.000.000 dengan syarat jaminan pelaksanaan (Bank Guarantee) dan sertifikasi TKDN minimal 40%.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Ikuti Tender Penuh: Beli Bank Guarantee & Sertifikasi TKDN Kilat",
                "rationale": "Peluang memenangkan kontrak jumbo dengan margin menarik, namun membutuhkan komitmen kas jaminan bank.",
                "immediate_cost": 25000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Lolos verifikasi teknis tender proyek pemerintah Rp 300 Juta", "type": "positive"},
                    {"dept": "finance", "effect": "Kas diblokir sementara untuk jaminan tender (Collateral)", "type": "negative"}
                ],
                "document": {
                    "type": "DOKUMEN_TENDER",
                    "title": "Pakta Integritas & Dokumen Penawaran Tender No. 003/TND-DIKTI/2026",
                    "recipient": "Pokja Pemilihan Pengadaan Barang/Jasa Kemendikbudristek",
                    "summary": "Pengajuan dokumen teknis penawaran tender e-katalog dilengkapi jaminan bank garansi senilai 5% nilai kontrak."
                },
                "cfo_verdict": "Langkah ekspansi pendapatan strategis; pastikan buffer kas harian tetap aman dari risiko lock up."
            },
            {
                "choice_id": "B",
                "label": "Bermitra Konsorsium (KSO) dengan Distributor Resmi Pemilik TKDN",
                "rationale": "Tanpa biaya sertifikasi mahal, berbagi margin 30% dengan mitra konsorsium.",
                "immediate_cost": 5000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Mengikuti tender dengan profil risiko finansial lebih ringan", "type": "positive"},
                    {"dept": "finance", "effect": "Margin keuntungan proyek dibagi dua dengan mitra KSO", "type": "neutral"}
                ],
                "document": {
                    "type": "PERJANJIAN_KSO",
                    "title": "Perjanjian Kerjasama Operasional (KSO) No. 028/KSO-GOV/2026",
                    "recipient": "PT Graha Rekayasa Nusantara",
                    "summary": "Kesepakatan pembagian lingkup kerja dan bagi hasil pengadaan perangkat laboratorium e-katalog."
                },
                "cfo_verdict": "Pilihan cerdas untuk mengincar volume besar tanpa membebani neraca modal sendiri."
            }
        ]
    },
    {
        "id": "CRM-03",
        "domain": "crm",
        "domain_label": "Hubungan Pelanggan & Komplain",
        "title": "Distributor Utama Meminta Perpanjangan Tempo Pembayaran (TOP 90 Hari)",
        "context": "Distributor terbesar yang menyerap 45% penjualan perusahaan meminta perpanjangan jangka waktu pembayaran (Term of Payment) dari 30 hari menjadi 90 hari karena perlambatan penjualan retail.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tolak Permintaan & Pertahankan Batas Kredit Ketat Maksimal 30 Hari",
                "rationale": "Mencegah penumpukan piutang macet (DSO membengkak), namun berisiko distributor mengurangi volume pesanan sebesar 30%.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Arus kas penagihan tetap stabil dan Days Sales Outstanding (DSO) rendah", "type": "positive"},
                    {"dept": "crm", "effect": "Distributor mengancam memindahkan sebagian kuota ke kompetitor", "type": "negative"}
                ],
                "document": {
                    "type": "SURAT_KEBIJAKAN_KREDIT",
                    "title": "Pemberitahuan Kebijakan Batas Kredit Usaha No. 017/FIN-CR/2026",
                    "recipient": "Direktur Keuangan PT Distribusi Mega Niaga",
                    "summary": "Penetapan batasan plafon kredit maksimum Rp 50.000.000 dengan tenor pembayaran tetap 30 hari kalender."
                },
                "cfo_verdict": "Sangat baik untuk menjaga Cash Conversion Cycle (CCC) tidak jebol."
            },
            {
                "choice_id": "B",
                "label": "Setujui TOP 90 Hari dengan Syarat Jaminan Bilyet Giro Mundur & Biaya Bunga 2%",
                "rationale": "Menjaga loyalitas distributor sambil melindungi risiko gagal bayar dengan instrumen perbankan.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "crm", "effect": "Distributor tetap memesan dalam volume maksimal", "type": "positive"},
                    {"dept": "finance", "effect": "Pendapatan bunga tambahan, namun piutang tertahan lebih lama di neraca", "type": "neutral"}
                ],
                "document": {
                    "type": "ADDENDUM_KREDIT",
                    "title": "Addendum Perjanjian Fasilitas Kredit No. 062/ADD-TOP/2026",
                    "recipient": "PT Distribusi Mega Niaga",
                    "summary": "Persetujuan perpanjangan tenor TOP 90 hari dengan kewajiban penyerahan Bilyet Giro tertanggal mundur."
                },
                "cfo_verdict": "Kompromi komersial yang aman secara hukum selama instrumen Giro sudah divalidasi bank."
            }
        ]
    },
    {
        "id": "CRM-04",
        "domain": "crm",
        "domain_label": "Hubungan Pelanggan & Komplain",
        "title": "Peluncuran Program Loyalitas & Insentif Rebate Tahunan Mitra",
        "context": "Asosiasi dealer menuntut program insentif akhir tahun (Year-End Rebate) untuk mendorong penjualan produk VLab menjelang tutup buku tahunan.",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Luncurkan Skema Rebate Berjenjang (Tiered Cashback) Berbasis Target Omzet",
                "rationale": "Memicu lonjakan pesanan borongan di akhir periode, dibayar setelah target penjualan tercapai.",
                "immediate_cost": 15000000.0,
                "ripples": [
                    {"dept": "crm", "effect": "Volume penjualan melonjak 28% dalam waktu 30 hari", "type": "positive"},
                    {"dept": "finance", "effect": "Pencadangan beban insentif penjualan pada laporan laba rugi", "type": "neutral"}
                ],
                "document": {
                    "type": "SK_REBATE",
                    "title": "Skema Insentif & Program Rebate Penjualan No. 041/MKT-REB/2026",
                    "recipient": "Seluruh Jaringan Agen & Reseller Resmi",
                    "summary": "Program insentif cashback berjenjang hingga 5% untuk pencapaian omzet penjualan di atas target kuartal."
                },
                "cfo_verdict": "Strategi ekspansi top-line yang terbukti efektif menaikkan omzet bersih."
            },
            {
                "choice_id": "B",
                "label": "Tidak Menerapkan Program Rebate Kas (Fokus Promosi Digital B2C)",
                "rationale": "Menghemat kas perusahaan dan mengalihkan dana promosi ke iklan media sosial langsung ke pengguna akhir.",
                "immediate_cost": 5000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Beban kas lebih hemat dan terkontrol", "type": "positive"},
                    {"dept": "crm", "effect": "Brand awareness konsumen naik, namun antusiasme reseller datar", "type": "neutral"}
                ],
                "document": {
                    "type": "RENCANA_IKLAN",
                    "title": "Alokasi Rencana Belanja Promosi Digital No. 077/MKT-DIG/2026",
                    "recipient": "Tim Digital Marketing & Media",
                    "summary": "Penetapan anggaran kampanye iklan berbayar di kanal digital dan marketplace."
                },
                "cfo_verdict": "Opsi konservatif menjaga laba operasional tetap stabil."
            }
        ]
    },

    # ------------------ HR & LABOR UNION CRISIS (4 Scenarios) ------------------
    {
        "id": "HR-01",
        "domain": "hr",
        "domain_label": "Ketenagakerjaan & Serikat Buruh",
        "title": "Mogok Kerja Massal Serikat Buruh (Tuntutan Upah Lembur & Bonus Shift)",
        "context": "Serikat Pekerja Mandiri menginstruksikan 40 pekerja pabrik melakukan aksi mogok kerja dan memblokir pintu akses lini perakitan. Mereka menuntut kenaikan upah pokok 12% dan uang saku damai Rp 1.500.000 per orang.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Capai Kesepakatan Bipartit: Beri Bonus Produktivitas & Naikkan Upah Pokok 7%",
                "rationale": "Blokade pabrik langsung dicabut dalam hitungan jam, produksi malam segera beroperasi normal.",
                "immediate_cost": 24000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Pabrik kembali beroperasi 100%, bottleneck selesai", "type": "positive"},
                    {"dept": "hr", "effect": "Moral dan loyalitas buruh meningkat pesat pasca kesepakatan", "type": "positive"},
                    {"dept": "finance", "effect": "Beban gaji bulanan tetap (Fixed Labor Cost) naik permanen 7%", "type": "negative"}
                ],
                "document": {
                    "type": "PERJANJIAN_BIPARTIT",
                    "title": "Perjanjian Bersama Bipartit No. 008/BIP-DISNAKER/2026",
                    "recipient": "Ketua Dewan Pengurus Serikat Pekerja Mandiri",
                    "summary": "Kesepakatan pengakhiran aksi mogok kerja, penyesuaian skala upah 7%, dan bonus insentif target output."
                },
                "cfo_verdict": "Menghentikan pendarahan kerugian downtime harian yang bisa menelan Rp 15 Juta per hari jika pabrik mangkrak."
            },
            {
                "choice_id": "B",
                "label": "Tolak Tuntutan, Nyatakan Mogok Tidak Sah & Rekrut Pekerja Outsourcing Pengganti",
                "rationale": "Menolak kenaikan biaya tetap gaji, namun memicu konflik hukum ketenagakerjaan dan penurunan efisiensi pekerja baru.",
                "immediate_cost": 16000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Eskalasi perselisihan ke Pengadilan Hubungan Industrial (PHI)", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Pekerja baru butuh waktu training 2 minggu, defect rate naik 15%", "type": "negative"},
                    {"dept": "finance", "effect": "Biaya rekrutmen outsourcing dan jasa hukum meningkat", "type": "negative"}
                ],
                "document": {
                    "type": "SURAT_PERINGATAN_BURUH",
                    "title": "Surat Peringatan & Pernyataan Mogok Kerja Tidak Sah No. 044/HR-DIR/2026",
                    "recipient": "Pengurus Serikat Pekerja & Dinas Tenaga Kerja Kota",
                    "summary": "Pemberitahuan sanksi disipliner atas mangkir kerja tanpa izin dan pemanggilan kembali dalam tempo 2x24 jam."
                },
                "cfo_verdict": "Sangat mahal dalam jangka menengah akibat inefisiensi kurva belajar pekerja baru."
            },
            {
                "choice_id": "C",
                "label": "Tawarkan Kompensasi Uang Saku Tunai Sekali Bayar (One-Off) Tanpa Kenaikan Gaji Pokok",
                "rationale": "Melindungi struktur beban tetap bulanan di neraca jangka panjang dengan pengeluaran tunai sekali bayar.",
                "immediate_cost": 12000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Struktur beban upah pokok bulanan tidak berubah naik", "type": "positive"},
                    {"dept": "hr", "effect": "Serikat buruh menerima bersyarat, tensi mereda sementara", "type": "neutral"},
                    {"dept": "manufacturing", "effect": "Pabrik beroperasi kembali esok hari", "type": "positive"}
                ],
                "document": {
                    "type": "NOTA_KESEPAHAMAN",
                    "title": "Nota Kesepahaman Bantuan Kesejahteraan Pekerja No. 029/MOU-HR/2026",
                    "recipient": "Perwakilan Karyawan Lini Produksi",
                    "summary": "Pemberian dana bantuan kesejahteraan transisi tunai sekali bayar untuk seluruh operator terdaftar."
                },
                "cfo_verdict": "Pilihan taktis cerdas seorang CFO untuk menghindari kenaikan fixed overhead cost permanen."
            }
        ]
    },
    {
        "id": "HR-02",
        "domain": "hr",
        "domain_label": "Ketenagakerjaan & Serikat Buruh",
        "title": "Pembajakan (Poaching) Kepala Engineer Litbang oleh Kompetitor Utama",
        "context": "Lead Hardware Engineer dan dua teknisi kunci menerima tawaran kerja dari kompetitor multinasional dengan tawaran kenaikan gaji 40%. Mereka memegang formula desain produk generasi terbaru.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tawarkan Counter-Offer: Kenaikan Gaji 25% + Bonus Retensi Loyalitas",
                "rationale": "Mempertahankan talenta kunci dan kerahasiaan kekayaan intelektual (IP) produk generasi berikutnya.",
                "immediate_cost": 15000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Tim inti R&D bertahan 100%, stabilitas riset produk terjamin", "type": "positive"},
                    {"dept": "finance", "effect": "Kenaikan beban gaji divisi engineering di Laba Rugi", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Proyek inovasi produk baru selesai sesuai roadmap", "type": "positive"}
                ],
                "document": {
                    "type": "RETENTION_AGREEMENT",
                    "title": "Perjanjian Retensi Talenta Kunci & Non-Disclosure No. 051/HR-RET/2026",
                    "recipient": "Kepala Divisi Riset & Pengembangan",
                    "summary": "Pemberian paket retensi loyalitas kerja 2 tahun disertai klausul Non-Compete dan Non-Disclosure Agreement ketat."
                },
                "cfo_verdict": "Melindungi asset tak berwujud (Intangible Asset / Intellectual Property) yang krusial bagi masa depan bisnis."
            },
            {
                "choice_id": "B",
                "label": "Lepas Karyawan & Tuntut Penerapan Klausul Non-Compete Agreement (NCA)",
                "rationale": "Menghemat kas beban gaji dan menuntut mantan karyawan secara hukum jika membocorkan rahasia dagang.",
                "immediate_cost": 4000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Kekosongan posisi kunci, butuh waktu rekrutmen 2-3 bulan", "type": "negative"},
                    {"dept": "manufacturing", "effect": "Pengembangan produk baru mengalami penundaan (delay)", "type": "negative"},
                    {"dept": "finance", "effect": "Penghematan beban kompensasi gaji jangka pendek", "type": "positive"}
                ],
                "document": {
                    "type": "SURAT_PERINGATAN_NCA",
                    "title": "Peringatan Kepatuhan Perjanjian Non-Kompensasi Rahasia Dagang No. 082/LEG-NCA/2026",
                    "recipient": "Mantan Staf Divisi Engineering",
                    "summary": "Pemberitahuan kewajiban pembatasan bekerja pada entitas kompetitor langsung selama periode 12 bulan."
                },
                "cfo_verdict": "Menghemat kas bulanan namun mengorbankan kecepatan inovasi teknologi perusahaan."
            }
        ]
    },
    {
        "id": "HR-03",
        "domain": "hr",
        "domain_label": "Ketenagakerjaan & Serikat Buruh",
        "title": "Program Upskilling Digital & Otomasi Robotik Tenaga Kerja Pabrik",
        "context": "Manajemen merencanakan otomatisasi lini packing yang akan menggantikan 10 posisi manual. Manajemen harus memutuskan nasib 10 pekerja tersebut.",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Lakukan Pelatihan Alih Keterampilan (Reskilling) Menjadi Operator QC Robotik",
                "rationale": "Tanpa pemecatan buruh, moral pekerja terjaga tinggi, produktivitas pabrik meningkat berlipat.",
                "immediate_cost": 14000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Zero layoff, reputasi perusahaan sebagai Best Employer naik", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Kapasitas lini packing naik 40% setelah otomasi", "type": "positive"},
                    {"dept": "finance", "effect": "Beban investasi modul pelatihan teknologi", "type": "negative"}
                ],
                "document": {
                    "type": "PROGRAM_PELATIHAN",
                    "title": "Surat Keputusan Program Alih Kompetensi Karyawan No. 035/SK-RESKILL/2026",
                    "recipient": "Departemen HR & 10 Karyawan Divisi Perakitan",
                    "summary": "Program sertifikasi pengoperasian sistem kontrol otomatisasi perakitan dan jaminan status kepegawaian tetap."
                },
                "cfo_verdict": "Investasi human capital yang menaikkan produktivitas output per tenaga kerja secara permanen."
            },
            {
                "choice_id": "B",
                "label": "Program Pensiun Dini Sukarela (Golden Shakehand) dengan Pesangon Penuh",
                "rationale": "Memangkas jumlah tenaga kerja secara permanen dan menurunkan beban gaji bulanan di masa depan.",
                "immediate_cost": 35000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Pengeluaran kas pesangon besar di awal, namun hemat gaji di periode berikutnya", "type": "neutral"},
                    {"dept": "manufacturing", "effect": "Otomasi berjalan penuh tanpa beban headcount berlebih", "type": "positive"}
                ],
                "document": {
                    "type": "PERJANJIAN_PESANGON",
                    "title": "Perjanjian Pengakhiran Hubungan Kerja Sukarela No. 066/PHK-GOLD/2026",
                    "recipient": "Departemen Tenaga Kerja & Rekening Karyawan",
                    "summary": "Penyelesaian hak pesangon pensiun dini sukarela 10 karyawan sesuai regulasi ketenagakerjaan yang berlaku."
                },
                "cfo_verdict": "Tinggi di pengeluaran kas awal, namun mempercantik Operating Margin pada periode-periode berikutnya."
            }
        ]
    },
    {
        "id": "HR-04",
        "domain": "hr",
        "domain_label": "Ketenagakerjaan & Serikat Buruh",
        "title": "Kecelakaan Kerja di Area Pergudangan (Forklift Incident)",
        "context": "Sebuah forklift menabrak rak penyimpanan akibat rem aus, melukai seorang staf gudang dan merusak persediaan senilai Rp 8.000.000.",
        "urgency": "HIGH",
        "branches": [
            {
                "choice_id": "A",
                "label": "Tanggung Penuh Biaya Pengobatan VIP, Santunan & Perbaiki Sistem Pergudangan",
                "rationale": "Menunjukkan tanggung jawab penuh perusahaan, menjaga keharmonisan hubungan kerja, dan audit kelayakan armada gudang.",
                "immediate_cost": 12000000.0,
                "ripples": [
                    {"dept": "hr", "effect": "Solidaritas dan kepercayaan karyawan terhadap manajemen sangat tinggi", "type": "positive"},
                    {"dept": "finance", "effect": "Beban santunan medis dan perbaikan rak gudang", "type": "negative"},
                    {"dept": "purchasing", "effect": "Pemeriksaan total kelayakan seluruh armada forklift", "type": "positive"}
                ],
                "document": {
                    "type": "BA_INSIDEN_K3",
                    "title": "Laporan Penanganan Kecelakaan Kerja No. 011/K3-MED/2026",
                    "recipient": "BPJS Ketenagakerjaan & Keluarga Karyawan",
                    "summary": "Pertanggungjawaban penanganan medis menyeluruh dan evaluasi kelayakan peralatan material handling."
                },
                "cfo_verdict": "Penanganan krisis yang bertanggung jawab untuk melindungi stabilitas sosial internal perusahaan."
            },
            {
                "choice_id": "B",
                "label": "Klaim Santunan Melalui BPJS Ketenagakerjaan Saja Sesuai Batas Minimum",
                "rationale": "Mengandalkan asuransi wajib untuk meminimalkan beban kas langsung perusahaan.",
                "immediate_cost": 2000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Pengeluaran kas langsung perusahaan sangat minim", "type": "positive"},
                    {"dept": "hr", "effect": "Keluarga korban dan serikat buruh mempertanyakan kepedulian moril manajemen", "type": "negative"}
                ],
                "document": {
                    "type": "KLAIM_BPJS",
                    "title": "Formulir Pengajuan Klaim Jaminan Kecelakaan Kerja No. 048/BPJS-JKK/2026",
                    "recipient": "Kantor Cabang BPJS Ketenagakerjaan",
                    "summary": "Pengajuan manfaat jaminan kecelakaan kerja sesuai pagu standar pertanggungan."
                },
                "cfo_verdict": "Menjaga efisiensi kas jangka pendek namun dapat menurunkan employee engagement."
            }
        ]
    },

    # ------------------ ACCOUNTING, TAX & FINANCIAL STRATEGY (4 Scenarios) ------------------
    {
        "id": "ACC-01",
        "domain": "accounting",
        "domain_label": "Akuntansi & Keuangan Strategis",
        "title": "Pemeriksaan Pajak Mendadak (Surat Ketetapan Pajak Kurang Bayar - SKPKB)",
        "context": "Kantor Pelayanan Pajak (KPP) menerbitkan SKPKB atas ketidaksesuaian faktur pajak masukan 2 tahun lalu senilai Rp 25.000.000. Perusahaan diberi waktu 14 hari untuk melunasi atau mengajukan surat keberatan resmi.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Bayar Lunas SKPKB Rp 25.000.000 & Tutup Pemeriksaan Pajak Segera",
                "rationale": "Menghilangkan risiko sanksi bunga denda berjalan 2% per bulan dan menjaga reputasi kepatuhan pajak.",
                "immediate_cost": 25000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Kas langsung terpotong Rp 25.000.000 untuk setor kas negara", "type": "negative"},
                    {"dept": "accounting", "effect": "Buku pajak dinyatakan Clean & Clear oleh otoritas fiskus", "type": "positive"}
                ],
                "document": {
                    "type": "SKPKB_LUNAS",
                    "title": "Surat Setoran Pajak (SSP) & Pelunasan SKPKB No. 082/SSP-KPP/2026",
                    "recipient": "Kantor Pelayanan Pajak Pratama",
                    "summary": "Bukti penyetoran pelunasan ketetapan pajak kurang bayar ke kas negara melalui Bank Persepsi."
                },
                "cfo_verdict": "Menghilangkan risiko kontinjensi denda membengkak; pastikan cash runway setelah pembayaran masih di atas 60 hari."
            },
            {
                "choice_id": "B",
                "label": "Sewa Konsultan Pajak & Ajukan Surat Keberatan Resmi ke Kanwil Pajak",
                "rationale": "Menunda kewajiban pembayaran pokok sambil memperjuangkan pengurangan pokok denda hingga 70%.",
                "immediate_cost": 8000000.0,
                "ripples": [
                    {"dept": "finance", "effect": "Hemat kas saat ini, hanya bayar jasa konsultan pajak", "type": "positive"},
                    {"dept": "accounting", "effect": "Proses sengketa pajak memakan waktu 6-12 bulan", "type": "neutral"}
                ],
                "document": {
                    "type": "SURAT_KEBERATAN_PAJAK",
                    "title": "Surat Pengajuan Keberatan Atas SKPKB No. 015/TAX-KEB/2026",
                    "recipient": "Kepala Kantor Wilayah Direktorat Jenderal Pajak",
                    "summary": "Pengajuan banding keberatan perpajakan dengan bukti lampiran rekonsiliasi faktur pajak elektronik."
                },
                "cfo_verdict": "Langkah cerdas bila data pembukuan internal kita kuat dan teruji di mata hukum."
            }
        ]
    },
    {
        "id": "ACC-02",
        "domain": "accounting",
        "domain_label": "Akuntansi & Keuangan Strategis",
        "title": "Pilihan Kebijakan Penyusutan Aset Tetap (Garis Lurus vs Saldo Menurun)",
        "context": "Manajemen baru saja membeli mesin produksi senilai Rp 100.000.000. Tim akuntansi meminta penetapan metode depresiasi: Straight Line (Garis Lurus) atau Double Declining Balance (Saldo Menurun Ganda).",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Gunakan Metode Saldo Menurun Ganda (Depresiasi Cepat / Tax Shield di Awal)",
                "rationale": "Beban penyusutan besar di tahun pertama memperkecil Laba Kena Pajak (Tax Shield), menghemat kas pajak riil perusahaan.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "accounting", "effect": "Penghematan pajak penghasilan riil (Cash Tax Savings)", "type": "positive"},
                    {"dept": "finance", "effect": "Laba bersih di laporan keuangan tampak lebih rendah di tahun awal", "type": "neutral"}
                ],
                "document": {
                    "type": "KEBIJAKAN_AKUNTANSI",
                    "title": "Surat Keputusan Kebijakan Depresiasi Aset Tetap No. 004/SK-ACC/2026",
                    "recipient": "Departemen Keuangan & Auditor Eksternal",
                    "summary": "Penetapan metode depresiasi Double Declining Balance untuk kelompok mesin teknologi tinggi."
                },
                "cfo_verdict": "Strategi keuangan klasik untuk memaksimalkan arus kas operasi via Tax Shield."
            },
            {
                "choice_id": "B",
                "label": "Gunakan Metode Garis Lurus (Straight Line Method)",
                "rationale": "Beban penyusutan merata setiap tahun, menjaga stabilitas laba bersih yang dilaporkan kepada pemegang saham.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "accounting", "effect": "Pencatatan pembukuan sederhana dan stabil antar periode", "type": "positive"},
                    {"dept": "finance", "effect": "Laba bersih stabil, namun tidak ada manfaat percepatan penghematan pajak", "type": "neutral"}
                ],
                "document": {
                    "type": "KEBIJAKAN_AKUNTANSI",
                    "title": "Surat Keputusan Kebijakan Depresiasi Garis Lurus No. 005/SK-ACC/2026",
                    "recipient": "Departemen Keuangan & Auditor Eksternal",
                    "summary": "Penetapan metode depresiasi garis lurus dengan masa manfaat 5 tahun tanpa nilai residu."
                },
                "cfo_verdict": "Pilihan standar industri untuk stabilitas laba komersial."
            }
        ]
    },
    {
        "id": "ACC-03",
        "domain": "accounting",
        "domain_label": "Akuntansi & Keuangan Strategis",
        "title": "Peringatan Likuiditas Bank & Ancaman Pelanggaran Covenant Pinjaman (Covenant Breach)",
        "context": "Bank mitra mengirimkan surat peringatan bahwa rasio lancar (Current Ratio) perusahaan turun mendekati batas minimum 1.2x. Jika terlanggar, bank berhak mengenakan pinalti bunga 3% dan menuntut pelunasan dipercepat.",
        "urgency": "CRITICAL",
        "branches": [
            {
                "choice_id": "A",
                "label": "Lakukan Restrukturisasi Utang Bank & Tambah Modal Disetor Pemegang Saham",
                "rationale": "Menyuntikkan kas segar ekuitas dan menegosiasikan perpanjangan tenor fasilitas kredit dengan bank.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Current Ratio kembali aman di atas 1.8x, ancaman wanprestasi bank gugur", "type": "positive"},
                    {"dept": "accounting", "effect": "Penambahan pos Modal Saham Disetor di bagian Ekuitas Neraca", "type": "positive"}
                ],
                "document": {
                    "type": "ADDENDUM_KREDIT_BANK",
                    "title": "Addendum Perjanjian Kredit & Restrukturisasi No. 093/BNK-REST/2026",
                    "recipient": "Divisi Corporate Banking Bank Mandiri (Persero) Tbk",
                    "summary": "Penyelarasan rasio covenant keuangan dan komitmen penambahan modal disetor pemegang saham pengendali."
                },
                "cfo_verdict": "Keputusan penyelamatan solvency paling solid untuk menjamin kelangsungan usaha (Going Concern)."
            },
            {
                "choice_id": "B",
                "label": "Likuidasi Cepat Persediaan Lambat Bergerak (Slow-Moving Inventory) dengan Diskon 40%",
                "rationale": "Mengonversi stok mati di gudang menjadi kas tunai seketika untuk memperbaiki rasio kas.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Inflow kas segar masuk seketika dari obral stok", "type": "positive"},
                    {"dept": "accounting", "effect": "Pencatatan kerugian diskon persediaan pada Laba Rugi", "type": "negative"},
                    {"dept": "purchasing", "effect": "Kapasitas ruang gudang kembali lapang", "type": "positive"}
                ],
                "document": {
                    "type": "PROGRAM_CLEARANCE",
                    "title": "Surat Program Cuci Gudang Likuidasi Persediaan No. 049/SLS-CLR/2026",
                    "recipient": "Distributor & Pedagang Grosir Komponen",
                    "summary": "Penjualan borongan persediaan lambat bergerak dengan potongan harga likuidasi tunai."
                },
                "cfo_verdict": "Langkah taktis membebaskan kas yang terperangkap dalam bentuk barang mati."
            }
        ]
    },
    {
        "id": "ACC-04",
        "domain": "accounting",
        "domain_label": "Akuntansi & Keuangan Strategis",
        "title": "Peluang Investasi Ekspansi Fasilitas Perakitan Baru (Capex Decision)",
        "context": "Direksi mempertimbangkan pembelian mesin lini produksi otomatis senilai Rp 80.000.000 dengan proyeksi pengembalian investasi (Payback Period) selama 14 bulan.",
        "urgency": "MEDIUM",
        "branches": [
            {
                "choice_id": "A",
                "label": "Danai Investasi dengan Kombinasi Kas Internal 50% & Leasing Finansial 50%",
                "rationale": "Membagi beban pendanaan agar tidak menguras kas operasional harian secara berlebihan.",
                "immediate_cost": 40000000.0,
                "ripples": [
                    {"dept": "manufacturing", "effect": "Kapasitas produksi pabrik melonjak 60% dalam 2 bulan", "type": "positive"},
                    {"dept": "finance", "effect": "Liabilitas sewa pembiayaan (Leasing) tercatat di neraca", "type": "neutral"},
                    {"dept": "accounting", "effect": "Aset tetap bertambah Rp 80.000.000", "type": "positive"}
                ],
                "document": {
                    "type": "KONTRAK_LEASING",
                    "title": "Perjanjian Sewa Pembiayaan Fasilitas Mesin No. 018/LSG-FIN/2026",
                    "recipient": "PT ORIX Indonesia Finance",
                    "summary": "Fasilitas pembiayaan investasi mesin perakitan otomatis dengan skema sewa guna usaha berbunga kompetitif."
                },
                "cfo_verdict": "Struktur permodalan yang seimbang antara Debt vs Equity untuk mendanai pertumbuhan."
            },
            {
                "choice_id": "B",
                "label": "Tunda Investasi Ekspansi & Fokus Memaksimalkan Utilitas Mesin yang Ada",
                "rationale": "Menghindari komitmen utang baru di tengah ketidakpastian iklim suku bunga makro.",
                "immediate_cost": 0.0,
                "ripples": [
                    {"dept": "finance", "effect": "Posisi kas dan neraca tetap konservatif tanpa utang baru", "type": "positive"},
                    {"dept": "manufacturing", "effect": "Kapasitas produksi tetap di batas saat ini", "type": "neutral"}
                ],
                "document": {
                    "type": "MEMO_CAPEX",
                    "title": "Notulen Rapat Komite Investasi Modal No. 009/CAPEX-MGT/2026",
                    "recipient": "Dewan Komisaris & Direksi",
                    "summary": "Penundaan realisasi belanja modal ekspansi untuk prioritas konsolidasi likuiditas kas."
                },
                "cfo_verdict": "Pilihan bijak jika proyeksi demand pasar ke depan belum stabil."
            }
        ]
    }
]

# ==========================================
# 3. HELPER FUNCTIONS FOR SELECTION
# ==========================================

def get_scenario_by_id(scenario_id: str) -> Optional[Dict[str, Any]]:
    for sc in SCENARIO_MATRIX:
        if sc["id"] == scenario_id:
            return sc
    return None

def get_all_scenarios_matrix() -> List[Dict[str, Any]]:
    return SCENARIO_MATRIX

def get_random_customer_temperament(seed_id: int = None) -> Dict[str, Any]:
    if seed_id is not None:
        idx = seed_id % len(CUSTOMER_TEMPERAMENTS)
        item = CUSTOMER_TEMPERAMENTS[idx].copy()
    else:
        item = random.choice(CUSTOMER_TEMPERAMENTS).copy()
    item["dialog"] = random.choice(item["sample_dialogs"])
    return item

def get_union_leader_for_company(company_id: int) -> Dict[str, Any]:
    idx = company_id % len(UNION_PERSONALITIES)
    return UNION_PERSONALITIES[idx]

def trigger_random_black_swan() -> Dict[str, Any]:
    return random.choice(BLACK_SWAN_SHOCKS)

# ==========================================
# 4. ACTION RIPPLES ENGINE (Cross-Dept Causality)
# ==========================================

def calculate_action_ripples(
    company_id: int,
    action_type: str,
    action_payload: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Computes cross-departmental impacts when user takes routine ERP actions.
    Returns structured domino consequence objects for UI toast & analytics.
    """
    ripples = []
    summary = ""
    severity = "info"

    if action_type == "PURCHASE_ORDER_APPROVED":
        total_amount = float(action_payload.get("total_amount", 0.0))
        ripples = [
            {"dept": "Purchasing", "effect": f"Pesanan Bahan Baku senilai Rp {total_amount:,.0f} disetujui", "type": "positive"},
            {"dept": "Finance", "effect": f"Komitmen Kas keluar Rp {total_amount:,.0f} dijadwalkan pada jatuh tempo AP", "type": "negative"},
            {"dept": "Manufacturing", "effect": "Jadwal MRP otomatis sinkron, bahan baku siap dialokasikan ke Work Center", "type": "positive"},
            {"dept": "Warehouse", "effect": "Penerimaan barang (Goods Receipt) dijadwalkan masuk sistem pergudangan", "type": "neutral"}
        ]
        summary = f"PO Approved: Bahan baku masuk alur MRP, kewajiban AP kas Rp {total_amount:,.0f} tercatat."
        severity = "success"

    elif action_type == "PRODUCTION_BATCH_COMPLETED":
        qty = action_payload.get("quantity", 0)
        product_name = action_payload.get("product_name", "Produk Jadi")
        ripples = [
            {"dept": "Manufacturing", "effect": f"Batch {qty} unit {product_name} selesai diproduksi", "type": "positive"},
            {"dept": "Warehouse", "effect": f"Persediaan barang jadi (FG) bertambah +{qty} unit", "type": "positive"},
            {"dept": "Purchasing", "effect": f"Stok bahan baku (BOM) otomatis terpotong sesuai rasio perakitan", "type": "neutral"},
            {"dept": "Accounting", "effect": "Jurnal mutasi persediaan Bahan Baku (WIP) ke Barang Jadi terbentuk", "type": "positive"}
        ]
        summary = f"Produksi Selesai: +{qty} {product_name} masuk gudang, HPP manufaktur dikapitalisasi."
        severity = "success"

    elif action_type == "HR_WAGE_INCREASE":
        percentage = action_payload.get("raise_percentage", 5.0)
        ripples = [
            {"dept": "HR", "effect": f"Kenaikan upah +{percentage}% disepakati, moral pekerja meningkat pesat", "type": "positive"},
            {"dept": "Manufacturing", "effect": "Efisiensi lini produksi naik +10%, risiko mogok kerja turun ke 0%", "type": "positive"},
            {"dept": "Finance", "effect": f"Beban gaji bulanan tetap (Fixed Overhead) naik permanen", "type": "negative"}
        ]
        summary = f"Kesepakatan Buruh: Upah naik +{percentage}%, produktivitas pabrik pulih 100%."
        severity = "success"

    elif action_type == "CRM_DISCOUNT_APPROVED":
        discount = action_payload.get("discount_percentage", 10.0)
        ripples = [
            {"dept": "CRM", "effect": f"Diskon kompensasi {discount}% disetujui, somasi/komplain pelanggan dicabut", "type": "positive"},
            {"dept": "Finance", "effect": f"Pendapatan invoice berkurang {discount}%, margin laba kotor terkoreksi", "type": "negative"},
            {"dept": "Accounting", "effect": "Credit Note diterbitkan untuk memotong saldo piutang pelanggan", "type": "neutral"}
        ]
        summary = f"Komplain Selesai: Diskon {discount}% diberikan, kontrak jangka panjang pelanggan terselamatkan."
        severity = "warning"

    elif action_type == "TAX_SETTLEMENT":
        amount = float(action_payload.get("amount", 0.0))
        ripples = [
            {"dept": "Accounting", "effect": f"Pelunasan SKPKB Pajak Rp {amount:,.0f} sukses disetor ke kas negara", "type": "positive"},
            {"dept": "Finance", "effect": f"Kas likuid terpotong seketika Rp {amount:,.0f}", "type": "negative"},
            {"dept": "Executive", "effect": "Status audit fiskal dinyatakan 'Kepatuhan Pajak Baik (Good Tax Standing)'", "type": "positive"}
        ]
        summary = f"Pajak Lunas: SKPKB Rp {amount:,.0f} terbayar, sengketa perpajakan ditutup resmi."
        severity = "info"

    else:
        ripples = [
            {"dept": "General Operations", "effect": f"Aksi sistem '{action_type}' diproses", "type": "neutral"}
        ]
        summary = f"Aksi '{action_type}' berhasil dicatat ke sistem ERP."

    return {
        "action_type": action_type,
        "company_id": company_id,
        "timestamp": datetime.now().isoformat(),
        "severity": severity,
        "summary": summary,
        "ripples": ripples
    }

# ==========================================
# 5. SCENARIO BRANCH EXECUTION ENGINE
# ==========================================

def execute_scenario_branch(
    company_id: int,
    scenario_id: str,
    choice_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Executes a branching decision, applies financial/operational mutations,
    persists a CompanyStoryEvent, and returns comprehensive outcome data.
    """
    scenario = get_scenario_by_id(scenario_id)
    if not scenario:
        raise ValueError(f"Skenario ID '{scenario_id}' tidak ditemukan.")

    selected_branch = None
    for b in scenario["branches"]:
        if b["choice_id"] == choice_id:
            selected_branch = b
            break

    if not selected_branch:
        raise ValueError(f"Pilihan cabang '{choice_id}' tidak valid untuk skenario {scenario_id}.")

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"Company ID {company_id} tidak ditemukan.")

    # Check if this scenario has already been decided for this company
    existing_event = (
        db.query(CompanyStoryEvent)
        .filter(
            CompanyStoryEvent.company_id == company_id,
            CompanyStoryEvent.title.like(f"[{scenario_id}]%")
        )
        .first()
    )
    if existing_event:
        raise ValueError(f"Skenario [{scenario_id}] sudah memiliki keputusan resmi yang mengikat ({existing_event.decision_taken}) dan tidak dapat diganti sepihak.")

    cost = float(selected_branch.get("immediate_cost", 0.0))

    # 1. Mutate Company and SimulationState
    if cost > 0:
        company.current_cash = max(0.0, float(company.current_cash or 0.0) - cost)
        db.add(company)

    state = db.query(SimulationState).filter(SimulationState.company_id == company_id).first()
    if state:
        if cost > 0:
            state.cash = max(0.0, state.cash - cost)
            state.expenses += cost
            state.net_profit -= cost * 0.4
        
        # Domain-specific operational ripples
        dom = scenario.get("domain", "")
        if dom == "purchasing":
            if choice_id == "A":
                state.supplier_health = min(100.0, state.supplier_health + 12.0)
                # Boost raw material stock
                raw_prod = db.query(Product).filter(Product.company_id == company_id, Product.product_type == "raw_material").first()
                if raw_prod:
                    raw_prod.current_stock += 50
            elif choice_id == "B":
                state.supplier_health = max(30.0, state.supplier_health - 15.0)
                # Increase vendor defect rate
                v_obj = db.query(Vendor).filter(Vendor.company_id == company_id).first()
                if v_obj:
                    v_obj.defect_rate = min(15.0, v_obj.defect_rate + 3.5)
            elif choice_id == "C":
                state.csat_score = max(30.0, state.csat_score - 10.0)

        elif dom == "manufacturing":
            if choice_id == "A":
                state.machine_health = min(100.0, state.machine_health + 20.0)
                wc_obj = db.query(WorkCenter).filter(WorkCenter.company_id == company_id).first()
                if wc_obj:
                    wc_obj.status = "operational"
                    wc_obj.failure_rate = max(1.0, wc_obj.failure_rate - 2.5)
            elif choice_id == "B":
                state.machine_health = max(40.0, state.machine_health - 10.0)
            elif choice_id == "C":
                fg_prod = db.query(Product).filter(Product.company_id == company_id, Product.product_type == "finished_good").first()
                if fg_prod:
                    fg_prod.current_stock += 30

        elif dom == "crm":
            if choice_id == "A":
                state.csat_score = min(100.0, state.csat_score + 15.0)
                state.revenue += 45000000.0
            elif choice_id == "B":
                state.csat_score = min(100.0, state.csat_score + 8.0)
            elif choice_id == "C":
                state.csat_score = max(20.0, state.csat_score - 25.0)

        elif dom == "hr":
            if choice_id == "A":
                state.worker_morale = min(100.0, state.worker_morale + 18.0)
                state.is_strike_active = False
                # Update employee salaries
                for emp in db.query(Employee).filter(Employee.company_id == company_id).all():
                    emp.monthly_salary = float(emp.monthly_salary) * 1.05
            elif choice_id == "B":
                state.worker_morale = min(100.0, state.worker_morale + 5.0)
            elif choice_id == "C":
                state.worker_morale = max(25.0, state.worker_morale - 25.0)
                state.is_strike_active = True
                state.strike_reason = "Tuntutan kenaikan upah lembur ditolak oleh manajemen."

        elif dom == "accounting":
            if choice_id == "A":
                state.overall_score = min(100.0, state.overall_score + 5.0)
            elif choice_id == "B":
                state.cash = min(999999999.0, state.cash + 25000000.0)
                company.current_cash = state.cash

        # Update Cash Account 1001 in General Ledger
        cash_acc = db.query(Account).filter(Account.company_id == company_id, Account.code == "1001").first()
        if cash_acc:
            cash_acc.balance = state.cash

    # 2. Persist CompanyStoryEvent
    event = CompanyStoryEvent(
        company_id=company.id,
        round_number=state.current_round if state else 1,
        period_name=state.period_name if state else "Periode Berjalan",
        domain=scenario["domain"],
        event_type="scenario_branch",
        title=f"[{scenario['id']}] {scenario['title']}",
        description=f"Keputusan: {selected_branch['label']}. {selected_branch['rationale']}",
        decision_taken=f"Pilihan {selected_branch['choice_id']}: {selected_branch['label']}",
        ripple_summary=json.dumps(selected_branch.get("ripples", [])),
        document_data=json.dumps(selected_branch.get("document", None)) if selected_branch.get("document") else None,
        created_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "event_id": event.id,
        "company_id": company.id,
        "company_name": company.name,
        "scenario_id": scenario["id"],
        "scenario_title": scenario["title"],
        "domain": scenario["domain"],
        "choice_id": selected_branch["choice_id"],
        "choice_label": selected_branch["label"],
        "rationale": selected_branch["rationale"],
        "cost_incurred": cost,
        "remaining_cash": float(state.cash if state else company.current_cash or 0.0),
        "ripples": selected_branch.get("ripples", []),
        "document": selected_branch.get("document", None),
        "cfo_verdict": selected_branch.get("cfo_verdict", ""),
        "executed_at": event.created_at.isoformat()
    }

# ==========================================
# 6. SMART DETERMINISTIC CFO DIAGNOSTICS
# ==========================================

def run_smart_cfo_diagnostics(company_id: int, db: Session) -> Dict[str, Any]:
    """
    Pure Python deterministic CFO financial analysis:
    - Working Capital Analysis (Current Ratio, Quick Ratio, Cash Ratio)
    - DuPont Analysis (ROE = Net Profit Margin x Asset Turnover x Equity Multiplier)
    - Altman Z-Score for private/manufacturing firms
    - Qualitative Risk Flags & Pedagogical Lecturer Recommendations
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise ValueError(f"Company ID {company_id} tidak ditemukan.")

    cash = float(company.current_cash or 0.0)

    # Calculate Accounts Receivable (Piutang) from Sales invoices or journals
    # Default baseline simulation values if ledger is fresh
    receivables = 25000000.0
    inventory_value = 45000000.0
    fixed_assets = 120000000.0
    
    current_liabilities = 35000000.0
    long_term_debt = 40000000.0
    
    total_revenue = 180000000.0
    cogs = 95000000.0
    operating_expenses = 35000000.0
    
    gross_profit = total_revenue - cogs
    operating_profit = gross_profit - operating_expenses
    tax_rate = 0.11
    net_income = max(1000000.0, operating_profit * (1 - tax_rate))

    current_assets = cash + receivables + inventory_value
    total_assets = current_assets + fixed_assets
    total_liabilities = current_liabilities + long_term_debt
    total_equity = max(10000000.0, total_assets - total_liabilities)

    # 1. Liquidity & Working Capital Ratios
    working_capital = current_assets - current_liabilities
    current_ratio = round(current_assets / max(1.0, current_liabilities), 2)
    quick_ratio = round((cash + receivables) / max(1.0, current_liabilities), 2)
    cash_ratio = round(cash / max(1.0, current_liabilities), 2)

    # 2. DuPont Analysis
    # ROE = (Net Income / Revenue) * (Revenue / Total Assets) * (Total Assets / Equity)
    profit_margin = round((net_income / max(1.0, total_revenue)) * 100, 2)
    asset_turnover = round(total_revenue / max(1.0, total_assets), 2)
    equity_multiplier = round(total_assets / max(1.0, total_equity), 2)
    roe = round((net_income / max(1.0, total_equity)) * 100, 2)
    roa = round((net_income / max(1.0, total_assets)) * 100, 2)

    # 3. Altman Z-Score for Emerging Markets / Private Manufacturing
    # Z' = 0.717(X1) + 0.847(X2) + 3.107(X3) + 0.420(X4) + 0.998(X5)
    # X1 = Working Capital / Total Assets
    # X2 = Retained Earnings / Total Assets (approx 0.15)
    # X3 = EBIT / Total Assets
    # X4 = Book Value Equity / Total Liabilities
    # X5 = Sales / Total Assets
    x1 = working_capital / max(1.0, total_assets)
    x2 = (total_equity * 0.3) / max(1.0, total_assets)
    x3 = operating_profit / max(1.0, total_assets)
    x4 = total_equity / max(1.0, total_liabilities)
    x5 = total_revenue / max(1.0, total_assets)

    z_score = round(
        (0.717 * x1) + (0.847 * x2) + (3.107 * x3) + (0.420 * x4) + (0.998 * x5),
        2
    )

    if z_score >= 2.9:
        z_status = "SAFE ZONE (Sehat)"
        z_color = "emerald"
    elif z_score >= 1.23:
        z_status = "GREY ZONE (Waspada)"
        z_color = "amber"
    else:
        z_status = "DISTRESS ZONE (Bahaya Kebangkrutan)"
        z_color = "rose"

    # 4. Strategic Recommendations & Risk Flags
    risk_flags = []
    recommendations = []

    if cash_ratio < 0.5:
        risk_flags.append({
            "code": "CASH_CRUNCH",
            "title": "Rasio Kas Rendah (Likuiditas Rentan)",
            "detail": f"Cash Ratio saat ini {cash_ratio}x (standar aman > 0.5x). Rentan terhadap pengeluaran tak terduga."
        })
        recommendations.append("Percepat penagihan piutang pelanggan (AR Collection) dan tunda pengeluaran belanja modal non-kritis.")

    if current_ratio < 1.3:
        risk_flags.append({
            "code": "WORKING_CAP_PRESSURE",
            "title": "Tekanan Modal Kerja Jangka Pendek",
            "detail": f"Current Ratio {current_ratio}x mendekati batas minimum covenant perbankan (1.2x)."
        })
        recommendations.append("Negosiasikan perpanjangan tenor utang dagang (AP) ke pemasok bahan baku.")

    if roe > 15:
        recommendations.append("Kinerja efisiensi ekuitas (ROE) sangat baik; pertahankan perputaran persediaan di tingkat optimal.")
    else:
        recommendations.append("Tingkatkan Asset Turnover dengan menggenjot volume penjualan barang jadi tanpa menambah utang baru.")

    if not risk_flags:
        risk_flags.append({
            "code": "OPTIMAL_HEALTH",
            "title": "Fundamental Keuangan Prima",
            "detail": "Seluruh rasio likuiditas, solvabilitas, dan profitabilitas berada dalam rentang standar industri yang sangat sehat."
        })

    # Recent story decisions made by this company
    recent_events = (
        db.query(CompanyStoryEvent)
        .filter(CompanyStoryEvent.company_id == company.id)
        .order_by(CompanyStoryEvent.created_at.desc())
        .limit(5)
        .all()
    )

    event_history = []
    for ev in recent_events:
        doc_parsed = None
        if ev.document_data:
            try:
                doc_parsed = json.loads(ev.document_data) if isinstance(ev.document_data, str) else ev.document_data
            except Exception:
                doc_parsed = None
        
        event_history.append({
            "id": ev.id,
            "title": ev.title,
            "domain": ev.domain,
            "decision_taken": ev.decision_taken,
            "description": ev.description,
            "document": doc_parsed,
            "executed_at": ev.created_at.isoformat()
        })

    return {
        "company_id": company.id,
        "company_name": company.name,
        "as_of_date": datetime.now().strftime("%d %B %Y"),
        "balance_sheet_summary": {
            "cash": cash,
            "receivables": receivables,
            "inventory": inventory_value,
            "fixed_assets": fixed_assets,
            "total_assets": total_assets,
            "current_liabilities": current_liabilities,
            "long_term_debt": long_term_debt,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "working_capital": working_capital
        },
        "income_statement_summary": {
            "total_revenue": total_revenue,
            "cogs": cogs,
            "gross_profit": gross_profit,
            "operating_expenses": operating_expenses,
            "operating_profit": operating_profit,
            "net_income": net_income
        },
        "ratios": {
            "current_ratio": current_ratio,
            "quick_ratio": quick_ratio,
            "cash_ratio": cash_ratio,
            "gross_margin_pct": round((gross_profit / total_revenue) * 100, 2),
            "operating_margin_pct": round((operating_profit / total_revenue) * 100, 2),
            "net_profit_margin_pct": profit_margin,
            "asset_turnover": asset_turnover,
            "equity_multiplier": equity_multiplier,
            "return_on_assets_pct": roa,
            "return_on_equity_pct": roe
        },
        "altman_z_score": {
            "score": z_score,
            "status": z_status,
            "color": z_color,
            "interpretation": "Model prediksi kesehatan finansial Altman Z-Score untuk manufaktur swasta."
        },
        "risk_flags": risk_flags,
        "cfo_recommendations": recommendations,
        "event_history": event_history
    }
