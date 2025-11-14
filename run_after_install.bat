@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Douyin Video Downloader

echo ========================================
echo   Douyin Video Downloader
echo ========================================
echo.

REM Tìm Python - ưu tiên python.org Python
set PYTHON_EXE=

REM Tìm trong AppData\Local\Programs\Python (python.org installation)
if exist "%LOCALAPPDATA%\Programs\Python" (
    for /f "delims=" %%i in ('dir /b /s /a-d "%LOCALAPPDATA%\Programs\Python\Python*\python.exe" 2^>nul') do (
        "%%i" --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_EXE=%%i
            goto :found
        )
    )
)

REM Tìm trong Program Files
if exist "C:\Program Files\Python" (
    for /f "delims=" %%i in ('dir /b /s /a-d "C:\Program Files\Python\Python*\python.exe" 2^>nul') do (
        "%%i" --version >nul 2>&1
        if not errorlevel 1 (
            set PYTHON_EXE=%%i
            goto :found
        )
    )
)

REM Thử python command (sau khi cài đặt python.org)
python --version >nul 2>&1
if not errorlevel 1 (
    for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do (
        if exist "%%i" (
            set PYTHON_EXE=%%i
            goto :found
        )
    )
    REM Nếu không lấy được path, thử dùng trực tiếp
    python -c "print('test')" >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_EXE=python
        goto :found
    )
)

REM Không tìm thấy
echo [ERROR] Không tìm thấy Python chính thức!
echo.
echo Vui lòng cài đặt Python từ https://www.python.org/downloads/
echo (Nhớ chọn "Add Python to PATH" khi cài đặt)
echo.
echo Sau khi cài đặt, khởi động lại máy tính và chạy lại file này.
echo.
pause
exit /b 1

:found
echo [INFO] Đã tìm thấy Python: !PYTHON_EXE!
!PYTHON_EXE! --version
echo.

echo [INFO] Đang kiểm tra dependencies...
echo.

REM Kiểm tra requests
!PYTHON_EXE! -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Đang cài đặt requests...
    echo.
    !PYTHON_EXE! -m pip install requests
    if errorlevel 1 (
        echo.
        echo [ERROR] Không thể cài đặt requests!
        echo Thử chạy với quyền Administrator
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [INFO] Đã cài đặt requests thành công!
    echo.
) else (
    echo [INFO] requests đã sẵn sàng!
    echo.
)

REM Kiểm tra opencv-python
!PYTHON_EXE! -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Đang cài đặt opencv-python...
    echo.
    REM Cài đặt numpy trước (nếu cần)
    !PYTHON_EXE! -c "import numpy" >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Đang cài đặt numpy...
        !PYTHON_EXE! -m pip install numpy --only-binary :all:
    )
    REM Cài đặt opencv-python
    !PYTHON_EXE! -m pip install opencv-python --only-binary :all:
    if errorlevel 1 (
        echo.
        echo [WARNING] Không thể cài đặt opencv-python!
        echo Tính năng lọc video theo hướng có thể không hoạt động đầy đủ.
        echo.
    ) else (
        echo.
        echo [INFO] Đã cài đặt opencv-python thành công!
        echo.
    )
) else (
    echo [INFO] opencv-python đã sẵn sàng!
    echo.
)

REM Chạy ứng dụng
echo [INFO] Đang khởi động ứng dụng...
echo.
!PYTHON_EXE! main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Ứng dụng đã dừng với lỗi!
    pause
)


