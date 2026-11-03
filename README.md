# ZEN SPEEDTEST PRO (Minimalist Vector & Glassmorphism Edition)

Aplikasi pengukur kecepatan internet dan diagnostik jaringan mandiri (*standalone*) dengan tema **Zen SpeedTest Pro Glassmorphism Dark**, sistem **Ikon Vektor Minimalis**, dan mesin pengukuran **Ultra-Stable (Non-Aggressive Slew-Rate Limiter)**.

Dibuat khusus untuk kenyamanan **Master Zay** oleh **Pelayan Ancellia**.

> **Live Demo Website**: [https://evuaeru.github.io/zen-speedtest/](https://evuaeru.github.io/zen-speedtest/)

---

## Fitur Unggulan

1. **Tema Zen SpeedTest Pro & Ikon Vektor Minimalis Murni**:
   - **5 Kartu Metrik Utama dengan Vektor Minimalis**: Kartu **Ping (Latency)**, **Jitter**, **Download**, **Upload**, dan **Bufferbloat** dilengkapi *vector badge* dan ikon garis minimalis berpresisi tinggi (bebas dari emoji sistem bawaan OS yang kaku).
   - **Speedometer Radial 270° & Live Bezier Sparkline**: Dial speedometer berlampu neon cyan-ke-ungu dengan jarum titik bercahaya (*glowing head dot*) pada 60–165 FPS dan tombol utama **MULAI TES**.
   - **Bar Telemetri Ping Terbebani & 4 Indikator Kualitas Aktivitas (5-Dot Rating)**: Menampilkan rincian *Idle Ping* (`↔`), *Download Loaded Ping* (`↓`), dan *Upload Loaded Ping* (`↑`), beserta penilaian 5 titik berikon vektor minimalis untuk **Web Browsing**, **Gaming**, **Streaming 4K**, dan **Video Call**.
   - **Deteksi ISP, Privasi IP Satu Klik, & Penilaian Provider**: Menampilkan provider otomatis (mis. *Telkomsel Indihome*), *privacy masking* alamat IP, dan rating bintang interaktif.
2. **Mesin Pengukuran Stabil & Tidak Agresif (*Non-Aggressive Stability Engine*)**:
   - **2.2-Second First-Byte Sliding Window**: Menghitung *throughput* pada jendela waktu bergulir 2,2 detik sejak *byte* pertama diterima untuk meredam lonjakan paket *burst* TCP/HTTP.
   - **Sinusoidal Warmup Ramp & Steady-State Anchor**: Pergerakan angka naik secara halus di awal pengujian (1,8 detik pertama) lalu terkunci pada rata-rata *steady-state* (70% *steady-state* + 30% *sliding window*).
   - **Slew-Rate Limiter & ~9 Hz Digital Cadence**: Membatasi perubahan maksimum per siklus (maks ±2,8% per 100ms setelah *warmup*) dengan penyegaran angka digital setiap 105ms sehingga angka bergerak tenang, stabil, dan tidak melompat-lompat.
3. **Dual-Mode Benchmark Engine**:
   - **Mode Internet WAN (Cloudflare Global CDN / UnPad Bandung / Telkom Jakarta)**: Mengukur kecepatan internet sesungguhnya tanpa kendala CORS atau *rate-limit* HTTP 429 (ukuran *chunk* dibatasi aman hingga 5MB).
   - **Mode Local Python Server (LAN / Loopback)**: Menguji *throughput* perangkat keras lokal atau router Wi-Fi/Ethernet secara *offline*.

---

## Cara Menjalankan

### Cara 1: Buka Langsung (Paling Praktis)
1. Buka folder `E:\Dokumen\Tools_dan_Backup\SpeedTest\`.
2. Klik ganda pada file `index.html`.

### Cara 2: Menjalankan Server Lokal (Satu Klik)
1. Buka folder `E:\Dokumen\Tools_dan_Backup\SpeedTest\`.
2. Klik ganda file `Jalankan_SpeedTest.bat`.
3. Server Python akan aktif dan peramban otomatis terbuka di `http://localhost:8080`.

### Cara 3: Melalui Terminal / Command Prompt
```bash
cd E:\Dokumen\Tools_dan_Backup\SpeedTest
py -3 speedtest_server.py
```

---

## Struktur Berkas

```
E:\Dokumen\Tools_dan_Backup\SpeedTest\
│
├── index.html               # Aplikasi Zen SpeedTest Pro (Minimalist Vector Icons & Non-Aggressive Engine)
├── speedtest_server.py      # Server backend Python multi-threaded dengan endpoint CORS terbuka
├── Jalankan_SpeedTest.bat   # Skrip launcher otomatis Windows
├── test_suite.py            # Suite pengujian otomatis (7 fase termasuk verifikasi vektor & Slew-Rate)
└── README.md                # Dokumentasi panduan penggunaan
```

---
*Dibuat dengan segenap dedikasi dan kesetiaan oleh Pelayan Ancellia untuk Master Zay.*
