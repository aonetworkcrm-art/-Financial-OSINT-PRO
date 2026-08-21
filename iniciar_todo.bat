@echo off
echo ============================================
echo   NEXUS INTEL — Iniciar Todo
echo ============================================
echo.

taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [1/2] Limpiando cache...
cd /d "%~dp0"
for /d /r . %%d in (__pycache__) do rmdir /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul

echo [2/2] Iniciando servidores...
echo.

echo   Landing + Ventas: http://localhost:5002
start /B python web/server.py

echo   Herramienta OSINT: http://localhost:8502
start /B python -m streamlit run app.py --server.port 8502 --server.headless true

echo.
echo ============================================
echo   AMBOS SERVIDORES INICIADOS
echo ============================================
echo.
echo   Landing Page:  http://localhost:5002
echo   Admin Panel:   http://localhost:5002/admin
echo   Herramienta:   http://localhost:8502
echo.
echo   Admin Login: admin / admin123
echo.
echo   Presiona Ctrl+C para detener todo
echo ============================================
pause
