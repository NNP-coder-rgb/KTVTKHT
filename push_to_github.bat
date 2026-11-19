@echo off
chcp 65001 > nul
title Đẩy mã nguồn lên GitHub - PTTKHT
echo ====================================================================
echo  ĐẨY MÃ NGUỒN DỰ ÁN LÊN GITHUB
echo ====================================================================
echo.

set /p REPO_URL="Nhập URL repository GitHub của bạn (ví dụ: https://github.com/NNP-coder-rgb/PTTKHT.git): "

if "%REPO_URL%"=="" (
    echo [LỖI] URL không được để trống!
    pause
    exit /b
)

echo.
echo Đang cấu hình remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo Đang đẩy nhánh main lên GitHub...
git branch -M main
git push -u origin main

echo.
echo ====================================================================
echo Hoàn tất! Nhấn phím bất kỳ để thoát.
pause
