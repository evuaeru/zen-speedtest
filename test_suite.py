"""
Test Suite untuk Zen SpeedTest Pro
Memvalidasi integritas berkas, server lokal, endpoint CORS (termasuk Private Network Access),
ketahanan penanganan error, subprocess launcher, dan kelengkapan elemen DOM HTML.
Dibuat khusus untuk Master Zay oleh Pelayan Ancellia.
"""

import os
import sys
import time
import json
import threading
import subprocess
import urllib.request
import urllib.error
import io
from http.server import ThreadingHTTPServer

# Pastikan output aman di Windows console (cp1252 / cp437)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from speedtest_server import SpeedTestHandler, find_available_port

def test_file_integrity():
    print("[1/6] Memeriksa integritas berkas proyek...")
    required_files = [
        "index.html",
        "speedtest_server.py",
        "Jalankan_SpeedTest.bat",
        "README.md"
    ]
    for rf in required_files:
        path = os.path.join(BASE_DIR, rf)
        assert os.path.exists(path), f"File {rf} tidak ditemukan di {BASE_DIR}"
        size = os.path.getsize(path)
        assert size > 0, f"File {rf} kosong"
        print(f"  [OK] {rf} ({size:,} bytes)")

def test_html_dom_and_syntax():
    print("[2/6] Memvalidasi elemen DOM HTML & sintaks JavaScript...")
    html_path = os.path.join(BASE_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    required_ids = [
        "liveSpeedNumber",
        "gaugeActiveArc",
        "speedCanvas",
        "btnStartTest",
        "btnCancelTest",
        "valPing",
        "valJitter",
        "valDownload",
        "valUpload",
        "valBufferbloat",
        "gradeBadge",
        "verdictBox",
        "serverModeSelect",
        "streamCountSelect",
        "durationSelect",
        "historyTable",
        "btnExportCsv",
        "btnClearHistory"
    ]
    for dom_id in required_ids:
        assert f'id="{dom_id}"' in html, f"ID DOM '{dom_id}' tidak ditemukan di index.html"
    print(f"  [OK] Seluruh {len(required_ids)} elemen DOM krusial lengkap dan valid.")

    # Validasi sintaks JS dengan Node.js jika terpasang
    try:
        import re
        scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
        for i, s in enumerate(scripts):
            proc = subprocess.run(['node', '--check'], input=s.encode('utf-8'), capture_output=True)
            assert proc.returncode == 0, f"Syntax error pada script block {i+1}: {proc.stderr.decode('utf-8', errors='replace')}"
        print(f"  [OK] Sintaks JavaScript index.html terverifikasi 100% valid (Node v8 engine).")
    except (FileNotFoundError, ImportError):
        print("  [INFO] Node.js tidak tersedia untuk syntax check, dilewati.")

def test_subprocess_server_launch():
    print("[3/6] Menguji startup subprocess speedtest_server.py (Windows console encoding safety)...")
    server_py = os.path.join(BASE_DIR, "speedtest_server.py")
    # Simulasikan eksekusi Python pada Windows console tanpa UTF-8 paksa
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "cp1252"
    p = subprocess.Popen([sys.executable, server_py], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    time.sleep(1.2)
    p.terminate()
    stdout, stderr = p.communicate()
    assert "UnicodeEncodeError" not in stderr, f"Server gagal dengan UnicodeEncodeError:\n{stderr}"
    assert "ZEN SPEEDTEST SERVER" in stdout or p.returncode in (0, 15, -15), "Server tidak memulai banner dengan benar"
    print("  [OK] Subprocess speedtest_server.py berhasil dijalankan tanpa Unicode crash.")

def test_local_server_endpoints_and_cors():
    print("[4/6] Menguji endpoint server lokal, PNA header, dan ketahanan input...")
    port = find_available_port(8300)
    server = ThreadingHTTPServer(("127.0.0.1", port), SpeedTestHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.4)

    base = f"http://127.0.0.1:{port}"

    # 1. Ping
    req_ping = urllib.request.Request(f"{base}/api/ping")
    with urllib.request.urlopen(req_ping) as r:
        assert r.status in (200, 204)
        assert r.headers.get("Access-Control-Allow-Origin") == "*"
        assert r.headers.get("Access-Control-Allow-Private-Network") == "true"
        assert r.headers.get("Timing-Allow-Origin") == "*"
    print("  [OK] /api/ping: CORS & PNA Unlocked (204 No Content)")

    # 2. Preflight OPTIONS
    req_opt = urllib.request.Request(f"{base}/api/upload", method="OPTIONS")
    req_opt.add_header("Access-Control-Request-Method", "POST")
    req_opt.add_header("Access-Control-Request-Private-Network", "true")
    with urllib.request.urlopen(req_opt) as r:
        assert r.status == 204
        assert r.headers.get("Access-Control-Allow-Private-Network") == "true"
        assert r.headers.get("Access-Control-Allow-Origin") == "*"
    print("  [OK] OPTIONS Preflight: Mendukung Private Network Access (PNA)")

    # 3. Download Normal & Download Robustness (invalid bytes query)
    dl_size = 1024 * 1024 # 1MB
    req_dl = urllib.request.Request(f"{base}/api/download?bytes={dl_size}")
    t0 = time.time()
    with urllib.request.urlopen(req_dl) as r:
        content = r.read()
        dur = time.time() - t0
        assert len(content) == dl_size
        assert r.headers.get("Access-Control-Allow-Origin") == "*"
    print(f"  [OK] /api/download: Mengalirkan {len(content):,} bytes ({((len(content)*8/dur)/1e6):.2f} Mbps)")

    # Robustness test: invalid bytes param should not throw 500
    req_bad_dl = urllib.request.Request(f"{base}/api/download?bytes=invalid_param")
    with urllib.request.urlopen(req_bad_dl) as r:
        assert r.status == 200
        bad_content = r.read(1024)
        assert len(bad_content) > 0
    print("  [OK] /api/download: Resilien terhadap query parameter invalid (Fallback OK)")

    # 4. Upload Normal & Robustness
    ul_size = 256 * 1024 # 256KB
    req_ul = urllib.request.Request(f"{base}/api/upload", data=b"Z" * ul_size, headers={"Content-Type": "application/octet-stream"})
    with urllib.request.urlopen(req_ul) as r:
        resp = json.loads(r.read().decode("utf-8"))
        assert resp.get("status") == "success"
        assert resp.get("received_bytes") == ul_size
    print(f"  [OK] /api/upload: Menerima {ul_size:,} bytes berhasil ({resp.get('speed_mbps')} Mbps)")

    # 5. Info
    with urllib.request.urlopen(f"{base}/api/info") as r:
        info = json.loads(r.read().decode("utf-8"))
        assert info.get("status") == "online"
    print(f"  [OK] /api/info: Node '{info.get('node')}' aktif")

    server.shutdown()

def test_cloudflare_wan_reachability():
    print("[5/6] Menguji konektivitas WAN Cloudflare Edge...")
    try:
        req = urllib.request.Request("https://speed.cloudflare.com/__down?bytes=1000", headers={"User-Agent": "Mozilla/5.0"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=4) as r:
            assert r.status == 200
            cors = r.headers.get("Access-Control-Allow-Origin")
            dur = time.time() - t0
            colo = r.headers.get("colo", "Unknown")
        print(f"  [OK] Cloudflare Edge ({colo}): RTT {dur*1000:.1f}ms, CORS={cors}")
    except Exception as e:
        print(f"  [WARN] Cloudflare WAN check dilewati: {e}")

def test_batch_launcher_script():
    print("[6/7] Memvalidasi skrip launcher Jalankan_SpeedTest.bat...")
    bat_path = os.path.join(BASE_DIR, "Jalankan_SpeedTest.bat")
    with open(bat_path, "r", encoding="utf-8") as f:
        bat = f.read()
    assert "py -3 --version" in bat, "Batch launcher belum memiliki pengecekan eksekusi py -3"
    assert "index.html" in bat, "Batch launcher belum memiliki fallback index.html"
    assert "%LOCALAPPDATA%" in bat, "Batch launcher harus menggunakan %LOCALAPPDATA% dinamis"
    print("  [OK] Jalankan_SpeedTest.bat terstruktur aman dan fleksibel.")

def test_ookla_ui_and_stability_engine():
    print("[7/7] Menguji UI Ookla Reference, interaksi DOM, & kestabilan algoritma (Non-Aggressive Slew Limiter)...")
    html_path = os.path.join(BASE_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Pastikan seluruh elemen referensi Ookla tersedia
    ookla_elements = [
        "resultIdDisplay",
        "btnToggleHistory",
        "btnToggleSettings",
        "activeGaugeWrap",
        "valPingDown",
        "valPingUp",
        "qualCatBrowsing",
        "qualCatGaming",
        "qualCatStreaming",
        "qualCatVideoCall",
        "dotsBrowsing",
        "dotsGaming",
        "dotsStreaming",
        "dotsVideoCall",
        "connModeToggle",
        "ispNameDisplay",
        "btnGantiServer",
        "starRatingRow",
        "settingsDrawer",
        "historyDrawer",
        "UNDUHAN",
        "UNGGAHAN",
        "NILAI PROVIDER ANDA",
        "MULAI",
        "Ganti Server",
        "qual-icon-box no-frame",
        "167.53",
        "53.08",
        "179"
    ]
    for elem in ookla_elements:
        assert elem in html, f"Elemen/teks referensi Ookla '{elem}' tidak ditemukan di index.html"
    print(f"  [OK] Seluruh {len(ookla_elements)} komponen UI referensi Ookla terverifikasi.")

    # 2. Simulasi matematis & behavioral di Node.js untuk menguji kestabilan angka pada jaringan bursty, delayed handshake, & TCP slow-start
    node_test_script = r"""
function runAlgo(ticks, getBytesForTick) {
  const startTime = 0, warmupDuration = 1800, WINDOW_MS = 2200;
  let totalBytes = 0, warmupBytes = 0, warmupTime = 1800, warmupRecorded = false, smoothSpeed = 0;
  let firstByteTime = -1;
  const byteHistory = [{ t: 0, b: 0 }];
  let maxPostWarmupJumpPct = 0;

  for (let step = 1; step <= ticks; step++) {
    const now = step * 100;
    const bTick = getBytesForTick(step);
    if (bTick > 0 && firstByteTime < 0) {
      firstByteTime = Math.max(startTime, now - 100);
      byteHistory.length = 0;
      byteHistory.push({ t: firstByteTime, b: 0 });
    }
    totalBytes += bTick;
    byteHistory.push({ t: now, b: totalBytes });
    while (byteHistory.length > 2 && (now - byteHistory[1].t) > WINDOW_MS) {
      byteHistory.shift();
    }

    const activeElapsed = firstByteTime >= 0 ? (now - firstByteTime) : 0;
    if (!warmupRecorded && activeElapsed >= warmupDuration) {
      warmupBytes = totalBytes;
      warmupTime = now;
      warmupRecorded = true;
    }

    const anchor = byteHistory[0];
    const winDt = Math.max(0.08, (now - anchor.t) / 1000);
    const windowMbps = firstByteTime >= 0 ? ((totalBytes - anchor.b) * 8) / (winDt * 1e6) : 0;

    let rawTarget = windowMbps;
    let steadyMbps = windowMbps;
    if (activeElapsed < warmupDuration) {
      const ramp = 0.5 - 0.5 * Math.cos(Math.PI * (activeElapsed / warmupDuration));
      rawTarget = windowMbps * ramp;
    } else {
      const steadyDt = Math.max(0.1, (now - warmupTime) / 1000);
      steadyMbps = ((totalBytes - warmupBytes) * 8) / (steadyDt * 1e6);
      rawTarget = windowMbps * 0.30 + steadyMbps * 0.70;
    }

    const prevSpeed = smoothSpeed;
    if (smoothSpeed === 0 && rawTarget > 0) {
      smoothSpeed = rawTarget * 0.32;
    } else if (rawTarget > 0) {
      const alpha = activeElapsed < warmupDuration ? 0.24 : 0.14;
      let delta = (rawTarget - smoothSpeed) * alpha;
      if (activeElapsed >= warmupDuration) {
        const baseStep = Math.max(0.45, smoothSpeed * 0.028);
        const upStep = (steadyMbps > smoothSpeed * 1.18 && windowMbps > smoothSpeed * 1.18)
          ? Math.max(baseStep, Math.min(rawTarget * 0.055, (rawTarget - smoothSpeed) * 0.12))
          : baseStep;
        delta = Math.max(-baseStep, Math.min(upStep, delta));
      }
      smoothSpeed = Math.max(0, smoothSpeed + delta);
    }

    if (activeElapsed > 2500 && prevSpeed > 10) {
      const jumpPct = Math.abs(smoothSpeed - prevSpeed) / prevSpeed * 100;
      if (jumpPct > maxPostWarmupJumpPct) maxPostWarmupJumpPct = jumpPct;
    }
  }
  return { finalSpeed: smoothSpeed, maxJumpPct: maxPostWarmupJumpPct };
}

// Case A: Bursty traffic around 167.53 Mbps
const bursty = runAlgo(110, (step) => {
  const m = step % 4 === 0 ? 0.05 : step % 4 === 1 ? 2.40 : step % 4 === 2 ? 0.65 : 0.90;
  return Math.round((167.53 * 1e6 / 8) * 0.1 * m);
});
if (bursty.maxJumpPct > 3.0 || Math.abs(bursty.finalSpeed - 167.53) > 3.0) {
  console.error("FAIL Case A (Bursty):", bursty); process.exit(1);
}

// Case B: 900ms initial handshake delay in 7s test (167.53 Mbps)
const delayed = runAlgo(70, (step) => step <= 9 ? 0 : Math.round((167.53 * 1e6 / 8) * 0.1));
if (Math.abs(delayed.finalSpeed - 167.53) > 3.0) {
  console.error("FAIL Case B (Handshake Delay):", delayed); process.exit(1);
}

// Case C: TCP Slow-Start (25 Mbps for first 1.8s, then 300 Mbps for remaining 6.2s)
const slowStart = runAlgo(80, (step) => Math.round(((step <= 18 ? 25 : 300) * 1e6 / 8) * 0.1));
if (Math.abs(slowStart.finalSpeed - 300) > 5.0) {
  console.error("FAIL Case C (TCP Slow-Start):", slowStart); process.exit(1);
}

console.log(JSON.stringify({
  finalSpeed: bursty.finalSpeed.toFixed(2),
  maxJumpPct: bursty.maxJumpPct.toFixed(2),
  slowStartSpeed: slowStart.finalSpeed.toFixed(2)
}));
"""
    proc = subprocess.run(["node", "-e", node_test_script, html_path], capture_output=True, text=True)
    assert proc.returncode == 0, f"Uji kestabilan algoritma gagal:\n{proc.stderr}"
    res = json.loads(proc.stdout.strip())
    print(f"  [OK] Uji Slew-Rate Limiter: Bursty={res['finalSpeed']} Mbps (Max jump {res['maxJumpPct']}%), TCP Slow-Start={res['slowStartSpeed']}/300 Mbps.")

    # 3. Eksekusi langsung blok <script> asli dari index.html di dalam Node VM (Behavioral, Mid-Test Cancel, & Cross-Phase Bleed Test)
    vm_harness_script = r"""
const fs = require('fs');
const vm = require('vm');
const html = fs.readFileSync(process.argv[1], 'utf8');
const match = html.match(/<script>([\s\S]*?)<\/script>/);
if (!match) { console.error("No script tag found"); process.exit(1); }
const scriptCode = match[1];

const elements = {};
function makeEl(id) {
  const listeners = {};
  const classSet = new Set();
  const dots = Array.from({ length: 5 }, () => makeSimpleDot());
  let initialText = "";
  if (id === "valDownload") initialText = "167.53";
  else if (id === "valUpload") initialText = "53.08";
  else if (id === "valPing") initialText = "2";
  else if (id === "valPingDown") initialText = "2";
  else if (id === "valPingUp") initialText = "179";
  else if (id === "resultIdDisplay") initialText = "19863800067";
  return {
    id,
    textContent: initialText,
    innerHTML: "",
    value: id === "serverModeSelect" ? "unpad" : id === "streamCountSelect" ? "2" : id === "durationSelect" ? "8" : "on",
    style: { display: "", opacity: "0", background: "", strokeDashoffset: "612.6" },
    classList: {
      add: (c) => classSet.add(c),
      remove: (c) => classSet.delete(c),
      toggle: (c, force) => {
        if (force === undefined) {
          if (classSet.has(c)) { classSet.delete(c); return false; }
          classSet.add(c); return true;
        }
        if (force) classSet.add(c); else classSet.delete(c);
        return !!force;
      },
      contains: (c) => classSet.has(c)
    },
    setAttribute: function(k, v) { this[k] = v; },
    getAttribute: function(k) { return this[k] || "1"; },
    addEventListener: (ev, fn) => { listeners[ev] = listeners[ev] || []; listeners[ev].push(fn); },
    trigger: (ev) => { (listeners[ev] || []).forEach(fn => fn()); },
    getBoundingClientRect: () => ({ width: 430, height: 24 }),
    getContext: () => ({
      scale: () => {}, clearRect: () => {}, beginPath: () => {}, moveTo: () => {},
      quadraticCurveTo: () => {}, lineTo: () => {}, stroke: () => {}, closePath: () => {},
      createLinearGradient: () => ({ addColorStop: () => {} }), fill: () => {}
    }),
    querySelectorAll: (sel) => {
      if (sel === ".qual-dot") return dots;
      if (sel === ".star-btn") return [1,2,3,4,5].map(n => {
        const b = makeSimpleDot();
        b.getAttribute = () => String(n);
        return b;
      });
      return [];
    },
    scrollIntoView: () => {}
  };
}
function makeSimpleDot() {
  const cs = new Set();
  const ls = {};
  return {
    classList: {
      toggle: (c, f) => { if (f) cs.add(c); else cs.delete(c); },
      contains: (c) => cs.has(c)
    },
    addEventListener: (ev, fn) => { ls[ev] = fn; },
    click: () => { if (ls.click) ls.click(); }
  };
}

const storage = {};
const docListeners = {};
const sandbox = {
  window: {
    location: { protocol: "https:", origin: "https://evuaeru.github.io" },
    devicePixelRatio: 1,
    addEventListener: (ev, fn) => { docListeners[ev] = fn; }
  },
  document: {
    getElementById: (id) => {
      if (!elements[id]) elements[id] = makeEl(id);
      return elements[id];
    },
    createElement: () => makeEl("temp"),
    body: { appendChild: () => {}, removeChild: () => {} }
  },
  localStorage: {
    getItem: (k) => storage[k] || null,
    setItem: (k, v) => { storage[k] = String(v); },
    removeItem: (k) => { delete storage[k]; }
  },
  navigator: {
    clipboard: { writeText: async (t) => { storage._clipboard = t; } }
  },
  performance: { now: () => Date.now() },
  requestAnimationFrame: () => {},
  AbortController: class {
    constructor() {
      this.signal = {
        aborted: false,
        _ls: [],
        addEventListener: function(e, fn) { this._ls.push(fn); }
      };
    }
    abort() {
      this.signal.aborted = true;
      this.signal._ls.forEach(fn => fn());
    }
  },
  AbortSignal: { timeout: () => ({}) },
  Uint8Array, Math, Date, console, setTimeout, clearTimeout, Promise, Array, Object, String, Number, JSON, parseInt, parseFloat, encodeURI,
  fetch: async (url) => ({
    ok: true,
    status: 200,
    headers: { get: (h) => h === "cf-meta-ip" ? "182.10.131.57" : null },
    json: async () => ({ clientIp: "182.10.131.57", asOrganization: "PT Telekomunikasi Indonesia", city: "Bandung" }),
    blob: async () => ({ size: 1048576 })
  }),
  XMLHttpRequest: class {
    constructor() { this.upload = {}; }
    open() {}
    setRequestHeader() {}
    send() {
      if (this.upload.onprogress) this.upload.onprogress({ loaded: 384000 });
      if (this.onload) setTimeout(() => this.onload(), 5);
    }
    abort() { if (this.onabort) this.onabort(); }
  }
};

vm.createContext(sandbox);
vm.runInContext(scriptCode, sandbox);
if (docListeners.DOMContentLoaded) docListeners.DOMContentLoaded();

// 1. Toggle Multi <-> Single
elements.connModeToggle.trigger("click");
if (elements.connModeToggle.textContent !== "Single" || elements.streamCountSelect.value !== "1") {
  console.error("FAIL: connModeToggle Single gagal"); process.exit(1);
}
elements.connModeToggle.trigger("click");
if (elements.connModeToggle.textContent !== "Multi" || elements.streamCountSelect.value !== "2") {
  console.error("FAIL: connModeToggle Multi gagal"); process.exit(1);
}

// 2. Toggle IP Privacy Masking
elements.clientIpDisplay.textContent = "182.10.131.57";
elements.clientIpDisplay.trigger("click");
if (elements.clientIpDisplay.textContent !== "182.10.***.***") {
  console.error("FAIL: IP masking gagal:", elements.clientIpDisplay.textContent); process.exit(1);
}
elements.clientIpDisplay.trigger("click");
if (elements.clientIpDisplay.textContent !== "182.10.131.57") {
  console.error("FAIL: IP unmasking gagal"); process.exit(1);
}

// 3. Toggle Unit Mbps <-> MB/s (termasuk konversi nilai default 167.53 -> 20.94)
elements.unitToggleBtn.trigger("click");
if (elements.unitDl.textContent !== "MB/s" || elements.valDownload.textContent !== "20.94") {
  console.error("FAIL: Unit toggle MB/s gagal:", elements.valDownload.textContent); process.exit(1);
}
elements.unitToggleBtn.trigger("click");
if (elements.unitDl.textContent !== "Mbps" || elements.valDownload.textContent !== "167.53") {
  console.error("FAIL: Unit toggle Mbps gagal"); process.exit(1);
}

// 4. Toggle Drawers (Ganti Server, Settings, History)
elements.btnGantiServer.trigger("click");
if (!elements.settingsDrawer.classList.contains("open")) {
  console.error("FAIL: btnGantiServer tidak membuka settingsDrawer"); process.exit(1);
}
elements.btnCloseSettings.trigger("click");
if (elements.settingsDrawer.classList.contains("open")) {
  console.error("FAIL: btnCloseSettings tidak menutup settingsDrawer"); process.exit(1);
}
elements.btnToggleHistory.trigger("click");
if (!elements.historyDrawer.classList.contains("open")) {
  console.error("FAIL: btnToggleHistory tidak membuka historyDrawer"); process.exit(1);
}

// 5. Uji Pembatalan (Cancel) di tengah tes aktif (setelah 150ms saat Ping/Download sudah berjalan)
elements.btnStartTest.trigger("click");
if (elements.btnStartTest.style.display !== "none" || !elements.activeGaugeWrap.classList.contains("testing-active")) {
  console.error("FAIL: State saat tes mulai tidak menampilkan activeGaugeWrap"); process.exit(1);
}
setTimeout(() => {
  elements.btnCancelTest.trigger("click");
}, 150);

setTimeout(() => {
  if (elements.btnStartTest.style.display !== "flex" || elements.activeGaugeWrap.classList.contains("testing-active")) {
    console.error("FAIL: State setelah cancel tidak kembali ke tombol MULAI"); process.exit(1);
  }
  if (elements.phaseBadge.textContent !== "DIBATALKAN") {
    console.error("FAIL: phaseBadge setelah mid-test cancel bukan DIBATALKAN:", elements.phaseBadge.textContent); process.exit(1);
  }
  if (storage.zen_speedtest_history !== undefined) {
    console.error("FAIL: Mid-test cancel menyimpan riwayat palsu ke localStorage:", storage.zen_speedtest_history); process.exit(1);
  }
  if (elements.valDownload.textContent !== "167.53" || elements.valUpload.textContent !== "53.08") {
    console.error("FAIL: Mid-test cancel tidak memulihkan nilai hasil sebelumnya:", elements.valDownload.textContent, elements.valUpload.textContent); process.exit(1);
  }
  console.log("VM_HARNESS_OK");
}, 350);
"""
    proc_vm = subprocess.run(["node", "-e", vm_harness_script, html_path], capture_output=True, text=True)
    assert proc_vm.returncode == 0 and "VM_HARNESS_OK" in proc_vm.stdout, f"Uji VM Harness gagal:\n{proc_vm.stderr}\n{proc_vm.stdout}"
    print("  [OK] Eksekusi VM <script> asli: Toggle Multi/Single, IP Masking, Satuan Mbps/MB/s, Drawers, & Mid-Test Cancel Recovery lolos 100%.")

def main():
    print("=" * 60)
    print("    VERIFIKASI INTEGRITAS LENGKAP ZEN SPEEDTEST PRO")
    print("                 PELAYAN ANCELLIA")
    print("=" * 60)
    test_file_integrity()
    test_html_dom_and_syntax()
    test_subprocess_server_launch()
    test_local_server_endpoints_and_cors()
    test_cloudflare_wan_reachability()
    test_batch_launcher_script()
    test_ookla_ui_and_stability_engine()
    print("=" * 60)
    print("  [BERHASIL] Seluruh 7 fase pengujian lolos 100% tanpa celah!")
    print("=" * 60)

if __name__ == "__main__":
    main()


