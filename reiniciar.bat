@echo off
echo =============================================
echo   Reiniciando Financial OSINT Tool...
echo =============================================
echo.

echo [1/3] Matar procesos anteriores...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] Limpiar caché...
cd /d C:\financial-osint
if exist __pycache__ rmdir /s /q __pycache__
if exist engines\__pycache__ rmdir /s /q engines\__pycache__
if exist core\__pycache__ rmdir /s /q core\__pycache__
echo Caché limpiado.

echo [3/3] Iniciando servidor...
python -m streamlit run app.py --server.port 8502 --server.headless true --server.fileWatcherType none

pause
