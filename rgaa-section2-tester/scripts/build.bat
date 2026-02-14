@echo off
setlocal enabledelayedexpansion

echo ================================
echo RGAA Tester - Standalone Build
echo ================================
echo.

:: Move to project root (parent of scripts/)
cd /d "%~dp0\.."

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    exit /b 1
)

:: Check PyInstaller
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec
echo.

:: Ensure assets directory exists (required by PyInstaller datas)
if not exist assets (
    echo Creating assets directory...
    mkdir assets
)

:: Build the data flags
set "DATA_FLAGS=--add-data config.json;."
set "DATA_FLAGS=%DATA_FLAGS% --add-data assets;assets"

:: Include XLSX template if present
for %%f in (*.xlsx) do (
    set "DATA_FLAGS=!DATA_FLAGS! --add-data %%f;."
)

:: Include rgaa_tester package
set "DATA_FLAGS=%DATA_FLAGS% --add-data rgaa_tester;rgaa_tester"

:: Include criterion_10_7 package if present
if exist criterion_10_7 (
    set "DATA_FLAGS=%DATA_FLAGS% --add-data criterion_10_7;criterion_10_7"
)

echo Building executable...
python -m PyInstaller ^
    --name RGAATester ^
    --onedir ^
    --windowed ^
    --noconfirm ^
    %DATA_FLAGS% ^
    --hidden-import tkinter ^
    --hidden-import tkinter.ttk ^
    --hidden-import tkinter.messagebox ^
    --hidden-import tkinter.filedialog ^
    --hidden-import tkinter.scrolledtext ^
    --hidden-import beautifulsoup4 ^
    --hidden-import bs4 ^
    --hidden-import lxml ^
    --hidden-import requests ^
    --hidden-import odfpy ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    main.py

if errorlevel 1 (
    echo.
    echo Build failed!
    exit /b 1
)

echo.
echo ================================
echo Build successful!
echo Output: dist\RGAATester\
echo ================================
echo.
echo Run with: dist\RGAATester\RGAATester.exe
endlocal
