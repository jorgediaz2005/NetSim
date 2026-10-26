@echo off
cd /d "%~dp0"
echo ==========================================
echo   NetSim - Simulador de redes informaticas
echo ==========================================
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo No se pudieron instalar las dependencias. Comprueba que Python esta instalado y que tienes Internet.
    pause
    exit /b 1
)
python -m streamlit run app.py
if errorlevel 1 (
    echo.
    echo NetSim no pudo iniciarse. Revisa el mensaje de error anterior.
    pause
)
