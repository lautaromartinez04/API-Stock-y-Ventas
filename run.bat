@echo off
echo Activando entorno virtual...
call venv\Scripts\activate

if errorlevel 1 (
    echo ❌ No se pudo activar el entorno virtual. ¿Existe la carpeta "venv\Scripts\"?
    pause
    exit /b
)

echo Entorno virtual activado.
echo Iniciando Uvicorn en todas las interfaces de red...
uvicorn main:app --host 0.0.0.0 --port 8000
echo Proceso finalizado.
pause