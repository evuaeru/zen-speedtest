# ⚡ ZEN SPEEDTEST PRO

Aplikasi pengukur kecepatan internet dan diagnostik jaringan mandiri (*standalone*), berakurasi tinggi, responsif, dan elegan dengan tema *glassmorphism cyberpunk dark mode*.

Dibuat khusus untuk kenyamanan **Master Zay** oleh **Pelayan Ancellia**.

> 🌐 **Live Demo Website**: [https://evuaeru.github.io/zen-speedtest/](https://evuaeru.github.io/zen-speedtest/)

---

## 🌟 Fitur Unggulan

1. **Dual-Mode Benchmark Engine**:
   - **Mode Internet WAN (Cloudflare Global Edge)**: Mengukur kecepatan unduh dan unggah jaringan internet sesungguhnya melalui ribuan titik server CDN global terdekat (Singapura & Jakarta) tanpa kendala CORS.
   - **Mode Local Python Server (LAN / Loopback)**: Menguji *throughput* perangkat keras lokal, router Wi-Fi 5/6, atau kabel Ethernet hingga kecepatan gigabit (1000+ Mbps) secara *offline*.
2. **Speedometer Gauge SVG Interaktif**:
   - Jarum dan *arc* dinamis terkalibrasi non-linear (0 hingga 1000+ Mbps) sehingga pergerakan tetap halus dan presisi baik pada koneksi 10 Mbps maupun 500+ Mbps.
   - Angka kecepatan digital real-time dengan tombol ganti satuan instan (**Mbps** $\leftrightarrow$ **MB/s**).
3. **Live Waveform / Sparkline Chart**:
   - Grafik canvas 60 FPS yang merekam fluktuasi dan kestabilan kecepatan transfer data secara real-time.
4. **Metrik Diagnostik Jaringan Komprehensif**:
   - **Ping / Latency**: Waktu tempuh bolak-balik (RTT) dalam milidetik (Nilai saat ini, minimum, dan rata-rata).
   - **Jitter (RFC 3550)**: Variasi selisih latency antar-paket data untuk mengukur kestabilan koneksi.
   - **Download Speed**: Kecepatan unduh rata-rata dan puncak dengan multi-stream paralel.
   - **Upload Speed**: Kecepatan unggah riil menggunakan *binary buffer streaming* via `XMLHttpRequest.upload`.
   - **Bufferbloat (Loaded Ping)**: Deteksi lonjakan latency saat jaringan sedang terbebani penuh oleh unduhan.
   - **Evaluasi Kualitas Jaringan**: Penilaian otomatis (Grade A+, A, B, C, D) dengan rekomendasi kesiapan untuk *gaming* kompetitif (Valorant/CS2), Discord, dan *streaming* 4K.
5. **Riwayat Pengujian & Ekspor Data**:
   - Menyimpan riwayat tes secara otomatis di peramban (`localStorage`).
   - Tombol **Salin Ringkasan** satu-klik untuk dibagikan.
   - Tombol **Unduh CSV** untuk analisis mendalam di Excel atau Google Sheets.
6. **Web Audio Synthesizer**:
   - Efek suara sintetis murni (*zero external audio files*) untuk notifikasi mulai dan selesai tes.

---

## 🚀 Cara Menjalankan

Master Zay memiliki beberapa pilihan mudah untuk membuka aplikasi ini:

### Cara 1: Buka Langsung (Paling Praktis)
1. Buka folder `E:\Dokumen\Tools_dan_Backup\SpeedTest\`.
2. Klik ganda pada file `index.html`.
3. Aplikasi akan langsung terbuka di peramban favorit Master Zay (Vivaldi, Chrome, Edge, dsb) dan siap digunakan!

### Cara 2: Menjalankan Server Lokal (Satu Klik)
1. Buka folder `E:\Dokumen\Tools_dan_Backup\SpeedTest\`.
2. Klik ganda file `Jalankan_SpeedTest.bat`.
3. Server Python berkecepatan tinggi akan otomatis aktif dan jendela peramban akan langsung terbuka di alamat `http://localhost:8080`.

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
├── index.html               # Aplikasi SpeedTest mandiri (HTML, CSS, JS, SVG, Canvas terintegrasi)
├── speedtest_server.py      # Server backend Python multi-threaded dengan endpoint CORS terbuka
├── Jalankan_SpeedTest.bat   # Skrip launcher otomatis Windows
└── README.md                # Dokumentasi panduan penggunaan
```

---

## 📖 Panduan Indikator Kualitas Jaringan

| Parameter | Sangat Bagus (A+) | Cukup Baik (B) | Butuh Perhatian (C/D) |
| :--- | :--- | :--- | :--- |
| **Ping** | < 20 ms | 20 - 60 ms | > 80 ms |
| **Jitter** | < 2 ms | 3 - 8 ms | > 15 ms |
| **Bufferbloat** | < +15 ms | +16 - +45 ms | > +60 ms |
| **Paket Hilang** | 0% | < 1% | > 2% |

---
*Dibuat dengan segenap dedikasi dan kesetiaan oleh Ancellia untuk Master Zay.*
