@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado. Criando .venv...
    python -m venv .venv
    call ".venv\Scripts\activate.bat"
    pip install -r requirements.txt
) else (
    call ".venv\Scripts\activate.bat"
)

streamlit run app.py

pause
