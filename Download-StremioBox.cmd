@echo off
rem SPDX-License-Identifier: MIT
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\download.ps1" -OutputDirectory "%~dp0downloads"
if errorlevel 1 (
    echo.
    echo Download failed. Read the error above before trying again.
    pause
    exit /b 1
)
echo.
echo Your verified ISO is in the downloads folder.
pause
