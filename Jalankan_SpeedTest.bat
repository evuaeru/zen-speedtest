@echo off
title Zen SpeedTest Pro - Master Zay
color 0B
cd /d "%~dp0"

echo ======================================================================
echo                 ZEN SPEEDTEST PRO - PELAYAN ANCELLIA
echo ======================================================================
echo.
echo Sedang menyiapkan server pengukur kecepatan jaringan untuk Master Zay...
echo.

:: 1. Coba Python Launcher (py -3)
py -3 --version >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [i] Menjalankan server menggunakan Python Launcher (py -3)...
    py -3 speedtest_server.py
    goto end
)

:: 2. Coba instalasi langsung Python user di %LOCALAPPDATA%
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    echo [i] Menjalankan server menggunakan Python 3.11 (%LOCALAPPDATA%)...
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" speedtest_server.py
    goto end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    echo [i] Menjalankan server menggunakan Python 3.12 (%LOCALAPPDATA%)...
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" speedtest_server.py
    goto end
)

:: 3. Coba perintah python umum di PATH (validasi eksekusi riil, bukan stub Microsoft Store)
python -c "import sys" >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [i] Menjalankan server menggunakan python sistem...
    python speedtest_server.py
    goto end
)

:: 4. Fallback jika Python tidak terpasang: buka antarmuka langsung di browser
echo [!] Python tidak terdeteksi aktif di sistem.
echo [*] Membuka Zen SpeedTest langsung di peramban web (Mode Standalone Browser)...
start "" "%~dp0index.html"

:end
echo.
echo Server selesai atau ditutup. Tekan sembarang tombol untuk keluar...
pause >nul
