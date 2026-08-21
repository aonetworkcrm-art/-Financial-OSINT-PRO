@echo off
echo ============================================
echo   NEXUS INTEL — Solo Landing Page
echo ============================================
echo.

taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

cd /d "%~dp0"
for /d /r . %%d in (__pycache__) do rmdir /s /q "%%d" 2>nul

echo Iniciando servidor web en puerto 5002...
echo.
echo   Landing Page:  http://localhost:5002
echo   Admin Panel:   http://localhost:5002/admin
echo.
echo   Admin Login: admin / admin123
echo.
python web/server.py
pause
