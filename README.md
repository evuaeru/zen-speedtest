# ⚡ ZEN SPEEDTEST PRO (Ookla Dark Edition)

Aplikasi pengukur kecepatan internet dan diagnostik jaringan mandiri (*standalone*) dengan antarmuka minimalis gelap bergaya **Ookla Speedtest** dan mesin pengukuran **Ultra-Stable (Non-Aggressive Slew-Rate Limiter)**.

Dibuat khusus untuk kenyamanan **Master Zay** oleh **Pelayan Ancellia**.

> 🌐 **Live Demo Website**: [https://evuaeru.github.io/zen-speedtest/](https://evuaeru.github.io/zen-speedtest/)

---

## 🌟 Fitur Unggulan

1. **Desain UI Minimalis Gelap (Ookla Speedtest Reference)**:
   - **Tombol Lingkaran `MULAI` Ikonik & Speedometer Terintegrasi**: Lingkaran ganda berlampu cyan saat *standby* yang bertransformasi mulus menjadi dial speedometer radial tanpa pergeseran tata letak (*zero layout shift*).
   - **Panel Hasil Presisi 2 Desimal**: Menampilkan angka **UNDUHAN Mbps** dan **UNGGAHAN Mbps** dengan tipografi *condensed* yang bersih dan mudah dibaca.
   - **3 Indikator Ping Real-Time (`Ping ms`)**: Menampilkan *Idle Ping* (`↔`), *Download Loaded Ping* (`↓`), dan *Upload Loaded Ping* (`↑`).
   - **4 Indikator Kualitas Aktivitas (5-Dot Rating)**: Penilaian otomatis berbasis 5 titik untuk **Web Browsing**, **Gaming Online**, **Video Streaming 4K**, dan **Video Call**.
   - **Informasi Koneksi, ISP, & Server + `NILAI PROVIDER ANDA`**: Deteksi nama provider (mis. *Telkomsel Indihome*), alamat IP (dengan fitur *privacy masking* satu klik), lokasi server (*UnPad Bandung*, *Telkom IIX Jakarta*, *Cloudflare Global Edge*, atau *Local Python Server*), serta 5 bintang penilaian provider interaktif.
2. **Mesin Pengukuran Stabil & Tidak Agresif (*Non-Aggressive Stability Engine*)**:
   - **2.2-Second Sliding Time Window**: Menghitung *throughput* pada jendela waktu bergulir 2,2 detik untuk meredam lonjakan paket *burst* TCP/HTTP.
   - **Sinusoidal Warmup Ramp & Steady-State Anchor**: Pergerakan angka naik secara halus di awal pengujian (1,8 detik pertama) lalu terkunci pada rata-rata *steady-state* (65% *steady-state* + 35% *sliding window*).
   - **Slew-Rate Limiter & 9 Hz Digital Cadence**: Membatasi perubahan maksimum per siklus (maks ±3,2% per 100ms) dengan penyegaran angka digital setiap 110ms sehingga angka bergerak tenang, stabil, dan tidak melompat-lompat.
3. **Dual-Mode Benchmark Engine**:
   - **Mode Internet WAN (Cloudflare Global Edge / UnPad Bandung / Telkom Jakarta)**: Mengukur kecepatan internet sesungguhnya tanpa kendala CORS.
   - **Mode Local Python Server (LAN / Loopback)**: Menguji *throughput* perangkat keras lokal atau router Wi-Fi/Ethernet secara *offline*.

---

## 🚀 Cara Menjalankan

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

## 🛠️ Struktur Berkas

```
E:\Dokumen\Tools_dan_Backup\SpeedTest\
│
├── index.html               # Aplikasi SpeedTest mandiri (UI Ookla Dark & Non-Aggressive Engine)
├── speedtest_server.py      # Server backend Python multi-threaded dengan endpoint CORS terbuka
├── Jalankan_SpeedTest.bat   # Skrip launcher otomatis Windows
├── test_suite.py            # Suite pengujian otomatis (7 fase termasuk uji kestabilan Slew-Rate)
└── README.md                # Dokumentasi panduan penggunaan
```

---
*Dibuat dengan segenap dedikasi dan kesetiaan oleh Pelayan Ancellia untuk Master Zay.*
