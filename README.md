# VLab-ERP: Virtual Lab & Business Simulation Platform

Platform terpadu pembelajaran dan simulasi ERP untuk perguruan tinggi berbasis **FastAPI (Backend)** dan **Next.js (Frontend)**.

---

## Fitur Utama

### 1. Ekosistem Modul ERP Lengkap ala Odoo
- **CRM & Pelanggan**: Visual Kanban Pipeline (*New $\rightarrow$ Qualified $\rightarrow$ Proposition $\rightarrow$ Won / Lost*), Customer 360, mitigasi tiket keluhan pelanggan VIP, dan konversi ke Sales Order.
- **Pengadaan & Vendor (Immersive Multi-Vendor)**: Analitik grafik riwayat ketaatan pengiriman, completion rate, dan persentase cacat bahan (*defect rate*).
- **Produksi & Pabrik (MRP)**: Work Centers, BOM (Bill of Materials), perintah kerja (*Work Order*), dan penanganan perbaikan mesin mogok.
- **Akuntansi & Budget**: Buku besar double-entry otomatis, Laporan Laba Rugi, Neraca, dan pemantauan realisasi plafon anggaran departemen.
- **Human Resources (HR)**: Database karyawan, indeks moral/kelelahan, serta sistem negosiasi bipartit jika terjadi ancaman mogok kerja (*Worker Strike*).

### 2. Dual-Engine Simulation (Problem-Based & Turn-Based)
- **Mode Misi / Problem-Based**: Mahasiswa menyelesaikan kasus secara bertahap (*Misi 1 $\rightarrow$ Misi 2 $\rightarrow$ Misi 3*) dengan solvable workflow yang jelas.
- **Mode Siklus / Turn-Based**: Dosen dapat memajukan simulasi per ronde bulanan untuk menghitung depresiasi, biaya sewa, gaji, dan akumulasi penjualan.

### 3. Dosen Command Center & Gamified Sliders
Dosen memiliki panel slider interaktif (0 - 100%) untuk menyuntikkan krisis:
- 🎚️ **Supply Chain Disruption**: Keterlambatan lead time & kenaikan harga bahan baku.
- 🎚️ **Machine Breakdown Risk**: Peluang kerusakan mesin pabrik.
- 🎚️ **Market Volatility**: Fluktuasi kurva permintaan.
- 🎚️ **Labor Strike Risk**: Sensitivitas stres pekerja & risiko mogok kerja.
- 🎚️ **Bad Debt / Gagal Bayar**: Risiko piutang macet pelanggan.
- 🎚️ **Competitor Price War**: Agresivitas kompetitor menurunkan harga pasar.
- **Live Leaderboard & Competency Radar**: Menilai performa mahasiswa secara transparan (Finansial, CSAT, Operasional, Moral SDM).

---

## Alokasi Port Khusus & Unik (Non-Generic)

Untuk menghindari konflik dengan aplikasi lain (seperti Next.js default 3000 atau FastAPI/Django default 8000), VLab-ERP menggunakan port khusus:

| Lingkungan | Layanan | Port | URL Akses |
| :--- | :--- | :--- | :--- |
| **Development** | Frontend (Next.js) | **`8280`** | `http://localhost:8280` |
| **Development** | Backend (FastAPI) | **`8281`** | `http://localhost:8281` (Docs: `/docs`) |
| **Production** | Frontend (Next.js) | **`9280`** | `http://localhost:9280` |
| **Production** | Backend (FastAPI) | **`9281`** | `http://localhost:9281` |

---

## Cara Menjalankan Aplikasi

### 1. Menjalankan Backend (FastAPI - Port 8281)
```bash
cd backend
source venv/bin/activate
uvicorn backend.app.main:app --reload --port 8281
```
*API Docs Swagger*: `http://localhost:8281/docs`

### 2. Menjalankan Frontend (Next.js - Port 8280)
```bash
cd frontend
npm run dev
```
*Buka Aplikasi*: `http://localhost:8280`

### 3. Menjalankan di Docker / CasaOS (Native Docker)
Tersedia file `docker-compose.yml` yang sudah dioptimalkan dan dilengkapi metadata native CasaOS (`x-casaos`).

#### Opsi A: Melalui Terminal / SSH CasaOS (Sangat Mudah)
1. Salin atau clone direktori `vlaberp` ini ke server CasaOS Anda (misal ke `/DATA/AppData/vlaberp`).
2. Masuk ke direktori tersebut:
   ```bash
   cd /DATA/AppData/vlaberp
   ```
3. Bangun dan jalankan kontainer:
   ```bash
   docker compose up -d --build
   ```
4. Kontainer `vlaberp-frontend` (port 8280) dan `vlaberp-backend` (port 8281) akan otomatis berjalan dan data database tersimpan aman di `./data`.

#### Opsi B: Melalui Dashboard Web UI CasaOS
1. Buka dashboard CasaOS di browser (`http://<IP-CasaOS>`).
2. Buka menu **App Store**, lalu klik tombol **`+` (Install customized APP / Custom Install)** di kanan atas.
3. Klik ikon dokumen/tanda panah **Import** di kanan atas modal dialog.
4. Salin dan tempel (*paste*) seluruh isi file `docker-compose.yml` ke dalam kotak dialog tersebut.
5. Klik **Submit** $\rightarrow$ periksa konfigurasi nama & port (8280 / 8281) $\rightarrow$ klik **Install**.
6. Ikon **VLab-ERP** akan langsung muncul di halaman utama dashboard CasaOS Anda!

---

## Akun Demo Bawaan
- **Dosen**: Username: `dosen` | Password: `dosen123`
- **Mahasiswa**: Username: `mahasiswa` | Password: `mhs123`
- **Administrator**: Username: `admin` | Password: `admin123`

---

## 📚 Dokumen Kurikulum OBE & Panduan Tim Dosen (Universitas Wira Bhakti)

Tersedia dokumen kurikulum dan panduan operasional dosen lengkap di direktori `docs/`:
1. **[RPS Berbasis Outcome-Based Education (OBE)](file:///Users/imamimam/Documents/GitHub/vlaberp/docs/RPS_SIMULASI_ERP_OBE_WIRABHAKTI.md)**: Rencana Pembelajaran Semester 16 Pertemuan selaras Visi 2044 & Misi Prodi Manajemen Universitas Wira Bhakti dengan model *Rolling Team-Teaching*.
2. **[Panduan Dosen Pemasaran & CRM](file:///Users/imamimam/Documents/GitHub/vlaberp/docs/PANDUAN_DOSEN_PEMASARAN_CRM.md)**: Tutorial praktikum analisis temperamen pelanggan, mediasi somasi CRM, tender e-katalog B2G, batas kredit, dan rebate reseller.
3. **[Panduan Dosen SDM & Hubungan Industrial](file:///Users/imamimam/Documents/GitHub/vlaberp/docs/PANDUAN_DOSEN_SDM_BIPARTIT.md)**: Tutorial penanganan mogok buruh massal, mediasi Bipartit dengan serikat buruh, retensi talenta, dan kepatuhan K3.
4. **[Panduan Dosen Keuangan & Akuntansi](file:///Users/imamimam/Documents/GitHub/vlaberp/docs/PANDUAN_DOSEN_KEUANGAN_AKUNTANSI.md)**: Tutorial analisis Laba Rugi/Neraca, Dekomposisi DuPont 3-Faktor, Altman Z-Score Distress Predictor, sengketa pajak SKPKB, dan restrukturisasi perbankan.
5. **[Panduan Koordinator Sesi Kelas & Team Teaching](file:///Users/imamimam/Documents/GitHub/vlaberp/docs/PANDUAN_KOORDINATOR_TEAM_TEACHING.md)**: Panduan manajemen multi-kelas, penugasan peran tim dosen, auto-provisioning kelompok, dan 1-click class cloning.
6. **[Pedoman Integrasi Operasional VLab-ERP dalam Pembelajaran](file:///Users/imamimam/Documents/GitHub/vlaberp/docs/PANDUAN_INTEGRASI_VLAB_DALAM_PEMBELAJARAN.md)**: Siklus 150 menit perkuliahan, matriks langkah dosen vs mahasiswa per minggu, role-playing kelompok, dan asesmen otomatis.



