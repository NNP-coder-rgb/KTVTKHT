@echo off
chcp 65001 > nul
title HỆ THỐNG PHÂN LOẠI PHẢN HỒI SINH VIÊN BẰNG AI - PTTKHT
echo ====================================================================
echo  HỆ THỐNG PHÂN LOẠI PHẢN HỒI CỦA SINH VIÊN BẰNG AI
echo  Môn học: Phân tích và Thiết kế Hệ thống (PTTKHT)
echo  Thành viên: Nguyễn Ngọc Phúc - Hà Minh Diệu (C)
echo ====================================================================
echo.
echo Đang kích hoạt môi trường ảo và khởi động máy chủ FastAPI...
echo Mở trình duyệt tại: http://127.0.0.1:8000
echo.

if exist ".\venv\Scripts\python.exe" (
    .\venv\Scripts\python.exe run.py
) else (
    python run.py
)

pause
