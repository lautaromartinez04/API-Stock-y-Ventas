@echo off
echo Activando entorno virtual...
call venv\Scripts\activate

if errorlevel 1 (
    echo ❌ No se pudo activar el entorno virtual. ¿Existe la carpeta "venv\Scripts\"?
    pause
    exit /b
)

echo Entorno virtual activado.
uvicorn main:app --host 127.0.0.1 --port 8000
echo Proceso finalizado.
pause